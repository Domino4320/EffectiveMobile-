from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from .models import User


class RegisterSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField()

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "patronymic",
            "email",
            "password",
            "confirm_password",
        ]

    def validate_password(self, value):
        try:
            validate_password(value)
            return value
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))

    def validate(self, data):
        if data.get("password") != data.get("confirm_password"):
            raise serializers.ValidationError(
                {"Validation error": "passwords not the same"}
            )
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        user = User.objects.create(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(email=data.get("email")).first()
        if user and check_password(data.get("password"), user.password):
            data.update({"user": user})
            return data
        dummy_hash = "pbkdf2_sha256$1200000$p4vY89O2VqU1n6Xb$hB8f8N9vK9L2m4S5P6Q7R8T9U0V1W2X3Y4Z5A6B7C8D="
        check_password(data["password"], dummy_hash)
        raise serializers.ValidationError(
            {"Validation error": "Incorrect password or email"}
        )
