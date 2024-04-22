from django.urls import include, path, re_path

from api.v1.users.views import RegisrtyView


urlpatterns = [
    path("registry/", RegisrtyView.as_view(), name="registry"),
    re_path(
        r"^password_reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
]
