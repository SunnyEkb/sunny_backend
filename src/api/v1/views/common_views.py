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
from api.v1.validators import validate_id
from core.choices import AdvertisementStatus
from categories.models import Category
from services.models import Service


@extend_schema(
    tags=["Advertisements"],
    request=None,
    summary="Список опубликованных объявлений.",
    description=(
        """
        Список опубликованных объявлений без разделения на категории,
        отсортированный по дате создания (сначала новые), с пагинацией.

        Query параметр "category_id" позволяет получить список объявлений,
        относящихся к конкретной категории.

        Query параметр limit - кол-во объявлений на странице (по умолчанию 50).
        """
    ),
    responses={
        status.HTTP_200_OK: schemes.ADVERTISEMENTS_LIST_OK_200,
        status.HTTP_400_BAD_REQUEST: schemes.WRONG_PARAMETR_400,
        status.HTTP_404_NOT_FOUND: schemes.CATEGORY_NOT_FOUND_404,
    },
    parameters=[
        OpenApiParameter(
            "category_id",
            int,
            description="Идентификатор категории",
        ),
        OpenApiParameter("page", int, description="Номер страницы"),
        OpenApiParameter(
            "limit", int, description="Количество объявлений на странице"
        ),
    ],
)
class AdvertisementView(APIView):
    """Класс для получения объявлений всех типов."""

    pagination_class = CustomPaginator

    def get(self, request):
        """Получение списка объявлений."""

        params = request.query_params
        if "category_id" in params:
            category_id = params.get("category_id")
            validate_id(category_id)
            category = get_object_or_404(Category, pk=category_id)
            ads_query = Ad.cstm_mng.filter(
                status=AdvertisementStatus.PUBLISHED,
                category=category,
            )
            service_query = Service.cstm_mng.filter(
                status=AdvertisementStatus.PUBLISHED,
                category=category,
            )
        else:
            ads_query = Ad.cstm_mng.filter(
                status=AdvertisementStatus.PUBLISHED,
            )
            service_query = Service.cstm_mng.filter(
                status=AdvertisementStatus.PUBLISHED,
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
                serializer = serializers.AdListSerializer(
                    entry, context={"request": request}
                )
            if isinstance(entry, Service):
                serializer = serializers.ServiceListSerializer(
                    entry, context={"request": request}
                )
            advertisements.append(serializer.data)
        return self.get_paginated_response(advertisements)

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


@extend_schema(
    tags=["Advertisements"],
    request=None,
    summary="Список объявлений пользователя",
    description=(
        """
        Список объявлений, созданных текущим пользователем,
        не зависимо от статуса объявления,
        отсортированный по дате создания (сначала новые), с пагинацией.

        Query параметр limit - кол-во объявлений на странице (по умолчанию 50).
        """
    ),
    responses={
        status.HTTP_200_OK: schemes.ADVERTISEMENTS_LIST_OK_200,
        status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
    },
    parameters=[
        OpenApiParameter("page", int, description="Номер страницы"),
        OpenApiParameter(
            "limit", int, description="Количество объявлений на странице"
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
