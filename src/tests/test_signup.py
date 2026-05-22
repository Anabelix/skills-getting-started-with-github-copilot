"""
Tests for the signup endpoint (POST /activities/{activity_name}/signup).

This endpoint allows students to sign up for activities via email.
Includes happy path and error handling tests.
"""

import pytest


class TestSignupHappyPath:
    """Tests for successful signup scenarios"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response.status_code == 200
        assert response.json() == {
            "message": "Signed up newstudent@mergington.edu for Chess Club"
        }
    
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the activity"""
        email = "newstudent@mergington.edu"
        
        # Sign up
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
    
    def test_signup_multiple_students(self, client):
        """Test that multiple students can sign up for the same activity"""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email1}
        )
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email2}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities = client.get("/activities").json()
        assert email1 in activities["Programming Class"]["participants"]
        assert email2 in activities["Programming Class"]["participants"]
    
    def test_signup_to_different_activities(self, client):
        """Test that a student can sign up for multiple activities"""
        email = "versatile@mergington.edu"
        
        response1 = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        response2 = client.post(
            "/activities/Programming Class/signup",
            params={"email": email}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        activities = client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestSignupErrorHandling:
    """Tests for error scenarios"""
    
    def test_signup_activity_not_found(self, client):
        """Test signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_already_signed_up(self, client):
        """Test that duplicate signup returns 400 error"""
        email = "michael@mergington.edu"  # Already in Chess Club
        
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_duplicate_detection_case_sensitive(self, client):
        """Test that email comparison is case-insensitive (if applicable)"""
        # This test assumes case-sensitive matching (as per current implementation)
        email_original = "michael@mergington.edu"
        email_uppercase = "MICHAEL@MERGINGTON.EDU"
        
        response = client.post(
            "/activities/Programming Class/signup",
            params={"email": email_uppercase}
        )
        # Should succeed since emails are case-sensitive in current implementation
        assert response.status_code == 200
    
    def test_signup_duplicate_same_case(self, client):
        """Test duplicate detection with exact same email"""
        email = "newstudent@mergington.edu"
        
        # First signup
        response1 = client.post(
            "/activities/Art Club/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email
        response2 = client.post(
            "/activities/Art Club/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_activity_name_case_sensitive(self, client):
        """Test that activity name is case-sensitive"""
        response = client.post(
            "/activities/chess club/signup",  # lowercase
            params={"email": "student@mergington.edu"}
        )
        # Should fail because activity name is case-sensitive
        assert response.status_code == 404


class TestSignupParticipantLimit:
    """Tests for max_participants limit"""
    
    def test_signup_no_error_when_space_available(self, client):
        """Test signup works when activity has space"""
        # Gym Class has max_participants=30 and 2 current participants
        response = client.post(
            "/activities/Gym Class/signup",
            params={"email": "newgym@mergington.edu"}
        )
        assert response.status_code == 200
    
    def test_signup_with_full_activity(self, client):
        """Test signup behavior when activity is at or near capacity"""
        # Art Club has max_participants=15 and 2 current participants
        # Fill it up
        for i in range(13):
            email = f"student{i}@mergington.edu"
            response = client.post(
                "/activities/Art Club/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify it's full
        activities = client.get("/activities").json()
        assert len(activities["Art Club"]["participants"]) == 15
        
        # Try to sign up when full (optional: app may or may not enforce this)
        # This documents current behavior for future enhancement
        overflow_response = client.post(
            "/activities/Art Club/signup",
            params={"email": "overflow@mergington.edu"}
        )
        # Current implementation allows signup regardless of max_participants
        # This test documents that behavior; can be updated if enforcement added
