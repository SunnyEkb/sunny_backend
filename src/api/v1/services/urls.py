from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.services.views import ServiceViewSet, TypeViewSet


v1_services_router = DefaultRouter()
v1_services_router.register("types", TypeViewSet, basename="types")
v1_services_router.register("services", ServiceViewSet, basename="services")

urlpatterns = [
    path("", include(v1_services_router.urls)),
]
