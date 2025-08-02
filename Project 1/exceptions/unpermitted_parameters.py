"""UnpermittedParameters exception."""

from .api_exception import APIException


class UnpermittedParameters(APIException):
    """Equivalent to ActionController::UnpermittedParameters."""

    def __init__(self, params: list):
        self.params = params
        message = f"Unpermitted parameters: {', '.join(params)}"
        super().__init__(message, 400)
