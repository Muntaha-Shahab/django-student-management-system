from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from .models import Student


class AuthenticationTests(TestCase):
    """Tests for signup, login, and authentication."""

    def test_login_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_signup_page_loads(self):
        response = self.client.get("/signup/")
        self.assertEqual(response.status_code, 200)

    @patch("accounts.views.EmailMessage.send", return_value=1)
    def test_signup_creates_inactive_user(self, mock_send):
        response = self.client.post(
            "/signup/",
            {
                "username": "teststudent",
                "email": "teststudent@example.com",
                "password": "TestPassword123!",
            },
            HTTP_HOST="testserver",
        )

        user = User.objects.get(username="teststudent")

        self.assertEqual(user.email, "teststudent@example.com")
        self.assertFalse(user.is_active)
        self.assertRedirects(response, "/")
        mock_send.assert_called_once()

    def test_login_rejects_inactive_user(self):
        User.objects.create_user(
            username="inactiveuser",
            password="TestPassword123!",
            is_active=False,
        )

        response = self.client.post(
            "/",
            {
                "username": "inactiveuser",
                "password": "TestPassword123!",
            },
            follow=True,
        )

        self.assertFalse(response.context["user"].is_authenticated)
        self.assertContains(response, "Invalid username or password")

    def test_login_accepts_active_user(self):
        User.objects.create_user(
            username="activeuser",
            password="TestPassword123!",
        )

        response = self.client.post(
            "/",
            {
                "username": "activeuser",
                "password": "TestPassword123!",
            },
        )

        self.assertRedirects(response, "/dashboard/")

    def test_dashboard_requires_login(self):
        response = self.client.get("/dashboard/")

        self.assertRedirects(
            response,
            "/accounts/login/?next=/dashboard/",
            fetch_redirect_response=False,
        )


class StudentManagementTests(TestCase):
    """Tests for viewing, adding, and deleting students."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="dashboarduser",
            password="TestPassword123!",
        )
        self.client.force_login(self.user)

    def test_dashboard_displays_students(self):
        Student.objects.create(
            name="Ali Khan",
            email="ali@example.com",
            age=21,
            course="Computer Science",
        )

        response = self.client.get("/dashboard/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total"], 1)
        self.assertContains(response, "Ali Khan")

    def test_add_student(self):
        response = self.client.post(
            "/add/",
            {
                "name": "Sara Ahmed",
                "email": "sara@example.com",
                "age": 22,
                "course": "Software Engineering",
            },
        )

        self.assertRedirects(response, "/dashboard/")
        self.assertTrue(
            Student.objects.filter(name="Sara Ahmed").exists()
        )

    def test_delete_student(self):
        student = Student.objects.create(
            name="Delete Me",
            email="delete@example.com",
            age=20,
            course="Computer Science",
        )

        response = self.client.get(f"/delete/{student.id}/")

        self.assertRedirects(response, "/dashboard/")
        self.assertFalse(
            Student.objects.filter(id=student.id).exists()
        )
