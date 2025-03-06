from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from elasticsearch_dsl import Q
from rest_framework import views, pagination

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

    def generate_q_expression(self, query):
        return Q(
            "multi_match",
            query=query,
            fields=["title", "description"],
            fuzziness="auto",
        )

    def get(self, request, query):
        try:
            q = self.generate_q_expression(query)
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
