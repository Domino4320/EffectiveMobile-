from django.urls import path
from .views import UserPermissionView, RolePermissionView

urlpatterns = [
    path("permissions/user", UserPermissionView.as_view(), name="user_permissions"),
    path("permissions/role", RolePermissionView.as_view(), name="role_permissions"),
]
