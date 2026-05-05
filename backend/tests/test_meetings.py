from __future__ import annotations

import json
from datetime import date

from app.schemas import GeneratedActionItem, InsightDraft, MeetingMetadataDraft, Priority
from app.services.insights import OpenAIInsightGenerator
from app.services.meetings import OpenAIMeetingMetadataGenerator


def test_create_meeting_persists_to_json_store(client) -> None:
    payload = {
        "title": "Executive Steering Committee",
        "date": "2026-04-30",
        "participants": ["Alice Johnson", "Ben Carter", "Priya Nair"],
        "transcript": (
            "Alice: We reviewed revenue performance and agreed to refresh the Q2 plan. "
            "Action: Priya Nair - share revised forecast by 2026-05-02."
        ),
    }

    response = client.post("/api/meetings", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["id"].startswith("mtg_")

    stored_records = json.loads(
        (client.app.state.settings.data_dir / "meetings.json").read_text(encoding="utf-8")
    )
    assert len(stored_records) == 1
    assert stored_records[0]["title"] == payload["title"]


def test_create_meeting_can_infer_metadata_from_transcript(client, monkeypatch) -> None:
    def fake_generate(self, transcript: str) -> MeetingMetadataDraft:
        return MeetingMetadataDraft(
            title="Critical Production Issues & Sprint Planning",
            date=date(2024, 5, 3),
            participants=["Sreekar", "Revanth", "Pruthvi", "Akash"],
        )

    monkeypatch.setattr(OpenAIMeetingMetadataGenerator, "generate", fake_generate)

    response = client.post(
        "/api/meetings",
        json={
            "transcript": (
                "Sreekar: Thanks everyone for joining. We have three critical items to discuss today. "
                "Revanth: We need to fix the payment gateway timeout. "
                "Pruthvi: I can prepare a rollback script. "
                "Akash: I will submit the Android build today."
            )
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Critical Production Issues & Sprint Planning"
    assert data["date"] == "2024-05-03"
    assert data["participants"] == ["Sreekar", "Revanth", "Pruthvi", "Akash"]


def test_delete_meeting_removes_related_insights_and_action_items(client, monkeypatch) -> None:
    def fake_generate(self, meeting) -> InsightDraft:
        return InsightDraft(
            summary_short="Renewal planning review completed.",
            summary_detailed="The team reviewed renewal blockers and follow-ups.",
            decisions=["The team agreed to keep the renewal plan focused on the top 20 accounts."],
            blockers=["The blocker is missing security review feedback from the customer."],
            action_items=[
                GeneratedActionItem(
                    owner="Jordan Reyes",
                    task="prepare revised proposal",
                    priority=Priority.MEDIUM,
                ),
                GeneratedActionItem(
                    owner="Chris Lane",
                    task="collect security review feedback",
                    priority=Priority.HIGH,
                ),
            ],
        )

    monkeypatch.setattr(OpenAIInsightGenerator, "generate", fake_generate)

    create_response = client.post(
        "/api/meetings",
        json={
            "title": "Renewal Planning Sync",
            "date": "2026-04-30",
            "participants": ["Ava Moore", "Chris Lane", "Jordan Reyes"],
            "transcript": (
                "Ava Moore: We agreed to keep the renewal plan focused on the top 20 accounts.\n"
                "Chris Lane: The blocker is missing security review feedback from the customer.\n"
                "Jordan Reyes: Decision noted, we will present the revised proposal on Friday.\n"
                "Action: Jordan Reyes - prepare revised proposal by 2026-05-02.\n"
                "Action: Chris Lane - collect security review feedback by 2026-05-01."
            ),
        },
    )
    meeting_id = create_response.json()["id"]

    generate_response = client.post(f"/api/meetings/{meeting_id}/insights")
    assert generate_response.status_code == 200

    delete_response = client.delete(f"/api/meetings/{meeting_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True}

    meetings_records = json.loads(
        (client.app.state.settings.data_dir / "meetings.json").read_text(encoding="utf-8")
    )
    insights_records = json.loads(
        (client.app.state.settings.data_dir / "insights.json").read_text(encoding="utf-8")
    )
    action_item_records = json.loads(
        (client.app.state.settings.data_dir / "action_items.json").read_text(encoding="utf-8")
    )

    assert meetings_records == []
    assert insights_records == []
    assert action_item_records == []
