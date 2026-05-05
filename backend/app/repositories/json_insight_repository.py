from __future__ import annotations

from pathlib import Path

from app.schemas import Insight
from app.utils.json_store import JsonFileStore


class JsonInsightRepository:
    def __init__(self, data_path: Path) -> None:
        self.store = JsonFileStore(data_path)

    def list(self) -> list[Insight]:
        records = self.store.read()
        return [Insight.model_validate(record) for record in records]

    def get_by_meeting(self, meeting_id: str) -> Insight | None:
        records = self.store.read()
        for record in records:
            if record["meeting_id"] == meeting_id:
                return Insight.model_validate(record)
        return None

    def upsert(self, insight: Insight) -> Insight:
        def updater(records: list[dict]) -> tuple[list[dict], Insight]:
            updated = False
            stored_records: list[dict] = []
            for record in records:
                if record["meeting_id"] == insight.meeting_id:
                    stored_records.append(insight.model_dump(mode="json"))
                    updated = True
                else:
                    stored_records.append(record)
            if not updated:
                stored_records.append(insight.model_dump(mode="json"))
            return stored_records, insight

        return self.store.update(updater)

    def delete_by_meeting(self, meeting_id: str) -> bool:
        def updater(records: list[dict]) -> tuple[list[dict], bool]:
            updated_records = [record for record in records if record["meeting_id"] != meeting_id]
            return updated_records, len(updated_records) != len(records)

        return self.store.update(updater)
