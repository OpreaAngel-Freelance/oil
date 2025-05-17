# File: app/api/v1/endpoints/oil.py
# Description: API endpoints for Oil resources with OAuth protection

import logging
import uuid

from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from fastapi_pagination.cursor import CursorPage, CursorParams

from app.core.dependencies import OilServiceDep
from app.core.security import has_role
from app.models.auth import JWTTokenData
from app.models.oil import OilResourceCreate, OilResourceResponse, OilResourceUpdate
from app.models.storage import UploadUrlRequest, UploadUrlResponse

# Initialize logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/oil", tags=["oil"])


@router.post(
    "/",
    response_model=OilResourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Oil Resource",
    description="Create a new oil resource with date, price, type, and optional document URL information (requires ROLE_ADMIN)"
)
async def create_oil(
    oil_data: OilResourceCreate,
    oil_service: OilServiceDep,
    token_data: JWTTokenData = Depends(has_role("ROLE_ADMIN"))
) -> OilResourceResponse:
    """Create a new oil resource (requires ROLE_ADMIN)"""
    logger.info(f"Create oil resource request received, date: {oil_data.date}, price: {oil_data.price}")

    # Delegate to the service layer, passing the user ID and email from the token
    oil_resource = await oil_service.create_oil(
        oil_data,
        user_id=token_data.sub,
        email=token_data.email
    )

    return oil_resource


@router.get(
    "/",
    response_model=CursorPage[OilResourceResponse],
    summary="Get All Oil Resources",
    description="Retrieve oil resources from the database with pagination (requires ROLE_USER)"
)
async def get_all_oil(
    oil_service: OilServiceDep,
    params: CursorParams = Depends(),
    _: JWTTokenData = Depends(has_role("ROLE_USER"))
) -> CursorPage[OilResourceResponse]:
    """Get oil resources with cursor-based pagination (requires ROLE_USER)"""
    logger.info(f"Get oil resources request received with params: {params}")

    # Delegate to the service layer
    return await oil_service.get_all_oil(params)


@router.get(
    "/{oil_id}",
    response_model=OilResourceResponse,
    summary="Get Oil Resource",
    description="Retrieve a single oil resource by its ID (requires ROLE_USER)"
)
async def get_oil(
    oil_id: uuid.UUID,
    oil_service: OilServiceDep,
    _: JWTTokenData = Depends(has_role("ROLE_USER"))
) -> OilResourceResponse:
    """Get a single oil resource by ID (requires ROLE_USER)"""
    logger.info(f"Get oil resource request received, ID: {oil_id}")

    # Delegate to the service layer
    oil_resource = await oil_service.get_oil(oil_id)

    return oil_resource


@router.put(
    "/{oil_id}",
    response_model=OilResourceResponse,
    summary="Update Oil Resource",
    description="Update an existing oil resource by its ID with date, price, type, and/or document URL information (requires ROLE_ADMIN)"
)
async def update_oil(
    oil_id: uuid.UUID,
    oil_data: OilResourceUpdate,
    oil_service: OilServiceDep,
    _: JWTTokenData = Depends(has_role("ROLE_ADMIN"))
) -> OilResourceResponse:
    """Update an existing oil resource (requires ROLE_ADMIN)"""
    logger.info(f"Update oil resource request received, ID: {oil_id}, date: {oil_data.date}, price: {oil_data.price}")

    # Delegate to the service layer
    updated_oil = await oil_service.update_oil(oil_id, oil_data)

    return updated_oil


@router.delete(
    "/{oil_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Oil Resource",
    description="Delete an oil resource by its ID (requires ROLE_ADMIN)"
)
async def delete_oil(
    oil_id: uuid.UUID,
    oil_service: OilServiceDep,
    _: JWTTokenData = Depends(has_role("ROLE_ADMIN"))
) -> None:
    """Delete an oil resource (requires ROLE_ADMIN)"""
    logger.info(f"Delete oil resource request received, ID: {oil_id}")

    # Delegate to the service layer
    await oil_service.delete_oil(oil_id)

    # Return 204 No Content (handled by FastAPI based on the status_code)


@router.post(
    "/upload-url",
    response_model=UploadUrlResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Pre-signed Upload URL (Admin Only)",
    description="Generate a pre-signed URL for direct file uploads to storage (requires ROLE_ADMIN)"
)
async def generate_upload_url(
    upload_request: UploadUrlRequest,
    oil_service: OilServiceDep,
    _: JWTTokenData = Depends(has_role("ROLE_ADMIN"))
) -> UploadUrlResponse:
    """
    Generate a pre-signed URL for uploading a file directly to storage.
    This endpoint is restricted to users with ROLE_ADMIN.
    """

    # Log the incoming request
    logger.info(f"Generate upload URL request received, key: {upload_request.key}")

    # Delegate to the service layer
    upload_data = await oil_service.generate_upload_url(upload_request)

    return UploadUrlResponse(**upload_data)