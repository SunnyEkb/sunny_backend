from core.choices import SystemMessages


class SerializerNotFoundError(Exception):
    """Сериализатор не найден."""

    def __init__(self) -> None:
        """Инициализация экземпляря класса."""
        message = SystemMessages.SERIALIZER_NOT_FOUND_ERROR
        super().__init__(message)
