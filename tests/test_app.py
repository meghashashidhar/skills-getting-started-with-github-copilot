"""
Test suite for the Mergington High School Activities API.
Uses AAA (Arrange-Act-Assert) pattern for clear test structure.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_all_activities(self, client):
        """
        Arrange: Activities are pre-populated in fixtures.
        Act: Make GET request to /activities.
        Assert: Response contains all activities with correct structure.
        """
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == 3
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities
    
    def test_get_activities_returns_correct_activity_structure(self, client):
        """
        Arrange: Activities are pre-populated.
        Act: Make GET request to /activities.
        Assert: Each activity has required fields.
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        activity = activities["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_get_activities_includes_participant_count(self, client):
        """
        Arrange: Chess Club has 2 existing participants.
        Act: Make GET request to /activities.
        Assert: Participants list includes expected emails.
        """
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        chess_participants = activities["Chess Club"]["participants"]
        assert "michael@mergington.edu" in chess_participants
        assert "daniel@mergington.edu" in chess_participants
        assert len(chess_participants) == 2


class TestSignUpForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_adds_participant_successfully(self, client):
        """
        Arrange: Chess Club has 2 participants initially.
        Act: Sign up a new student for Chess Club.
        Assert: Response is success and participant count increases.
        """
        # Arrange
        new_email = "new_student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/Chess Club/signup?email={new_email}",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "Signed up" in result["message"]
        assert new_email in result["message"]
    
    def test_signup_persists_participant(self, client):
        """
        Arrange: Chess Club has 2 participants initially.
        Act: Sign up a new student, then fetch activities.
        Assert: New student appears in participants list.
        """
        # Arrange
        new_email = "new_student@mergington.edu"
        
        # Act - Sign up
        client.post(f"/activities/Chess Club/signup?email={new_email}")
        
        # Act - Verify
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert new_email in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 3
    
    def test_signup_with_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Nonexistent activity "Fake Club" doesn't exist.
        Act: Try to sign up for "Fake Club".
        Assert: API returns 404 error.
        """
        # Arrange
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/Fake Club/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_signup_allows_duplicate_email(self, client):
        """
        Arrange: michael@mergington.edu is already in Chess Club.
        Act: Sign up michael@mergington.edu again.
        Assert: Signup succeeds (current behavior allows duplicates).
        """
        # Arrange
        email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        
        # Assert
        assert response.status_code == 200
        # Verify duplicate was added
        response = client.get("/activities")
        participants = response.json()["Chess Club"]["participants"]
        assert participants.count(email) == 2  # 1 original + 1 new


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint."""
    
    def test_remove_participant_successfully(self, client):
        """
        Arrange: michael@mergington.edu is in Chess Club.
        Act: Delete michael@mergington.edu from Chess Club.
        Assert: Response is success and participant removed.
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/{activity}/participants/{email}")
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "Removed" in result["message"]
        assert email in result["message"]
    
    def test_remove_participant_persists(self, client):
        """
        Arrange: michael@mergington.edu is in Chess Club (2 participants total).
        Act: Delete michael@mergington.edu, then fetch activities.
        Assert: Participant no longer appears in list.
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act - Remove
        client.delete(f"/activities/{activity}/participants/{email}")
        
        # Act - Verify
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert email not in activities[activity]["participants"]
        assert len(activities[activity]["participants"]) == 1
        assert activities[activity]["participants"][0] == "daniel@mergington.edu"
    
    def test_remove_participant_from_nonexistent_activity_returns_404(self, client):
        """
        Arrange: "Fake Club" doesn't exist.
        Act: Try to remove a participant from "Fake Club".
        Assert: API returns 404 error.
        """
        # Arrange
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(f"/activities/Fake Club/participants/{email}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"
    
    def test_remove_nonexistent_participant_returns_404(self, client):
        """
        Arrange: fake@example.com is not in Chess Club.
        Act: Try to remove fake@example.com from Chess Club.
        Assert: API returns 404 error.
        """
        # Arrange
        email = "fake@example.com"
        
        # Act
        response = client.delete(f"/activities/Chess Club/participants/{email}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Participant not found in this activity"


class TestRootRedirect:
    """Tests for GET / endpoint."""
    
    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: Root path is configured to redirect.
        Act: Make GET request to /.
        Assert: Response redirects to /static/index.html.
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
