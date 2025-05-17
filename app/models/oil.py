import uuid
from datetime import date as DateType
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class OilType(str, Enum):
    """Enum for oil types"""
    PETROL = "PETROL"
    DIESEL = "DIESEL"
    GAS = "GAS"


# Database model
class OilResource(SQLModel, table=True):
    """Oil resource database model"""
    __tablename__ = "oil_resources"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    date: DateType = Field(index=True, description="The date of the oil price record")
    price: float = Field(ge=0, description="The price of the oil resource")
    type: OilType = Field(default=OilType.PETROL, description="The type of oil resource")
    oil_document_url: Optional[str] = Field(default=None, description="URL to the oil document stored in cloud storage")
    userId: Optional[str] = Field(default=None, index=True, description="ID of the user who created the resource")
    email: Optional[str] = Field(default=None, index=True, description="Email of the user who created the resource")
    created_at: datetime = Field(
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False
        )
    )
    updated_at: datetime = Field(
        sa_column=sa.Column(
            sa.DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            nullable=False
        )
    )


# API models
class OilResourceBase(SQLModel):
    """Base model for Oil resources"""
    date: DateType = Field(description="The date of the oil price record")
    price: float = Field(ge=0, description="The price of the oil resource")
    type: OilType = Field(default=OilType.PETROL, description="The type of oil resource")
    oil_document_url: Optional[str] = Field(None, description="URL to the oil document stored in cloud storage")


class OilResourceCreate(OilResourceBase):
    """Model for creating Oil resources"""
    pass


class OilResourceUpdate(OilResourceBase):
    """Model for updating Oil resources with optional fields"""
    date: Optional[DateType] = Field(None, description="The date of the oil price record")
    price: Optional[float] = Field(None, ge=0, description="The price of the oil resource")
    type: Optional[OilType] = Field(None, description="The type of oil resource")


class OilResourceResponse(OilResourceBase):
    """Model for Oil resource response"""
    id: uuid.UUID
    userId: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
