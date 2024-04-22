from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from core.choices import APIResponses
from users.serializers import NonErrorFieldSerializer, UserCreateSerializer


USER_CREATE_EXAMPLE = OpenApiExample(
    name="Данные для регистрации",
    value={
        "email": "example@example.com",
        "password": "your-password",
        "confirmation": "your-password",
    },
)

USER_CREATED_EXAMPLE = OpenApiExample(
    name="Пользователь зарегистрирован",
    value={"email": "example@example.com"},
)

LOGIN_EXAMPLE = OpenApiExample(
    name="Данные для входа в систему.",
    value={"email": "foo@bar.bar", "password": "password"},
)

LOGIN_SUCCESS_EXAMPLE = OpenApiExample(
    name="Пользователь вошел в систему",
    value={"Success": APIResponses.SUCCESS_LOGIN.value}
)

LOGIN_INVALID_CREDENTIALS_EXAMPLE = OpenApiExample(
    name="Неверные данные для входа",
    value={"detail": APIResponses.INVALID_CREDENTIALS.value}
)

LOGIN_INACTIVE_EXAMPLE = OpenApiExample(
    name="Неверные данные для входа",
    value={"No active": APIResponses.ACCOUNT_IS_INACTIVE.value}
)

PASSWORD_DO_NOT_MATCH_EXAMPLE = OpenApiExample(
    name="Пароль не соответствует подтверждению",
    value={"non_field_errors": [APIResponses.PASSWORD_DO_NOT_MATCH.value]},
)

WRONG_EMAIL_EXAMPLE = OpenApiExample(
    name="Неверная электронаая почта",
    value={"email": ["Введите правильный адрес электронной почты."]},
)

USER_CREATED_201: OpenApiResponse = OpenApiResponse(
    response=UserCreateSerializer,
    description="Пользователь зарегистрирован",
    examples=[USER_CREATED_EXAMPLE],
)

USER_BAD_REQUEST_400: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Bad request",
    examples=[PASSWORD_DO_NOT_MATCH_EXAMPLE, WRONG_EMAIL_EXAMPLE],
)

LOGIN_OK_200: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Пользователь вошел в систему",
    examples=[LOGIN_SUCCESS_EXAMPLE],
)

LOGIN_UNAUTORIZED_401: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Неверные учетные данные",
    examples=[LOGIN_INVALID_CREDENTIALS_EXAMPLE],
)

LOGIN_FORBIDDEN_403: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Пользователь неактивен",
    examples=[LOGIN_INACTIVE_EXAMPLE],
)
