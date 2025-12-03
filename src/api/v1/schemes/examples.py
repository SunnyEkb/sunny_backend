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
    value={"datail": APIResponses.VERIFICATION_SUCCESS},
)

VERIFICATION_FAILED_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Регистрация не подтверждена",
    value={"datail": APIResponses.VERIFICATION_FAILED},
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
    value={"avatar": "data:<MIME-type>;base64,<data>"},
)

UPLOAD_FILE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Загрузка изображения.",
    value={"images": [{"image": "data:<MIME-type>;base64,<data>"}]},
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
    value={"Success": APIResponses.SUCCESS_LOGIN},
)

LOGOUT_SUCCESS_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Пользователь вышел из системы",
    value={"Success": APIResponses.SUCCESS_LOGOUT},
)

LOGIN_INVALID_CREDENTIALS_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Неверные данные для входа",
    value={"detail": APIResponses.INVALID_CREDENTIALS},
)

LOGIN_INACTIVE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Неактивный аккаунт",
    value={"No active": APIResponses.ACCOUNT_IS_INACTIVE},
)

UNAUTHORIZED_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Пользователь не авторизован",
    value={"detail": APIResponses.UNAUTHORIZED},
)

PASSWORD_DO_NOT_MATCH_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Пароль не соответствует подтверждению",
    value={"non_field_errors": [APIResponses.PASSWORD_DO_NOT_MATCH]},
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
    value={"Success": APIResponses.PASSWORD_CHANGED},
)

REFRESH_SUCCESS_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Токен успешно обновлен",
    value={"Success": APIResponses.SUCCESS_TOKEN_REFRESH},
)

TYPE_LIST_HIERARCHY_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Иерархический список категорий услуг",
    value={
        "id": 1,
        "title": "Красота и здоровье",
        "subcategories": [
            {
                "id": 3,
                "title": "Массаж",
                "image": "url",
                "subcategories": [
                    {
                        "id": 4,
                        "title": "Массаж спины",
                        "subcategories": None,
                        "image": None,
                    },
                ],
            },
        ],
    },
)

TYPE_LIST_FLAT_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Cписок категорий услуг при фильтрации по названию",
    value={
        "id": 1,
        "title": "Красота и здоровье",
        "image": "url",
    },
)

CATEGORY_LIST_HIERARCHY_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Иерархический список категорий",
    value={
        "id": 1,
        "title": "Красота и здоровье",
        "subcategories": [
            {
                "id": 3,
                "title": "Массаж",
                "image": "url",
                "subcategories": [
                    {
                        "id": 4,
                        "title": "Массаж спины",
                        "subcategories": None,
                        "image": None,
                    },
                ],
            },
        ],
    },
)

CATEGORY_LIST_FLAT_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Cписок категорий при фильтрации по названию",
    value={
        "id": 1,
        "title": "Красота и здоровье",
        "image": "url",
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
        "rating": 5,
        "feedback": "Супер",
        "images": [
            {"image": "data:<MIME-type>;base64,<data>"},
            {"image": "data:<MIME-type>;base64,<data>"},
        ],
    },
)

COMMENT_NOT_AUTHOR_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Комментарий пытается удалить не его автор",
    value={"detail": APIResponses.NO_PERMISSION},
)

PRICE_LIST_ENTRIES_CREATE_UPDATE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Список подуслуг для создания.",
    value=[
        {"title": "Диагностика", "price": "2000.00"},
        {"title": "Замена деталей", "price": "5000.00"},
    ],
)

PRICE_LIST_ENTRIES_READ_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Список подуслуг для обновления.",
    value=[
        {"id": 1, "title": "Диагностика", "price": "2000.00"},
        {"id": 2, "title": "Замена деталей", "price": "5000.00"},
    ],
)

SERVICE_LIST_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Список услуг",
    value={
        "id": 1,
        "provider": USER_INFO_EXAMPLE.value,
        "title": "string",
        "description": "string",
        "experience": 50,
        "place_of_provision": ServicePlace.OPTIONS,
        "type": [1, 2, 3],
        "status": AdvertisementStatus.DRAFT,
        "images": [{"id": 1, "image": "string"}],
        "address": "Lenina st, 8/13",
        "salon_name": "Salon",
        "avg_rating": 4.1,
        "comments_quantity": 15,
        "created_at": timezone.now(),
        "is_favorited": False,
        "price_list_entries": PRICE_LIST_ENTRIES_READ_EXAMPLE.value,
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
        "place_of_provision": ServicePlace.OPTIONS,
        "type": [1, 2, 3],
        "status": AdvertisementStatus.DRAFT,
        "images": [{"id": 1, "image": "string"}],
        "address": "Lenina st, 8/13",
        "salon_name": "Salon",
        "avg_rating": 4.1,
        "comments_quantity": 15,
        "created_at": timezone.now(),
        "comments": COMMENT_LIST_EXAMPLE.value,
        "price_list_entries": PRICE_LIST_ENTRIES_READ_EXAMPLE.value,
    },
)

SERVICE_CREATE_UPDATE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Создание и изменение услуги",
    value={
        "title": "string",
        "description": "string",
        "experience": 50,
        "place_of_provision": ServicePlace.OPTIONS,
        "type_id": 2,
        "address": "Lenina st, 8/13",
        "salon_name": "Salon",
        "price_list_entries": PRICE_LIST_ENTRIES_CREATE_UPDATE_EXAMPLE.value,
    },
)

