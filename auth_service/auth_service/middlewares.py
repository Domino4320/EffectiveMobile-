from django.http import HttpRequest
from rest_framework import status
from users.models import UserToken
from datetime import datetime, timezone
from rest_framework.response import Response
from django.urls import resolve, Resolver404


class CustomAuthMiddleware:

    def __init__(self, next_step):
        self.next_step = next_step
        self.except_paths = [
            "registration",
            "login",
        ]

    def __call__(self, request: HttpRequest):
        try:
            view_name = resolve(request.path_info).url_name
            if view_name in self.except_paths:
                return self.next_step(request)
        except Resolver404:
            return self.next_step(request)
        auth_token = request.COOKIES.get("auth_token")
        token_obj = (
            UserToken.objects.filter(token=auth_token).select_related("user_id").first()
        )
        if token_obj and datetime.now(timezone.utc) < token_obj.expire_at:
            request.user = token_obj.user_id
            request.token = token_obj
            return self.next_step(request)
        return Response({"Auth error": "Not authorized"}, status.HTTP_401_UNAUTHORIZED)
