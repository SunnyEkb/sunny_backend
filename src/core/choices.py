from django.db import models


class Role(models.IntegerChoices):
    ADMIN = 1
    MODERATOR = 2
    USER = 3


class ServicePlace(models.TextChoices):
    HOUSE_CALL = "Выезд"
    OFFICE = "В офисе"
    ON_LINE = "On line"


class APIResponses(models.TextChoices):
    ACCOUNT_IS_INACTIVE = "This account is not active"
    INVALID_TOKEN = "No valid token found in cookie 'refresh_token'"
    INVALID_CREDENTIALS = "Invalid email or password"
    PASSWORD_DO_NOT_MATCH = "Password and confirmation do not match"
    PASSWORD_CHANGED = "Password changed successfully"
    SUCCESS_LOGIN = "Login successfully"
    SUCCESS_LOGOUT = "Logout successfully"
    SUCCESS_TOKEN_REFRESH = "Token refreshed"
    WRONG_PASSWORD = "Wrong password"
    UNAUTHORIZED = "Учетные данные не были предоставлены."


class SystemMessages(models.TextChoices):
    TELEGRAM_ERROR = "Сообщение об ошибке не отпралено в телеграм."


class Notifications(models.TextChoices):
    WELCOME = (
        "{0}, Приветствуем Вас на нашем сайте! Благодарим, за регистрацию!"
    )


class EmailSubjects(models.TextChoices):
    WELCOME = "Регистрация на сервие Солнечный Екатеринбург"
    PASSWORD_CHANGE = "Сброс пароля на сервисе Солнечный Екатеринбург"


class ServiceCategory(models.TextChoices):
    BEAUTY = "Красота и здоровье"
    SPORT = "Спорт"
    PETS = "Домашние животные"
    CHILDREN = "Для детей"
    REPAIR = "Ремонт"
    OTHER = "Другое"