SERVICE_PARTIAL_UPDATE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Частичное изменение услуги",
    value={
        "description": "string",
        "place_of_provision": ServicePlace.OPTIONS,
        "address": "Lenina st, 8/13",
    },
)

SERVICE_AD_NO_PERMISSION_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Нет прав для выполнения действия",
    value={"detail": APIResponses.NO_PERMISSION},
)

WRONG_PARAMETR_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Неверно задан параметр",
    value={"detail": APIResponses.INVALID_PARAMETR},
)

CANT_HIDE_SERVICE_OR_AD_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга/объявление не может быть скрыта",
    value={"detail": APIResponses.CAN_NOT_HIDE_SERVICE_OR_AD},
)

CANT_ADD_NOT_PUBLISHED_OBJECT_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга(объявление) не опубликована",
    value={"detail": APIResponses.OBJECT_IS_NOT_PUBLISHED},
)

PORVIDER_CANT_FAVORITE_OBJECT_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Владелец объекта, не может добавить его в избранное",
    value={"detail": APIResponses.OBJECT_PROVIDER_CANT_ADD_TO_FAVORITE},
)

OBJECT_ALREADY_IN_FAVORITES_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Объект уже в избранном",
    value={"detail": APIResponses.OBJECT_ALREADY_IN_FAVORITES},
)

NOT_IN_FAVORITES_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга не в избранном",
    value={"detail": APIResponses.OBJECT_NOT_IN_FAVORITES},
)

ADDED_TO_FAVORITES_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Добавлено в избранное",
    value={"detail": APIResponses.ADDED_TO_FAVORITES},
)

DELETED_FROM_FAVORITES_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Удалено из избранного",
    value={"detail": APIResponses.DELETED_FROM_FAVORITES},
)

CANT_MODERATE_AD_OR_SERVICE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга (объявление) не может быть отправлена на модерацию",
    value={"detail": APIResponses.AD_OR_SERVICE_CANT_BE_SENT_TO_MODERATION},
)

AD_OR_SERVICE_SENT_TO_MODERATION_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга (объявление) отправлена на модерацию",
    value={"detail": APIResponses.AD_OR_SERVICE_SENT_MODERATION},
)

AD_OR_SERVICE_IS_UNDER_MODERATION_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга (объявление) находится на модерации",
    value={"detail": APIResponses.AD_OR_SERVICE_IS_UNDER_MODERATION},
)

CANT_PUBLISH_SERVICE_OR_AD_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Услуга(объявление) не скрыта",
    value={"detail": APIResponses.SERVICE_OR_AD_CANT_BE_PUBLISHED},
)

CANT_ADD_PHOTO_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Превышено максимальное количество фотографий",
    value={"detail": APIResponses.MAX_IMAGE_QUANTITY_EXEED},
)

MAX_FILE_SIZE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Превышен допустимый размер файла",
    value={"detail": APIResponses.MAX_FILE_SIZE_EXEED},
)

AD_CREATE_UPDATE_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Создание и изменение объявления",
    value={
        "title": "Ботинки",
        "description": "Зимние ботинки",
        "price": "1000.00",
        "address": "some address",
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
        "address": "some address",
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
        "condition": AdState.USED,
        "price": "500.00",
        "address": "some address",
        "status": AdvertisementStatus.DRAFT,
        "images": [{"id": 1, "image": "string"}],
        "is_favorited": False,
        "avg_rating": 4.1,
        "comments_quantity": 15,
        "created_at": timezone.now(),
        "comments": COMMENT_LIST_EXAMPLE.value,
    },
)

AD_LIST_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Список объявлений",
    value={
        "id": 1,
        "provider": USER_INFO_EXAMPLE.value,
        "title": "string",
        "description": "string",
        "category": [1, 2, 3],
        "condition": AdState.USED,
        "price": "500.00",
        "address": "some address",
        "status": AdvertisementStatus.DRAFT,
        "images": [{"id": 1, "image": "string"}],
        "is_favorited": False,
        "avg_rating": 4.1,
        "comments_quantity": 15,
        "created_at": timezone.now(),
    },
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
    value={"subject": AD_RETRIEVE_EXAMPLE.value},
)

OBJ_APPROVED_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Одобрено",
    value={"subject": APIResponses.OBJECT_APPROVED},
)

OBJ_REJECTED_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Отклонено",
    value={"subject": APIResponses.OBJECT_REJECTED},
)

CHAT_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Список чатов",
    value={
        "id": 1,
        "subject": AD_RETRIEVE_EXAMPLE.value,
        "seller": USER_INFO_EXAMPLE.value,
        "buyer": USER_INFO_EXAMPLE.value,
    },
)

NOTIFICATION_IS_READ_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Уведомление помечено как прочитанное",
    value={"subject": APIResponses.NOTIFICATION_IS_READ},
)

NOTIFICATION_IS_UNREAD_EXAMPLE: OpenApiExample = OpenApiExample(
    name="Уведомление помечено как ytпрочитанное",
    value={"subject": APIResponses.NOTIFICATION_IS_UNREAD},
)
