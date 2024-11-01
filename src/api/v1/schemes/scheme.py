from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.utils import OpenApiResponse

from api.v1 import serializers
from api.v1.schemes import examples


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
    response=serializers.CommentCreateSerializer,
    description="Комментарий создан",
    examples=[examples.COMMENT_CREATE_EXAMPLE],
)

USER_CREATED_201: OpenApiResponse = OpenApiResponse(
    response=serializers.UserCreateSerializer,
    description="Пользователь зарегистрирован",
    examples=[examples.USER_CREATED_EXAMPLE],
)

USER_BAD_REQUEST_400: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Bad request",
    examples=[
        examples.PASSWORD_DO_NOT_MATCH_EXAMPLE,
        examples.WRONG_EMAIL_EXAMPLE,
    ],
)

LOGIN_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Пользователь вошел в систему",
    examples=[examples.LOGIN_SUCCESS_EXAMPLE],
)

LOGIN_BADREQUEST_400: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Неверные учетные данные",
    examples=[examples.LOGIN_INVALID_CREDENTIALS_EXAMPLE],
)

LOGIN_FORBIDDEN_403: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Пользователь неактивен",
    examples=[
        examples.LOGIN_INACTIVE_EXAMPLE,
        examples.LOGIN_INVALID_CREDENTIALS_EXAMPLE,
    ],
)

LOGOUT_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Пользователь вышел из системы",
    examples=[examples.LOGOUT_SUCCESS_EXAMPLE],
)

UNAUTHORIZED_401: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Пользователь не авторизован",
    examples=[examples.UNAUTHORIZED_EXAMPLE],
)

REFRESH_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Токен обновлен",
    examples=[examples.REFRESH_SUCCESS_EXAMPLE],
)

PASSWORD_CHANGED_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Пароль обновлен",
    examples=[examples.PASSWORD_CHANGED_SUCCESS_EXAMPLE],
)

USER_GET_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.UserReadSerializer,
    description="Данные пользователя",
    examples=[examples.USER_INFO_EXAMPLE],
)

USER_PUT_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.UserUpdateSerializer,
    description="Изменение данных пользователя",
    examples=[examples.USER_CHANGE_EXAMPLE],
)

USER_UPDATE_AVATR_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.UserUpdateSerializer,
    description="Изменение аватара пользователя",
    examples=[examples.USER_UPDATE_AVATAR_EXAMPLE],
)

USER_PATCH_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.UserUpdateSerializer,
    description="Частичное изменение данных пользователя",
    examples=[examples.USER_PART_CHANGE_EXAMPLE],
)

TYPES_GET_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.TypeGetSerializer,
    description="Получение списка типов услуг",
    examples=[examples.TYPE_LIST_EXAMPLE],
)

SERVICE_LIST_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.ServiceListSerializer,
    description="Получение списка услуг",
    examples=[examples.SERVICE_LIST_EXAMPLE],
)

SERVICE_RETRIEVE_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.ServiceListSerializer,
    description="Получение информации об услуге",
    examples=[examples.SERVICE_RETRIEVE_EXAMPLE],
)

SERVICE_CREATED_201: OpenApiResponse = OpenApiResponse(
    response=serializers.ServiceCreateUpdateSerializer,
    description="Услуга содана",
    examples=[examples.SERVICE_CREATE_UPDATE_EXAMPLE],
)

SERVICE_AD_FORBIDDEN_403: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Нет прав для выполнения действия",
    examples=[examples.SERVICE_AD_NO_PERMISSION_EXAMPLE],
)

COMMENT_FORBIDDEN_403: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Только автор может удалить комментарий",
    examples=[examples.COMMENT_NOT_AUTHOR_EXAMPLE],
)

CANT_HIDE_SERVICE_OR_AD_406: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Нельзя скрыть услугу/объявление",
    examples=[examples.CANT_HIDE_SERVICE_OR_AD_EXAMPLE],
)

CANT_DELETE_SERVICE_406: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Услуга не может быть удалена",
    examples=[examples.CANT_DELETE_SERVICE_EXAMPLE],
)

CANT_CANCELL_SERVICE_OR_AD_406: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Услуга (объявление) не может быть отменена",
    examples=[examples.CANT_CANCELL_SERVICE_OR_AD_EXAMPLE],
)

CANT_MODERATE_SERVICE_406: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Услуга не может быть отправлена на модерацию",
    examples=[examples.CANT_MODERATE_AD_OR_SERVICE_EXAMPLE],
)

CANT_PUBLISH_SERVICE_OR_AD_406: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Услуга(объявление) не скрыта",
    examples=[examples.CANT_PUBLISH_SERVICE_OR_AD_EXAMPLE],
)

CANT_ADD_PHOTO_406: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Превышено максимальное количество фотографий",
    examples=[examples.CANT_ADD_PHOTO_EXAMPLE],
)

CANT_ADD_PHOTO_400: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Превышен допустимый размер файла",
    examples=[examples.MAX_FILE_SIZE_EXAMPLE],
)

COMMENT_LIST_200_OK: OpenApiResponse = OpenApiResponse(
    response=serializers.CommentReadSerializer,
    description="Список комментариев",
    examples=[examples.COMMENT_LIST_EXAMPLE],
)

CANT_ADD_TO_FAVORITES_406: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Объект не может быть добавлен в Избранное",
    examples=[
        examples.CANT_ADD_NOT_PUBLISHED_OBJECT_EXAMPLE,
        examples.PORVIDER_CANT_FAVORITE_OBJECT_EXAMPLE,
        examples.OBJECT_ALREADY_IN_FAVORITES_EXAMPLE,
    ],
)

CANT_DELETE_FROM_FAVORITES_406: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Объект не в Избранном",
    examples=[examples.NOT_IN_FAVORITES_EXAMPLE],
)

ADDED_TO_FAVORITES_201: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Добавлено в Избранное",
    examples=[examples.ADDED_TO_FAVORITES_EXAMPLE],
)

DELETED_FROM_FAVORITES_204: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Удалено из избранного",
    examples=[
        examples.DELETED_FROM_FAVORITES_EXAMPLE,
    ],
)

AD_LIST_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.ServiceListSerializer,
    description="Получение списка объявлений",
    examples=[examples.AD_LIST_EXAMPLE],
)

AD_RETRIEVE_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.ServiceListSerializer,
    description="Получение информации об объявлении",
    examples=[examples.AD_LIST_EXAMPLE],
)

AD_CREATED_201: OpenApiResponse = OpenApiResponse(
    response=serializers.ServiceCreateUpdateSerializer,
    description="Объявление содано",
    examples=[examples.AD_CREATED_EXAMPLE],
)

AD_CATEGORIES_GET_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.CategorySerializer,
    description="Получение списка категорий объявлений",
    examples=[examples.AD_CATEGORIES_EXAMPLE],
)

FAVORITES_LIST_200_OK: OpenApiResponse = OpenApiResponse(
    response=serializers.FavoritesSerialiser,
    description="Получение списка объектов избранного",
    examples=[examples.FAVORITES_EXAMPLE],
)
