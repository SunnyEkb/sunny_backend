from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, viewsets

from ads.models import AdCategory
from ads.serializers import AdCategorySerializer


@extend_schema(
    tags=["Ads"],
)
@extend_schema_view(
    list=extend_schema(summary="Список категорий объявлений"),
)
class AdCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Список категорий объявлений."""

    queryset = AdCategory.objects.filter(parent=None)
    serializer_class = AdCategorySerializer

    @method_decorator(cache_page(60 * 60 * 2))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
