"""RecordInvalid exception."""

from fastapi import status
from .api_exception import APIException


class RecordInvalid(APIException):
    """Equivalent to ActiveRecord::RecordInvalid."""

    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)
