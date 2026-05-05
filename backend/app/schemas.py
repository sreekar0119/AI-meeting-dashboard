from __future__ import annotations

from datetime import date as Date, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionItemStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class ItemSource(str, Enum):
    MANUAL = "manual"
    INSIGHT = "insight"


class MeetingCreateInput(BaseModel):
    transcript: str = Field(min_length=20, max_length=20000)
    title: str | None = Field(default=None, min_length=3, max_length=120)
    date: Date | None = None
    participants: list[str] | None = Field(default=None, max_length=20)

    @field_validator("title", "transcript")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be empty.")
        return stripped

    @field_validator("participants")
    @classmethod
    def normalize_participants(cls, participants: list[str] | None) -> list[str] | None:
        if participants is None:
            return None
        cleaned: list[str] = []
        for participant in participants:
            name = participant.strip()
            if name and name not in cleaned:
                cleaned.append(name)
        if not cleaned:
            raise ValueError("At least one participant is required.")
        return cleaned


class Meeting(BaseModel):
    title: str
    date: Date
    participants: list[str]
    transcript: str
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MeetingMetadataDraft(BaseModel):
    title: str = Field(min_length=3, max_length=120)
    date: Date | None = None
    participants: list[str] = Field(min_length=1, max_length=20)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be empty.")
        return stripped

    @field_validator("participants")
    @classmethod
    def normalize_participants(cls, participants: list[str]) -> list[str]:
        cleaned: list[str] = []
        for participant in participants:
            name = participant.strip()
            if name and name not in cleaned:
                cleaned.append(name)
        if not cleaned:
            raise ValueError("At least one participant is required.")
        return cleaned


class GeneratedActionItem(BaseModel):
    owner: str = Field(min_length=2, max_length=80)
    task: str = Field(min_length=5, max_length=220)
    priority: Priority = Priority.MEDIUM

    @field_validator("owner", "task")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be empty.")
        return stripped


class InsightDraft(BaseModel):
    summary_short: str = Field(min_length=10, max_length=300)
    summary_detailed: str = Field(min_length=20, max_length=1200)
    decisions: list[str] = Field(default_factory=list, max_length=10)
    blockers: list[str] = Field(default_factory=list, max_length=10)
    action_items: list[GeneratedActionItem] = Field(default_factory=list, max_length=12)

    @field_validator("summary_short", "summary_detailed")
    @classmethod
    def strip_summaries(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be empty.")
        return stripped


class Insight(InsightDraft):
    id: str
    meeting_id: str
    generated_at: datetime


class ActionItemBase(BaseModel):
    meeting_id: str
    owner: str = Field(min_length=2, max_length=80)
    task: str = Field(min_length=5, max_length=220)
    priority: Priority = Priority.MEDIUM
    status: ActionItemStatus = ActionItemStatus.OPEN

    @field_validator("meeting_id", "owner", "task")
    @classmethod
    def strip_fields(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be empty.")
        return stripped


class ActionItemCreate(ActionItemBase):
    source: ItemSource = ItemSource.MANUAL
    insight_id: str | None = None


class ActionItemUpdate(BaseModel):
    owner: str | None = Field(default=None, min_length=2, max_length=80)
    task: str | None = Field(default=None, min_length=5, max_length=220)
    priority: Priority | None = None
    status: ActionItemStatus | None = None

    @field_validator("owner", "task")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("Field cannot be empty.")
        return stripped


class ActionItemStatusUpdate(BaseModel):
    status: ActionItemStatus


class ActionItem(ActionItemBase):
    id: str
    source: ItemSource = ItemSource.MANUAL
    insight_id: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MeetingListItem(Meeting):
    action_item_count: int = 0
    open_action_item_count: int = 0
    completed_action_item_count: int = 0
    overdue_action_item_count: int = 0
    has_insights: bool = False
    summary_short: str | None = None


class MeetingDetailResponse(BaseModel):
    meeting: Meeting
    insight: Insight | None = None
    action_items: list[ActionItem] = Field(default_factory=list)


class DashboardSummary(BaseModel):
    total_meetings: int
    open_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    overdue_tasks: int
    recent_meetings: list[MeetingListItem]
    overdue_action_items: list[ActionItem]


class HealthResponse(BaseModel):
    status: str


class DeleteResponse(BaseModel):
    deleted: bool
