from itertools import chain

from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)
from rest_framework.permissions import IsAuthenticated
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
        status.HTTP_200_OK: schemes.ADVERTISEMENTS_LIST__OK_200,
        status.HTTP_400_BAD_REQUEST: schemes.WRONG_PARAMETR_400,
    },
    parameters=[
        OpenApiParameter(
            "category_id",
            int,
            description="Идентификатор категории",
        ),
        OpenApiParameter(
            "page",
            int,
            description="A page number within the paginated result set.",
        ),
    ],
)
class AdvertisementView(APIView):
    """Класс для получения объявлений всех типов."""

    pagination_class = CustomPaginator

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
            queryset = list(chain(service_query, ads_query))
            result = self.paginate_queryset(queryset, request)
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
            return self.get_paginated_response(results)

        return Response(data=results, status=status.HTTP_200_OK)

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset, request):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


@extend_schema(
    tags=["Advertisements"],
    request=None,
    summary="Список объявлений объявлений пользователя",
    responses={
        status.HTTP_200_OK: schemes.ADVERTISEMENTS_LIST__OK_200,
    },
    parameters=[
        OpenApiParameter(
            "page",
            int,
            description="A page number within the paginated result set.",
        ),
    ],
)
class UserAdvertisementView(APIView):
    """Класс для получения объявлений пользователя."""

    pagination_class = CustomPaginator
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Получение списка объявлений пользователя."""

        ads_query = Ad.objects.none()
        service_query = Ad.objects.none()
        results: list = []
        ads_query = Ad.cstm_mng.filter(provider=request.user)
        service_query = Service.cstm_mng.filter(provider=request.user)
        queryset = list(chain(service_query, ads_query))
        result = self.paginate_queryset(queryset, request)
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
        return self.get_paginated_response(results)

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset, request):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)
