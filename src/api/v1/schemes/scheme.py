from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.utils import OpenApiResponse

from api.v1.schemes import examples
from api.v1.serializers import (
    CommentReadSerializer,
    CommentCreateSerializer,
    NonErrorFieldSerializer,
    ServiceCreateUpdateSerializer,
    ServiceListSerializer,
    TypeGetSerializer,
    UserCreateSerializer,
    UserReadSerializer,
    UserUpdateSerializer,
)


class CookieTokenScheme(OpenApiAuthenticationExtension):
    target_class = "api.v1.auth.CustomAuthentication"
    name = "CookieTokenAuth"

    def get_security_definition(self, auto_schema):
        return {
            "type": "apiKey",
            "in": "cookie",
            "name": "Authorization",
            "description": "Token-based authentication in Cookie.",
        }


COMMENT_CREATED_201: OpenApiResponse = OpenApiResponse(
    response=CommentCreateSerializer,
    description="Комментарий создан",
    examples=[examples.COMMENT_CREATE_EXAMPLE],
)

USER_CREATED_201: OpenApiResponse = OpenApiResponse(
    response=UserCreateSerializer,
    description="Пользователь зарегистрирован",
    examples=[examples.USER_CREATED_EXAMPLE],
)

USER_BAD_REQUEST_400: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Bad request",
    examples=[
        examples.PASSWORD_DO_NOT_MATCH_EXAMPLE,
        examples.WRONG_EMAIL_EXAMPLE,
    ],
)

LOGIN_OK_200: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Пользователь вошел в систему",
    examples=[examples.LOGIN_SUCCESS_EXAMPLE],
)

LOGIN_BADREQUEST_400: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Неверные учетные данные",
    examples=[examples.LOGIN_INVALID_CREDENTIALS_EXAMPLE],
)

LOGIN_FORBIDDEN_403: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Пользователь неактивен",
    examples=[
        examples.LOGIN_INACTIVE_EXAMPLE,
        examples.LOGIN_INVALID_CREDENTIALS_EXAMPLE,
    ],
)

LOGOUT_OK_200: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Пользователь вышел из системы",
    examples=[examples.LOGOUT_SUCCESS_EXAMPLE],
)

UNAUTHORIZED_401: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Пользователь не авторизован",
    examples=[examples.UNAUTHORIZED_EXAMPLE],
)

REFRESH_OK_200: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Токен обновлен",
    examples=[examples.REFRESH_SUCCESS_EXAMPLE],
)

PASSWORD_CHANGED_OK_200: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Пароль обновлен",
    examples=[examples.PASSWORD_CHANGED_SUCCESS_EXAMPLE],
)

USER_GET_OK_200: OpenApiResponse = OpenApiResponse(
    response=UserReadSerializer,
    description="Данные пользователя",
    examples=[examples.USER_INFO_EXAMPLE],
)

USER_PUT_OK_200: OpenApiResponse = OpenApiResponse(
    response=UserUpdateSerializer,
    description="Изменение данных пользователя",
    examples=[examples.USER_CHANGE_EXAMPLE],
)

USER_PATCH_OK_200: OpenApiResponse = OpenApiResponse(
    response=UserUpdateSerializer,
    description="Частичное изменение данных пользователя",
    examples=[examples.USER_PART_CHANGE_EXAMPLE],
)

TYPES_GET_OK_200: OpenApiResponse = OpenApiResponse(
    response=TypeGetSerializer,
    description="Получение списка типов услуг",
    examples=[examples.TYPE_LIST_EXAMPLE],
)

SERVICE_LIST_OK_200: OpenApiResponse = OpenApiResponse(
    response=ServiceListSerializer,
    description="Получение списка услуг",
    examples=[examples.SERVICE_LIST_EXAMPLE],
)

SERVICE_RETRIEVE_OK_200: OpenApiResponse = OpenApiResponse(
    response=ServiceListSerializer,
    description="Получение информации об услуге",
    examples=[examples.SERVICE_RETRIEVE_EXAMPLE],
)

SERVICE_CREATED_201: OpenApiResponse = OpenApiResponse(
    response=ServiceCreateUpdateSerializer,
    description="Услуга содана",
    examples=[examples.SERVICE_CREATE_EXAMPLE],
)

SERVICE_AD_FORBIDDEN_403: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Нет прав для выполнения действия",
    examples=[examples.SERVICE_AD_NO_PERMISSION_EXAMPLE],
)

COMMENT_FORBIDDEN_403: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Только автор может удалить комментарий",
    examples=[examples.COMMENT_NOT_AUTHOR_EXAMPLE],
)

CANT_HIDE_SERVICE_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Нельзя скрыть услугу",
    examples=[examples.CANT_HIDE_SERVICE_EXAMPLE],
)

CANT_DELETE_SERVICE_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Услуга не может быть удалена",
    examples=[examples.CANT_DELETE_SERVICE_EXAMPLE],
)

CANT_CANCELL_SERVICE_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Услуга не может быть отменена",
    examples=[examples.CANT_CANCELL_SERVICE_EXAMPLE],
)

CANT_MODERATE_SERVICE_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Услуга не может быть отправлена на модерацию",
    examples=[examples.CANT_MODERATE_SERVICE_EXAMPLE],
)

CANT_PUBLISH_SERVICE_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Услуга не скрыта",
    examples=[examples.CANT_PUBLISH_SERVICE_EXAMPLE],
)

CANT_ADD_PHOTO_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Превышено максимальное количество фотографий",
    examples=[examples.CANT_ADD_PHOTO_EXAMPLE],
)

CANT_ADD_PHOTO_400: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Превышен допустимый размер файла",
    examples=[examples.MAX_FILE_SIZE_EXAMPLE],
)

COMMENT_LIST_200_OK: OpenApiResponse = OpenApiResponse(
    response=CommentReadSerializer,
    description="Список комментариев",
    examples=[examples.COMMENT_LIST_EXAMPLE],
)

CANT_ADD_SERVICE_TO_FAVORITES_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Услуга не может быть добавлена в Избранное",
    examples=[
        examples.CANT_FAVORITE_SERVICE_NOT_PUBLISHED_EXAMPLE,
        examples.PORVIDER_CANT_FAVORITE_SERVICE_EXAMPLE,
        examples.SERVICE_ALREADY_IN_FAVORITES_EXAMPLE,
    ],
)

CANT_DELETE_SERVICE_FROM_FAVORITES_406: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Услуга не в Избранном",
    examples=[examples.SERVICE_NOT_IN_FAVORITES_EXAMPLE],
)

SERVICE_ADDED_TO_FAVORITES_201: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Услуга добавлена в Избранное",
    examples=[examples.SERVICE_ADDED_TO_FAVORITES_EXAMPLE],
)

SERVICE_DELETED_FROM_FAVORITES_204: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Услуга удалена из в Избранного",
    examples=[
        examples.SERVICE_DELETED_FROM_FAVORITES_EXAMPLE,
    ],
)

AD_LIST_OK_200: OpenApiResponse = OpenApiResponse(
    response=ServiceListSerializer,
    description="Получение списка объявлений",
    examples=[examples.AD_LIST_EXAMPLE],
)

AD_RETRIEVE_OK_200: OpenApiResponse = OpenApiResponse(
    response=ServiceListSerializer,
    description="Получение информации об объявлении",
    examples=[examples.AD_LIST_EXAMPLE],
)

AD_CREATED_201: OpenApiResponse = OpenApiResponse(
    response=ServiceCreateUpdateSerializer,
    description="Объявление содано",
    examples=[examples.ADD_CREATED_EXAMPLE],
)
