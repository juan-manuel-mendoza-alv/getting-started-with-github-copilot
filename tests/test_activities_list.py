"""
Tests for GET /activities endpoint

Tests for retrieving the list of all available activities.
"""

import pytest
from fastapi.testclient import TestClient

from src.app import app


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities"""
        # Arrange - client fixture provides a fresh TestClient

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0

    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has all required fields"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert all(field in activity_data for field in required_fields)

    def test_get_activities_participants_is_list(self, client):
        """Test that participants field is always a list"""
        # Arrange - client fixture provides a fresh TestClient

        # Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list)
            assert all(isinstance(p, str) for p in activity_data["participants"])

    def test_get_activities_max_participants_is_positive_int(self, client):
        """Test that max_participants is a positive integer"""
        # Arrange - client fixture provides a fresh TestClient

        # Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int)
            assert activity_data["max_participants"] > 0

    def test_get_activities_chess_club_exists(self, client):
        """Test that Chess Club activity exists with expected details"""
        # Arrange - client fixture provides a fresh TestClient

        # Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert "Chess Club" in activities
        chess_club = activities["Chess Club"]
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]
