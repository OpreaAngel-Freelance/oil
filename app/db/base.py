# File: app/db/base.py
# Description: Database configuration and session management

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create async engine with connection pool settings
database_uri = str(settings.DATABASE_URI)

# Ensure the connection string uses the asyncpg driver if it's a PostgreSQL connection
if database_uri.startswith("postgresql://"):
    database_uri = database_uri.replace("postgresql://", "postgresql+asyncpg://")

# Configure SSL context for secure connections
import ssl

ssl_context = None
if "sslmode=require" in database_uri:
    # Create SSL context that doesn't verify certificates (for self-signed certs)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Remove the sslmode parameter from the URI as it will be handled by connect_args
    database_uri = database_uri.replace("?sslmode=require", "")
    database_uri = database_uri.replace("&sslmode=require", "")

# Create the engine with the appropriate configuration
engine = create_async_engine(
    database_uri,
    echo=settings.SQL_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    connect_args={
        "server_settings": {"application_name": settings.PROJECT_NAME},
        "statement_cache_size": 0,  # Disable statement cache for pgbouncer compatibility
        **({"ssl": ssl_context} if ssl_context else {})
    }
)

# Create thread-safe session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator for database sessions.
    Uses the modern SQLAlchemy 2.0 approach with async context managers.
    The transaction is automatically committed when the context exits normally,
    or rolled back if an exception occurs.

    Following the modern approach, we start a transaction at the request boundary
    and commit/rollback at the end of the request.
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                yield session
            except Exception:
                raise
            finally:
                pass


# Database session dependency
DBSession = Annotated[AsyncSession, Depends(get_db)]
