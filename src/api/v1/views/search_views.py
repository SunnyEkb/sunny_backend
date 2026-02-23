import copy
import logging
from typing import List, Optional

from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
from elasticsearch_dsl import Q
from rest_framework import views, request, response, status

from ads.documents import AdDocument
from api.v1 import schemes, serializers
from services.documents import ServiceDocument

logger = logging.getLogger("django")


@extend_schema(
    summary="Поиск по услугам и объявлениям.",
    tags=["Search"],
    request=None,
    parameters=[OpenApiParameter("search", str)],
    responses={status.HTTP_200_OK: schemes.SEARCH_OK_200},
)
class SearchView(views.APIView):
    document_classes = [AdDocument, ServiceDocument]
    serializer_class = serializers.SearchSerialiser

    def generate_q_expression(self, search_terms_list: Optional[List[str]]):
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
        query = query | wildcard_query
        return query

    def get(self, request: request.Request):
        try:
            params = copy.deepcopy(request.query_params)
            search_terms = params.pop("search", None)
            q = self.generate_q_expression(search_terms_list=search_terms)
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
            return response.Response(
                data=ads_results.data + services_results.data,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(e, exc_info=True)
            return HttpResponse(
                "Поиск недоступен", status=status.HTTP_501_NOT_IMPLEMENTED
            )
