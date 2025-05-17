# File: app/infrastructure/storage/base_client.py
# Description: Abstract base class for storage clients

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseStorageClient(ABC):
    """Abstract base class for storage clients"""

    @abstractmethod
    async def delete_file(self, key: str) -> bool:
        """
        Delete a file from storage

        Args:
            key: The storage key/path of the file

        Returns:
            True if the file was deleted, False otherwise
        """
        pass

    @abstractmethod
    async def get_upload_url(
        self,
        key: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Get a pre-signed URL for uploading a file directly to storage using PUT

        Args:
            key: The storage key/path where the file will be stored
            metadata: Optional metadata to store with the file, including content-type and content-size

        Returns:
            A dictionary containing the upload URL and method information
        """
        pass
