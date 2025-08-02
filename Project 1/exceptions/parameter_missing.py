"""ParameterMissing exception."""

from fastapi import status
from .api_exception import APIException


class ParameterMissing(APIException):
    """Equivalent to ParameterMissing."""

    def __init__(self, param: str):
        self.param = param
        message = f"Parameter '{param}' is required"
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)
