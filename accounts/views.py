from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Student
from .serializers import RegistrationSerialiser, LoginSerialiser, ProfileSerialiser
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
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
        return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)


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
            form.save()
            return redirect("login")
        return render(request, "signup.html", {"form": form})


class LoginPageView(View):
    def get(self, request):
        return render(request, "login.html", {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"].lower()
            password = form.cleaned_data["password"]
            try:
                user = Student.objects.get(email__iexact=email)
            except Student.DoesNotExist:
                user = None
            if user and user.check_password(password):
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
        payments = PaymentTransaction.objects.filter(student=request.user).order_by("-created_at")
        return render(request, "dashboard.html", {"bots": bots, "payments": payments})


