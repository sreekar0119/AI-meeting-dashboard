from __future__ import annotations

import json
from datetime import date, datetime, timezone
from urllib import request

from app.errors import NotFoundError
from app.repositories.contracts import ActionItemRepository, InsightRepository, MeetingRepository
from app.schemas import (
    ActionItem,
    ActionItemStatus,
    Meeting,
    MeetingCreateInput,
    MeetingDetailResponse,
    MeetingListItem,
    MeetingMetadataDraft,
)
from app.config import Settings
from app.utils.ids import generate_id


class OpenAIMeetingMetadataGenerator:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate(self, transcript: str) -> MeetingMetadataDraft:
        prompt = (
            "Extract meeting metadata as JSON with keys title, date, participants. "
            "title should be a short descriptive meeting title. "
            "date should be ISO format YYYY-MM-DD if explicitly mentioned, otherwise null. "
            "Do not infer or guess the date; only use dates found in the transcript. "
            "participants should be an array of distinct participant names found in the transcript. "
            "Use only names that appear in speaker labels or are clearly referred to as participants. "
            f"Transcript:\n{transcript}"
        )
        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a precise meeting metadata extractor. Return valid JSON only. "
                        "Do not invent participants."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
        }
        request_body = json.dumps(payload).encode("utf-8")
        api_request = request.Request(
            url="https://api.openai.com/v1/chat/completions",
            data=request_body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with request.urlopen(api_request, timeout=30) as response:
            raw_body = response.read().decode("utf-8")
        parsed_body = json.loads(raw_body)
        content = parsed_body["choices"][0]["message"]["content"]
        parsed_content = json.loads(content)
        return MeetingMetadataDraft.model_validate(parsed_content)


class MeetingService:
    def __init__(
        self,
        meeting_repository: MeetingRepository,
        action_item_repository: ActionItemRepository,
        insight_repository: InsightRepository,
        settings: Settings,
    ) -> None:
        self.meeting_repository = meeting_repository
        self.action_item_repository = action_item_repository
        self.insight_repository = insight_repository
        self.settings = settings

    def create_meeting(self, payload: MeetingCreateInput) -> Meeting:
        now = datetime.now(timezone.utc)
        metadata = self._resolve_metadata(payload)
        meeting = Meeting(
            id=generate_id("mtg"),
            title=metadata.title,
            date=metadata.date,
            participants=metadata.participants,
            transcript=payload.transcript,
            created_at=now,
            updated_at=now,
        )
        return self.meeting_repository.create(meeting)

    def _resolve_metadata(self, payload: MeetingCreateInput) -> MeetingMetadataDraft:
        if payload.title and payload.date and payload.participants:
            return MeetingMetadataDraft(
                title=payload.title,
                date=payload.date,
                participants=payload.participants,
            )

        if not self.settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required to infer meeting metadata.")

        generator = OpenAIMeetingMetadataGenerator(
            api_key=self.settings.openai_api_key,
            model=self.settings.openai_model,
        )
        metadata = generator.generate(payload.transcript)

        if payload.title:
            metadata.title = payload.title
        if payload.date:
            metadata.date = payload.date
        if payload.participants:
            metadata.participants = payload.participants

        if not metadata.date:
            metadata.date = date.today()

        return metadata

    def get_meeting(self, meeting_id: str) -> Meeting:
        meeting = self.meeting_repository.get(meeting_id)
        if meeting is None:
            raise NotFoundError(f"Meeting '{meeting_id}' was not found.")
        return meeting

    def get_meeting_detail(self, meeting_id: str) -> MeetingDetailResponse:
        meeting = self.get_meeting(meeting_id)
        insight = self.insight_repository.get_by_meeting(meeting_id)
        action_items = [
            item
            for item in self.action_item_repository.list()
            if item.meeting_id == meeting_id
        ]
        action_items.sort(key=self._action_item_sort_key)
        return MeetingDetailResponse(
            meeting=meeting,
            insight=insight,
            action_items=action_items,
        )

    def list_meetings(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        participant: str | None = None,
        owner: str | None = None,
        status: ActionItemStatus | None = None,
    ) -> list[MeetingListItem]:
        meetings = self.meeting_repository.list()
        action_items = self.action_item_repository.list()
        insights = {insight.meeting_id: insight for insight in self.insight_repository.list()}
        today = date.today()

        results: list[MeetingListItem] = []
        for meeting in meetings:
            if date_from and meeting.date < date_from:
                continue
            if date_to and meeting.date > date_to:
                continue
            if participant and participant.lower() not in {name.lower() for name in meeting.participants}:
                continue

            related_items = [item for item in action_items if item.meeting_id == meeting.id]
            if owner and not any(item.owner.lower() == owner.lower() for item in related_items):
                continue
            if status and not any(item.status == status for item in related_items):
                continue

            results.append(
                MeetingListItem(
                    **meeting.model_dump(),
                    action_item_count=len(related_items),
                    open_action_item_count=sum(
                        1 for item in related_items if item.status == ActionItemStatus.OPEN
                    ),
                    completed_action_item_count=sum(
                        1 for item in related_items if item.status == ActionItemStatus.COMPLETE
                    ),
                    overdue_action_item_count=0,
                    has_insights=meeting.id in insights,
                    summary_short=insights[meeting.id].summary_short if meeting.id in insights else None,
                )
            )

        return sorted(results, key=lambda meeting: (meeting.date, meeting.created_at), reverse=True)

    def delete_meeting(self, meeting_id: str) -> None:
        self.get_meeting(meeting_id)
        self.action_item_repository.delete_by_meeting(meeting_id)
        self.insight_repository.delete_by_meeting(meeting_id)
        deleted = self.meeting_repository.delete(meeting_id)
        if not deleted:
            raise NotFoundError(f"Meeting '{meeting_id}' was not found.")

    def _action_item_sort_key(self, item: ActionItem) -> tuple[str]:
        return (item.status.value,)
