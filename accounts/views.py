from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Student
from .serializers import RegistrationSerialiser, LoginSerialiser, ProfileSerialiser
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.core.mail import send_mail
from django.views import View
from .forms import RegistrationForm, LoginForm, ProfileForm



# Create your views here.

class RegistrationViewSet(viewsets.GenericViewSet):
    queryset = Student.objects.all()
    serializer_class = RegistrationSerialiser
    permission_classes = [AllowAny]
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Mark inactive until email verified
        try:
            user.is_active = False
            user.save(update_fields=["is_active"])
        except Exception:
            pass
        # Send verification email
        try:
            signer = TimestampSigner()
            token = signer.sign(user.email)
            verify_url = request.build_absolute_uri(f"/api/accounts/verify-email/?token={token}")
            subject = "Verify your email"
            message = f"Hi {user.username},\n\nPlease verify your email by clicking the link below:\n{verify_url}\n\nIf you didn't sign up, you can ignore this message."
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com')
            send_mail(subject, message, from_email, [user.email], fail_silently=True)
        except Exception:
            pass
        return Response({"message": "Registration successful. Please check your email to verify your account."}, status=status.HTTP_201_CREATED)


class LoginViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = LoginSerialiser
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        # Establish a server-side session for browser clients (optional alongside JWT)
        user = serializer.validated_data.get("user")
        if user is not None:
            login(request, user)
        return Response(serializer.data, status=status.HTTP_200_OK)


def verify_email_view(request):
    token = request.GET.get("token", "")
    signer = TimestampSigner()
    try:
        email = signer.unsign(token, max_age=60 * 60 * 24 * 3)  # 3 days
        try:
            user = Student.objects.get(email__iexact=email)
            if not user.is_active:
                user.is_active = True
                user.save(update_fields=["is_active"])
        except Student.DoesNotExist:
            pass
        return redirect("login")
    except (BadSignature, SignatureExpired):
        return render(request, "verification_failed.html", {})

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = ProfileSerialiser
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "patch", "delete", "head", "options"]


class SignupPageView(View):
    def get(self, request):
        return render(request, "signup.html", {"form": RegistrationForm()})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Mark inactive and send verification email (same flow as API)
            try:
                user.is_active = False
                user.save(update_fields=["is_active"])
                signer = TimestampSigner()
                token = signer.sign(user.email)
                verify_url = request.build_absolute_uri(f"/api/accounts/verify-email/?token={token}")
                subject = "Verify your email"
                message = (
                    f"Hi {user.username},\n\nPlease verify your email by clicking the link below:\n"
                    f"{verify_url}\n\nIf you didn't sign up, you can ignore this message."
                )
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com')
                send_mail(subject, message, from_email, [user.email], fail_silently=True)
            except Exception:
                pass
            return render(request, "verification_sent.html", {"email": user.email})
        return render(request, "signup.html", {"form": form})


class LoginPageView(View):
    def get(self, request):
        return render(request, "login.html", {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data["email"].strip()
            password = form.cleaned_data["password"]
            try:
                from django.db.models import Q
                user = Student.objects.get(Q(email__iexact=identifier) | Q(username__iexact=identifier))
            except Student.DoesNotExist:
                user = None
            if user and user.check_password(password):
                if not user.is_active:
                    return render(request, "login.html", {"form": form, "error": "Please verify your email before signing in."})
                login(request, user)
                return redirect("home")
        return render(request, "login.html", {"form": form, "error": "Invalid credentials"})


class ProfilePageView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        form = ProfileForm(instance=request.user)
        return render(request, "profile.html", {"form": form})

    def post(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("profile")
        return render(request, "profile.html", {"form": form})


class LogoutView(View):
    def post(self, request):
        from django.contrib.auth import logout

        logout(request)
        return redirect("home")


class DashboardView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("login")
        from payments.models import BotInstance, PaymentTransaction

        bots = BotInstance.objects.filter(owner=request.user).order_by("-created_at")
        payments_qs = PaymentTransaction.objects.filter(student=request.user).order_by("-created_at")
        payments = list(payments_qs)

        # Map payment reference -> bot status if linked in raw_payload
        payment_to_bot = {}
        for p in payments:
            try:
                raw = p.raw_payload or {}
                if isinstance(raw, dict):
                    ref = raw.get("bot_reference")
                    if ref:
                        bot = BotInstance.objects.filter(reference=ref).first()
                        if bot:
                            payment_to_bot[p.reference] = {"status": bot.status, "reference": str(bot.reference), "url": bot.bot_url}
                        else:
                            ref = None
                # Auto-link on dashboard if payment is successful but bot missing
                if (not payment_to_bot.get(p.reference)) and p.status == PaymentTransaction.Status.SUCCESS:
                    bot = BotInstance.objects.create(owner=request.user, status=BotInstance.Status.PENDING)
                    # persist bot_reference onto payment payload
                    try:
                        raw = raw if isinstance(raw, dict) else {}
                        raw["bot_reference"] = str(bot.reference)
                        p.raw_payload = raw
                        p.save(update_fields=["raw_payload"])
                    except Exception:
                        pass
                    payment_to_bot[p.reference] = {"status": bot.status, "reference": str(bot.reference), "url": bot.bot_url}
            except Exception:
                pass

        # Attach bot_info to each payment for easy template access
        for p in payments:
            p.bot_info = payment_to_bot.get(p.reference)

        return render(request, "dashboard.html", {"bots": bots, "payments": payments})


