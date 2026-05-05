from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.dependencies import get_services
from app.schemas import DashboardSummary
from app.services.container import ServiceContainer

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardSummary)
def get_dashboard_summary(
    services: ServiceContainer = Depends(get_services),
) -> DashboardSummary:
    return services.dashboard.get_summary()
