from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from .models import User, RolePermission, UserPermission, Role, Resource


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "patronymic",
            "email",
            "password",
        ]

    def validate_password(self, value):
        try:
            validate_password(value)
            return value
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))

    def create(self, validated_data):
        user = User.objects.create(**validated_data)
        return user


class RegisterSerializer(BaseUserSerializer):

    confirm_password = serializers.CharField()

    class Meta:
        model = User
        fields = BaseUserSerializer.Meta.fields + ["confirm_password"]

    def validate(self, data):
        if data.get("password") != data.get("confirm_password"):
            raise serializers.ValidationError(
                {"Validation error": "passwords not the same"}
            )
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


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


class UserPatchSerializer(BaseUserSerializer): ...


class RolePermissionSerializer(serializers.ModelSerializer):

    role_name = serializers.SlugRelatedField(
        slug_field="role_name", queryset=Role.objects.all(), source="role"
    )

    resource = serializers.SlugRelatedField(
        slug_field="resource_name", queryset=Resource.objects.all()
    )

    class Meta:
        model = RolePermission
        fields = ["role_name", "resource", "access_level"]
        validators = []

    def validate_access_level(self, value):
        if value == 4:
            raise serializers.ValidationError(
                {"details": "admin can`t give admin`s permissions for other users"},
            )
        return value

    def create(self, validated_data):
        role = validated_data.pop("role")
        resource = validated_data.pop("resource")
        instance, created = RolePermission.objects.update_or_create(
            role=role,
            resource=resource,
            defaults={"access_level": validated_data["access_level"]},
        )
        return instance


class UserPermissionSerializer(serializers.ModelSerializer):

    user_email = serializers.SlugRelatedField(
        slug_field="email", queryset=User.objects.all(), source="user"
    )

    resource = serializers.SlugRelatedField(
        slug_field="resource_name", queryset=Resource.objects.all()
    )

    class Meta:
        model = UserPermission
        fields = ["user_email", "resource", "access_level"]
        validators = []

    def validate_access_level(self, value):
        if value == 4:
            raise serializers.ValidationError(
                {"details": "admin can`t give admin`s permissions for other users"},
            )
        return value

    def create(self, validated_data):
        user = validated_data.pop("user")
        resource = validated_data.pop("resource")
        instance, created = UserPermission.objects.update_or_create(
            user=user,
            resource=resource,
            defaults={"access_level": validated_data["access_level"]},
        )
        return instance
