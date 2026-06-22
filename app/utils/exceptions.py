
from pydantic import Exception


class UserAlreadyExistsException(Exception):
    """Raised when a user with the given username already exists."""
    pass

class InvalidCredentialsException(Exception):
    """Raised when an unauthorized user tries to update an account."""
    pass

class UserNotFoundException(Exception):
    """Raised when a user with the given username is not found."""
    pass

class TokenExpiredException(Exception):
    """Raised when the provided JWT token has expired."""
    pass

