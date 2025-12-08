from rest_framework.views import APIView

from api.v1.validators import validate_id
from core.choices import AdvertisementStatus


class AdvertisementView(APIView):
    """Класс для получения объявлений всех типов."""

    def list(self, request):
        """Получение списка объявлений."""

        pass

    def treat_queryset(self, queryset):
        if self.action == "list":
            params = self.request.query_params
            if "category_id" in params:
                category_id = params.get("category_id")
                validate_id(category_id)
                queryset = queryset.filter(
                    category__id=category_id,
                    status=AdvertisementStatus.PUBLISHED,
                )
