from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.middleware import csrf
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view

from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed, ParseError
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from api.v1 import schemes
from api.v1 import serializers as api_serializers
from api.v1.auth_utils import (
    get_tokens_for_user,
    set_access_cookie,
    set_refresh_cookie,
)
from api.v1.permissions import SelfOnly
from core.choices import APIResponses
from services.tasks import delete_image_files, delete_image_files_task

User = get_user_model()


@extend_schema(
    request=api_serializers.UserCreateSerializer,
    summary="Регистрация пользователя.",
    tags=["Users"],
    examples=[schemes.USER_CREATE_EXAMPLE],
    responses={
        status.HTTP_201_CREATED: schemes.USER_CREATED_201,
        status.HTTP_400_BAD_REQUEST: schemes.USER_BAD_REQUEST_400,
    },
)
class RegisrtyView(APIView):
    """
    Регистрация пользователей.
    """

    def post(self, request):
        serializer = api_serializers.UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Users"],
    request=api_serializers.LoginSerializer,
    summary="Login.",
    examples=[schemes.LOGIN_EXAMPLE],
    responses={
        status.HTTP_200_OK: schemes.LOGIN_OK_200,
        status.HTTP_403_FORBIDDEN: schemes.LOGIN_FORBIDDEN_403,
    },
)
class LoginView(APIView):
    """
    Вход пользователя в систему.
    """

    authentication_classes = ()

    def post(self, request, format=None):
        serializer = api_serializers.LoginSerializer(data=request.data)
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
        status.HTTP_200_OK: schemes.LOGOUT_OK_200,
        status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
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
        status.HTTP_200_OK: schemes.REFRESH_OK_200,
        status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
    },
)
class CookieTokenRefreshView(TokenRefreshView):
    """
    Обновление refresh и access токена.
    """

    serializer_class = api_serializers.CookieTokenRefreshSerializer

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
    request=api_serializers.PasswordChangeSerializer,
    examples=[schemes.PASSWORD_CHANGE_EXAMPLE],
    responses={
        status.HTTP_200_OK: schemes.PASSWORD_CHANGED_OK_200,
        status.HTTP_400_BAD_REQUEST: schemes.USER_BAD_REQUEST_400,
        status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
    },
)
class ChangePassowrdView(GenericAPIView):
    """
    Регистрация пользователей.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = api_serializers.PasswordChangeSerializer

    def post(self, request):
        data = request.data
        data["user"] = request.user
        serializer = api_serializers.PasswordChangeSerializer(data=data)
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
        request=api_serializers.UserUpdateSerializer,
        responses={
            status.HTTP_200_OK: schemes.USER_GET_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
        },
        examples=[schemes.USER_CHANGE_EXAMPLE],
    ),
    partial_update=extend_schema(
        summary="Изменение сведений о пользователе.",
        request=api_serializers.UserUpdateSerializer,
        responses={
            status.HTTP_200_OK: schemes.USER_GET_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
        },
        examples=[schemes.USER_PART_CHANGE_EXAMPLE],
    ),
    retrieve=extend_schema(
        summary="Просмотр сведений о пользователе.",
        responses={
            status.HTTP_200_OK: schemes.USER_GET_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
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

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return api_serializers.UserUpdateSerializer
        return api_serializers.UserReadSerializer

    @extend_schema(
        request=None,
        summary="Получить информацию о текущем пользователе.",
        methods=["GET"],
        responses={
            status.HTTP_200_OK: schemes.USER_GET_OK_200,
            status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
        },
    )
    @action(
        detail=False,
        methods=("get",),
        url_path="me",
        url_name="me",
        permission_classes=(IsAuthenticated,),
    )
    def get_me(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.get_serializer(user)
        return Response(serializer.data)


@extend_schema(
    tags=["Users"],
    summary="Изменение аватара пользователя.",
    request=api_serializers.UserAdAvatarSerializer,
    examples=[schemes.USER_UPDATE_AVATAR_EXAMPLE],
    responses={
        status.HTTP_200_OK: schemes.USER_GET_OK_200,
        status.HTTP_401_UNAUTHORIZED: schemes.UNAUTHORIZED_401,
    },
)
class AdAvatarView(generics.UpdateAPIView):
    """
    Добавление аватара пользователя.
    """

    permission_classes = (SelfOnly,)
    serializer_class = api_serializers.UserAdAvatarSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.avatar:
            old_image = instance.avatar
            if settings.PROD_DB:
                delete_image_files_task.delay(str(old_image))
            else:
                delete_image_files(str(old_image))
        return super().update(request, *args, **kwargs)
