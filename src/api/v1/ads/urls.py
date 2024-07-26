from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.ads.views import AdViewSet, CategoryViewSet


v1_ads_router = DefaultRouter()
v1_ads_router.register("categories", CategoryViewSet, basename="categories")
v1_ads_router.register("ads", AdViewSet, basename="ads")

urlpatterns = [
    path("", include(v1_ads_router.urls)),
]
