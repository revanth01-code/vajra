import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import app


def test_sanitizer_removes_required_secret_patterns():
    from src.services.sanitizer import sanitize_text

    sanitized = sanitize_text(
        "AKIA1234567890ABCDEF postgresql://user:secret@db "
        "10.1.2.3 Authorization: Bearer abc.def"
    )

    assert "AKIA" not in sanitized
    assert "secret" not in sanitized
    assert "10.1.2.3" not in sanitized
    assert "abc.def" not in sanitized
    assert sanitized.count("[REDACTED]") == 4


def test_investigate_rejects_empty_input():
    with TestClient(app) as client:
        response = client.post("/api/investigate", json={"incident_text": ""})

    assert response.status_code == 422


def test_history_and_feedback_routes():
    with TestClient(app) as client:
        assert client.get("/api/history").status_code == 200
        response = client.post(
            "/api/feedback",
            json={"session_id": "missing", "hypothesis_rank": 1, "rating": "up"},
        )

    assert response.status_code == 404
