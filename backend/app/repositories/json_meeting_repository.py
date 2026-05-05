from __future__ import annotations

from pathlib import Path

from app.schemas import Meeting
from app.utils.json_store import JsonFileStore


class JsonMeetingRepository:
    def __init__(self, data_path: Path) -> None:
        self.store = JsonFileStore(data_path)

    def list(self) -> list[Meeting]:
        records = self.store.read()
        return [Meeting.model_validate(record) for record in records]

    def get(self, meeting_id: str) -> Meeting | None:
        records = self.store.read()
        for record in records:
            if record["id"] == meeting_id:
                return Meeting.model_validate(record)
        return None

    def create(self, meeting: Meeting) -> Meeting:
        def updater(records: list[dict]) -> tuple[list[dict], Meeting]:
            records.append(meeting.model_dump(mode="json"))
            return records, meeting

        return self.store.update(updater)

    def delete(self, meeting_id: str) -> bool:
        def updater(records: list[dict]) -> tuple[list[dict], bool]:
            updated_records = [record for record in records if record["id"] != meeting_id]
            return updated_records, len(updated_records) != len(records)

        return self.store.update(updater)
