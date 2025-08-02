"""Rails-style rescue_from handlers."""

import traceback

from api_response import json_response
from exceptions import (
    RecordNotFound,
    RecordInvalid,
    UnpermittedParameters,
    ParameterMissing,
)
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError


def error_formatting(msg: str) -> str:
    """Format error messages (equivalent to Rails error_formatting)."""
    return msg.replace("Blueprint", "").strip()


def setup_exception_handlers(app: FastAPI):
    """Setup Rails-style rescue_from handlers."""

    @app.exception_handler(RecordNotFound)
    async def rescue_from_record_not_found(_request: Request, exc: RecordNotFound):
        return json_response(
            {"errors": {"message": exc.message}}, status=exc.status_code
        )

    @app.exception_handler(RecordInvalid)
    async def rescue_from_record_invalid(_request: Request, exc: RecordInvalid):
        return json_response(
            {"errors": {"message": exc.message}}, status=exc.status_code
        )

    @app.exception_handler(UnpermittedParameters)
    async def rescue_from_unpermitted_parameters(
        _request: Request, exc: UnpermittedParameters
    ):
        return json_response(
            {"errors": {"unknown_parameters": exc.params}}, status=exc.status_code
        )

    @app.exception_handler(ParameterMissing)
    async def rescue_from_parameter_missing(_request: Request, exc: ParameterMissing):
        error = {exc.param: ["parameter is required"]}
        return json_response({"errors": error}, status=status.HTTP_400_BAD_REQUEST)

    @app.exception_handler(RequestValidationError)
    async def rescue_from_validation_error(
        _request: Request, exc: RequestValidationError
    ):
        errors = {}
        for error in exc.errors():
            field = ".".join(
                str(loc) for loc in error["loc"][1:]
            )  # Skip 'path'/'query'
            errors[field] = [error["msg"]]
        return json_response(
            {"errors": errors}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    @app.exception_handler(ValueError)
    async def rescue_from_argument_error(_request: Request, exc: ValueError):
        return json_response(
            {"errors": {"message": str(exc)}}, status=status.HTTP_400_BAD_REQUEST
        )

    @app.exception_handler(Exception)
    async def rescue_from_general_exception(_request: Request, _exc: Exception):
        # Log the full traceback for debugging
        print(f"Unhandled exception: {traceback.format_exc()}")

        return json_response(
            {"errors": {"message": "Internal server error"}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
