from django.http import HttpRequest
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView, Response
from .serializers import RegisterSerializer, LoginSerializer, UserPatchSerializer
from .models import UserToken
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["Регистрация"],
    summary="Регистрация учетной записи",
)
class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request: HttpRequest):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True}, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Аутентификация"],
    summary="Вход в учетную запись",
)
class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request: HttpRequest):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get("user")
            token = UserToken.objects.create(user=user)
            response = Response({"success": True}, status.HTTP_200_OK)
            response.set_cookie(
                key="auth_token",
                value=token.token,
                expires=token.expire_at,
                httponly=True,
            )
            return response
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Аутентификация"], summary="Выход из учетной записи")
class LogoutView(APIView):
    def post(self, request: HttpRequest):
        token = request.COOKIES.get("auth_token")
        if token:
            UserToken.objects.filter(token=token).delete()
        response = Response({"detail": "Successfully logged out"}, status.HTTP_200_OK)
        response.delete_cookie("auth_token")
        return response


@extend_schema(tags=["Действия с текущим пользователем"])
class UserActionView(APIView):

    @extend_schema(request=UserPatchSerializer)
    def patch(self, request):
        serializer = UserPatchSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "user was successfully updated"}, status.HTTP_200_OK
            )
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        current_user = request.user
        current_user.is_active = False
        current_user.save()
        return Response({"detail": "user was successfully deleted"}, status.HTTP_200_OK)
