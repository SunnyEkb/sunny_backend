from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.ads.views import AdCategoryViewSet


v1_ads_router = DefaultRouter()
v1_ads_router.register("categories", AdCategoryViewSet, basename="categories")

urlpatterns = [
    path("", include(v1_ads_router.urls)),
]
