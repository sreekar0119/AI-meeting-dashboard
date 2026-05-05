from __future__ import annotations

import json


def test_update_action_item_status(client) -> None:
    meeting_response = client.post(
        "/api/meetings",
        json={
            "title": "Weekly Delivery Sync",
            "date": "2026-04-30",
            "participants": ["Ava Moore", "Chris Lane"],
            "transcript": (
                "Ava: We reviewed delivery targets. "
                "Action: Chris Lane - confirm deployment window by 2026-05-02."
            ),
        },
    )
    meeting_id = meeting_response.json()["id"]

    create_response = client.post(
        "/api/action-items",
        json={
            "meeting_id": meeting_id,
            "owner": "Chris Lane",
            "task": "Confirm deployment window",
            "priority": "high",
            "status": "open",
        },
    )
    assert create_response.status_code == 201
    action_item = create_response.json()

    update_response = client.patch(
        f"/api/action-items/{action_item['id']}/status",
        json={"status": "complete"},
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["status"] == "complete"

    stored_records = json.loads(
        (client.app.state.settings.data_dir / "action_items.json").read_text(encoding="utf-8")
    )
    stored_item = next(record for record in stored_records if record["id"] == action_item["id"])
    assert stored_item["status"] == "complete"
