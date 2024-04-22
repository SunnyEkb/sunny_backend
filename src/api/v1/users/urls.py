from django.urls import include, path, re_path

from api.v1.users.views import (
    ChangePassowrdView,
    CookieTokenRefreshView,
    LoginView,
    LogoutView,
    RegisrtyView,
)


urlpatterns = [
    path("registry/", RegisrtyView.as_view(), name="registry"),
    re_path(
        r"^password_reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "token-refresh/",
        CookieTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "change-password/",
        ChangePassowrdView.as_view(),
        name="change_password",
    ),
]
