from fastapi.testclient import TestClient

from src.app import app


def test_signup_prevents_duplicate_registration_for_same_email():
    client = TestClient(app)

    first_response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "student@example.com"},
    )
    assert first_response.status_code == 200

    second_response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "student@example.com"},
    )

    assert second_response.status_code == 400
    assert "already signed up" in second_response.json()["detail"].lower()


def test_unregister_participant_removes_email_from_activity():
    client = TestClient(app)

    signup_response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "student@example.com"},
    )
    assert signup_response.status_code == 200

    unregister_response = client.delete(
        "/activities/Chess Club/participants/student@example.com"
    )

    assert unregister_response.status_code == 200
    assert "student@example.com" not in client.get("/activities").json()["Chess Club"]["participants"]
