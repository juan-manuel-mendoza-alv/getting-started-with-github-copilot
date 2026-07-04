"""
Tests for error handling and edge cases across all endpoints

Tests for URL encoding, special characters, malformed inputs, and cross-endpoint scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from urllib.parse import quote

from src.app import app


class TestErrorHandling:
    """Tests for error handling and edge cases"""

    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup with activity name that requires URL encoding"""
        # Arrange
        activity_name = "Chess Club"
        encoded_activity_name = quote(activity_name)
        test_email = "student@example.com"

        # Act
        response = client.post(
            f"/activities/{encoded_activity_name}/signup",
            params={"email": test_email},
        )

        # Assert
        assert response.status_code == 200

    def test_unregister_with_url_encoded_email(self, client):
        """Test unregister with email that requires URL encoding"""
        # Arrange
        activity_name = "Programming Class"
        test_email = "user+test@example.com"
        encoded_email = quote(test_email)

        # Signup first
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email},
        )

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants/{encoded_email}"
        )

        # Assert
        assert response.status_code == 200

    def test_signup_with_case_sensitive_activity_name(self, client):
        """Test that activity names are case-sensitive"""
        # Arrange
        correct_name = "Chess Club"
        wrong_case_name = "chess club"
        test_email = "student@example.com"

        # Act
        response_correct = client.post(
            f"/activities/{correct_name}/signup",
            params={"email": test_email},
        )
        response_wrong = client.post(
            f"/activities/{wrong_case_name}/signup",
            params={"email": "student2@example.com"},
        )

        # Assert
        assert response_correct.status_code == 200
        assert response_wrong.status_code == 404

    def test_signup_with_activity_name_extra_spaces(self, client):
        """Test signup with activity name containing extra spaces"""
        # Arrange
        activity_name_with_spaces = "Chess%20Club"
        test_email = "student@example.com"

        # Act
        response = client.post(
            f"/activities/{activity_name_with_spaces}/signup",
            params={"email": test_email},
        )

        # Assert
        assert response.status_code == 200

    def test_multiple_signup_and_unregister_cycles(self, client):
        """Test multiple cycles of signup and unregister for same student"""
        # Arrange
        activity_name = "Soccer Team"
        test_email = "athlete@example.com"

        # Act & Assert - First cycle
        signup1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email},
        )
        assert signup1.status_code == 200

        unregister1 = client.delete(
            f"/activities/{activity_name}/participants/{test_email}"
        )
        assert unregister1.status_code == 200

        # Act & Assert - Second cycle (signup again after unregistering)
        signup2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email},
        )
        assert signup2.status_code == 200

    def test_student_can_signup_for_multiple_different_activities(self, client):
        """Test that a student can sign up for multiple different activities"""
        # Arrange
        test_email = "busy_student@example.com"
        activities = ["Chess Club", "Programming Class", "Soccer Team"]

        # Act
        responses = []
        for activity in activities:
            response = client.post(
                f"/activities/{activity}/signup",
                params={"email": test_email},
            )
            responses.append(response)

        # Assert
        assert all(r.status_code == 200 for r in responses)

        # Verify student is in all activities
        all_activities = client.get("/activities").json()
        for activity in activities:
            assert test_email in all_activities[activity]["participants"]

    def test_get_activities_is_consistent_after_modifications(self, client):
        """Test that GET /activities returns consistent data after signup/unregister"""
        # Arrange
        activity_name = "Basketball Club"
        test_email = "player@example.com"

        # Get initial state
        initial = client.get("/activities").json()
        initial_count = len(initial[activity_name]["participants"])

        # Act - Sign up
        client.post(f"/activities/{activity_name}/signup", params={"email": test_email})
        after_signup = client.get("/activities").json()
        count_after_signup = len(after_signup[activity_name]["participants"])

        # Act - Unregister
        client.delete(f"/activities/{activity_name}/participants/{test_email}")
        after_unregister = client.get("/activities").json()
        final_count = len(after_unregister[activity_name]["participants"])

        # Assert
        assert count_after_signup == initial_count + 1
        assert final_count == initial_count
