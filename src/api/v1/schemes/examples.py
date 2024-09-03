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

LOGIN_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Данные для входа в систему.",
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

WRONG_EMAIL_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Неверная электронаая почта",
    value={"email": ["Введите правильный адрес электронной почты."]},
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

REFRESH_SUCCESS_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Токен успешно обновлен",
    value={"Success": APIResponses.SUCCESS_TOKEN_REFRESH.value},
)

TYPE_LIST_EXAMPLE: OpenApiExample = OpenApiExample(
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
        "price": {"маникюр": 500},
        "status": AdvertisementStatus.DRAFT,
        "images": [{"id": 1, "image": "string"}],
        "address": "Lenina st, 8/13",
        "salon_name": "Salon",
        "avg_rating": 4.1,
        "comments_quantity": 15,
        "created_at": "2024-06-20T06:25:52.449498Z",
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
        "price": {"маникюр": 500},
        "status": AdvertisementStatus.DRAFT,
        "images": [{"id": 1, "image": "string"}],
        "address": "Lenina st, 8/13",
        "salon_name": "Salon",
        "avg_rating": 4.1,
        "comments_quantity": 15,
        "created_at": "2024-06-20T06:25:52.449498Z",
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

SERVICE_AD_NO_PERMISSION_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Нет прав для выполнения действия",
    value={"detail": APIResponses.NO_PERMISSION.value},
)

CANT_HIDE_SERVICE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга не может быть скрыта",
    value={"detail": APIResponses.CAN_NOT_HIDE_SERVICE.value},
)

CANT_DELETE_SERVICE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга не может быть удалена",
    value={"detail": APIResponses.CAN_NOT_DELETE_SEVICE.value},
)

CANT_CANCELL_SERVICE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга не может быть отменена",
    value={"detail": APIResponses.CAN_NOT_CANCELL_SERVICE.value},
)

CANT_FAVORITE_SERVICE_NOT_PUBLISHED_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга не опубликована",
    value={"detail": APIResponses.SERVICE_IS_NOT_PUBLISHED.value},
)

PORVIDER_CANT_FAVORITE_SERVICE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Лицо, оказывающее услугу, не может добавить её в избранное",
    value={"detail": APIResponses.SERVICE_PROVIDER_CANT_ADD_TO_FAVORITE.value},
)

SERVICE_ALREADY_IN_FAVORITES_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга уже в избранном",
    value={"detail": APIResponses.SERVICE_ALREADY_IN_FAVORITES.value},
)

SERVICE_NOT_IN_FAVORITES_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга не в избранном",
    value={"detail": APIResponses.SERVICE_NOT_IN_FAVORITES.value},
)

SERVICE_ADDED_TO_FAVORITES_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга добавлена в избранное",
    value={"detail": APIResponses.SERVICE_ADDED_TO_FAVORITES.value},
)

SERVICE_DELETED_FROM_FAVORITES_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга удалена из избранного",
    value={"detail": APIResponses.SERVICE_DELETED_FROM_FAVORITES.value},
)

CANT_MODERATE_SERVICE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга не может быть отправлена на модерацию",
    value={"detail": APIResponses.SERVICE_IS_CANCELLED.value},
)

CANT_PUBLISH_SERVICE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга не скрыта",
    value={"detail": APIResponses.SERVICE_IS_NOT_HIDDEN.value},
)

CANT_ADD_PHOTO_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Превышено максимальное количество фотографий",
    value={"detail": APIResponses.MAX_IMAGE_QUANTITY_EXEED.value},
)

MAX_FILE_SIZE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Превышен допустимый размер файла",
    value={"detail": APIResponses.MAX_FILE_SIZE_EXEED.value},
)

ADD_CREATE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Создание объявления",
    value={
        "title": "Ботинки",
        "description": "Зимние ботинки",
        "price": "1000.00",
        "condition": "Б/у",
        "category_id": 4,
    },
)

ADD_CREATED_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Объявления создано",
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
        "created_at": "2024-06-20T06:25:52.449498Z",
        "is_favorited": False,
    },
)

AD_LIST_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Список объявлений",
    value=[
        {
            "id": 1,
            "provider": USER_INFO_EXAMPLE.value,
            "title": "string",
            "description": "string",
            "category": [1, 2, 3],
            "condition": AdState.USED.value,
            "price": "500.00",
            "status": AdvertisementStatus.DRAFT.value,
            "images": [{"id": 1, "image": "string"}],
            "created_at": "2024-06-20T06:25:52.449498Z",
            "is_favorited": False,
        }
    ],
)
