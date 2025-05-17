# File: app/infrastructure/storage/r2_client.py
# Description: Cloudflare R2 storage client implementation for direct uploads

import asyncio
import logging
import uuid
from typing import Any, Dict, Optional

import boto3
from botocore.client import Config
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.infrastructure.storage.base_client import BaseStorageClient
from app.utils.logging_utils import log_retry_attempt

# Initialize logger
logger = logging.getLogger(__name__)


class R2StorageClient(BaseStorageClient):
    """Cloudflare R2 storage client implementation for direct uploads"""

    def __init__(self):
        """Initialize the R2 client with configuration from settings"""
        self.access_key_id = settings.R2_ACCESS_KEY_ID
        self.secret_access_key = settings.R2_SECRET_ACCESS_KEY
        self.bucket_name = settings.R2_BUCKET_NAME
        self.region = settings.R2_REGION
        self.endpoint_url = settings.R2_ENDPOINT_URL
        self.public_url = settings.R2_PUBLIC_URL
        self.presigned_url_expiration = settings.R2_PRESIGNED_URL_EXPIRATION

        # Initialize boto3 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region,
            config=Config(signature_version='s3v4')
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before=log_retry_attempt("get_upload_url"),
        reraise=True
    )
    async def get_upload_url(
        self,
        key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Get a pre-signed URL for uploading a file directly to R2 storage using PUT"""
        # Generate a unique key if not provided
        if not key:
            key = f"uploads/{uuid.uuid4()}"
        elif not key.startswith("uploads/"):
            key = f"uploads/{key}"

        # Prepare parameters for the presigned URL
        params = {
            'Bucket': self.bucket_name,
            'Key': key,
        }

        # Extract content type from metadata if available
        content_type = None
        if metadata and 'content-type' in metadata:
            content_type = metadata['content-type']
            params['ContentType'] = content_type

        # Add metadata if provided
        if metadata:
            meta_dict = {}
            for key_name, value in metadata.items():
                meta_dict[key_name] = value
            if meta_dict:
                params['Metadata'] = meta_dict

        # Generate the presigned PUT URL using asyncio.to_thread
        url = await asyncio.to_thread(
            self.s3_client.generate_presigned_url,
            ClientMethod='put_object',
            Params=params,
            ExpiresIn=self.presigned_url_expiration
        )

        # Return the presigned URL data
        return {
            'url': url,
            'method': 'PUT',
            'key': key,
            'metadata': metadata,
            'expires_in': self.presigned_url_expiration,
            'public_url': f"{self.public_url}/{key}"
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        before=log_retry_attempt("delete_file"),
        reraise=True
    )
    async def delete_file(self, key: str) -> bool:
        # Use asyncio.to_thread to run the synchronous boto3 operation in a separate thread
        await asyncio.to_thread(
            self.s3_client.delete_object,
            Bucket=self.bucket_name,
            Key=key
        )
        return True
