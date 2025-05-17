# File: app/core/exceptions.py
# Description: Custom exceptions for the application

from http import HTTPStatus


class AppException(Exception):
    """Base exception for all application exceptions"""
    def __init__(self, message: str, http_status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR):
        self.message = message
        self.http_status = http_status
        super().__init__(self.message)


class AuthException(AppException):
    """Exception for authentication and authorization errors"""
    def __init__(self, message: str, http_status: HTTPStatus = HTTPStatus.UNAUTHORIZED):
        super().__init__(message=message, http_status=http_status)
