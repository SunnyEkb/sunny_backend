from uuid import uuid4

from django.utils import timezone
from drf_spectacular.utils import OpenApiExample

from core.choices import (
    AdState,
    AdvertisementStatus,
    APIResponses,
    ServicePlace,
)


USER_CREATE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Данные для регистрации",
    value={
        "username": "some_user",
        "email": "example@example.com",
        "phone": "+79000000000",
        "password": "your-password",
        "confirmation": "your-password",
    },
)

REGISTRY_VERIFICATION_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Подтверждение регистрации",
    value={"token": uuid4()},
)

VERIFICATION_SUCCESS_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Регистрация подтверждена",
    value={"datail": APIResponses.VERIFICATION_SUCCESS.value},
)

VERIFICATION_FAILED_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Регистрация не подтверждена",
    value={"datail": APIResponses.VERIFICATION_FAILED.value},
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

USER_UPDATE_AVATAR_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Изменение аватара пользователя",
    value={"avatar": "string"},
)


USER_INFO_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Данные пользователя",
    value={
        "id": 1,
        "username": "Some_username",
        "email": "example@example.com",
        "phone": "+79000000000",
        "first_name": "Some_name",
        "last_name": "Some_name",
        "role": "user",
        "avatar": "string",
    },
)

LOGIN_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Данные для входа в систему",
    value={"email": "foo@bar.bar", "password": "password"},
)

LOGIN_SUCCESS_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Пользователь вошел в систему",
    value={"Success": APIResponses.SUCCESS_LOGIN.value},
)

LOGOUT_SUCCESS_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Пользователь вышел из системы",
    value={"Success": APIResponses.SUCCESS_LOGOUT.value},
)

LOGIN_INVALID_CREDENTIALS_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Неверные данные для входа",
    value={"detail": APIResponses.INVALID_CREDENTIALS.value},
)

LOGIN_INACTIVE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Неактивный аккаунт",
    value={"No active": APIResponses.ACCOUNT_IS_INACTIVE.value},
)

UNAUTHORIZED_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Пользователь не авторизован",
    value={"detail": APIResponses.UNAUTHORIZED.value},
)

PASSWORD_DO_NOT_MATCH_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Пароль не соответствует подтверждению",
    value={"non_field_errors": [APIResponses.PASSWORD_DO_NOT_MATCH.value]},
)

PASSWORD_ERRORS: OpenApiExample = OpenApiExample(
    name="Пароль не соответствует требованиям безопасности.",
    value={
        "non_field_errors": [
            (
                "Введённый пароль слишком короткий. "
                "Он должен содержать как минимум 8 символов."
            ),
            "Введённый пароль слишком широко распространён.",
            "Введённый пароль состоит только из цифр.",
        ]
    },
)

WRONG_EMAIL_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Неверная электронаая почта",
    value={"email": ["Введите правильный адрес электронной почты."]},
)

PASSWORD_CHANGE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Пример изменения пароля пользователя",
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

REFRESH_SUCCESS_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Токен успешно обновлен",
    value={"Success": APIResponses.SUCCESS_TOKEN_REFRESH.value},
)

TYPE_LIST_HIERARCHY_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Иерархический список типов услуг",
    value={
        "id": 1,
        "title": "Красота и здоровье",
        "subcategories": [
            {
                "id": 3,
                "title": "Массаж",
                "subcategories": [
                    {
                        "id": 4,
                        "title": "Массаж спины",
                        "subcategories": None,
                    },
                ],
            },
        ],
    },
)

TYPE_LIST_FLAT_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Cписок типов услуг при фильтрации по названию",
    value={
        "id": 1,
        "title": "Красота и здоровье",
    },
)

COMMENT_LIST_EXAMPLE: OpenApiExample = OpenApiExample(
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

COMMENT_CREATE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Создать комментарий",
    value={
        "content_type": 23,
        "object_id": 2,
        "rating": 5,
        "feedback": "Супер",
    },
)

COMMENT_NOT_AUTHOR_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Комментарий пытается удалить не его автор",
    value={"detail": APIResponses.NO_PERMISSION.value},
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
        "price": [{"маникюр": 500}],
        "status": AdvertisementStatus.DRAFT,
        "images": [{"id": 1, "image": "string"}],
        "address": "Lenina st, 8/13",
        "salon_name": "Salon",
        "avg_rating": 4.1,
        "comments_quantity": 15,
        "created_at": timezone.now(),
        "is_favorited": False,
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
        "price": [{"маникюр": 500}],
        "status": AdvertisementStatus.DRAFT,
        "images": [{"id": 1, "image": "string"}],
        "address": "Lenina st, 8/13",
        "salon_name": "Salon",
        "avg_rating": 4.1,
        "comments_quantity": 15,
        "created_at": timezone.now(),
        "comments": COMMENT_LIST_EXAMPLE.value,
    },
)

