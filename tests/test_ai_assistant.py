"""
Tests for /ai/chat endpoint.
The Gemini client call is mocked so tests run offline without a real API key.
"""
from unittest.mock import MagicMock, patch


def test_chat_returns_reply(client, sample_profile):
    """AI endpoint returns a reply when Gemini client is mocked."""
    mock_response = MagicMock()
    mock_response.text = "Great job! Keep pushing for your muscle goal. 💪"

    with patch("app.routers.ai_assistant.genai.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client

        resp = client.post("/ai/chat", json={
            "user_id": sample_profile["id"],
            "message": "How many calories should I eat today?",
        })

    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert len(data["reply"]) > 0


def test_chat_profile_not_found(client):
    """Returns 404 when user_id doesn't match any profile."""
    resp = client.post("/ai/chat", json={
        "user_id": "00000000-0000-0000-0000-000000000000",
        "message": "Hello",
    })
    assert resp.status_code == 404
