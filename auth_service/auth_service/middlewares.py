from django.http import HttpRequest, JsonResponse
from rest_framework import status
from users.models import UserToken
from datetime import datetime, timezone
from rest_framework.response import Response
from django.urls import resolve, Resolver404
from users.models import UserPermission, RolePermission, Resource


class CustomAuthMiddleware:

    def __init__(self, next_step):
        self.next_step = next_step
        self.except_paths = [
            "registration",
            "login",
            "swagger",
            "redoc",
            "schema",
            "admin",
        ]

    def __call__(self, request: HttpRequest):
        try:
            path_info = resolve(request.path_info)
            view_name = path_info.url_name
            namespace = path_info.namespace
            if view_name in self.except_paths:
                return self.next_step(request)
        except Resolver404:
            return self.next_step(request)
        auth_token = request.COOKIES.get("auth_token")
        token_obj = (
            UserToken.objects.filter(token=auth_token).select_related("user").first()
        )
        if token_obj and datetime.now(timezone.utc) < token_obj.expire_at:
            request.user = token_obj.user
            if not request.user.is_active:
                return JsonResponse(
                    {"Auth error": "Your account is deleted"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            request.token = token_obj
            request.view_name = view_name
            request.namespace = namespace
            return self.next_step(request)
        return JsonResponse(
            {"Auth error": "Not authorized"}, status=status.HTTP_401_UNAUTHORIZED
        )


class PermissionMiddleware:

    def __init__(self, next_step):
        self.next_step = next_step
        self.except_paths = [
            "registration",
            "login",
            "swagger",
            "redoc",
            "schema",
            "admin",
            "logout",
        ]

    def __call__(self, request):
        try:
            path_info = resolve(request.path_info)
            view_name = path_info.url_name
            if view_name in self.except_paths:
                return self.next_step(request)
        except Resolver404:
            return self.next_step(request)
        resource = Resource.objects.filter(resource_name=request.view_name).first()
        user_permission = UserPermission.objects.filter(
            user=request.user, resource=resource
        ).first()
        access_level = user_permission.access_level if user_permission else None
        if not user_permission:
            role_permission = RolePermission.objects.filter(
                role=request.user.role, resource=resource
            ).first()
            access_level = (
                role_permission.access_level
                if role_permission
                else request.user.role.default_permission_level
            )
        read_only = (
            access_level == 1 and request.method == "GET"
        ) and request.namespace != "admins"
        read_write_update = (
            access_level == 2
            and (
                request.method == "GET"
                or request.method == "POST"
                or request.method == "PATCH"
                or request.method == "PUT"
            )
            and request.namespace != "admins"
        )
        full_crud = (
            access_level == 3
            and (
                request.method == "GET"
                or request.method == "POST"
                or request.method == "PATCH"
                or request.method == "PUT"
                or request.method == "DELETE"
            )
            and request.namespace != "admins"
        )
        admin = access_level == 4 and request.namespace == "admins"
        if read_only or read_write_update or full_crud or admin:
            return self.next_step(request)
        return JsonResponse(
            {"details": "access denied"}, status=status.HTTP_403_FORBIDDEN
        )
