from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from comments.serializers import CommentReadSerializer
from core.choices import (
    APIResponses,
    ServicePlace,
    AdvertisementStatus,
)
from users.serializers import (
    NonErrorFieldSerializer,
    UserCreateSerializer,
    UserReadSerializer,
    UserUpdateSerializer,
)
from services.serializers import (
    ServiceCreateUpdateSerializer,
    ServiceListSerializer,
    TypeGetSerializer,
)


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
    name="Изменение данных о пользователе",
    value={
        "username": "Some_username",
        "first_name": "Some_name",
        "last_name": "Some_name",
        "phone": "+79000000000",
    },
)

USER_PART_CHANGE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Частичное изменение данных о пользователе",
    value={"last_name": "Some_name"},
)


USER_INFO_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Изменение данных о пользователе",
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
        {
            "id": 1,
            "title": "Красота и здоровье",
            "subcategories": {
                "id": 3,
                "title": "Массаж",
                "subcategories": {
                    "id": 4,
                    "title": "Массаж воротниковой зоны",
                },
            },
        },
        {"id": 2, "title": "Ремонт"},
    ],
)

COMMENT_LIST_EXAMPLE = OpenApiExample(
    name="Список комментариев",
    value=[
        {
            "content_type": 23,
            "object_id": 2,
            "rating": 5,
            "feedback": "Супер",
            "id": 1,
            "author": USER_INFO_EXAMPLE.value,
            "images": [{"id": 1, "image": "string"}],
        },
    ],
)

COMMENT_CREATE_EXAMPLE = OpenApiExample(
    name="Создать комментарий",
    value=[
        {
            "content_type": 23,
            "object_id": 2,
            "rating": 5,
            "feedback": "Супер",
        },
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
    description="Получение списка типов услуг",
    examples=[TYPE_LIST_EXAMPLE],
)

SERVICE_LIST_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Список услуг",
    value={
        "id": 1,
        "provider": USER_INFO_EXAMPLE.value,
        "title": "string",
        "description": "string",
        "experience": 50,
        "place_of_provision": ServicePlace.OPTIONS.value,
        "type": [1, 2, 3],
        "price": {"маникюр": 500},
        "status": AdvertisementStatus.DRAFT,
        "images": [{"id": 1, "image": "string"}],
        "address": "Lenina st, 8/13",
        "salon_name": "Salon",
        "avg_rating": 4.1,
        "comments_quantity": 15,
    },
)

SERVICE_RETRIEVE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Информация об услуге",
    value={
        "id": 1,
        "provider": USER_INFO_EXAMPLE.value,
        "title": "string",
        "description": "string",
        "experience": 50,
        "place_of_provision": ServicePlace.OPTIONS.value,
        "type": [1, 2, 3],
        "price": {"маникюр": 500},
        "status": AdvertisementStatus.DRAFT,
        "images": [{"id": 1, "image": "string"}],
        "address": "Lenina st, 8/13",
        "salon_name": "Salon",
        "avg_rating": 4.1,
        "comments_quantity": 15,
        "comments": COMMENT_LIST_EXAMPLE.value,
    },
)

SERVICE_CREATE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Создание услуге",
    value={
        "title": "string",
        "description": "string",
        "experience": 50,
        "place_of_provision": ServicePlace.OPTIONS.value,
        "type_id": 2,
        "price": {"маникюр": 500},
        "address": "Lenina st, 8/13",
        "salon_name": "Salon",
    },
)

SERVICE_LIST_OK_200: OpenApiResponse = OpenApiResponse(
    response=ServiceListSerializer,
    description="Получение списка услуг",
    examples=[SERVICE_LIST_EXAMPLE],
)

SERVICE_RETRIEVE_OK_200: OpenApiResponse = OpenApiResponse(
    response=ServiceListSerializer,
    description="Получение информации об услуге",
    examples=[SERVICE_RETRIEVE_EXAMPLE],
)

SERVICE_CREATED_201: OpenApiResponse = OpenApiResponse(
    response=ServiceCreateUpdateSerializer,
    description="Услуга содана",
    examples=[SERVICE_CREATE_EXAMPLE],
)

SERVICE_NOT_PROVIDER_EXAMPLE = OpenApiExample(
    name="Услугу пытается изменить не исполнитель",
    value={"detail": APIResponses.NO_PERMISSION.value},
)

SERVICE_FORBIDDEN_403: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Только испольнитель может изменить информацию об услуге",
    examples=[SERVICE_NOT_PROVIDER_EXAMPLE],
)

CANT_HIDE_SERVICE_EXAMPLE = OpenApiExample(
    name="Услуга не может быть скрыта",
    value={"detail": APIResponses.CAN_NOT_HIDE_SERVICE.value},
)

CANT_HIDE_SERVICE_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Нельзя скрыть услугу",
    examples=[CANT_HIDE_SERVICE_EXAMPLE],
)

CANT_DELETE_SERVICE_EXAMPLE = OpenApiExample(
    name="Услуга не может быть удалена",
    value={"detail": APIResponses.CAN_NOT_DELETE_SEVICE.value},
)

CANT_DELETE_SERVICE_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Услуга не может быть удалена",
    examples=[CANT_DELETE_SERVICE_EXAMPLE],
)

CANT_CANCELL_SERVICE_EXAMPLE = OpenApiExample(
    name="Услуга не может быть отменена",
    value={"detail": APIResponses.CAN_NOT_CANCELL_SERVICE.value},
)

CANT_CANCELL_SERVICE_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Услуга не может быть отменена",
    examples=[CANT_CANCELL_SERVICE_EXAMPLE],
)

CANT_MODERATE_SERVICE_EXAMPLE = OpenApiExample(
    name="Услуга не может быть отправлена на модерацию",
    value={"detail": APIResponses.SERVICE_IS_CANCELLED.value},
)

CANT_MODERATE_SERVICE_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Услуга не может быть отправлена на модерацию",
    examples=[CANT_MODERATE_SERVICE_EXAMPLE],
)

CANT_PUBLISH_SERVICE_EXAMPLE = OpenApiExample(
    name="Услуга не скрыта",
    value={"detail": APIResponses.SERVICE_IS_NOT_HIDDEN.value},
)

CANT_PUBLISH_SERVICE_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Услуга не скрыта",
    examples=[CANT_PUBLISH_SERVICE_EXAMPLE],
)

CANT_ADD_PHOTO_EXAMPLE = OpenApiExample(
    name="Превышено максимальное количество фотографий",
    value={"detail": APIResponses.MAX_IMAGE_QUANTITY_EXEED.value},
)

CANT_ADD_PHOTO_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Превышено максимальное количество фотографий",
    examples=[CANT_ADD_PHOTO_EXAMPLE],
)

MAX_FILE_SIZE_EXAMPLE = OpenApiExample(
    name="Превышен допустимый размер файла",
    value={"detail": APIResponses.MAX_FILE_SIZE_EXEED.value},
)

CANT_ADD_PHOTO_400: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Превышен допустимый размер файла",
    examples=[MAX_FILE_SIZE_EXAMPLE],
)

COMMENT_LIST_200_OK: OpenApiResponse = OpenApiResponse(
    response=CommentReadSerializer,
    description="Список комментариев",
    examples=[COMMENT_LIST_EXAMPLE],
)
