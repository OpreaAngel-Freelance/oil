# File: app/services/oil_service.py
# Description: Service for Oil resources business logic

import logging
import uuid
from http import HTTPStatus
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select

from app.core.exceptions import AppException
from app.infrastructure.storage.base_client import BaseStorageClient
from app.models.oil import OilResource, OilResourceCreate, OilResourceUpdate
from app.models.storage import UploadUrlRequest
from app.repositories.oil_repository import OilRepository

# Initialize logger
logger = logging.getLogger(__name__)


class OilService:
    """Service for Oil resources"""

    def __init__(self, repository: OilRepository, storage_client: Optional[BaseStorageClient] = None):
        self.repository = repository
        self.storage_client = storage_client

    async def get_oil(self, oil_id: uuid.UUID) -> OilResource:
        """
        Get a single oil resource by ID.

        Args:
            oil_id: The ID of the oil resource to retrieve

        Returns:
            The oil resource

        Raises:
            AppException: If the oil resource is not found (with NOT_FOUND status)
        """
        oil = await self.repository.get(oil_id)
        if not oil:
            raise AppException(f"Oil resource with ID {oil_id} not found", http_status=HTTPStatus.NOT_FOUND)
        logger.info(f"Retrieved oil resource with ID: {oil_id}")
        return oil

    async def get_all_oil(self, params):
        """
        Get all oil resources with pagination.

        Args:
            params: Pagination parameters from fastapi-pagination

        Returns:
            Paginated response with oil resources
        """
        # Create a select query for oil resources
        query = select(self.repository.model_class).order_by(self.repository.model_class.id)

        # Use fastapi-pagination's paginate function
        result = await paginate(self.repository.db, query, params=params)

        logger.info(f"Retrieved {len(result.items)} oil resources (paginated, total: {result.total})")

        return result

    async def generate_upload_url(self, request: UploadUrlRequest) -> Dict[str, Any]:
        """
        Generate a pre-signed URL for uploading a file directly to storage.

        Args:
            request: The upload URL request containing key and metadata

        Returns:
            A dictionary containing the upload URL and related information

        Raises:
            AppException: If there's an error generating the upload URL
        """
        try:
            upload_data = await self.storage_client.get_upload_url(
                key=request.key if request.key else "",
                metadata=request.metadata
            )
            logger.info(f"Generated upload URL: {upload_data['url']}")
            return upload_data
        except Exception as e:
            raise AppException(str(e), http_status=HTTPStatus.INTERNAL_SERVER_ERROR) from e


    async def create_oil(self, oil_data: OilResourceCreate, user_id: str, email: str) -> OilResource:
        """
        Create a new oil resource.

        Args:
            oil_data: The data for the new oil resource
            user_id: The ID of the user creating the resource (from JWT token)
            email: The email of the user creating the resource (from JWT token)

        Returns:
            The created oil resource
        """
        # Convert the model to a dictionary and add the userId and email
        oil_dict = oil_data.model_dump()
        oil_dict["userId"] = user_id
        oil_dict["email"] = email

        # Create the resource with the userId and email included
        oil_resource = await self.repository.create_from_dict(oil_dict)
        logger.info(f"Created new oil resource with ID: {oil_resource.id}, date: {oil_resource.date}, userId: {oil_resource.userId}, email: {oil_resource.email}")
        return oil_resource

    async def update_oil(self, oil_id: uuid.UUID, oil_data: OilResourceUpdate) -> OilResource:
        """
        Update an existing oil resource.

        Args:
            oil_id: The ID of the oil resource to update
            oil_data: The updated data for the oil resource (fields can be None to indicate no change)

        Returns:
            The updated oil resource

        Raises:
            AppException: If the oil resource is not found (with NOT_FOUND status)
        """
        # Filter out None values to only update provided fields
        update_data = {k: v for k, v in oil_data.model_dump().items() if v is not None}

        # Perform update with the filtered data (partial update)
        updated_oil = await self.repository.update(oil_id, update_data)
        if not updated_oil:
            raise AppException(f"Oil resource with ID {oil_id} not found", http_status=HTTPStatus.NOT_FOUND)

        logger.info(f"Updated oil resource with ID: {oil_id}")
        return updated_oil

    async def delete_oil(self, oil_id: uuid.UUID) -> bool:
        """
        Delete an oil resource and its associated document file if it exists.

        Args:
            oil_id: The ID of the oil resource to delete

        Returns:
            True if the resource was deleted, False otherwise

        Raises:
            AppException: If the oil resource is not found (with NOT_FOUND status)
        """
        # First, get the oil resource to check if it has an associated document
        oil_resource = await self.repository.get(oil_id)
        if not oil_resource:
            raise AppException(f"Oil resource with ID {oil_id} not found", http_status=HTTPStatus.NOT_FOUND)

        # Delete the oil resource from the database
        await self.repository.delete(oil_id)

        # If the oil resource has an associated document, delete it from storage
        if oil_resource.oil_document_url:
            try:
                # Extract the key from the URL
                parsed_url = urlparse(oil_resource.oil_document_url)
                # The path component without the leading slash is the key
                key = parsed_url.path.lstrip('/')

                # Delete the file from storage directly using the storage client
                await self.storage_client.delete_file(key)
                logger.info(f"Deleted associated document file with key: {key}")
            except Exception as e:
                raise AppException(str(e), http_status=HTTPStatus.INTERNAL_SERVER_ERROR) from e

        logger.info(f"Deleted oil resource with ID: {oil_id}")
        return True
