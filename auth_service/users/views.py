from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView, Response
from .serializers import UserSerializer


class RegisterView(APIView):
    serializer_class = UserSerializer

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True}, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
