from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("register/", views.RegisterView.as_view(), name="account-register"),
    path("login/", views.LoginView.as_view(), name="account-login"),
    path("logout/", views.LogoutView.as_view(), name="account-logout"),

    # Password reset
    path("password-reset/", views.PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset/confirm/", views.PasswordResetConfirmView.as_view(), name="password-reset-confirm"),

    # Current user & profile
    path("user/", views.UserView.as_view(), name="current-user"),
    path("user/profile/", views.ProfileView.as_view(), name="current-user-profile"),
]
