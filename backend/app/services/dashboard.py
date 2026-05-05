from __future__ import annotations

from app.schemas import ActionItemStatus, DashboardSummary
from app.services.action_items import ActionItemService
from app.services.meetings import MeetingService


class DashboardService:
    def __init__(
        self,
        meeting_service: MeetingService,
        action_item_service: ActionItemService,
    ) -> None:
        self.meeting_service = meeting_service
        self.action_item_service = action_item_service

    def get_summary(self) -> DashboardSummary:
        meetings = self.meeting_service.list_meetings()
        action_items = self.action_item_service.list_action_items()
        return DashboardSummary(
            total_meetings=len(meetings),
            open_tasks=sum(1 for item in action_items if item.status == ActionItemStatus.OPEN),
            in_progress_tasks=sum(
                1 for item in action_items if item.status == ActionItemStatus.IN_PROGRESS
            ),
            completed_tasks=sum(
                1 for item in action_items if item.status == ActionItemStatus.COMPLETE
            ),
            overdue_tasks=len(self.action_item_service.list_action_items(overdue=True)),
            recent_meetings=meetings[:5],
            overdue_action_items=self.action_item_service.list_action_items(overdue=True)[:6],
        )
