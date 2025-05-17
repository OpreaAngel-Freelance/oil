# File: app/repositories/oil_repository.py
# Description: Repository for Oil resources

import logging
from typing import List
from sqlalchemy import select

from app.core.dependencies import DBSession
from app.models.oil import OilResource
from app.repositories.base_repository import BaseRepository

# Initialize logger
logger = logging.getLogger(__name__)

class OilRepository(BaseRepository[OilResource]):
    """Repository for Oil resources"""

    def __init__(self, db: DBSession):
        super().__init__(db, OilResource)

    async def get_by_date(self, date_value: str) -> List[OilResource]:
        """Get oil resources by date"""
        query = select(OilResource).where(OilResource.date == date_value)
        result = await self.db.execute(query)
        resources = result.scalars().all()
        return resources
