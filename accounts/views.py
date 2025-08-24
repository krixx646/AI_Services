from django.shortcuts import render
from rest_framework import viewsets, views, status
from rest_framework.response import Response
from .models import Student
from .serializers import RegistrationSerialiser, LoginSerialiser, ProfileSerialiser
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly



# Create your views here.

class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = RegistrationSerialiser
    permission_classes = [AllowAny]


class LoginViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = LoginSerialiser
    permission_classes = [AllowAny]

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = ProfileSerialiser
    permission_classes = [IsAuthenticated]


