from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import Settings
from app.main import create_app


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    settings = Settings(
        app_name="AI Meeting Insights Dashboard API",
        api_prefix="/api",
        data_dir=tmp_path / "data",
        frontend_origins=["http://localhost:5173"],
        openai_api_key="test-key",
        openai_model="gpt-4.1-mini",
    )
    app = create_app(settings)
    with TestClient(app) as test_client:
        yield test_client
