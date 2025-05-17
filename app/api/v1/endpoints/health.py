# File: app/api/v1/endpoints/health.py
# Description: Health check endpoints

import logging
from fastapi import APIRouter, status
from pydantic import BaseModel

# Initialize logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    version: str = "1.0.0"


@router.get(
    "/",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the API is up and running"
)
async def healthcheck() -> HealthResponse:
    """
    Perform a health check of the API.
    
    Returns:
        A health response with status "ok" if the API is running
    """
    logger.info("Health check request received")
    return HealthResponse(status="ok")
