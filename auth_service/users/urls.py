from django.urls import path
from .views import RegisterView, LoginView, LogoutView, UserActionView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="registration"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", UserActionView.as_view(), name="current_user_actions"),
]
