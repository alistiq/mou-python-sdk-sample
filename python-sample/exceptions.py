class NotFoundError(Exception):
    pass

class NoGrantError(NotFoundError):
    pass

class ChildNotFoundError(NotFoundError):
    pass

class AddressNotFoundError(NotFoundError):
    pass
