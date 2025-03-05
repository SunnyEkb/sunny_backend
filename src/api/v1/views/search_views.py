from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from elasticsearch_dsl import Q
from rest_framework import views, pagination

from api.v1.serializers import AdListSerializer, ServiceListSerializer
from ads.documents import AdDocument
from services.documents import ServiceDocument


@extend_schema(
    summary="Поиск по услугам.",
    tags=["Search"],
)
class SearchServices(views.APIView, pagination.LimitOffsetPagination):
    document_classes = [AdDocument, ServiceDocument]

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
            search = self.document_class.search().query(q)
            response = search.execute()
            results = self.paginate_queryset(response, request, view=self)
            serializer = self.get_serializer_class(results, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return HttpResponse(e, status=500)

    def get_serializer_class(self):
        if False:
            return AdListSerializer
        else:
            return ServiceListSerializer
