"""Tests for /ai/chat endpoint.

The Groq (AsyncOpenAI) client call is mocked so tests run offline
without a live API key.
"""
from unittest.mock import AsyncMock, MagicMock, patch


def test_chat_returns_reply(client, sample_profile):
    """AI endpoint returns a reply when the Groq client is mocked."""
    mock_message = MagicMock()
    mock_message.content = "Great job! Keep pushing for your muscle goal."

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    # Patch the AsyncOpenAI client inside the router
    with patch("app.routers.ai_assistant.AsyncOpenAI") as mock_cls:
        mock_instance = MagicMock()
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_completion)
        mock_cls.return_value = mock_instance

        resp = client.post(
            "/ai/chat",
            json={
                "profile_id": sample_profile["id"],
                "message": "How many calories should I eat today?",
            },
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert len(data["reply"]) > 0


def test_chat_profile_not_found(client):
    """Returns 404 when the requested profile_id doesn't belong to the user."""
    with patch("app.routers.ai_assistant.AsyncOpenAI"):
        resp = client.post(
            "/ai/chat",
            json={
                "profile_id": "00000000-0000-0000-0000-000000000000",
                "message": "Hello",
            },
        )
    assert resp.status_code == 404
