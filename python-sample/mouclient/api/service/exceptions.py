from mouclient.serializable import SerializableObject


class ErrorBody(SerializableObject):
    def __init__(self, error: str, error_description: str = None) -> None:
        self.error = error
        self.error_description = error_description

class MouApiError(Exception):
    def __init__(self, status_code: int, body: ErrorBody) -> None:
        super().__init__(body.error)
        self.status_code = status_code
        self.description = body.error_description
        self.body = body
class UnauthorizedError(Exception):
    pass

class InvalidInputError(Exception):
    pass
class InvalidWebIdError(InvalidInputError):
    pass
