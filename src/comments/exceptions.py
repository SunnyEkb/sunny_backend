class WrongObjectType(Exception):
    """Неверный тип объекта."""

    def __init__(self):
        message = "Wrong type of object"
        super().__init__(message)
