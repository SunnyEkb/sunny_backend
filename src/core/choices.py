from django.db import models

from core.enums import Limits
from config.settings.base import ALLOWED_IMAGE_FILE_EXTENTIONS


class Role(models.TextChoices):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"


class ServicePlace(models.TextChoices):
    HOUSE_CALL = "Выезд"
    OFFICE = "В офисе"
    ON_LINE = "On line"
    OPTIONS = "По выбору"


class CommentStatus(models.IntegerChoices):
    DRAFT = 0
    PUBLISHED = 1
    MODERATION = 2


class AdvertisementStatus(models.IntegerChoices):
    DRAFT = 0
    MODERATION = 1
    PUBLISHED = 2
    HIDDEN = 3


class APIResponses(models.TextChoices):
    ACCOUNT_IS_INACTIVE = "This account is not active"
    ADDED_TO_FAVORITES = "Добавлено в избранное."
    INVALID_TOKEN = "No valid token found in cookie 'refresh_token'"
    INVALID_CREDENTIALS = "Invalid email or password"
    PASSWORD_DO_NOT_MATCH = "Password and confirmation do not match"
    PASSWORD_CHANGED = "Password changed successfully"
    NOT_SAME_PASSWORD = "New password is the same as the latest"
    SUCCESS_LOGIN = "Login successfully"
    SUCCESS_LOGOUT = "Logout successfully"
    SUCCESS_TOKEN_REFRESH = "Token refreshed"
    WRONG_PASSWORD = "Wrong password"
    UNAUTHORIZED = "Учетные данные не были предоставлены."
    CAN_NOT_HIDE_SERVICE_OR_AD = (
        "Скрыть можно только опубликованную услугу (объявление)."
    )
    NO_PERMISSION = "У вас недостаточно прав для выполнения данного действия."
    AD_OR_SERVICE_CANT_BE_SENT_TO_MODERATION = (
        "Данная услуга (объявление) уже на модерации."
    )
    AD_OR_SERVICE_SENT_MODERATION = (
        "Услуга (объявление) отправлены на модерацию."
    )
    AD_OR_SERVICE_IS_UNDER_MODERATION = (
        "Услуга (объявление) не может быть изменена, т.к. она на модерации."
    )
    SERVICE_OR_AD_CANT_BE_PUBLISHED = "Данная услуга (объявление) не скрыта."
    OBJECT_IS_NOT_PUBLISHED = "Данная услуга (объявление) не опубликована."
    OBJECT_ALREADY_IN_FAVORITES = "Данная услуга (объявление) уже в избраном."
    OBJECT_NOT_IN_FAVORITES = "Данная услуга (объявление) не в избраном."
    OBJECT_PROVIDER_CANT_ADD_TO_FAVORITE = (
        "Вледелец не может добавить свой объект в избранное."
    )
    DELETED_FROM_FAVORITES = "Удалено из избранного."
    MAX_IMAGE_QUANTITY_EXEED = (
        f"Можно добавить только {Limits.MAX_FILE_QUANTITY} фотографий."
    )
    MAX_FILE_SIZE_EXEED = (
        f"Максимальный размер файла - {Limits.MAX_FILE_SIZE} байт."
    )
    COMMENT_ALREADY_EXISTS = (
        "Комментарий от данного пользователя уже существует."
    )
    COMMENTS_BY_PROVIDER_PROHIBITED = (
        "Лицо, оказывающее услуги не может оставлять комментарий."
    )
    COMMENT_ADDED = "Комментарий создан."
    INVALID_PARAMETR = "Параметр должен быть положительным числом."
    VERIFICATION_SUCCESS = "Регистрация подтверждена."
    VERIFICATION_FAILED = "Пользователь не найден."
    TOKEN_EXPIRED = "Токен просрочен."
    WRONG_USERNAME = (
        "Псевдоним должен содержать от 2 до 25 символов и может состоять из"
        " кириллицы, латиницы, цифр, cимволов:"
        " '@', '.', '+', '-', '_' в верхнем или нижнем регистре."
    )
    WRONG_OBJECT_TYPE = "Неверный тип объекта."
    USERNAME_EXISTS = "Пользователь с таким именем уже существует."
    EMAIL_EXISTS = "Пользователь с таким адресом электронной почты существует."
    PHONE_EXISTS = "Пользователь с таким номером телефона существует."
    WRONG_CONTENT = (
        "Изображение должно быть передано в формате base64: "
        "data:<MIME-type>;base64,<data>"
    )
    WRONG_EXTENTION = (
        "Расширение файлов {0} не поддерживается. Разрешенные"
        f" расширения: {', '.join(ALLOWED_IMAGE_FILE_EXTENTIONS)}"
    )
    OBJECT_APPROVED = "Объект одобрен."
    OBJECT_REJECTED = "Объект отклонен."


class SystemMessages(models.TextChoices):
    TELEGRAM_ERROR = "Сообщение об ошибке не отпралено в телеграм."
    SERIALIZER_NOT_FOUND_ERROR = "Не найден тип объекта Избранного."
    AUTOMATIC_COMMENT_MODERATION_FAILED = (
        "К сожалению, Ваш комментарий не прошел автоматическую"
        " модерацию и не может быть опубликован."
    )


class Notifications(models.TextChoices):
    WELCOME = (
        "{0}, приветствуем Вас на нашем сайте! Благодарим, за регистрацию!"
    )
    APPROVE_OBJECT = "Модерация успешно пройдена."
    REJECT_OBJECT = "Модерация не пройдена."


class EmailSubjects(models.TextChoices):
    WELCOME = "Регистрация на сервие Солнечный Екатеринбург"
    PASSWORD_CHANGE = "Сброс пароля на сервисе Солнечный Екатеринбург"


class AdState(models.TextChoices):
    USED = "Б/у"
    NEW = "Новый"
