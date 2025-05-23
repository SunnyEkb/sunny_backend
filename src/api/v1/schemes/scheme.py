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

USER_VERIFIED_200: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Регистрация подтверждена",
    examples=[examples.VERIFICATION_SUCCESS_EXAMPLE],
)

VERIFICACTION_FAILED_403: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Регистрация не подтверждена",
    examples=[examples.VERIFICATION_FAILED_EXAMPLE],
)

USER_BAD_REQUEST_400: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Bad request",
    examples=[
        examples.PASSWORD_DO_NOT_MATCH_EXAMPLE,
        examples.WRONG_EMAIL_EXAMPLE,
        examples.PASSWORD_ERRORS,
    ],
)

PASSWORD_ERRORS_400: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Bad request",
    examples=[
        examples.PASSWORD_ERRORS,
        examples.PASSWORD_DO_NOT_MATCH_EXAMPLE,
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
    examples=[
        examples.TYPE_LIST_HIERARCHY_EXAMPLE,
        examples.TYPE_LIST_FLAT_EXAMPLE,
    ],
)

CATEGORIES_GET_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.TypeGetSerializer,
    description="Получение списка категорий объявлений",
    examples=[
        examples.CATEGORY_LIST_HIERARCHY_EXAMPLE,
        examples.CATEGORY_LIST_FLAT_EXAMPLE,
    ],
)

SERVICE_LIST_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.ServiceListSerializer,
    description="Получение списка услуг",
    examples=[examples.SERVICE_LIST_EXAMPLE],
)

SERVICE_LIST_FOR_MODERATION_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.ServiceForModerationSerializer,
    description="Список услуг для модерации.",
)

AD_SERVICE_SENT_TO_MODERATION: OpenApiResponse = OpenApiResponse(
    response=serializers.ServiceListSerializer,
    description="Получение списка услуг",
    examples=[
        examples.SERVICE_LIST_EXAMPLE,
        examples.AD_OR_SERVICE_SENT_TO_MODERATION_EXAMPLE,
    ],
)

SERVICE_RETRIEVE_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.ServiceListSerializer,
    description="Получение информации об услуге",
    examples=[examples.SERVICE_RETRIEVE_EXAMPLE],
)

SERVICE_CREATED_201: OpenApiResponse = OpenApiResponse(
    response=serializers.ServiceCreateUpdateSerializer,
    description="Услуга создана",
    examples=[examples.SERVICE_LIST_EXAMPLE],
)

SERVICE_AD_FORBIDDEN_403: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Нет прав для выполнения действия",
    examples=[examples.SERVICE_AD_NO_PERMISSION_EXAMPLE],
)

SERVICE_AD_NOT_ACCEPT_406: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Услуга (объявление) находятся на модерации",
    examples=[examples.AD_OR_SERVICE_IS_UNDER_MODERATION_EXAMPLE],
)

WRONG_PARAMETR_400: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Неверно указан параметр",
    examples=[examples.WRONG_PARAMETR_EXAMPLE],
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

OBJECT_IS_NOT_PUBLISED_406: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Услуга (объявление) не опубликована",
    examples=[examples.CANT_ADD_NOT_PUBLISHED_OBJECT_EXAMPLE],
)

CANT_ADD_PHOTO_406: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Нельзя добавить фото.",
    examples=[
        examples.CANT_ADD_PHOTO_EXAMPLE,
        examples.AD_OR_SERVICE_IS_UNDER_MODERATION_EXAMPLE,
    ],
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

COMMENT_LIST_FOR_MODERATION_200_OK: OpenApiResponse = OpenApiResponse(
    response=serializers.CommentForModerationSerializer,
    description="Список комментариев для модерации",
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

AD_LIST_FOR_MODERATION_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.AdForModerationSerializer,
    description="Получение списка объявлений модерации",
)

AD_RETRIEVE_OK_200: OpenApiResponse = OpenApiResponse(
    response=serializers.ServiceListSerializer,
    description="Получение информации об объявлении",
    examples=[examples.AD_RETRIEVE_EXAMPLE],
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

OBJ_APPROVED_200_OK: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Объект одобрен",
    examples=[examples.OBJ_APPROVED_EXAMPLE],
)

OBJ_REJECTED_200_OK: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Объект отклонен",
    examples=[examples.OBJ_REJECTED_EXAMPLE],
)

CHATS_LIST_200_OK: OpenApiResponse = OpenApiResponse(
    response=serializers.ChatSerializer,
    description="Получение списка чатов",
    examples=[examples.CHAT_EXAMPLE],
)

NOTIFICATIONS_LIST_200_OK: OpenApiResponse = OpenApiResponse(
    response=serializers.NotificationSerializer,
    description="Получение списка чатов",
)

NOTIFICATION_MARKED_AS_READ_200_OK: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Уведомление помечено как прочитанное",
    examples=[examples.NOTIFICATION_IS_READ_EXAMPLE],
)

NOTIFICATION_MARKED_AS_UNREAD_200_OK: OpenApiResponse = OpenApiResponse(
    response=serializers.NonErrorFieldSerializer,
    description="Уведомление помечено как ytпрочитанное",
    examples=[examples.NOTIFICATION_IS_UNREAD_EXAMPLE],
)
