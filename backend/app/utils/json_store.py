from __future__ import annotations

from collections.abc import Callable
import json
import os
from pathlib import Path
import tempfile
from typing import TypeVar

from app.utils.file_lock import FileLock

T = TypeVar("T")


class JsonFileStore:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.lock_path = file_path.with_suffix(file_path.suffix + ".lock")
        self._ensure_file_exists()

    def read(self) -> list[dict]:
        with FileLock(self.lock_path):
            return self._read_unlocked()

    def update(self, callback: Callable[[list[dict]], tuple[list[dict], T]]) -> T:
        with FileLock(self.lock_path):
            current = self._read_unlocked()
            updated, result = callback(current)
            self._write_unlocked(updated)
            return result

    def _ensure_file_exists(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        with FileLock(self.lock_path):
            if not self.file_path.exists():
                self._write_unlocked([])

    def _read_unlocked(self) -> list[dict]:
        if not self.file_path.exists() or self.file_path.stat().st_size == 0:
            return []
        with self.file_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _write_unlocked(self, data: list[dict]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_handle = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            delete=False,
            dir=self.file_path.parent,
            prefix=f"{self.file_path.stem}_",
            suffix=".tmp",
        )
        temp_path = Path(temp_handle.name)
        try:
            with temp_handle:
                json.dump(data, temp_handle, indent=2, ensure_ascii=False)
                temp_handle.write("\n")
                temp_handle.flush()
                os.fsync(temp_handle.fileno())
            os.replace(temp_path, self.file_path)
        finally:
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
