"""
Tests for the activities endpoint (GET /activities).

This endpoint returns the full list of all extracurricular activities
with their details (description, schedule, max_participants, participants).
"""

import pytest


def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all 9 activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    activities = response.json()
    assert len(activities) == 9
    
    # Verify all expected activities are present
    expected_activities = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Soccer Team",
        "Swimming Club",
        "Art Club",
        "Drama Club",
        "Math Olympiad",
        "Science Club"
    ]
    assert set(activities.keys()) == set(expected_activities)


def test_get_activities_response_structure(client):
    """Test that each activity has the required fields"""
    response = client.get("/activities")
    activities = response.json()
    
    for activity_name, activity_data in activities.items():
        # Verify required fields exist
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        
        # Verify field types
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)
        
        # Verify participants are emails (strings)
        for participant in activity_data["participants"]:
            assert isinstance(participant, str)
            assert "@" in participant  # Basic email validation


def test_get_activities_contains_expected_data(client):
    """Test that activities contain expected data"""
    response = client.get("/activities")
    activities = response.json()
    
    # Verify Chess Club specifically
    chess_club = activities["Chess Club"]
    assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
    assert "Fridays" in chess_club["schedule"]
    assert chess_club["max_participants"] == 12
    assert "michael@mergington.edu" in chess_club["participants"]
    assert "daniel@mergington.edu" in chess_club["participants"]


def test_get_activities_initial_participants(client):
    """Test that activities have their initial participants"""
    response = client.get("/activities")
    activities = response.json()
    
    # Verify that each activity has at least some participants initially
    for activity_name, activity_data in activities.items():
        assert len(activity_data["participants"]) >= 2, \
            f"{activity_name} should have at least 2 initial participants"
