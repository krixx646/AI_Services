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
from django.shortcuts import redirect

logger = logging.getLogger(__name__)


class InitPaymentView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        currency = str(request.data.get("currency", "NGN")).upper()
        plan = (request.data.get("plan") or "").strip()
        model_selected = (request.data.get("model") or "").strip()
        try:
            quantity_raw = request.data.get("quantity", 1)
            quantity = int(quantity_raw)
        except Exception:
            quantity = 1
        if quantity < 1:
            quantity = 1
        if quantity > 20:
            quantity = 20
        express = bool(request.data.get("express", False))

        # Validate currency
        allowed_currencies = getattr(settings, "PAYSTACK_ALLOWED_CURRENCIES", ["NGN"]) or ["NGN"]
        if currency not in allowed_currencies:
            return Response({"detail": f"currency not allowed: {currency}"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate plan and compute server-side total in major units (ignore client amount)
        catalog = getattr(settings, "PRICING_CATALOG", {})
        express_prices = getattr(settings, "EXPRESS_ADDON_PRICE", {})
        currency_catalog = catalog.get(currency, {})
        if not plan or plan not in currency_catalog:
            return Response({"detail": f"invalid plan for {currency}: {plan or '(missing)'}"}, status=status.HTTP_400_BAD_REQUEST)

        base_price_major = Decimal(str(currency_catalog[plan]))
        # Multiply by quantity for single-course plan only
        if plan == "single-course":
            base_price_major = (base_price_major * Decimal(str(quantity)))
        express_major = Decimal(str(express_prices.get(currency, 0))) if express else Decimal("0")
        amount_value = (base_price_major + express_major).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

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
        # amount_value computed server-side above

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
        # Validate and persist model in metadata (single select; default to gpt-5)
        allowed_models = set(getattr(settings, "AI_MODELS_ALLOWED", []))
        if model_selected not in allowed_models:
            model_selected = "gpt-5" if "gpt-5" in allowed_models else (next(iter(allowed_models)) if allowed_models else "")

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
                "model": model_selected,
                "quantity": quantity if plan == "single-course" else 1,
                "server_pricing": True,
            },
        }

        try:
            logger.warning("[Paystack Init] currency=%s amount=%s plan=%s express=%s key_present=%s email=%s", currency, smallest_unit, plan, express, bool(secret_key), user_email)
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
            # Preserve paystack payload and attach bot_reference after creation
            tx.raw_payload = payload if isinstance(payload, dict) else {"paystack": payload}
            tx.save(update_fields=["status", "raw_payload"])
            bot = BotInstance.objects.create(owner=tx.student, status=BotInstance.Status.PENDING)
            try:
                raw = tx.raw_payload or {}
                if isinstance(raw, dict):
                    raw["bot_reference"] = str(bot.reference)
                    tx.raw_payload = raw
                    tx.save(update_fields=["raw_payload"])
            except Exception:
                pass
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
            if status_text == "success":
                # Update status/payload if not already saved
                if tx.status != PaymentTransaction.Status.SUCCESS:
                    tx.status = PaymentTransaction.Status.SUCCESS
                    tx.raw_payload = data
                    tx.save(update_fields=["status", "raw_payload"])
                # Ensure a bot is linked even if webhook was missed
                try:
                    raw = tx.raw_payload if isinstance(tx.raw_payload, dict) else {}
                    has_bot = isinstance(raw, dict) and bool(raw.get("bot_reference"))
                    if not has_bot:
                        bot = BotInstance.objects.create(owner=tx.student, status=BotInstance.Status.PENDING)
                        raw = raw or {}
                        raw["bot_reference"] = str(bot.reference)
                        tx.raw_payload = raw
                        tx.save(update_fields=["raw_payload"])
                except Exception:
                    pass
        except PaymentTransaction.DoesNotExist:
            pass
        return Response(data, status=resp.status_code)


class PaymentSuccessPageView(TemplateView):
    template_name = "payments/success.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["reference"] = self.request.GET.get("reference")
        return ctx


