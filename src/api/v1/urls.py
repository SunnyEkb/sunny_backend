from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from api.v1.views import (
    AdAvatarView,
    AdImageViewSet,
    AdModerationViewSet,
    AdViewSet,
    AdvertisementView,
    ChangePassowrdView,
    ChatViewSet,
    CommonCategoriesViewSet,
    CommentDestroyViewSet,
    CommentModerationViewSet,
    CommentViewSet,
    CookieTokenRefreshView,
    FavoritesViewSet,
    LoginView,
    LogoutView,
    NotificationViewSet,
    RegisrtyView,
    ServiceImageViewSet,
    ServiceModerationViewSet,
    ServiceViewSet,
    SearchView,
    VerificationView,
    UserViewSet,
)

api_v1_router = DefaultRouter()
api_v1_router.register(
    "categories", CommonCategoriesViewSet, basename="common_categories"
)
api_v1_router.register("ads", AdViewSet, basename="ads")
api_v1_router.register("chats", ChatViewSet, basename="chats")
api_v1_router.register(
    "comments",
    CommentDestroyViewSet,
    basename="comments_destroy",
)
api_v1_router.register(
    "notifications",
    NotificationViewSet,
    basename="notifications",
)
api_v1_router.register(
    r"comments/(?P<type>\w+)/(?P<obj_id>\d+)",
    CommentViewSet,
    basename="comments",
)
api_v1_router.register("favorite", FavoritesViewSet, "favorite")
api_v1_router.register("services", ServiceViewSet, basename="services")
api_v1_router.register(
    "moderator/services",
    ServiceModerationViewSet,
    basename="moderation_services",
)
api_v1_router.register(
    "moderator/ads",
    AdModerationViewSet,
    basename="moderation_ads",
)
api_v1_router.register(
    "moderator/comments",
    CommentModerationViewSet,
    basename="moderation_comments",
)
api_v1_router.register(
    "serviceimage", ServiceImageViewSet, basename="serviceimage"
)
api_v1_router.register("adimage", AdImageViewSet, basename="adimage")
api_v1_router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("registry/", RegisrtyView.as_view(), name="registry"),
    path(
        "verify-registration/",
        VerificationView.as_view(),
        name="veryfy_registration",
    ),
    path("users/avatar/<int:pk>/", AdAvatarView.as_view(), name="avatar"),
    re_path(
        r"^password_reset/",
        include("django_rest_passwordreset.urls", namespace="password_reset"),
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "token-refresh/",
        CookieTokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path(
        "change-password/",
        ChangePassowrdView.as_view(),
        name="change_password",
    ),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"
    ),
    re_path(
        r"^auth/", include("drf_social_oauth2.urls", namespace="social_auth")
    ),
    path("search", SearchView.as_view()),
    path(
        "advertisements/", AdvertisementView.as_view(), name="advertisements"
    ),
    path("", include(api_v1_router.urls)),
]
