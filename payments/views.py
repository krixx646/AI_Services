import json
import uuid
import logging
import os
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import PaymentTransaction, BotInstance
import hmac
import hashlib
from django.urls import reverse
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class InitPaymentView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        currency = str(request.data.get("currency", "NGN")).upper()
        plan = request.data.get("plan")
        express = bool(request.data.get("express", False))
        if not amount:
            return Response({"detail": "amount is required"}, status=status.HTTP_400_BAD_REQUEST)
        if currency not in getattr(settings, "PAYSTACK_ALLOWED_CURRENCIES", ["NGN", "USD"]):
            return Response({"detail": f"currency not allowed: {currency}"}, status=status.HTTP_400_BAD_REQUEST)

        # Resolve secret key at request time to avoid stale settings during dev
        secret_key = (os.environ.get('PAYSTACK_SECRET_KEY') or settings.PAYSTACK_SECRET_KEY or '').strip()
        # Dev overrides to ensure correct key is used locally without DevTools
        if settings.DEBUG:
            force_env = (os.environ.get('PAYSTACK_FORCE_SECRET_KEY') or '').strip()
            if force_env:
                secret_key = force_env
        if not secret_key:
            return Response({"detail": "PAYSTACK_SECRET_KEY not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user_email = (request.user.email or '').strip()
        if not user_email:
            return Response({"detail": "Your account has no email set. Please add an email on your profile and try again."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            amount_value = Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, TypeError, ValueError):
            return Response({"detail": "amount must be a valid decimal number"}, status=status.HTTP_400_BAD_REQUEST)

        reference = str(uuid.uuid4())
        tx = PaymentTransaction.objects.create(
            student=request.user,
            reference=reference,
            amount=amount_value,
            currency=currency,
            status=PaymentTransaction.Status.PENDING,
        )

        headers = {
            "Authorization": f"Bearer {secret_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        smallest_unit = int((amount_value * 100).to_integral_value(rounding=ROUND_HALF_UP))
        callback_url = request.build_absolute_uri(reverse("payment_success"))
        payload = {
            "email": user_email,
            "amount": smallest_unit,
            "currency": currency,
            "reference": reference,
            "callback_url": callback_url,
            "metadata": {
                "plan": plan,
                "express": express,
                "user_id": request.user.id,
            },
        }

        try:
            logger.warning("[Paystack Init] currency=%s amount=%s key_present=%s email=%s", currency, smallest_unit, bool(secret_key), user_email)
        except Exception:
            pass

        resp = requests.post("https://api.paystack.co/transaction/initialize", headers=headers, json=payload, timeout=20)
        if resp.status_code != 200:
            paystack_error = None
            message = "Failed to initialize payment"
            try:
                paystack_error = resp.json()
                if isinstance(paystack_error, dict):
                    message = paystack_error.get("message") or message
            except Exception:
                paystack_error = {"message": resp.text}
            try:
                logger.error("[Paystack Init ERROR] status=%s body=%s", resp.status_code, resp.text)
            except Exception:
                pass
            tx.status = PaymentTransaction.Status.FAILED
            tx.raw_payload = {"error": paystack_error, "init_payload": {"currency": currency, "metadata": payload.get("metadata")}}
            tx.save(update_fields=["status", "raw_payload"])
            # Treat 4xx from Paystack as client errors (bad request), else 502
            http_status = status.HTTP_400_BAD_REQUEST if 400 <= resp.status_code < 500 else status.HTTP_502_BAD_GATEWAY
            return Response({"detail": message, "paystack": paystack_error}, status=http_status)

        data = resp.json()
        tx.raw_payload = data
        tx.save(update_fields=["raw_payload"])
        return Response({"authorization_url": data.get("data", {}).get("authorization_url"), "reference": reference})


@method_decorator(csrf_exempt, name="dispatch")
class PaystackWebhookView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        signature = request.META.get("HTTP_X_PAYSTACK_SIGNATURE")
        if settings.PAYSTACK_SECRET_KEY:
            computed = hmac.new(
                key=settings.PAYSTACK_SECRET_KEY.encode("utf-8"),
                msg=request.body,
                digestmod=hashlib.sha512,
            ).hexdigest()
            if not signature or signature != computed:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        event = payload.get("event")
        data = payload.get("data", {})
        reference = data.get("reference")
        if not reference:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            tx = PaymentTransaction.objects.get(reference=reference)
        except PaymentTransaction.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if event == "charge.success":
            tx.status = PaymentTransaction.Status.SUCCESS
            tx.raw_payload = payload
            tx.save(update_fields=["status", "raw_payload"])
            BotInstance.objects.create(owner=tx.student, status=BotInstance.Status.PENDING)
        elif event in {"charge.failed", "charge.error"}:
            tx.status = PaymentTransaction.Status.FAILED
            tx.raw_payload = payload
            tx.save(update_fields=["status", "raw_payload"])

        return Response(status=status.HTTP_200_OK)


class VerifyPaymentView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, reference: str):
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        resp = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
        data = resp.json() if resp.content else {}
        status_text = data.get("data", {}).get("status") if data else None
        try:
            tx = PaymentTransaction.objects.get(reference=reference)
            if status_text == "success" and tx.status != PaymentTransaction.Status.SUCCESS:
                tx.status = PaymentTransaction.Status.SUCCESS
                tx.raw_payload = data
                tx.save(update_fields=["status", "raw_payload"])
        except PaymentTransaction.DoesNotExist:
            pass
        return Response(data, status=resp.status_code)


class PaymentSuccessPageView(TemplateView):
    template_name = "payments/success.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["reference"] = self.request.GET.get("reference")
        return ctx
