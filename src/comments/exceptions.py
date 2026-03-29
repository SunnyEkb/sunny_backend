class WrongObjectTypeError(Exception):
    """Неверный тип объекта."""

    def __init__(self) -> None:
        """Инициация экземпляра класса."""
        message = "Wrong type of object"
        super().__init__(message)
