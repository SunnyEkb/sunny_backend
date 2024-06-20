from enum import IntEnum


class Limits(IntEnum):
    """
    Предельные значения.
    """

    MAX_LENGTH_FIRST_NAME = 50
    MAX_LENGTH_LAST_NAME = 50
    MAX_LENGTH_PHONE_NUMBER = 12
    MAX_LENGTH_NOTIFICATION_TEXT = 500
    MAX_LENGTH_SERVICE_TITLE = 250
    MAX_LENGTH_SERVICE_DESCRIPTION = 500
    MAX_LENGTH_SERVICE_PLACE = 50
    MAX_LENGTH_SERVICE_CATEGORY = 50
    MAX_LENGTH_TYPE_TITLE = 50
    MAXIMUM_EXPERIENCE = 50
