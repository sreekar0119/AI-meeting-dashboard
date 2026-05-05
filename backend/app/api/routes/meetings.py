from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_services
from app.errors import NotFoundError
from app.schemas import (
    ActionItemStatus,
    DeleteResponse,
    Insight,
    Meeting,
    MeetingCreateInput,
    MeetingDetailResponse,
    MeetingListItem,
)
from app.services.container import ServiceContainer

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("", response_model=Meeting, status_code=status.HTTP_201_CREATED)
def create_meeting(
    payload: MeetingCreateInput,
    services: ServiceContainer = Depends(get_services),
) -> Meeting:
    return services.meetings.create_meeting(payload)


@router.get("", response_model=list[MeetingListItem])
def list_meetings(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    participant: str | None = Query(default=None),
    owner: str | None = Query(default=None),
    status_value: ActionItemStatus | None = Query(default=None, alias="status"),
    services: ServiceContainer = Depends(get_services),
) -> list[MeetingListItem]:
    return services.meetings.list_meetings(
        date_from=date_from,
        date_to=date_to,
        participant=participant,
        owner=owner,
        status=status_value,
    )


@router.get("/{meeting_id}", response_model=MeetingDetailResponse)
def get_meeting_detail(
    meeting_id: str,
    services: ServiceContainer = Depends(get_services),
) -> MeetingDetailResponse:
    try:
        return services.meetings.get_meeting_detail(meeting_id)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{meeting_id}/insights", response_model=Insight | None)
def get_meeting_insights(
    meeting_id: str,
    services: ServiceContainer = Depends(get_services),
) -> Insight | None:
    try:
        services.meetings.get_meeting(meeting_id)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return services.insights.get_insights_for_meeting(meeting_id)


@router.post("/{meeting_id}/insights", response_model=Insight)
def generate_meeting_insights(
    meeting_id: str,
    services: ServiceContainer = Depends(get_services),
) -> Insight:
    try:
        return services.insights.generate_insights(meeting_id)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.delete("/{meeting_id}", response_model=DeleteResponse)
def delete_meeting(
    meeting_id: str,
    services: ServiceContainer = Depends(get_services),
) -> DeleteResponse:
    try:
        services.meetings.delete_meeting(meeting_id)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return DeleteResponse(deleted=True)
