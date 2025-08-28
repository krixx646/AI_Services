from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch
import json


class PaymentsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(username="u1", email="u1@example.com", password="pass12345")
        self.client.force_authenticate(self.user)

    @patch("payments.views.requests.post")
    def test_init_payment(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "status": True,
            "data": {"authorization_url": "https://paystack.test/redirect"},
        }
        r = self.client.post("/api/payments/init/", {"amount": "5000", "currency": "NGN"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("authorization_url", r.data)

    @patch("payments.views.requests.get")
    def test_verify_payment(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": {"status": "success"}}
        r = self.client.get("/api/payments/verify/any-ref/")
        self.assertEqual(r.status_code, 200)

# Create your tests here.
