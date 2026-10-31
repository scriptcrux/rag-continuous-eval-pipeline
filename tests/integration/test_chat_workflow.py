"""Integration tests for multi-turn chat conversations."""

import pytest
from fastapi import status


@pytest.mark.integration
def test_multi_turn_chat_workflow(test_client):
    """Test multi-turn conversational interaction maintaining session id."""
    session_id = "user_session_101"

    # Turn 1
    res1 = test_client.post(
        "/api/v1/chat",
        json={
            "message": "What is the initial response SLA for a Sev-1 incident?",
            "session_id": session_id,
            "history": [],
        },
    )
    assert res1.status_code == status.HTTP_200_OK
    data1 = res1.json()
    assert "5 minutes" in data1["answer"]
    assert data1["session_id"] == session_id

    # Turn 2 with history
    res2 = test_client.post(
        "/api/v1/chat",
        json={
            "message": "Within what timeframe must the post-mortem retrospective meeting be held?",
            "session_id": session_id,
            "history": [
                {"role": "user", "content": "What is the initial response SLA for a Sev-1 incident?"},
                {"role": "assistant", "content": data1["answer"]},
            ],
        },
    )
    assert res2.status_code == status.HTTP_200_OK
    data2 = res2.json()
    assert "48 hours" in data2["answer"]
    assert data2["session_id"] == session_id

