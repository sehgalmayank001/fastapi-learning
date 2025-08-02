"""NotAuthorized exception."""

from fastapi import status
from .api_exception import APIException


class NotAuthorized(APIException):
    """Equivalent to Pundit::NotAuthorizedError."""

    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)
