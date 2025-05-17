# File: app/core/dependencies.py
# Description: Application dependencies

from typing import Annotated
from fastapi import Depends

from app.db.base import DBSession
from app.infrastructure.storage.base_client import BaseStorageClient
from app.infrastructure.storage.r2_client import R2StorageClient
from app.repositories.oil_repository import OilRepository
from app.services.oil_service import OilService


# Repository dependencies
def get_oil_repository(db: DBSession) -> OilRepository:
    """Get the Oil repository instance"""
    return OilRepository(db)

# Storage dependencies
def get_storage_client() -> BaseStorageClient:
    """Get the storage client instance"""
    return R2StorageClient()

# Service dependencies
def get_oil_service(
    repo: Annotated[OilRepository, Depends(get_oil_repository)],
    storage_client: Annotated[BaseStorageClient, Depends(get_storage_client)]
) -> OilService:
    """Get the Oil service instance with storage client for file operations"""
    return OilService(repo, storage_client)


# Type annotations for all dependencies - consistent pattern
OilRepositoryDep = Annotated[OilRepository, Depends(get_oil_repository)]
StorageClientDep = Annotated[BaseStorageClient, Depends(get_storage_client)]
OilServiceDep = Annotated[OilService, Depends(get_oil_service)]