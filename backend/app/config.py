from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key or key in os.environ:
            continue

        if (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in {'"', "'"}
        ):
            value = value[1:-1]

        os.environ[key] = value


@dataclass(slots=True)
class Settings:
    app_name: str
    api_prefix: str
    data_dir: Path
    frontend_origins: list[str]
    openai_api_key: str | None
    openai_model: str

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> "Settings":
        backend_dir = Path(__file__).resolve().parents[1]
        _load_dotenv(env_file or backend_dir / ".env")

        root_data_dir = backend_dir / "data"
        origins_raw = os.getenv("FRONTEND_ORIGINS") or os.getenv(
            "FRONTEND_ORIGIN", "http://localhost:5173"
        )
        origins = [origin.strip() for origin in origins_raw.split(",") if origin.strip()]
        return cls(
            app_name="AI Meeting Insights Dashboard API",
            api_prefix="/api",
            data_dir=Path(os.getenv("APP_DATA_DIR", str(root_data_dir))),
            frontend_origins=origins,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        )
