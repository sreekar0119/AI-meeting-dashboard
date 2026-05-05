from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_services
from app.errors import NotFoundError
from app.schemas import (
    ActionItem,
    ActionItemCreate,
    ActionItemStatus,
    ActionItemStatusUpdate,
    ActionItemUpdate,
    DeleteResponse,
    Priority,
)
from app.services.container import ServiceContainer

router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.get("", response_model=list[ActionItem])
def list_action_items(
    meeting_id: str | None = Query(default=None),
    owner: str | None = Query(default=None),
    status_value: ActionItemStatus | None = Query(default=None, alias="status"),
    priority: Priority | None = Query(default=None),
    overdue: bool | None = Query(default=None),
    services: ServiceContainer = Depends(get_services),
) -> list[ActionItem]:
    return services.action_items.list_action_items(
        meeting_id=meeting_id,
        owner=owner,
        status=status_value,
        priority=priority,
        overdue=overdue,
    )


@router.post("", response_model=ActionItem, status_code=status.HTTP_201_CREATED)
def create_action_item(
    payload: ActionItemCreate,
    services: ServiceContainer = Depends(get_services),
) -> ActionItem:
    try:
        return services.action_items.create_action_item(payload)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.get("/{item_id}", response_model=ActionItem)
def get_action_item(
    item_id: str,
    services: ServiceContainer = Depends(get_services),
) -> ActionItem:
    try:
        return services.action_items.get_action_item(item_id)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.patch("/{item_id}", response_model=ActionItem)
def update_action_item(
    item_id: str,
    payload: ActionItemUpdate,
    services: ServiceContainer = Depends(get_services),
) -> ActionItem:
    try:
        return services.action_items.update_action_item(item_id, payload)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.patch("/{item_id}/status", response_model=ActionItem)
def update_action_item_status(
    item_id: str,
    payload: ActionItemStatusUpdate,
    services: ServiceContainer = Depends(get_services),
) -> ActionItem:
    try:
        return services.action_items.update_status(item_id, payload.status)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.delete("/{item_id}", response_model=DeleteResponse)
def delete_action_item(
    item_id: str,
    services: ServiceContainer = Depends(get_services),
) -> DeleteResponse:
    try:
        services.action_items.delete_action_item(item_id)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return DeleteResponse(deleted=True)
