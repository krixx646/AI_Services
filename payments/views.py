import json
import uuid
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


class InitPaymentView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        currency = str(request.data.get("currency", "NGN")).upper()
        if not amount:
            return Response({"detail": "amount is required"}, status=status.HTTP_400_BAD_REQUEST)
        if currency not in getattr(settings, "PAYSTACK_ALLOWED_CURRENCIES", ["NGN", "USD"]):
            return Response({"detail": f"currency not allowed: {currency}"}, status=status.HTTP_400_BAD_REQUEST)
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

        # Create Paystack transaction
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        smallest_unit = int((amount_value * 100).to_integral_value(rounding=ROUND_HALF_UP))
        payload = {
            "email": request.user.email,
            "amount": smallest_unit,
            "currency": currency,
            "reference": reference,
        }
        resp = requests.post("https://api.paystack.co/transaction/initialize", headers=headers, json=payload)
        if resp.status_code != 200:
            tx.status = PaymentTransaction.Status.FAILED
            tx.raw_payload = {"error": resp.text}
            tx.save(update_fields=["status", "raw_payload"])
            return Response({"detail": "Failed to initialize payment"}, status=status.HTTP_502_BAD_GATEWAY)

        data = resp.json()
        tx.raw_payload = data
        tx.save(update_fields=["raw_payload"])
        return Response({"authorization_url": data.get("data", {}).get("authorization_url"), "reference": reference})


@method_decorator(csrf_exempt, name="dispatch")
class PaystackWebhookView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Verify signature using Paystack secret key (HMAC SHA512 of raw body)
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
            # Create a bot instance for the user
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
        # Optionally update local record
        try:
            tx = PaymentTransaction.objects.get(reference=reference)
            if status_text == "success" and tx.status != PaymentTransaction.Status.SUCCESS:
                tx.status = PaymentTransaction.Status.SUCCESS
                tx.raw_payload = data
                tx.save(update_fields=["status", "raw_payload"])
        except PaymentTransaction.DoesNotExist:
            pass
        return Response(data, status=resp.status_code)
