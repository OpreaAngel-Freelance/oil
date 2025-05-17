# File: app/repositories/base_repository.py
# Description: Base repository for data access

from typing import Any, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """Base class for all repositories"""

    def __init__(self, db_session: AsyncSession, model_class: Type[ModelType]):
        self.db = db_session
        self.model_class = model_class

    async def get(self, id: Any) -> Optional[ModelType]:
        """Get a resource by ID"""
        query = select(self.model_class).where(self.model_class.id == id)
        result = await self.db.execute(query)
        resource = result.scalar_one_or_none()
        return resource

    async def get_all(self) -> List[ModelType]:
        """Get all resources"""
        query = select(self.model_class)
        result = await self.db.execute(query)
        resources = result.scalars().all()
        return resources

    # The get_paginated method has been removed in favor of using fastapi-pagination directly in the service layer

    async def create(self, obj_in: BaseModel) -> ModelType:
        """Create a new resource"""
        obj_data = obj_in.model_dump()
        return await self.create_from_dict(obj_data)

    async def create_from_dict(self, obj_data: dict) -> ModelType:
        """Create a new resource from a dictionary"""
        db_obj = self.model_class(**obj_data)

        # No need to use begin() as transaction is managed at the request boundary
        self.db.add(db_obj)

        # Flush to get the ID without committing the transaction
        await self.db.flush()

        # Refresh to get the latest data
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: Any, obj_in: BaseModel | dict) -> Optional[ModelType]:
        """
        Update a resource. Supports both full updates with a Pydantic model and partial updates with a dict.

        Args:
            id: The ID of the resource to update
            obj_in: Either a Pydantic model for full update or a dict for partial update

        Returns:
            The updated resource or None if not found
        """
        db_obj = await self.get(id)
        if not db_obj:
            return None

        # Convert input to dictionary based on its type
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump()

        # Only update if there are fields to update
        if update_data:
            query = (
                update(self.model_class)
                .where(self.model_class.id == id)
                .values(**update_data)
                .execution_options(synchronize_session="fetch")
            )

            # No need to use begin() as transaction is managed at the request boundary
            await self.db.execute(query)

            # Flush to ensure the changes are visible
            await self.db.flush()

            # Refresh to get the latest data
            await self.db.refresh(db_obj)

            # No logging needed

        return db_obj

    async def delete(self, id: Any) -> bool:
        """Delete a resource"""
        db_obj = await self.get(id)
        if not db_obj:
            return False

        query = (
            delete(self.model_class)
            .where(self.model_class.id == id)
            .execution_options(synchronize_session="fetch")
        )

        # No need to use begin() as transaction is managed at the request boundary
        await self.db.execute(query)

        # Flush to ensure the changes are visible
        await self.db.flush()

        return True
