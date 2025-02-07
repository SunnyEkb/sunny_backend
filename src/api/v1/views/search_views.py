from drf_spectacular.utils import extend_schema
from elasticsearch_dsl import Q

from api.v1.serializers import ServiceListSerializer
from api.v1.views.base_views import PaginatedElasticSearchAPIView
from services.documents import ServiceDocument


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
