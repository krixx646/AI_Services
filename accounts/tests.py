from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model


class AccountsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_and_login(self):
        # Register
        payload = {
            "email": "test@example.com",
            "password": "strongpass123",
            "confirm_password": "strongpass123",
            "username": "testuser",
            "phone": "0800000000",
        }
        r = self.client.post("/api/accounts/register/", payload, format="json")
        self.assertEqual(r.status_code, 201)

        # Login
        r = self.client.post(
            "/api/accounts/login/",
            {"email": payload["email"], "password": payload["password"]},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)
        self.assertIn("refresh", r.data)

    def test_auth_required_for_payments(self):
        # Unauthenticated should get 401 on payments init
        client = APIClient()
        r = client.post("/api/payments/init/", {"currency": "NGN", "plan": "trial"}, format="json")
        self.assertEqual(r.status_code, 401)

# Create your tests here.
