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
    def test_init_payment_server_pricing_and_model(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "status": True,
            "data": {"authorization_url": "https://paystack.test/redirect"},
        }
        # Client tries to spoof amount but server will compute from plan + express
        r = self.client.post(
            "/api/payments/init/",
            {"amount": "1", "currency": "NGN", "plan": "starter", "express": True, "model": "gpt-5"},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("authorization_url", r.data)

    @patch("payments.views.requests.get")
    def test_verify_payment_backfills_bot(self, mock_get):
        mock_get.return_value.status_code = 200
        ref = "ref-123"
        mock_get.return_value.json.return_value = {"data": {"status": "success", "reference": ref}}
        # Create a pending tx first
        from payments.models import PaymentTransaction
        PaymentTransaction.objects.create(student=self.user, reference=ref, amount=5000, currency="NGN")
        r = self.client.get(f"/api/payments/verify/{ref}/")
        self.assertEqual(r.status_code, 200)
        # Ensure a bot is created and linked
        from payments.models import BotInstance, PaymentTransaction
        tx = PaymentTransaction.objects.get(reference=ref)
        raw = tx.raw_payload or {}
        self.assertTrue(isinstance(raw, dict) and raw.get("bot_reference"))
        self.assertEqual(BotInstance.objects.filter(owner=self.user).count(), 1)

    def test_receipt_access_control(self):
        # Create tx for user
        from payments.models import PaymentTransaction
        ref = "abc"
        PaymentTransaction.objects.create(student=self.user, reference=ref, amount=1000, currency="NGN")
        # Other user cannot access
        from django.contrib.auth import get_user_model
        other = get_user_model().objects.create_user(username="u2", email="u2@example.com", password="pass12345")
        client2 = APIClient()
        client2.force_authenticate(other)
        r = client2.get(f"/api/payments/receipt/{ref}/")
        self.assertIn(r.status_code, [302, 403, 404])

# Create your tests here.
