# File: app/models/storage.py
# Description: Models for storage operations

from typing import Dict, Optional
from pydantic import BaseModel, Field


class UploadUrlRequest(BaseModel):
    """Request model for generating a pre-signed upload URL"""
    key: Optional[str] = Field(None, description="The storage key/path where the file will be stored. If not provided, a random key will be generated.")
    metadata: Optional[Dict[str, str]] = Field(None, description="Optional metadata to store with the file, including content-type and content-size")


class UploadUrlResponse(BaseModel):
    """Response model for a pre-signed upload URL"""
    url: str = Field(..., description="The pre-signed URL to which the file should be uploaded")
    method: str = Field(..., description="The HTTP method to use for the upload (PUT)")
    key: str = Field(..., description="The storage key/path where the file will be stored")
    metadata: Optional[Dict[str, str]] = Field(None, description="Metadata associated with the file, including content-type and content-size")
    expires_in: int = Field(..., description="The number of seconds the URL is valid for")
    public_url: str = Field(..., description="The public URL where the file will be accessible after upload")
