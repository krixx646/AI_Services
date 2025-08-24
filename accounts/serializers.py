from rest_framework import serializers
from .models import Student


class RegistrationSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('email', 'password', 'username', 'phone')

        extra_kwargs = {'password': {'write_only': True}}


class LoginSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Student

        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class ProfileSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Student

        fields = ('bio', 'avatar', 'username', 'phone', 'email')    
        extra_kwargs = {'password': {'write_only': True}}

