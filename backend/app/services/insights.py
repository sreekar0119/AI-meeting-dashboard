from __future__ import annotations

from datetime import date, datetime, timezone
import json
from pathlib import Path
import re
from typing import Iterable
from urllib import error, request

from app.config import Settings
from app.errors import NotFoundError
from app.repositories.contracts import ActionItemRepository, InsightRepository, MeetingRepository
from app.schemas import (
    ActionItem,
    ActionItemStatus,
    GeneratedActionItem,
    Insight,
    InsightDraft,
    ItemSource,
    Meeting,
    Priority,
)
from app.utils.ids import generate_id

DECISION_KEYWORDS = (
    "decided",
    "decision",
    "agreed",
    "approved",
    "confirmed",
    "move forward",
    "signed off",
    "go live",
)
BLOCKER_KEYWORDS = (
    "blocker",
    "blocked",
    "risk",
    "issue",
    "dependency",
    "waiting",
    "delay",
    "concern",
)
ACTION_PATTERN = re.compile(
    r"action\s*:\s*(?P<owner>[^:-]+?)\s*[-:]\s*(?P<task>.*?)(?:\s+(?:by|before|on)\s+(?P<due>\d{4}-\d{2}-\d{2}))?$",
    re.IGNORECASE,
)
FOLLOW_UP_PATTERN = re.compile(
    r"(?P<owner>[A-Z][A-Za-z .'-]+?)\s+(?:will|needs to|should)\s+(?P<task>.*?)(?:\s+(?:by|before|on)\s+(?P<due>\d{4}-\d{2}-\d{2}))?$",
    re.IGNORECASE,
)
SPEAKER_PATTERN = re.compile(r"^[A-Z][A-Za-z .'-]{1,30}:\s*")


