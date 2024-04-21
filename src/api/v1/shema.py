from drf_spectacular.utils import OpenApiExample, OpenApiResponse

from users.serializers import NonErrorFieldSerializer, UserCreateSerializer


USER_CREATE_EXAMPLE = OpenApiExample(
    name="Данные для регистрации",
    value={
        "email": "example@example.com",
        "password": "your-password",
        "confirmation": "your-password",
    },
)

USER_CREATED_EXAMPLE = OpenApiExample(
    name="Пользователь зарегистрирован",
    value={"email": "example@example.com"},
)

PASSWORD_DO_NOT_MATCH = OpenApiExample(
    name="Пароль не соответствует подтверждению",
    value={"non_field_errors": ["the password and confirmation do not match"]},
)

WRONG_EMAIL = OpenApiExample(
    name="Неверная электронаая почта",
    value={"email": ["Введите правильный адрес электронной почты."]},
)

USER_CREATED_201: OpenApiResponse = OpenApiResponse(
    response=UserCreateSerializer,
    description="Пользователь зарегистрирован",
    examples=[USER_CREATED_EXAMPLE],
)

USER_BAD_REQUEST_400: OpenApiResponse = OpenApiResponse(
    response=NonErrorFieldSerializer,
    description="Bad request",
    examples=[PASSWORD_DO_NOT_MATCH, WRONG_EMAIL],
)
