# File: app/core/error_handlers.py
# Description: Global exception handlers

import logging
import traceback
from fastapi import Request
from fastapi.responses import Response

from app.core.exceptions import AppException, AuthException
from app.models.error import ErrorResponse

# Initialize logger
logger = logging.getLogger(__name__)


async def auth_exception_handler(request: Request, exc: AuthException):
    """Handle authentication and authorization exceptions"""
    # Log the exception with auth-specific details
    logger.error(
        f"Auth exception: {exc.message} | Status: {exc.http_status.value} | Path: {request.url.path} | Method: {request.method}"
    )

    error_response = ErrorResponse(
        status=exc.http_status.value,
        message=exc.message
    )
    return Response(
        content=error_response.model_dump_json(),
        status_code=exc.http_status.value,
        media_type="application/json"
    )


async def app_exception_handler(request: Request, exc: AppException):
    """Handle application-specific exceptions"""
    # Log the exception
    logger.error(
        f"Application exception: {exc.message} | Type: {exc.__class__.__name__} | Status: {exc.http_status.value} | Path: {request.url.path} | Method: {request.method}"
    )

    error_response = ErrorResponse(
        status=exc.http_status.value,
        message=exc.message
    )
    return Response(
        content=error_response.model_dump_json(),
        status_code=exc.http_status.value,
        media_type="application/json"
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle any unhandled exceptions"""
    # Get the full exception traceback
    exception_traceback = traceback.format_exception(type(exc), exc, exc.__traceback__)

    # Log the unhandled exception with detailed information
    logger.critical(
        f"Unhandled exception: {str(exc)} | Type: {exc.__class__.__name__} | Path: {request.url.path} | Method: {request.method}\nTraceback: {''.join(exception_traceback)}"
    )

    error_response = ErrorResponse.from_exception(exc)
    return Response(
        content=error_response.model_dump_json(),
        status_code=error_response.status,
        media_type="application/json"
    )


def register_exception_handlers(app):
    """Register all exception handlers with the application"""
    # Register specific exception handlers first (more specific to more general)
    app.add_exception_handler(AuthException, auth_exception_handler)
    app.add_exception_handler(AppException, app_exception_handler)
    # Register general exception handler last
    app.add_exception_handler(Exception, general_exception_handler)
