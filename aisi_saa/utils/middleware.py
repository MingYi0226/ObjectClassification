from typing import Union
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from utils.ilogger import logger
from utils.common import auth_key
from utils.schema import APIFailureResponse, ErrorDetails

# Change for Work Item-3775
class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get('X-Api-Key')
        allowed_paths = ["/docs", "/openapi.json"]
        # TODO: authKey should ideally come from a key vault store and not hard-coded in the code
        if request.url.path not in allowed_paths:
            if (origin is None) or (not origin == auth_key):
                logger.error("Incorrect authorization key: Unauthorized")
                status_code = 401
                response = APIFailureResponse(
                    message = "Unauthorized",
                    error_details = ErrorDetails(
                        status_code = status_code,
                        error_message = "Incorrect authorization key"
                    )
                )
                return JSONResponse(response.dict(), status_code=status_code)
        response = await call_next(request)
        return response

async def generic_exception_handler(request: Request, exception: Exception):
    status_code = 500
    try:
        message = exception.message if hasattr(exception, "message") else repr(exception)
        logger.error(message)
    except:
        message = "Internal Server Error"
        logger.error(message)
    response = APIFailureResponse(
        error_details = ErrorDetails(
            status_code = status_code,
            detail = message
        )
    )
    return JSONResponse(response.dict(), status_code=status_code)

async def http_exception_handler(request: Request, exception: HTTPException):
    status_code = exception.status_code
    message = exception.detail
    logger.error(message)
    response = APIFailureResponse(
        error_details = ErrorDetails(
            status_code = status_code,
            detail = message
        )
    )
    return JSONResponse(response.dict(), status_code=status_code)

async def validation_exception_handler(request: Request, exception: Union[RequestValidationError, ValidationError]):
    details = exception.errors()
    error_str = ""
    for idx, error in enumerate(details):
        error_str += f"{error['type']}: {error['msg']} {error['loc']} | "
        if idx == len(details) - 1:
            error_str = error_str[:-2]
    status_code = 422
    response = APIFailureResponse(
        message = "Request validation error",
        error_details = ErrorDetails(
            status_code = status_code,
            detail = error_str
        )
    )
    return JSONResponse(response.dict(), status_code=status_code)