SERVICE_CREATE_UPDATE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Создание и изменение услуги",
    value={
        "title": "string",
        "description": "string",
        "experience": 50,
        "place_of_provision": ServicePlace.OPTIONS.value,
        "type_id": 2,
        "price": [{"маникюр": 500}],
        "address": "Lenina st, 8/13",
        "salon_name": "Salon",
    },
)

SERVICE_PARTIAL_UPDATE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Частичное изменение услуги",
    value={
        "description": "string",
        "place_of_provision": ServicePlace.OPTIONS.value,
        "price": [{"маникюр": 500}],
        "address": "Lenina st, 8/13",
    },
)

SERVICE_AD_NO_PERMISSION_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Нет прав для выполнения действия",
    value={"detail": APIResponses.NO_PERMISSION.value},
)

WRONG_PARAMETR_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Неверно задан параметр",
    value={"detail": APIResponses.INVALID_PARAMETR.value},
)

CANT_HIDE_SERVICE_OR_AD_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга/объявление не может быть скрыта",
    value={"detail": APIResponses.CAN_NOT_HIDE_SERVICE_OR_AD.value},
)

CANT_DELETE_SERVICE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга не может быть удалена",
    value={"detail": APIResponses.CAN_NOT_DELETE_SEVICE.value},
)

CANT_CANCELL_SERVICE_OR_AD_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга(объявление) не может быть отменена",
    value={"detail": APIResponses.CAN_NOT_CANCELL_SERVICE_OR_AD.value},
)

CANT_ADD_NOT_PUBLISHED_OBJECT_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга(объявление) не опубликована",
    value={"detail": APIResponses.OBJECT_IS_NOT_PUBLISHED.value},
)

PORVIDER_CANT_FAVORITE_OBJECT_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Владелец объекта, не может добавить его в избранное",
    value={"detail": APIResponses.OBJECT_PROVIDER_CANT_ADD_TO_FAVORITE.value},
)

OBJECT_ALREADY_IN_FAVORITES_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Объект уже в избранном",
    value={"detail": APIResponses.OBJECT_ALREADY_IN_FAVORITES.value},
)

NOT_IN_FAVORITES_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга не в избранном",
    value={"detail": APIResponses.OBJECT_NOT_IN_FAVORITES.value},
)

ADDED_TO_FAVORITES_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Добавлено в избранное",
    value={"detail": APIResponses.ADDED_TO_FAVORITES.value},
)

DELETED_FROM_FAVORITES_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Удалено из избранного",
    value={"detail": APIResponses.DELETED_FROM_FAVORITES.value},
)

CANT_MODERATE_AD_OR_SERVICE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга (объявление) не может быть отправлена на модерацию",
    value={"detail": APIResponses.AD_OR_SERVICE_IS_CANCELLED.value},
)

CANT_PUBLISH_SERVICE_OR_AD_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга(объявление) не скрыта",
    value={"detail": APIResponses.SERVICE_OR_AD_IS_NOT_HIDDEN.value},
)

CANT_ADD_PHOTO_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Превышено максимальное количество фотографий",
    value={"detail": APIResponses.MAX_IMAGE_QUANTITY_EXEED.value},
)

MAX_FILE_SIZE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Превышен допустимый размер файла",
    value={"detail": APIResponses.MAX_FILE_SIZE_EXEED.value},
)

AD_CREATE_UPDATE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Создание и изменение объявления",
    value={
        "title": "Ботинки",
        "description": "Зимние ботинки",
        "price": "1000.00",
        "condition": "Б/у",
        "category_id": 4,
    },
)

AD_CREATED_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Объявление создано",
    value={
        "title": "Ботинки",
        "description": "Зимние ботинки",
        "price": "1000.00",
        "condition": "Б/у",
        "category_id": [1, 4],
    },
)

AD_RETRIEVE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Информация об объвлении",
    value={
        "id": 1,
        "provider": USER_INFO_EXAMPLE.value,
        "title": "string",
        "description": "string",
        "category": [1, 2, 3],
        "condition": AdState.USED.value,
        "price": "500.00",
        "status": AdvertisementStatus.DRAFT.value,
        "images": [{"id": 1, "image": "string"}],
        "created_at": timezone.now(),
        "is_favorited": False,
    },
)

AD_LIST_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Список объявлений", value=AD_RETRIEVE_EXAMPLE.value
)

AD_CATEGORIES_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Список категорий объявлений",
    value={
        "id": 1,
        "title": "Личные вещи",
        "subcategories": [
            {
                "id": 3,
                "title": "Одежа",
                "subcategories": [
                    {
                        "id": 4,
                        "title": "Одежда мужская",
                        "subcategories": None,
                    },
                    {
                        "id": 5,
                        "title": "Одежда женская",
                        "subcategories": None,
                    },
                ],
            }
        ],
    },
)

AD_PARTIAL_UPDATE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Частичное изменение объявления",
    value={
        "description": "string",
        "price": "100.00",
    },
)

FAVORITES_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Список избранного",
    value={
        "subject": AD_RETRIEVE_EXAMPLE.value,
    },
)
