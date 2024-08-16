from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"
    ),
    re_path(
        r"^auth/", include("drf_social_oauth2.urls", namespace="social_auth")
    ),
    path("", include("api.v1.users.urls")),
    path("", include("api.v1.services.urls")),
    path("", include("api.v1.ads.urls")),
    path("", include("api.v1.comments.urls")),
]
