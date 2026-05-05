from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import action_items, dashboard, health, meetings
from app.config import Settings
from app.services.container import build_services
#from fastapi.staticfiles import StaticFiles

#app = FastAPI()

# serve React build
#app.mount("/", StaticFiles(directory="static", html=True), name="static")


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings.from_env()
    services = build_services(resolved_settings)

    app = FastAPI(title=resolved_settings.app_name, version="1.0.0")
    app.state.settings = resolved_settings
    app.state.services = services

    app.add_middleware(
        CORSMiddleware,
        allow_origins=resolved_settings.frontend_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix=resolved_settings.api_prefix)
    app.include_router(meetings.router, prefix=resolved_settings.api_prefix)
    app.include_router(action_items.router, prefix=resolved_settings.api_prefix)
    app.include_router(dashboard.router, prefix=resolved_settings.api_prefix)

    return app


app = create_app()