class PreparePaymentView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Prepare an inline checkout: create server-side transaction and return
        reference and computed fields for Paystack inline JS. Does NOT call
        Paystack initialize API.
        """
        currency = str(request.data.get("currency", "NGN")).upper()
        plan = (request.data.get("plan") or "").strip()
        express = bool(request.data.get("express", False))
        model_selected = (request.data.get("model") or "").strip()
        try:
            quantity_raw = request.data.get("quantity", 1)
            quantity = int(quantity_raw)
        except Exception:
            quantity = 1
        quantity = max(1, min(20, quantity))

        allowed_currencies = getattr(settings, "PAYSTACK_ALLOWED_CURRENCIES", ["NGN"]) or ["NGN"]
        if currency not in allowed_currencies:
            return Response({"detail": f"currency not allowed: {currency}"}, status=status.HTTP_400_BAD_REQUEST)

        catalog = getattr(settings, "PRICING_CATALOG", {})
        express_prices = getattr(settings, "EXPRESS_ADDON_PRICE", {})
        currency_catalog = catalog.get(currency, {})
        if not plan or plan not in currency_catalog:
            return Response({"detail": f"invalid plan for {currency}: {plan or '(missing)'}"}, status=status.HTTP_400_BAD_REQUEST)

        base_price_major = Decimal(str(currency_catalog[plan]))
        if plan == "single-course":
            base_price_major = (base_price_major * Decimal(str(quantity)))
        express_major = Decimal(str(express_prices.get(currency, 0))) if express else Decimal("0")
        amount_value = (base_price_major + express_major).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        public_key = (os.environ.get('PAYSTACK_PUBLIC_KEY') or settings.PAYSTACK_PUBLIC_KEY or '').strip()
        if not public_key:
            return Response({"detail": "PAYSTACK_PUBLIC_KEY not configured"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        user_email = (request.user.email or '').strip()
        if not user_email:
            return Response({"detail": "Your account has no email set. Please add an email on your profile and try again."}, status=status.HTTP_400_BAD_REQUEST)

        reference = str(uuid.uuid4())
        tx = PaymentTransaction.objects.create(
            student=request.user,
            reference=reference,
            amount=amount_value,
            currency=currency,
            status=PaymentTransaction.Status.PENDING,
        )

        callback_url = request.build_absolute_uri(reverse("payment_success"))
        amount_kobo = int((amount_value * 100).to_integral_value(rounding=ROUND_HALF_UP))

        allowed_models = set(getattr(settings, "AI_MODELS_ALLOWED", []))
        if model_selected not in allowed_models:
            model_selected = "gpt-5" if "gpt-5" in allowed_models else (next(iter(allowed_models)) if allowed_models else "")

        metadata = {
            "plan": plan,
            "express": express,
            "user_id": request.user.id,
            "model": model_selected,
            "quantity": quantity if plan == "single-course" else 1,
            "server_pricing": True,
        }

        # Stash minimal metadata into tx.raw_payload for reference
        try:
            tx.raw_payload = {"preinit": {"amount_kobo": amount_kobo, "metadata": metadata}}
            tx.save(update_fields=["raw_payload"])
        except Exception:
            pass

        return Response({
            "reference": reference,
            "amount_kobo": amount_kobo,
            "currency": currency,
            "email": user_email,
            "public_key": public_key,
            "callback_url": callback_url,
            "metadata": metadata,
        })


class PaymentReceiptPageView(TemplateView):
    template_name = "payments/receipt.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        reference = kwargs.get("reference")
        try:
            tx = PaymentTransaction.objects.get(reference=reference, student=self.request.user)
        except PaymentTransaction.DoesNotExist:
            # Hide existence details
            ctx["not_found"] = True
            return ctx

        # Extract metadata if present
        metadata = {}
        amount_minor = None
        currency = tx.currency
        status_text = tx.status
        paid_at = None
        if isinstance(tx.raw_payload, dict):
            data = tx.raw_payload.get("data") or {}
            if isinstance(data, dict):
                metadata = data.get("metadata") or {}
                amount_minor = data.get("amount")
                currency = data.get("currency") or currency
                status_text = data.get("status") or status_text
                paid_at = data.get("paidAt") or data.get("transaction_date")

        # Fallbacks
        amount_major = float(tx.amount)
        if isinstance(amount_minor, int):
            amount_major = round(amount_minor / 100.0, 2)

        ctx.update({
            "tx": tx,
            "reference": tx.reference,
            "amount": amount_major,
            "currency": currency,
            "status": status_text,
            "paid_at": paid_at,
            "metadata": metadata,
            "model": metadata.get("model") or "gpt-5",
            "quantity": metadata.get("quantity") or (1 if metadata.get("plan") == "single-course" else 1),
            "plan": metadata.get("plan"),
            "express": bool(metadata.get("express")),
        })
        return ctx


class ForceLinkBotView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, reference: str):
        try:
            tx = PaymentTransaction.objects.get(reference=reference, student=request.user)
        except PaymentTransaction.DoesNotExist:
            return Response({"detail": "payment not found"}, status=status.HTTP_404_NOT_FOUND)

        if tx.status != PaymentTransaction.Status.SUCCESS:
            return Response({"detail": "payment not successful"}, status=status.HTTP_400_BAD_REQUEST)

        raw = tx.raw_payload if isinstance(tx.raw_payload, dict) else {}
        bot_ref = raw.get("bot_reference") if isinstance(raw, dict) else None
        if bot_ref:
            try:
                bot = BotInstance.objects.get(reference=bot_ref)
                return Response({"linked": True, "bot_reference": str(bot.reference), "status": bot.status, "url": bot.bot_url})
            except BotInstance.DoesNotExist:
                pass

        bot = BotInstance.objects.create(owner=tx.student, status=BotInstance.Status.PENDING)
        raw = raw or {}
        raw["bot_reference"] = str(bot.reference)
        tx.raw_payload = raw
        tx.save(update_fields=["raw_payload"])
        return Response({"linked": True, "bot_reference": str(bot.reference), "status": bot.status, "url": bot.bot_url})
