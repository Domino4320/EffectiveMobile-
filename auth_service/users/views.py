from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView, Response
from .serializers import RegisterSerializer, LoginSerializer
from .models import UserToken
from drf_spectacular.utils import extend_schema


@extend_schema(
    tags=["Регистрация"],
    summary="Регистрация пользователя",
)
class RegisterView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True}, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Аутентификация"],
    summary="Аутентификация пользователя",
)
class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get("user")
            token = UserToken.objects.create(user_id=user)
            response = Response({"success": True}, status.HTTP_200_OK)
            response.set_cookie(
                key="auth_token",
                value=token.token,
                expires=token.expire_at,
                httponly=True,
            )
            return response
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class UserActionView(APIView):
    def patch(request): ...
