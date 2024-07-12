from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.services.views import (
    ServiceImageViewSet,
    ServiceViewSet,
    TypeViewSet,
)


v1_services_router = DefaultRouter()
v1_services_router.register("types", TypeViewSet, basename="types")
v1_services_router.register("services", ServiceViewSet, basename="services")
v1_services_router.register(
    "serviceimage", ServiceImageViewSet, basename="serviceimage"
)

urlpatterns = [
    path("", include(v1_services_router.urls)),
]