class MockInsightGenerator:
    def generate(self, meeting: Meeting) -> InsightDraft:
        sentences = self._extract_sentences(meeting.transcript)
        decisions = self._extract_labeled_items(sentences, DECISION_KEYWORDS, limit=4)
        blockers = self._extract_labeled_items(sentences, BLOCKER_KEYWORDS, limit=4)
        action_items = self._extract_action_items(meeting, decisions, blockers)

        headline = sentences[0] if sentences else meeting.title
        summary_short = (
            f"{meeting.title}: {headline[:120]}. "
            f"{len(decisions)} decisions, {len(blockers)} blockers, and {len(action_items)} action items were captured."
        )
        summary_detailed = " ".join(sentences[:5])[:1000]
        if len(summary_detailed) < 20:
            summary_detailed = (
                f"The team reviewed {meeting.title.lower()} and aligned on follow-up work "
                f"for {', '.join(meeting.participants[:3])}."
            )

        if not decisions:
            decisions = [
                f"The team aligned on the next steps for {meeting.title.lower()}."
            ]
        return InsightDraft(
            summary_short=summary_short,
            summary_detailed=summary_detailed,
            decisions=decisions,
            blockers=blockers,
            action_items=action_items,
        )

    def _extract_sentences(self, transcript: str) -> list[str]:
        prepared = transcript.replace("\r", "\n")
        raw_parts = re.split(r"[\n]+|(?<=[.!?])\s+", prepared)
        sentences: list[str] = []
        for raw_part in raw_parts:
            cleaned = SPEAKER_PATTERN.sub("", raw_part).strip(" -*")
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            if cleaned and cleaned not in sentences:
                sentences.append(cleaned)
        return sentences

    def _extract_labeled_items(
        self, sentences: Iterable[str], keywords: tuple[str, ...], limit: int
    ) -> list[str]:
        matches: list[str] = []
        for sentence in sentences:
            lowered = sentence.lower()
            if any(keyword in lowered for keyword in keywords):
                normalized = sentence.rstrip(".") + "."
                if normalized not in matches:
                    matches.append(normalized)
            if len(matches) >= limit:
                break
        return matches

    def _extract_action_items(
        self,
        meeting: Meeting,
        decisions: list[str],
        blockers: list[str],
    ) -> list[GeneratedActionItem]:
        transcript_sentences = self._extract_sentences(meeting.transcript)
        participants = meeting.participants
        extracted: list[GeneratedActionItem] = []
        seen_signatures: set[str] = set()

        for sentence in transcript_sentences:
            content = sentence.strip()
            match = ACTION_PATTERN.search(content) or FOLLOW_UP_PATTERN.search(content)
            direct_assignment = None if match else self._extract_direct_assignment(content, participants)
            if direct_assignment is not None:
                match = direct_assignment
            if not match:
                continue
            owner = self._match_owner(match.group("owner"), participants)
            task_text = match.group("task").strip().rstrip(".")
            task_text = self._clean_task_text(task_text)
            signature = f"{owner.lower()}::{task_text.lower()}"
            if task_text and signature not in seen_signatures:
                extracted.append(
                    GeneratedActionItem(
                        owner=owner,
                        task=task_text,
                        priority=self._infer_priority(task_text),
                    )
                )
                seen_signatures.add(signature)

        if not extracted:
            owners = participants or ["Team"]
            for index, sentence in enumerate((blockers + decisions)[:3]):
                owner = owners[index % len(owners)]
                task = (
                    f"Resolve: {sentence[:110]}" if sentence in blockers else f"Follow through on: {sentence[:110]}"
                )
                signature = f"{owner.lower()}::{task.lower()}"
                if signature in seen_signatures:
                    continue
                extracted.append(
                    GeneratedActionItem(
                        owner=owner,
                        task=task,
                        priority=Priority.HIGH if sentence in blockers else Priority.MEDIUM,
                    )
                )
                seen_signatures.add(signature)

        return extracted[:6]

    def _match_owner(self, raw_owner: str, participants: list[str]) -> str:
        lowered_owner = raw_owner.lower()
        for participant in participants:
            if participant.lower() in lowered_owner or lowered_owner in participant.lower():
                return participant
        return raw_owner.strip().title()[:80]

    def _extract_direct_assignment(self, sentence: str, participants: list[str]) -> re.Match[str] | None:
        lowered_sentence = sentence.lower()
        for participant in participants:
            prefix = f"{participant.lower()},"
            if not lowered_sentence.startswith(prefix):
                continue

            remainder = sentence[len(participant) + 1 :].strip()
            remainder = re.sub(
                r"^(?:can you|could you|would you|please|kindly|go ahead and)\s+",
                "",
                remainder,
                flags=re.IGNORECASE,
            )
            remainder = remainder.strip()
            if not remainder:
                continue

            match = re.match(
                r"(?P<owner>.+?)\s*:\s*(?P<task>.+?)$",
                f"{participant}: {remainder}",
            )
            if match:
                return match

            class _DirectAssignmentMatch:
                def __init__(self, owner: str, task: str) -> None:
                    self._owner = owner
                    self._task = task

                def group(self, key: str) -> str:
                    if key == "owner":
                        return self._owner
                    if key == "task":
                        return self._task
                    raise KeyError(key)

                def groupdict(self) -> dict[str, str | None]:
                    return {"owner": self._owner, "task": self._task, "due": None}

            return _DirectAssignmentMatch(participant, remainder)  # type: ignore[return-value]

        return None

    def _clean_task_text(self, task_text: str) -> str:
        cleaned = re.sub(
            r"^(?:can you|could you|would you|please|kindly|go ahead and)\s+",
            "",
            task_text,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"^(?:to\s+)", "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()

    def _infer_priority(self, task_text: str) -> Priority:
        lowered = task_text.lower()
        if any(keyword in lowered for keyword in ("urgent", "critical", "today", "blocker")):
            return Priority.HIGH
        if any(keyword in lowered for keyword in ("later", "backlog", "optional")):
            return Priority.LOW
        return Priority.MEDIUM 


class OpenAIInsightGenerator:
    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate(self, meeting: Meeting) -> InsightDraft:
        prompt = (
            "Extract structured meeting insights as JSON with keys "
            "summary_short, summary_detailed, decisions, blockers, action_items. "
            "action_items must be an array of objects with owner, task, priority. "
            "Keep priority in {high, medium, low}. "
            f"Meeting title: {meeting.title}\n"
            f"Meeting date: {meeting.date.isoformat()}\n"
            f"Participants: {', '.join(meeting.participants)}\n"
            f"Transcript:\n{meeting.transcript}"
        )
        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a precise meeting analyst. Return valid JSON only. "
                        "Keep summaries concise and preserve concrete decisions, blockers, and action items."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
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
        normalized_content = self._normalize_payload(parsed_content)
        return InsightDraft.model_validate(normalized_content)

    def _normalize_payload(self, payload: dict) -> dict:
        normalized = dict(payload)
        action_items = normalized.get("action_items")
        if isinstance(action_items, list):
            normalized["action_items"] = [
                item
                for item in (self._normalize_action_item(action_item) for action_item in action_items)
                if item is not None
            ]
        return normalized

    def _normalize_action_item(self, item: object) -> dict | None:
        if not isinstance(item, dict):
            return None

        owner = str(item.get("owner", "")).strip()
        task = str(item.get("task", "")).strip()
        if not owner or not task:
            return None
        if len(owner) > 80 or len(task) > 220:
            return None

        priority = item.get("priority", Priority.MEDIUM.value)
        return {
            "owner": owner,
            "task": task,
            "priority": priority,
        }


class InsightService:
    def __init__(
        self,
        meeting_repository: MeetingRepository,
        insight_repository: InsightRepository,
        action_item_repository: ActionItemRepository,
        settings: Settings,
    ) -> None:
        self.meeting_repository = meeting_repository
        self.insight_repository = insight_repository
        self.action_item_repository = action_item_repository
        self.settings = settings

    def get_insights_for_meeting(self, meeting_id: str) -> Insight | None:
        return self.insight_repository.get_by_meeting(meeting_id)

    def generate_insights(self, meeting_id: str) -> Insight:
        meeting = self.meeting_repository.get(meeting_id)
        if meeting is None:
            raise NotFoundError(f"Meeting '{meeting_id}' was not found.")

        draft = self._generate_draft(meeting)
        previous = self.insight_repository.get_by_meeting(meeting_id)
        generated_at = datetime.now(timezone.utc)
        insight = Insight(
            id=previous.id if previous else generate_id("ins"),
            meeting_id=meeting.id,
            generated_at=generated_at,
            summary_short=draft.summary_short,
            summary_detailed=draft.summary_detailed,
            decisions=draft.decisions,
            blockers=draft.blockers,
            action_items=draft.action_items,
        )
        saved = self.insight_repository.upsert(insight)
        self._sync_generated_action_items(meeting, saved, generated_at)
        return saved

    def _generate_draft(self, meeting: Meeting) -> InsightDraft:
        if not self.settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required to generate insights.")

        generator = OpenAIInsightGenerator(
            api_key=self.settings.openai_api_key,
            model=self.settings.openai_model,
        )
        return generator.generate(meeting)

    def _sync_generated_action_items(
        self,
        meeting: Meeting,
        insight: Insight,
        generated_at: datetime,
    ) -> None:
        existing_items = self.action_item_repository.list()
        existing_generated = {
            self._signature(item.owner, item.task): item
            for item in existing_items
            if item.meeting_id == meeting.id and item.source == ItemSource.INSIGHT
        }
        generated_items: list[ActionItem] = []
        for suggestion in insight.action_items:
            signature = self._signature(suggestion.owner, suggestion.task)
            existing = existing_generated.get(signature)
            generated_items.append(
                ActionItem(
                    id=existing.id if existing else generate_id("act"),
                    meeting_id=meeting.id,
                    owner=suggestion.owner,
                    task=suggestion.task,
                    priority=suggestion.priority,
                    status=existing.status if existing else ActionItemStatus.OPEN,
                    source=ItemSource.INSIGHT,
                    insight_id=insight.id,
                    created_at=existing.created_at if existing else generated_at,
                    updated_at=generated_at,
                )
            )
        self.action_item_repository.replace_generated_for_meeting(meeting.id, generated_items)

    def _signature(self, owner: str, task: str) -> str:
        return f"{owner.strip().lower()}::{task.strip().lower()}"
