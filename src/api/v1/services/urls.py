from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.services.views import TypeViewSet


v1_services_router = DefaultRouter()
v1_services_router.register("types", TypeViewSet, basename="types")

urlpatterns = [
    path("", include(v1_services_router.urls)),
]
