import copy
from typing import List, Optional

from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from elasticsearch_dsl import Q
from rest_framework import views, pagination, request

from api.v1.serializers import SearchSerialiser
from ads.documents import AdDocument
from services.documents import ServiceDocument


@extend_schema(
    summary="Поиск по услугам и объявлениям.",
    tags=["Search"],
)
class SearchView(views.APIView, pagination.LimitOffsetPagination):
    document_classes = [AdDocument, ServiceDocument]
    serializer_class = SearchSerialiser

    def generate_q_expression(self, search_terms_list: Optional[List[str]]):
        if search_terms_list is None:
            return Q("match_all")
        search_terms = search_terms_list[0].replace("\x00", "")
        search_terms.replace(",", " ")
        search_fields = ["title", "description"]
        query = Q(
            "multi_match",
            query=search_terms,
            ields=search_fields,
            fuzziness="auto",
        )
        return query

    def get(self, request: request.Request):
        try:
            params = copy.deepcopy(request.query_params)
            search_terms = params.pop("search", None)
            q = self.generate_q_expression(search_terms_list=search_terms)
            search_for_ads = AdDocument.search().query(q)
            ads = search_for_ads.execute()
            ads_results = self.paginate_queryset(ads, request, view=self)
            search_for_services = ServiceDocument.search().query(q)
            services = search_for_services.execute()
            services_results = self.paginate_queryset(
                services, request, view=self
            )
            results = ads_results + services_results
            serializer = self.serializer_class(results, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return HttpResponse(e, status=500)
