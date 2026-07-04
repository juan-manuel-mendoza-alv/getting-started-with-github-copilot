"""
Tests for POST /activities/{activity_name}/signup endpoint

Tests for student signup functionality with duplicate prevention.
"""

import pytest
from fastapi.testclient import TestClient

from src.app import app


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful_adds_email_to_participants(self, client):
        """Test that a student can successfully sign up for an activity"""
        # Arrange
        activity_name = "Chess Club"
        test_email = "newstudent@example.com"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email},
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert test_email in response.json()["message"]

    def test_signup_prevents_duplicate_registration_for_same_email(self, client):
        """Test that signing up twice for same activity with same email returns 400"""
        # Arrange
        activity_name = "Chess Club"
        test_email = "duplicate@example.com"

        # Act - First signup
        first_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email},
        )
        # Act - Second signup with same email
        second_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email},
        )

        # Assert
        assert first_response.status_code == 200
        assert second_response.status_code == 400
        assert "already signed up" in second_response.json()["detail"].lower()

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        test_email = "student@example.com"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": test_email},
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_response_contains_message_field(self, client):
        """Test that successful signup response contains proper message field"""
        # Arrange
        activity_name = "Programming Class"
        test_email = "testuser@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": test_email},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert activity_name in data["message"]
        assert test_email in data["message"]

    def test_signup_multiple_different_emails_for_same_activity(self, client):
        """Test that multiple different students can sign up for the same activity"""
        # Arrange
        activity_name = "Gym Class"
        emails = ["student1@example.com", "student2@example.com", "student3@example.com"]

        # Act & Assert
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email},
            )
            assert response.status_code == 200
