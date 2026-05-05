from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings
from app.repositories.json_action_item_repository import JsonActionItemRepository
from app.repositories.json_insight_repository import JsonInsightRepository
from app.repositories.json_meeting_repository import JsonMeetingRepository
from app.services.action_items import ActionItemService
from app.services.dashboard import DashboardService
from app.services.insights import InsightService
from app.services.meetings import MeetingService


@dataclass(slots=True)
class ServiceContainer:
    meetings: MeetingService
    insights: InsightService
    action_items: ActionItemService
    dashboard: DashboardService


def build_services(settings: Settings) -> ServiceContainer:
    settings.data_dir.mkdir(parents=True, exist_ok=True)

    meeting_repository = JsonMeetingRepository(settings.data_dir / "meetings.json")
    action_item_repository = JsonActionItemRepository(settings.data_dir / "action_items.json")
    insight_repository = JsonInsightRepository(settings.data_dir / "insights.json")

    action_items = ActionItemService(action_item_repository, meeting_repository)
    meetings = MeetingService(
        meeting_repository,
        action_item_repository,
        insight_repository,
        settings,
    )
    insights = InsightService(
        meeting_repository=meeting_repository,
        insight_repository=insight_repository,
        action_item_repository=action_item_repository,
        settings=settings,
    )
    dashboard = DashboardService(meeting_service=meetings, action_item_service=action_items)

    return ServiceContainer(
        meetings=meetings,
        insights=insights,
        action_items=action_items,
        dashboard=dashboard,
    )
