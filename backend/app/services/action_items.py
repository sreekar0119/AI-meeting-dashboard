from __future__ import annotations

from datetime import datetime, timezone

from app.errors import NotFoundError
from app.repositories.contracts import ActionItemRepository, MeetingRepository
from app.schemas import (
    ActionItem,
    ActionItemCreate,
    ActionItemStatus,
    ActionItemUpdate,
    Priority,
)
from app.utils.ids import generate_id


class ActionItemService:
    def __init__(
        self,
        action_item_repository: ActionItemRepository,
        meeting_repository: MeetingRepository,
    ) -> None:
        self.action_item_repository = action_item_repository
        self.meeting_repository = meeting_repository

    def list_action_items(
        self,
        meeting_id: str | None = None,
        owner: str | None = None,
        status: ActionItemStatus | None = None,
        priority: Priority | None = None,
        overdue: bool | None = None,
    ) -> list[ActionItem]:
        items = self.action_item_repository.list()
        filtered: list[ActionItem] = []
        for item in items:
            if meeting_id and item.meeting_id != meeting_id:
                continue
            if owner and item.owner.lower() != owner.lower():
                continue
            if status and item.status != status:
                continue
            if priority and item.priority != priority:
                continue
            if overdue is not None:
                continue
            filtered.append(item)
        return sorted(
            filtered,
            key=lambda item: (
                item.priority.value,
                item.created_at,
            ),
        )

    def create_action_item(self, payload: ActionItemCreate) -> ActionItem:
        self._require_meeting(payload.meeting_id)
        now = datetime.now(timezone.utc)
        item = ActionItem(
            id=generate_id("act"),
            meeting_id=payload.meeting_id,
            owner=payload.owner,
            task=payload.task,
            priority=payload.priority,
            status=payload.status,
            source=payload.source,
            insight_id=payload.insight_id,
            created_at=now,
            updated_at=now,
        )
        return self.action_item_repository.create(item)

    def get_action_item(self, item_id: str) -> ActionItem:
        item = self.action_item_repository.get(item_id)
        if item is None:
            raise NotFoundError(f"Action item '{item_id}' was not found.")
        return item

    def update_action_item(self, item_id: str, payload: ActionItemUpdate) -> ActionItem:
        current = self.get_action_item(item_id)
        changes = payload.model_dump(exclude_unset=True)
        updated = current.model_copy(
            update={
                **changes,
                "updated_at": datetime.now(timezone.utc),
            }
        )
        return self.action_item_repository.update(updated)

    def update_status(self, item_id: str, status: ActionItemStatus) -> ActionItem:
        current = self.get_action_item(item_id)
        updated = current.model_copy(
            update={
                "status": status,
                "updated_at": datetime.now(timezone.utc),
            }
        )
        return self.action_item_repository.update(updated)

    def delete_action_item(self, item_id: str) -> None:
        deleted = self.action_item_repository.delete(item_id)
        if not deleted:
            raise NotFoundError(f"Action item '{item_id}' was not found.")

    def _require_meeting(self, meeting_id: str) -> None:
        if self.meeting_repository.get(meeting_id) is None:
            raise NotFoundError(f"Meeting '{meeting_id}' was not found.")
