from __future__ import annotations

from pathlib import Path

from app.config import Settings


def test_settings_can_load_values_from_dotenv(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.delenv("FRONTEND_ORIGIN", raising=False)
    monkeypatch.delenv("FRONTEND_ORIGINS", raising=False)

    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "OPENAI_API_KEY=test-key-123",
                "OPENAI_MODEL=gpt-4.1-mini",
                "FRONTEND_ORIGIN=http://localhost:5173",
            ]
        ),
        encoding="utf-8",
    )

    settings = Settings.from_env(env_file=env_file)

    assert settings.openai_api_key == "test-key-123"
    assert settings.openai_model == "gpt-4.1-mini"
    assert settings.frontend_origins == ["http://localhost:5173"]
