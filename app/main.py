# File: app/main.py
# Description: Main FastAPI application

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.error_handlers import register_exception_handlers

# Initialize logger
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    # Configure logging using explicit log level from settings
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    application = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
    )

    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        # In production, restrict origins to your frontend domains
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    # Register exception handlers
    register_exception_handlers(application)

    # Include API router
    application.include_router(api_router, prefix=settings.API_PREFIX)

    # Add pagination
    add_pagination(application)

    return application


app = create_application()


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint, redirects to API documentation"""
    return {"message": f"Welcome to {settings.PROJECT_NAME}. Visit {settings.API_PREFIX}/docs for API documentation."}