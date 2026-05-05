from __future__ import annotations

from datetime import date, datetime, timezone

from app.services.insights import MockInsightGenerator, OpenAIInsightGenerator
from app.schemas import GeneratedActionItem, InsightDraft, Meeting, Priority


def test_mock_match_owner_truncates_long_transcript_fragment() -> None:
    generator = MockInsightGenerator()
    owner = generator._match_owner(
        "But We Found Some Memory Leak In The Frontend That Was Critical For Release But It Kept Growing And Growing",
        ["Maya Chen", "Leo Brooks"],
    )

    assert len(owner) <= 80


def test_openai_payload_skips_oversized_action_item_owner() -> None:
    generator = OpenAIInsightGenerator(api_key="test-key", model="gpt-4.1-mini")
    normalized = generator._normalize_payload(
        {
            "summary_short": "Vendor review completed.",
            "summary_detailed": "The team reviewed the vendor proposal.",
            "decisions": ["The team agreed to review the proposal."],
            "blockers": [],
            "action_items": [
                {
                    "owner": "But We Found Some Memory Leak In The Frontend That Was Critical For Release But It Kept Growing",
                    "task": "Review vendor proposal",
                    "priority": "medium",
                },
                {
                    "owner": "Maya Chen",
                    "task": "Share vendor proposal notes",
                    "priority": "high",
                },
            ],
        }
    )

    assert len(normalized["action_items"]) == 1
    assert normalized["action_items"][0]["owner"] == "Maya Chen"


def test_generate_insights_creates_structured_output_and_tasks(client, monkeypatch) -> None:
    def fake_generate(self, meeting: Meeting) -> InsightDraft:
        return InsightDraft(
            summary_short="Launch readiness review completed.",
            summary_detailed="The team reviewed launch blockers and assigned follow-ups.",
            decisions=["The team agreed to keep the launch date on 2026-05-20."],
            blockers=["The blocker is final design approval from legal."],
            action_items=[
                GeneratedActionItem(
                    owner="Nina Patel",
                    task="finalize partner email copy",
                    priority=Priority.MEDIUM,
                ),
                GeneratedActionItem(
                    owner="Leo Brooks",
                    task="collect legal approval notes",
                    priority=Priority.HIGH,
                ),
            ],
        )

    monkeypatch.setattr(OpenAIInsightGenerator, "generate", fake_generate)

    create_response = client.post(
        "/api/meetings",
        json={
            "title": "Launch Readiness Review",
            "date": "2026-04-29",
            "participants": ["Maya Chen", "Leo Brooks", "Nina Patel"],
            "transcript": """
            Maya Chen: We agreed to keep the launch date on 2026-05-20.
            Leo Brooks: The blocker is final design approval from legal.
            Action: Nina Patel - finalize partner email copy by 2026-05-03.
            Action: Leo Brooks - collect legal approval notes by 2026-05-02.
            """,
        },
    )
    meeting_id = create_response.json()["id"]

    response = client.post(f"/api/meetings/{meeting_id}/insights")
    assert response.status_code == 200
    payload = response.json()
    assert payload["meeting_id"] == meeting_id
    assert "summary_short" in payload
    assert len(payload["decisions"]) >= 1
    assert len(payload["action_items"]) >= 2

    action_items_response = client.get("/api/action-items", params={"meeting_id": meeting_id})
    assert action_items_response.status_code == 200
    action_items = action_items_response.json()
    assert len(action_items) >= 2
    assert all(item["source"] == "insight" for item in action_items)
