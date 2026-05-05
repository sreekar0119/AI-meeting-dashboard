from __future__ import annotations

from typing import Protocol

from app.schemas import ActionItem, Insight, Meeting


class MeetingRepository(Protocol):
    def list(self) -> list[Meeting]:
        ...

    def get(self, meeting_id: str) -> Meeting | None:
        ...

    def create(self, meeting: Meeting) -> Meeting:
        ...

    def delete(self, meeting_id: str) -> bool:
        ...


class ActionItemRepository(Protocol):
    def list(self) -> list[ActionItem]:
        ...

    def get(self, item_id: str) -> ActionItem | None:
        ...

    def create(self, item: ActionItem) -> ActionItem:
        ...

    def update(self, item: ActionItem) -> ActionItem:
        ...

    def delete(self, item_id: str) -> bool:
        ...

    def delete_by_meeting(self, meeting_id: str) -> int:
        ...

    def replace_generated_for_meeting(
        self, meeting_id: str, generated_items: list[ActionItem]
    ) -> list[ActionItem]:
        ...


class InsightRepository(Protocol):
    def list(self) -> list[Insight]:
        ...

    def get_by_meeting(self, meeting_id: str) -> Insight | None:
        ...

    def upsert(self, insight: Insight) -> Insight:
        ...

    def delete_by_meeting(self, meeting_id: str) -> bool:
        ...
