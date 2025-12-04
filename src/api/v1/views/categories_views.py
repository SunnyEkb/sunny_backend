from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, status, viewsets

from categories.models import Category
from api.v1 import schemes
from api.v1 import serializers as api_serializers


@extend_schema(
    tags=["Categories"],
    responses={status.HTTP_200_OK: schemes.CATEGORIES_GET_OK_200},
)
@extend_schema_view(
    list=extend_schema(
        summary="Список категорий объявлений.",
        parameters=[OpenApiParameter("title", str)],
    ),
    retrieve=extend_schema(summary="Категория объявления."),
)
class CommonCategoriesViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Вьюсет для категорий сервиса."""

    @method_decorator(cache_page(60 * 2))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 2))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Category.objects.all()
        if self.action == "list":
            params = self.request.query_params
            if "title" in params:
                title = params.get("title")
                queryset = queryset.filter(title__icontains=title)
            else:
                queryset = queryset.filter(parent=None)
        return queryset

    def get_serializer_class(self):
        params = self.request.query_params
        if self.action == "list" and "title" in params:
            return api_serializers.CommonCategoryNoSubCatSerializer
        return api_serializers.CommonCategorySerializer
