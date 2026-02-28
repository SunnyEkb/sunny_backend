class TokenDoesNotExistsError(Exception):
    """Токен не найден."""

    def __init__(self) -> None:
        """Инициализация экземпляра класса."""
        message = "Token not found"
        super().__init__(message)


class TokenExpiredError(Exception):
    """Токен просрочен."""

    def __init__(self) -> None:
        """Инициализация экземпляра класса."""
        message = "Token expired"
        super().__init__(message)
