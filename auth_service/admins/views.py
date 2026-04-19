from django.shortcuts import render
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.views import APIView, Response
from users.serializers import RolePermissionSerializer, UserPermissionSerializer


@extend_schema(
    tags=["Админы"],
    summary="Измнение и добавление прав для определенной роли",
)
class RolePermissionView(APIView):
    serializer_class = RolePermissionSerializer

    def post(self, request):
        serializer = RolePermissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "permissions added"}, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Админы"],
    summary="Измнение и добавление прав для определенного пользователя",
)
class UserPermissionView(APIView):
    serializer_class = UserPermissionSerializer

    def post(self, request):
        serializer = UserPermissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "permissions added"}, status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
