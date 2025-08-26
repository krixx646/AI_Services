from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Student


class RegistrationSerialiser(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = ("email", "password", "confirm_password", "username", "phone", "bio", "avatar")
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        if Student.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        confirm = attrs.get("confirm_password")
        if password != confirm:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match"})
        if password and len(password) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password", None)
        password = validated_data.pop("password")
        username = validated_data.get("username") or validated_data.get("email", "").split("@")[0]
        user = Student.objects.create_user(username=username, password=password, **validated_data)
        return user


class LoginSerialiser(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        try:
            user = Student.objects.get(email__iexact=email)
        except Student.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")
        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")
        attrs["user"] = user
        return attrs

    def to_representation(self, instance):
        user = instance["user"] if isinstance(instance, dict) else instance
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class ProfileSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ("public_id", "username", "email", "phone", "bio", "avatar")
        read_only_fields = ("public_id", "email")

