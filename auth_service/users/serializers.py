from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User


class UserSerializer(serializers.ModelSerializer):

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
