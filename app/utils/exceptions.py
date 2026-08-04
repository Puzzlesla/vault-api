
from fastapi import HTTPException, status


class UserAlreadyExistsException(HTTPException):
    """Raised when a user with the given username already exists."""
    def __init__(self, message: str = "User already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)

class InvalidCredentialsException(HTTPException):
    """Raised when an unauthorized user tries to update an account."""
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)

class UserNotFoundException(HTTPException):
    """Raised when a user with the given username is not found."""
    def __init__(self, message: str = "User not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)

class TokenExpiredException(HTTPException):
    """Raised when the provided JWT token has expired."""
    def __init__(self, message: str = "Token expired"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)

class InvalidTokenException(HTTPException):
    """Raised when an invalid token payload is received."""
    def __init__(self, message: str = "Invalid token"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

