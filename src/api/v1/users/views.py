from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.middleware import csrf
from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ParseError
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from api.v1.permissions import SelfOnly
from api.v1.scheme import (
    LOGIN_EXAMPLE,
    USER_CREATE_EXAMPLE,
    USER_PART_CHANGE_EXAMPLE,
    USER_PUT_OK_200,
    USER_PATCH_OK_200,
    LOGIN_OK_200,
    LOGIN_FORBIDDEN_403,
    LOGOUT_OK_200,
    PASSWORD_CHANGE_EXAMPLE,
    PASSWORD_CHANGED_OK_200,
    REFRESH_OK_200,
    USER_CREATED_201,
    USER_GET_OK_200,
    USER_BAD_REQUEST_400,
    UNAUTHORIZED_401,
)
from api.v1.users.utils import (
    get_tokens_for_user,
    set_access_cookie,
    set_refresh_cookie,
)
from core.choices import APIResponses
from users.serializers import (
    CookieTokenRefreshSerializer,
    LoginSerializer,
    UserCreateSerializer,
    UserReadSerializer,
    UserUpdateSerializer,
    PasswordChangeSerializer,
)

User = get_user_model()


@extend_schema(
    request=UserCreateSerializer,
    summary="Регистрация пользователя.",
    tags=["Users"],
    examples=[USER_CREATE_EXAMPLE],
    responses={
        status.HTTP_201_CREATED: USER_CREATED_201,
        status.HTTP_400_BAD_REQUEST: USER_BAD_REQUEST_400,
    },
)
class RegisrtyView(APIView):
    """
    Регистрация пользователей.
    """

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Users"],
    request=LoginSerializer,
    summary="Login.",
    examples=[LOGIN_EXAMPLE],
    responses={
        status.HTTP_200_OK: LOGIN_OK_200,
        status.HTTP_403_FORBIDDEN: LOGIN_FORBIDDEN_403,
    },
)
class LoginView(APIView):
    """
    Вход пользователя в систему.
    """

    authentication_classes = ()

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            response = Response()
            email = serializer.validated_data.get("email", None)
            password = serializer.validated_data.get("password", None)
            user = authenticate(email=email, password=password)
            if user is not None:
                if user.is_active:
                    data = get_tokens_for_user(user)
                    set_access_cookie(response, data)
                    set_refresh_cookie(response, data)
                    response["X-CSRFToken"] = csrf.get_token(request)
                    response.data = {
                        "Success": APIResponses.SUCCESS_LOGIN.value
                    }
                    return response
                else:
                    return Response(
                        {"No active": APIResponses.ACCOUNT_IS_INACTIVE.value},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            else:
                raise AuthenticationFailed(
                    APIResponses.INVALID_CREDENTIALS.value
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Users"],
    summary="Logout.",
    responses={
        status.HTTP_200_OK: LOGOUT_OK_200,
        status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
    },
)
class LogoutView(APIView):
    """
    Выход из системы.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = None

    def post(self, request, format=None):
        try:
            refreshToken = request.COOKIES.get(
                settings.SIMPLE_JWT["AUTH_REFRESH"]
            )
            token = RefreshToken(refreshToken)
            token.blacklist()

            response: Response = Response()
            response.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE"])
            response.delete_cookie(settings.SIMPLE_JWT["AUTH_REFRESH"])
            response.delete_cookie("X-CSRFToken")
            response.delete_cookie("csrftoken")
            response["X-CSRFToken"] = None
            response.data = {"Success": APIResponses.SUCCESS_LOGOUT.value}
            return response
        except Exception:
            raise ParseError(APIResponses.INVALID_TOKEN.value)


@extend_schema(
    tags=["Users"],
    request=None,
    summary="Обновление refresh токена.",
    responses={
        status.HTTP_200_OK: REFRESH_OK_200,
        status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
    },
)
class CookieTokenRefreshView(TokenRefreshView):
    """
    Обновление refresh токена.
    """

    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            res = Response()
            res.data = {"detail": APIResponses.INVALID_TOKEN}
            res.status_code = response.status_code
            return super().finalize_response(request, res, *args, **kwargs)
        if response.data.get("refresh"):
            set_refresh_cookie(response, response.data)
            del response.data["refresh"]
        if response.data.get("access"):
            set_access_cookie(response, response.data)
            del response.data["access"]
        response["X-CSRFToken"] = request.COOKIES.get("csrftoken")
        response.data = {"Success": APIResponses.SUCCESS_TOKEN_REFRESH.value}
        return super().finalize_response(request, response, *args, **kwargs)


@extend_schema(
    tags=["Users"],
    summary="Изменение пароля пользователя.",
    request=PasswordChangeSerializer,
    examples=[PASSWORD_CHANGE_EXAMPLE],
    responses={
        status.HTTP_200_OK: PASSWORD_CHANGED_OK_200,
        status.HTTP_400_BAD_REQUEST: USER_BAD_REQUEST_400,
        status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
    },
)
class ChangePassowrdView(GenericAPIView):
    """
    Регистрация пользователей.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request):
        data = request.data
        data["user"] = request.user
        serializer = PasswordChangeSerializer(data=data)
        if serializer.is_valid():
            user = request.user
            user.set_password(request.data["new_password"])
            user.save()
            return Response(
                data={"Success": APIResponses.PASSWORD_CHANGED.value},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Users"])
@extend_schema_view(
    update=extend_schema(
        summary="Изменение сведений о пользователе.",
        responses={
            status.HTTP_200_OK: USER_PUT_OK_200,
            status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
        },
    ),
    partial_update=extend_schema(
        summary="Изменение сведений о пользователе.",
        responses={
            status.HTTP_200_OK: USER_PATCH_OK_200,
            status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
        },
        examples=[USER_PART_CHANGE_EXAMPLE],
    ),
    retrieve=extend_schema(
        summary="Просмотр сведений о пользователе.",
        responses={
            status.HTTP_200_OK: USER_GET_OK_200,
            status.HTTP_401_UNAUTHORIZED: UNAUTHORIZED_401,
        },
    ),
)
class UserViewSet(RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    """
    Изменение и получение данных о пользователе.
    """

    permission_classes = (SelfOnly,)

    def get_queryset(self):
        return User.objects.all()

    def get_object(self):
        if self.kwargs.get("pk", None) == "me":
            self.kwargs["pk"] = self.request.user.pk
        return super(UserViewSet, self).get_object()

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserReadSerializer
