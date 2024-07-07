from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from core.choices import (
    APIResponses,
    ServiceCategory,
    ServicePlace,
    ServiceStatus,
)
from users.serializers import (
    NonErrorFieldSerializer,
    UserCreateSerializer,
    UserReadSerializer,
    UserUpdateSerializer,
)
from services.serializers import ServiceRetrieveSerializer, TypeGetSerializer


class CookieTokenScheme(OpenApiAuthenticationExtension):
    target_class = "api.v1.users.auth.CustomAuthentication"
    name = "CookieTokenAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "Authorization",
            "description": "Token-based authentication in Cookie.",
        }


USER_CREATE_EXAMPLE = OpenApiExample(
    name="Данные для регистрации",
    value={
        "username": "some_user",
        "email": "example@example.com",
        "phone": "+79000000000",
        "password": "your-password",
        "confirmation": "your-password",
    },
)

USER_CREATED_EXAMPLE = OpenApiExample(
    name="Пользователь зарегистрирован",
    value={"email": "example@example.com"},
)

USER_CHANGE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Изменение данных о пользователе.",
    value={
        "username": "Some_username",
        "first_name": "Some_name",
        "last_name": "Some_name",
        "phone": "+79000000000",
    },
)

USER_PART_CHANGE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Частичное изменение данных о пользователе.",
    value={"last_name": "Some_name"},
)


USER_INFO_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Изменение данных о пользователе.",
    value={
        "username": "Some_username",
        "email": "example@example.com",
        "phone": "+79000000000",
        "first_name": "Some_name",
        "last_name": "Some_name",
        "role": "user",
    },
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
        "confirmation": "superPuper2",
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

TYPE_LIST_EXAMPLE = OpenApiExample(
    name="Список типов услуг",
    value=[
        {"id": 1, "category": "Красота и здоровье", "title": "Маникюр"},
        {"id": 2, "category": "Красота и здоровье", "title": "Массаж"},
    ],
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

USER_GET_OK_200: OpenApiResponse = OpenApiResponse(
    response=UserReadSerializer,
    description="Данные пользователя",
    examples=[USER_INFO_EXAMPLE],
)

USER_PUT_OK_200: OpenApiResponse = OpenApiResponse(
    response=UserUpdateSerializer,
    description="Изменение данных пользователя",
    examples=[USER_CHANGE_EXAMPLE],
)

USER_PATCH_OK_200: OpenApiResponse = OpenApiResponse(
    response=UserUpdateSerializer,
    description="Частичное изменение данных пользователя",
    examples=[USER_PART_CHANGE_EXAMPLE],
)


TYPES_GET_OK_200: OpenApiResponse = OpenApiResponse(
    response=TypeGetSerializer,
    description="Получение списка типов услуг.",
    examples=[TYPE_LIST_EXAMPLE],
)

SERVICE_GET_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Информация об услуге",
    value={
        "id": 1,
        "provider": "example@example.example",
        "title": "string",
        "description": "string",
        "experience": 50,
        "place_of_provision": ServicePlace.OPTIONS.value,
        "type": {"category": ServiceCategory.BEAUTY.value, "title": "маникюр"},
        "price": {"маникюр": 500},
        "status": ServiceStatus.DRAFT,
        "images": [{"image": "string"}],
    },
)

SERVICE_GET_OK_200: OpenApiResponse = OpenApiResponse(
    response=ServiceRetrieveSerializer,
    description="Получение информауции об услуге.",
    examples=[SERVICE_GET_EXAMPLE],
)

CANT_HIDE_SERVICE_EXAMPLE = OpenApiExample(
    name="Услуга не может быть скрыта",
    value={"detail": APIResponses.CAN_NOT_HIDE_SERVICE.value},
)

CANT_HIDE_SERVICE_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Нельзя скрыть услугу.",
    examples=[CANT_HIDE_SERVICE_EXAMPLE],
)

CANT_DELETE_SERVICE_EXAMPLE = OpenApiExample(
    name="Услуга не может быть удалена.",
    value={"detail": APIResponses.CAN_NOT_DELETE_SEVICE.value},
)

CANT_DELETE_SERVICE_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Услуга не может быть удалена.",
    examples=[CANT_DELETE_SERVICE_EXAMPLE],
)
