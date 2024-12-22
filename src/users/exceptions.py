class TokenDoesNotExists(Exception):
    def __init__(self):
        message = "Token not found"
        super().__init__(message)
