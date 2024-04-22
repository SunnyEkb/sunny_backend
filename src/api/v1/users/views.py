from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.middleware import csrf
from drf_spectacular.utils import extend_schema

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, ParseError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.v1.shema import (
    LOGIN_EXAMPLE,
    USER_CREATE_EXAMPLE,
    LOGIN_OK_200,
    LOGIN_FORBIDDEN_403,
    LOGIN_UNAUTORIZED_401,
    USER_CREATED_201,
    USER_BAD_REQUEST_400,
)
from api.v1.users.utils import (
    get_tokens_for_user,
    set_access_cookie,
    set_refresh_cookie
)
from core.choices import APIResponses
from users.serializers import (
    UserCreateSerializer,
)

User = get_user_model()


@extend_schema(
    request=UserCreateSerializer,
    summary="Регистрация пользователя",
    tags=["Users"],
    examples=[USER_CREATE_EXAMPLE],
    responses={
        status.HTTP_201_CREATED: USER_CREATED_201,
        status.HTTP_400_BAD_REQUEST: USER_BAD_REQUEST_400,
    },
)
class RegisrtyView(GenericAPIView):
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
    summary="Login",
    examples=[LOGIN_EXAMPLE],
    responses={
        status.HTTP_200_OK: LOGIN_OK_200,
        status.HTTP_401_UNAUTHORIZED: LOGIN_UNAUTORIZED_401,
        status.HTTP_403_FORBIDDEN: LOGIN_FORBIDDEN_403,
    },
)
class LoginView(GenericAPIView):
    """
    Вход пользователя в систему.
    """

    authentication_classes = ()

    def post(self, request, format=None):
        data = request.data
        response = Response()
        email = data.get("email", None)
        password = data.get("password", None)
        user = authenticate(email=email, password=password)
        if user is not None:
            if user.is_active:
                data = get_tokens_for_user(user)
                set_access_cookie(response, data)
                set_refresh_cookie(response, data)
                response["X-CSRFToken"] = csrf.get_token(request)
                response.data = {"Success": APIResponses.SUCCESS_LOGIN.value}
                return response
            else:
                return Response(
                    {"No active": APIResponses.ACCOUNT_IS_INACTIVE.value},
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            raise AuthenticationFailed(APIResponses.INVALID_CREDENTIALS.value)


@extend_schema(
    tags=["Users"],
    summary="Logout",
)
class LogoutView(GenericAPIView):
    """
    Выход из системы.
    """

    permission_classes = [IsAuthenticated]

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
            raise ParseError("Invalid token")
