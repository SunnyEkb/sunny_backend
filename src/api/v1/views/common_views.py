from itertools import chain

from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)
from rest_framework.response import Response
from rest_framework.views import APIView, status

from ads.models import Ad
from api.v1 import serializers
from api.v1 import schemes
from api.v1.paginators import CustomPaginator
from api.v1.validators import validate_id
from core.choices import AdvertisementStatus
from services.models import Service


@extend_schema(
    tags=["Advertisements"],
    request=None,
    summary=(
        "Список объявлений. Для получения списка объявлений необходимо"
        " указать query параметр 'category_id'. При отсутствии параметра"
        " будет выведен пустой список."
    ),
    responses={
        status.HTTP_200_OK: schemes.AD_LIST_OK_200,  # wrong!
        status.HTTP_400_BAD_REQUEST: schemes.WRONG_PARAMETR_400,
    },
    parameters=[OpenApiParameter("category_id", int)],
)
class AdvertisementView(APIView):
    """Класс для получения объявлений всех типов."""

    def get(self, request):
        """Получение списка объявлений."""

        ads_query = Ad.objects.none()
        service_query = Ad.objects.none()
        params = request.query_params
        results: list = []
        if "category_id" in params:
            category_id = params.get("category_id")
            validate_id(category_id)
            ads_query = Ad.cstm_mng.filter(
                status=AdvertisementStatus.PUBLISHED,
                category__id=category_id,
            )
            service_query = Service.cstm_mng.filter(
                status=AdvertisementStatus.PUBLISHED,
                category__id=category_id,
            )
            result = list(chain(service_query, ads_query))
            sorted_result = sorted(
                result,
                key=lambda item: item.created_at,
                reverse=True,
            )
            for entry in sorted_result:
                if isinstance(entry, Ad):
                    serializer = serializers.AdListSerializer(entry)
                if isinstance(entry, Service):
                    serializer = serializers.ServiceListSerializer(entry)
                results.append(serializer.data)

        return Response(data=results, status=status.HTTP_200_OK)
