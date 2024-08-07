from enum import IntEnum


class Limits(IntEnum):
    """
    Предельные значения.
    """

    MAX_LENGTH_FIRST_NAME = 50
    MAX_LENGTH_LAST_NAME = 50
    MAX_LENGTH_USER_ROLE = 20
    MAX_LENGTH_PHONE_NUMBER = 12
    MAX_LENGTH_NOTIFICATION_TEXT = 500
    MAX_LENGTH_ADVMNT_TITLE = 250
    MAX_LENGTH_ADVMNT_DESCRIPTION = 500
    MAX_LENGTH_SERVICE_ADDRESS = 250
    MAX_LENGTH_SERVICE_SALON_NAME = 250
    MAX_LENGTH_SERVICE_PLACE = 50
    MAX_LENGTH_ADVMNT_CATEGORY = 50
    MAX_LENGTH_ADVMNT_STATE = 15
    MAX_LENGTH_TYPE_TITLE = 50
    MAXIMUM_EXPERIENCE = 50
    MAX_FILE_SIZE = 5 * 1024 * 1024
    MAX_FILE_QUANTITY = 5
    MAX_RATING = 5
    MIN_RATING = 1
    MAX_COMMENT_TEXT = 500
