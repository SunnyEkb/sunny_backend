from itertools import chain

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, status

from ads.models import Ad
from api.v1 import serializers
from api.v1 import schemes
from api.v1.paginators import CustomPaginator
from core.choices import AdvertisementStatus
from categories.models import Category
from services.models import Service


@extend_schema(
    tags=["Advertisements"],
    request=None,
    summary="Список объявлений по категориям.",
    responses={
        status.HTTP_200_OK: schemes.ADVERTISEMENTS_LIST_OK_200,
        status.HTTP_404_NOT_FOUND: schemes.ADVERTISEMENTS_LIST_NOT_FOUND_404,
    },
    parameters=[
        OpenApiParameter("page", int, description="Номер страницы."),
    ],
)
class AdvertisementView(APIView):
    """Класс для получения объявлений всех типов."""

    pagination_class = CustomPaginator

    def get(self, request, category_id: int):
        """Получение списка объявлений."""

        category = get_object_or_404(Category, pk=category_id)
        ads_query = Ad.cstm_mng.filter(
            status=AdvertisementStatus.PUBLISHED,
            category=category,
        )
        service_query = Service.cstm_mng.filter(
            status=AdvertisementStatus.PUBLISHED,
            category=category,
        )
        queryset = list(chain(service_query, ads_query))
        paginated_queryset = self.paginate_queryset(queryset, request)
        sorted_result = sorted(
            paginated_queryset,
            key=lambda item: item.created_at,
            reverse=True,
        )
        advertisements = list()
        for entry in sorted_result:
            if isinstance(entry, Ad):
                serializer = serializers.AdListSerializer(entry)
            if isinstance(entry, Service):
                serializer = serializers.ServiceListSerializer(entry)
            advertisements.append(serializer.data)
        return self.get_paginated_response(advertisements)

    @property
    def paginator(self) -> CustomPaginator | None:
        """Возвращает класс пагинатора."""

        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset, request):
        """Возвращает запрос для одной страницы пагинатора."""

        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, request, view=self)

    def get_paginated_response(self, data):
        """Возвращает http ответ с пагинацией."""

        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


@extend_schema(
    tags=["Advertisements"],
    request=None,
    summary="Список объявлений объявлений пользователя",
    responses={
        status.HTTP_200_OK: schemes.ADVERTISEMENTS_LIST_OK_200,
    },
    parameters=[
        OpenApiParameter("page", int, description="Номер страницы."),
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
        """Возвращает класс пагинатора."""

        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset, request):
        """Возвращает запрос для одной страницы пагинатора."""

        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, request, view=self)

    def get_paginated_response(self, data):
        """Возвращает http ответ с пагинацией."""

        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)
