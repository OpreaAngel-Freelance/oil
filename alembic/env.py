# File: alembic/env.py
# Description: Alembic environment configuration

import os
from logging.config import fileConfig
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, pool
from sqlmodel import SQLModel

from alembic import context

# Import all SQLModel models so Alembic can detect them
from app.models.oil import OilResource

# Load environment variables from .env file
dotenv_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path, override=True)

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get database URI from environment
database_uri = os.environ.get("DATABASE_URI")
if not database_uri:
    print("WARNING: DATABASE_URI not found in environment")
    exit(1)

# Set URI for Alembic operations
config.set_main_option("sqlalchemy.url", database_uri)

# Models metadata for autogenerate support
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode for generation."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )
    
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # psycopg2 includes SSL via the connection string, not connect_args
    # No need to modify - "sslmode=require" is already in the connection string
    
    # Using standard synchronous engine for Alembic
    connectable = create_engine(database_uri, poolclass=pool.NullPool)
    
    with connectable.connect() as connection:
        do_run_migrations(connection)
            
    connectable.dispose()

# Run migrations based on mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()