from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from api.v1.views import (
    AdViewSet,
    CategoryViewSet,
    FavoritesViewSet,
)

api_v1_router = DefaultRouter()
api_v1_router.register("ads", AdViewSet, basename="ads")
api_v1_router.register("categories", CategoryViewSet, basename="categories")
api_v1_router.register("favorite", FavoritesViewSet, "favorite")

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
    path("", include("api.v1.comments.urls")),
    path("", include(api_v1_router.urls)),
]
