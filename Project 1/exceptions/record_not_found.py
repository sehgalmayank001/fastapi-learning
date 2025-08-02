"""RecordNotFound exception."""

from typing import Any
from fastapi import status
from .api_exception import APIException


class RecordNotFound(APIException):
    """Equivalent to ActiveRecord::RecordNotFound."""

    def __init__(self, resource: str, identifier: Any):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)
