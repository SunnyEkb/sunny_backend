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
    value={"Success": APIResponses.SUCCESS_LOGIN.value},
)

LOGOUT_SUCCESS_EXAMPLE = OpenApiExample(
    name="Пользователь вышел из системы",
    value={"Success": APIResponses.SUCCESS_LOGOUT.value},
)

LOGIN_INVALID_CREDENTIALS_EXAMPLE = OpenApiExample(
    name="Неверные данные для входа",
    value={"detail": APIResponses.INVALID_CREDENTIALS.value},
)

LOGIN_INACTIVE_EXAMPLE = OpenApiExample(
    name="Неактивный аккаунт",
    value={"No active": APIResponses.ACCOUNT_IS_INACTIVE.value},
)

UNAUTHORIZED_EXAMPLE = OpenApiExample(
    name="Пользователь не авторизован",
    value={"detail": APIResponses.UNAUTHORIZED.value},
)

PASSWORD_DO_NOT_MATCH_EXAMPLE = OpenApiExample(
    name="Пароль не соответствует подтверждению",
    value={"non_field_errors": [APIResponses.PASSWORD_DO_NOT_MATCH.value]},
)

PASSWORD_CHANGE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Пример изменения пароля пользователя.",
    value={
        "current_password": "superPuper",
        "new_password": "superPuper2",
    },
)

PASSWORD_CHANGED_SUCCESS_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Пароль обновлен",
    value={"Success": APIResponses.PASSWORD_CHANGED.value},
)

REFRESH_SUCCESS_EXAMPLE = OpenApiExample(
    name="Токен успешно обновлен",
    value={"Success": APIResponses.SUCCESS_TOKEN_REFRESH.value},
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

LOGIN_BADREQUEST_400: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Неверные учетные данные",
    examples=[LOGIN_INVALID_CREDENTIALS_EXAMPLE],
)

LOGIN_FORBIDDEN_403: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Пользователь неактивен",
    examples=[LOGIN_INACTIVE_EXAMPLE, LOGIN_INVALID_CREDENTIALS_EXAMPLE],
)

LOGOUT_OK_200: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Пользователь вышел из системы",
    examples=[LOGOUT_SUCCESS_EXAMPLE],
)

UNAUTHORIZED_401: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Пользователь не авторизован",
    examples=[UNAUTHORIZED_EXAMPLE],
)

REFRESH_OK_200: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Токен обновлен",
    examples=[REFRESH_SUCCESS_EXAMPLE],
)

PASSWORD_CHANGED_OK_200: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Пароль обновлен",
    examples=[PASSWORD_CHANGED_SUCCESS_EXAMPLE],
)
