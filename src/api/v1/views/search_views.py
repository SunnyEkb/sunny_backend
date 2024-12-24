import abc

from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from elasticsearch_dsl import Q
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView

from api.v1.serializers import ServiceListSerializer
from services.documents import ServiceDocument


class PaginatedElasticSearchAPIView(APIView, LimitOffsetPagination):
    serializer_class = None
    document_class = None

    @abc.abstractmethod
    def generate_q_expression(self, query):
        """This method should be overridden
        and return a Q() expression."""

    def get(self, request, query):
        try:
            q = self.generate_q_expression(query)
            search = self.document_class.search().query(q)
            response = search.execute()
            results = self.paginate_queryset(response, request, view=self)
            serializer = self.serializer_class(results, many=True)
            return self.get_paginated_response(serializer.data)
        except Exception as e:
            return HttpResponse(e, status=500)


@extend_schema(
    summary="Поиск по услугам.",
    tags=["Search"],
)
class SearchServices(PaginatedElasticSearchAPIView):
    serializer_class = ServiceListSerializer
    document_class = ServiceDocument

    def generate_q_expression(self, query):
        return Q(
            "multi_match",
            query=query,
            fields=["title", "description"],
            fuzziness="auto",
        )
