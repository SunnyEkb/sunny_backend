import copy
import logging

from django.http import HttpResponse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from elasticsearch_dsl import Q
from rest_framework import request, response, status, views

from ads.documents import AdDocument
from api.v1 import schemes, serializers
from api.v1.validators import validate_id
from services.documents import ServiceDocument

logger = logging.getLogger("django")


@extend_schema(
    summary="Поиск по услугам и объявлениям.",
    tags=["Search"],
    request=None,
    parameters=[
        OpenApiParameter("search", str, description="Строка поиска"),
        OpenApiParameter("limit", int, description="Лимит вывода записей"),
        OpenApiParameter("category", str, description="Категория объявления"),
    ],
    responses={status.HTTP_200_OK: schemes.SEARCH_OK_200},
)
class SearchView(views.APIView):
    """Вью класс для потска."""

    document_classes = (AdDocument, ServiceDocument)
    serializer_class = serializers.SearchSerialiser

    def generate_q_expression(
        self,
        search_terms_list: list[str] | None,
        category: list[str] | None,
    ) -> list[Q]:
        """Сформировать list[str].

        Args:
            search_terms_list (list[str]): параметры поиска
            category (list[str]): категория объявления

        Returns:
            list[Q]: запрос

        """
        if search_terms_list is None:
            return Q("match_all")
        search_terms = search_terms_list[0].replace("\x00", "")
        search_terms.replace(",", " ")
        search_fields = ["title", "description"]
        query = Q(
            "multi_match",
            query=search_terms,
            fields=search_fields,
            fuzziness="auto",
        )
        wildcard_query = Q(
            "bool",
            should=[
                Q("wildcard", **{field: f"*{search_terms.lower()}*"})
                for field in search_fields
            ],
        )
        if category is not None:
            cat = category[0].replace("\x00", "")
            cat.replace(",", " ")
            category_query = Q("terms", categories_titles=cat)
            return query | wildcard_query | category_query
        return query | wildcard_query

    def get(self, request: request.Request):
        try:
            params = copy.deepcopy(request.query_params)
            search_terms = params.pop("search", None)
            limit = params.pop("limit", None)
            if limit is not None:
                validate_id(limit[0])
                limit = int(limit[0])
            category = params.pop("category", None)
            q = self.generate_q_expression(
                search_terms_list=search_terms, category=category
            )
            search_for_ads = AdDocument.search().query(q)
            ads = search_for_ads.execute()
            ads_results = serializers.AdSearchSerializer(
                ads, many=True, context={"request": request}
            )
            search_for_services = ServiceDocument.search().query(q)
            services = search_for_services.execute()
            services_results = serializers.ServiceSearchSerializer(
                services, many=True, context={"request": request}
            )
            data = ads_results.data + services_results.data
            if limit is not None:
                data = data[:limit]
            return response.Response(data=data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(e, exc_info=True)
            return HttpResponse(
                "Поиск недоступен", status=status.HTTP_501_NOT_IMPLEMENTED
            )
