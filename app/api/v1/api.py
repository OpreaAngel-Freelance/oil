# File: app/api/v1/api.py
# Description: API router for v1 endpoints

from fastapi import APIRouter

from app.api.v1.endpoints import oil, health

# Create v1 router
api_router = APIRouter()

# Include resource routers
api_router.include_router(oil.router)
api_router.include_router(health.router)