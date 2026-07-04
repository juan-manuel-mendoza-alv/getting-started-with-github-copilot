"""
Tests for DELETE /activities/{activity_name}/participants/{email} endpoint

Tests for student unregistration and removal from activities.
"""

import pytest
from fastapi.testclient import TestClient

from src.app import app


class TestUnregisterParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""

    def test_unregister_participant_removes_email_from_activity(self, client):
        """Test that unregistering removes a participant from an activity"""
        # Arrange
        activity_name = "Chess Club"
        test_email = "student@example.com"

        # First signup the student
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email},
        )
        assert signup_response.status_code == 200

        # Act - Unregister the student
        response = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]
        assert test_email not in client.get("/activities").json()[activity_name]["participants"]

    def test_unregister_nonexistent_participant_returns_404(self, client):
        """Test that attempting to unregister a non-existent participant returns 404"""
        # Arrange
        activity_name = "Soccer Team"
        nonexistent_email = "notreal@example.com"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{nonexistent_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_unregister_from_nonexistent_activity_returns_404(self, client):
        """Test that attempting to unregister from a non-existent activity returns 404"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        test_email = "student@example.com"

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{test_email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_response_contains_message_field(self, client):
        """Test that successful unregister response contains proper message field"""
        # Arrange
        activity_name = "Programming Class"
        test_email = "unregister@example.com"

        # Signup first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email},
        )

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Removed" in data["message"]
        assert activity_name in data["message"]

    def test_unregister_specific_participant_leaves_others_untouched(self, client):
        """Test that unregistering one participant doesn't affect others"""
        # Arrange
        activity_name = "Art Workshop"
        email1 = "artist1@example.com"
        email2 = "artist2@example.com"

        # Signup two students
        client.post(f"/activities/{activity_name}/signup", params={"email": email1})
        client.post(f"/activities/{activity_name}/signup", params={"email": email2})

        # Act - Unregister first student
        response = client.delete(
            f"/activities/{activity_name}/participants/{email1}"
        )

        # Assert
        assert response.status_code == 200
        participants = client.get("/activities").json()[activity_name]["participants"]
        assert email1 not in participants
        assert email2 in participants

    def test_unregister_same_participant_twice_returns_404(self, client):
        """Test that attempting to unregister the same participant twice returns 404"""
        # Arrange
        activity_name = "Drama Club"
        test_email = "actor@example.com"

        # Signup and unregister once
        client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
        first_unregister = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )
        assert first_unregister.status_code == 200

        # Act - Try to unregister again
        second_unregister = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )

        # Assert
        assert second_unregister.status_code == 404
