"""
Tests for the remove participant endpoint (DELETE /activities/{activity_name}/participants/{email}).

This endpoint allows removing students from activities.
Includes happy path and error handling tests.
"""

import pytest


class TestRemoveParticipantHappyPath:
    """Tests for successful removal scenarios"""
    
    def test_remove_participant_successful(self, client):
        """Test successful removal of a participant"""
        email = "michael@mergington.edu"  # In Chess Club
        
        response = client.delete(
            "/activities/Chess Club/participants/michael@mergington.edu"
        )
        assert response.status_code == 200
        assert response.json() == {
            "message": "Removed michael@mergington.edu from Chess Club"
        }
    
    def test_remove_participant_actually_removes(self, client):
        """Test that removal actually removes the participant"""
        email = "michael@mergington.edu"
        
        # Verify participant exists
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        
        # Remove
        response = client.delete(
            "/activities/Chess Club/participants/michael@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify participant is gone
        activities = client.get("/activities").json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_remove_all_participants(self, client):
        """Test removing all participants from an activity"""
        activity = "Chess Club"
        
        # Get current participants
        activities = client.get("/activities").json()
        participants = activities[activity]["participants"].copy()
        
        # Remove each participant
        for email in participants:
            response = client.delete(
                f"/activities/{activity}/participants/{email}"
            )
            assert response.status_code == 200
        
        # Verify activity has no participants
        activities = client.get("/activities").json()
        assert len(activities[activity]["participants"]) == 0
    
    def test_remove_participant_from_different_activities(self, client):
        """Test removing same email from multiple activities"""
        email = "sophia@mergington.edu"  # In Programming Class and Drama Club
        
        # Verify participant is in both
        activities = client.get("/activities").json()
        assert email in activities["Programming Class"]["participants"]
        assert email in activities["Drama Club"]["participants"]
        
        # Remove from first activity
        response1 = client.delete(
            f"/activities/Programming Class/participants/{email}"
        )
        assert response1.status_code == 200
        
        # Verify removed from first but still in second
        activities = client.get("/activities").json()
        assert email not in activities["Programming Class"]["participants"]
        assert email in activities["Drama Club"]["participants"]
        
        # Remove from second activity
        response2 = client.delete(
            f"/activities/Drama Club/participants/{email}"
        )
        assert response2.status_code == 200
        
        # Verify removed from both
        activities = client.get("/activities").json()
        assert email not in activities["Programming Class"]["participants"]
        assert email not in activities["Drama Club"]["participants"]


class TestRemoveParticipantErrorHandling:
    """Tests for error scenarios"""
    
    def test_remove_from_nonexistent_activity(self, client):
        """Test removing participant from non-existent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent Club/participants/student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_remove_nonexistent_participant(self, client):
        """Test removing non-existent participant returns 404"""
        response = client.delete(
            "/activities/Chess Club/participants/notexist@mergington.edu"
        )
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]
    
    def test_remove_participant_twice(self, client):
        """Test removing the same participant twice returns 404 on second attempt"""
        email = "michael@mergington.edu"
        
        # First removal
        response1 = client.delete(
            f"/activities/Chess Club/participants/{email}"
        )
        assert response1.status_code == 200
        
        # Second removal (should fail)
        response2 = client.delete(
            f"/activities/Chess Club/participants/{email}"
        )
        assert response2.status_code == 404
        assert "Participant not found" in response2.json()["detail"]
    
    def test_remove_participant_case_sensitive_email(self, client):
        """Test that email removal is case-sensitive"""
        email_lowercase = "michael@mergington.edu"
        email_uppercase = "MICHAEL@MERGINGTON.EDU"
        
        # Try to remove with different case
        response = client.delete(
            f"/activities/Chess Club/participants/{email_uppercase}"
        )
        # Should fail since emails are case-sensitive
        assert response.status_code == 404
        
        # Verify original email is still there
        activities = client.get("/activities").json()
        assert email_lowercase in activities["Chess Club"]["participants"]
    
    def test_remove_participant_case_sensitive_activity(self, client):
        """Test that activity name is case-sensitive in removal"""
        email = "michael@mergington.edu"
        
        response = client.delete(
            f"/activities/chess club/participants/{email}"  # lowercase
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRemoveParticipantIntegration:
    """Integration tests combining signup and removal"""
    
    def test_signup_then_remove(self, client):
        """Test signing up then removing a participant"""
        email = "integration@mergington.edu"
        activity = "Programming Class"
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        # Verify added
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
        
        # Remove
        remove_response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        assert remove_response.status_code == 200
        
        # Verify removed
        activities = client.get("/activities").json()
        assert email not in activities[activity]["participants"]
    
    def test_signup_remove_signup_again(self, client):
        """Test signing up, removing, then signing up again"""
        email = "flexible@mergington.edu"
        activity = "Soccer Team"
        
        # First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Remove
        response2 = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response3.status_code == 200
        
        # Verify final state
        activities = client.get("/activities").json()
        assert email in activities[activity]["participants"]
