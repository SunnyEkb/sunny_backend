from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.comments.views import CommentViewSet, CommentCreateDestroyViewSet


v1_comments_router = DefaultRouter()
v1_comments_router.register(
    "comments",
    CommentCreateDestroyViewSet,
    basename="comments_create",
)
v1_comments_router.register(
    r"comments/(?P<type>\w+)/(?P<obj_id>\d+)",
    CommentViewSet,
    basename="comments",
)


urlpatterns = [
    path("", include(v1_comments_router.urls)),
]
