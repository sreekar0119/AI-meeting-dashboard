from __future__ import annotations

from pathlib import Path

from app.schemas import ActionItem, ItemSource
from app.utils.json_store import JsonFileStore


class JsonActionItemRepository:
    def __init__(self, data_path: Path) -> None:
        self.store = JsonFileStore(data_path)

    def list(self) -> list[ActionItem]:
        records = self.store.read()
        return [ActionItem.model_validate(record) for record in records]

    def get(self, item_id: str) -> ActionItem | None:
        records = self.store.read()
        for record in records:
            if record["id"] == item_id:
                return ActionItem.model_validate(record)
        return None

    def create(self, item: ActionItem) -> ActionItem:
        def updater(records: list[dict]) -> tuple[list[dict], ActionItem]:
            records.append(item.model_dump(mode="json"))
            return records, item

        return self.store.update(updater)

    def update(self, item: ActionItem) -> ActionItem:
        def updater(records: list[dict]) -> tuple[list[dict], ActionItem]:
            updated_records: list[dict] = []
            for record in records:
                if record["id"] == item.id:
                    updated_records.append(item.model_dump(mode="json"))
                else:
                    updated_records.append(record)
            return updated_records, item

        return self.store.update(updater)

    def delete(self, item_id: str) -> bool:
        def updater(records: list[dict]) -> tuple[list[dict], bool]:
            updated_records = [record for record in records if record["id"] != item_id]
            return updated_records, len(updated_records) != len(records)

        return self.store.update(updater)

    def delete_by_meeting(self, meeting_id: str) -> int:
        def updater(records: list[dict]) -> tuple[list[dict], int]:
            updated_records = [record for record in records if record["meeting_id"] != meeting_id]
            return updated_records, len(records) - len(updated_records)

        return self.store.update(updater)

    def replace_generated_for_meeting(
        self, meeting_id: str, generated_items: list[ActionItem]
    ) -> list[ActionItem]:
        def updater(records: list[dict]) -> tuple[list[dict], list[ActionItem]]:
            preserved = [
                record
                for record in records
                if not (
                    record["meeting_id"] == meeting_id
                    and record.get("source") == ItemSource.INSIGHT.value
                )
            ]
            preserved.extend(item.model_dump(mode="json") for item in generated_items)
            return preserved, generated_items

        return self.store.update(updater)
