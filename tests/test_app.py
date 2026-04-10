"""
FastAPI Backend Tests for Mergington High School Activities API

All tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and preconditions
- Act: Execute the API endpoint/method being tested
- Assert: Verify response status code, content, and side effects
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client, activities):
        """
        Test: GET /activities returns all available activities
        
        Arrange: Use clean activities fixture
        Act: Call GET /activities
        Assert: Response status is 200 and contains all activities
        """
        # Arrange
        expected_activity_count = len(activities)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == expected_activity_count
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_has_correct_structure(self, client, activities):
        """
        Test: GET /activities returns activities with correct structure
        
        Arrange: Use clean activities fixture
        Act: Call GET /activities
        Assert: Each activity has required fields (description, schedule, max_participants, participants)
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        for activity_name, activity_details in data.items():
            assert isinstance(activity_details, dict)
            assert required_fields.issubset(activity_details.keys())
            assert isinstance(activity_details["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_happy_path(self, client, activities):
        """
        Test: New student can successfully sign up for an activity
        
        Arrange: Set up Gym Class with 0 participants
        Act: POST signup for new student to Gym Class
        Assert: Response status 200, message confirms signup, participants list updated
        """
        # Arrange
        activity_name = "Gym Class"
        new_email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert new_email in data["message"]
        assert activity_name in data["message"]
        assert new_email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_duplicate_student_returns_400(self, client, activities):
        """
        Test: Duplicate signup (same email twice) returns 400 error
        
        Arrange: Chess Club has michael@mergington.edu as participant
        Act: Try to sign up michael@mergington.edu again
        Assert: Response status 400, error message about already signed up
        """
        # Arrange
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": existing_email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client, activities):
        """
        Test: Signup to non-existent activity returns 404 error
        
        Arrange: Pick an activity that does not exist
        Act: Try to sign up to non-existent activity
        Assert: Response status 404, error message about activity not found
        """
        # Arrange
        activity_name = "Underwater Basket Weaving"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant_happy_path(self, client, activities):
        """
        Test: Existing participant can successfully unregister from activity
        
        Arrange: Programming Class has emma@mergington.edu as participant
        Act: DELETE unregister emma@mergington.edu from Programming Class
        Assert: Response status 200, message confirms unregister, participants list updated
        """
        # Arrange
        activity_name = "Programming Class"
        email_to_remove = "emma@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email_to_remove}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email_to_remove in data["message"]
        assert activity_name in data["message"]
        assert email_to_remove not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_nonexistent_email_returns_400(self, client, activities):
        """
        Test: Unregister with email not in participants returns 400 error
        
        Arrange: Chess Club exists, but nonexistent@email.com is not a participant
        Act: Try to unregister nonexistent@email.com from Chess Club
        Assert: Response status 400, error message about not registered
        """
        # Arrange
        activity_name = "Chess Club"
        email = "nonexistent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()

    def test_unregister_from_nonexistent_activity_returns_404(self, client, activities):
        """
        Test: Unregister from non-existent activity returns 404 error
        
        Arrange: Activity does not exist
        Act: Try to unregister from non-existent activity
        Assert: Response status 404, error message about activity not found
        """
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestIntegration:
    """Integration tests combining multiple operations"""

    def test_signup_then_unregister_workflow(self, client, activities):
        """
        Test: Complete workflow of signing up and then unregistering
        
        Arrange: Use clean Gym Class (0 participants)
        Act: Sign up new student, verify signup, then unregister, verify removal
        Assert: Student added then removed, participant count correct at each step
        """
        # Arrange
        activity_name = "Gym Class"
        email = "test_student@mergington.edu"

        # Act & Assert: Sign up
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]

        # Act & Assert: Unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_multiple_signups_increase_participant_count(self, client, activities):
        """
        Test: Multiple signups correctly increase participant count
        
        Arrange: Use Gym Class with 0 initial participants
        Act: Sign up 3 different students sequentially
        Assert: Participant count increases by 1 each time, all emails present
        """
        # Arrange
        activity_name = "Gym Class"
        emails = ["student1@mergington.edu", "student2@mergington.edu", "student3@mergington.edu"]

        # Act & Assert
        for i, email in enumerate(emails):
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
            assert len(activities[activity_name]["participants"]) == i + 1
            assert email in activities[activity_name]["participants"]
