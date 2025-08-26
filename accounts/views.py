from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Student
from .serializers import RegistrationSerialiser, LoginSerialiser, ProfileSerialiser
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, IsAuthenticatedOrReadOnly



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
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = ProfileSerialiser
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "put", "patch", "delete", "head", "options"]


