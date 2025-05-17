# File: app/models/error.py
# Description: Error response model

from pydantic import BaseModel
from http import HTTPStatus


class ErrorResponse(BaseModel):
    status: int
    message: str

    @classmethod
    def from_exception(cls, exception: Exception, status: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR):
        if hasattr(exception, 'http_status'):
            status = exception.http_status
        return cls(
            status=status.value,
            message=str(exception)
        )