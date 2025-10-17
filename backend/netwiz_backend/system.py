"""
System and health endpoints router

This router contains boilerplate endpoints for:
- Health checks
- System information
- API metadata
- Service status
"""

import os
import signal
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from netwiz_backend.config import settings
from netwiz_backend.models import HealthResponse

# Create system router
router = APIRouter(tags=["system", "health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers

    Returns the current status of the API service including version and environment information.
    This endpoint is used by monitoring systems, load balancers, and health check services.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/")
async def root():
    """
    Root endpoint with basic API information

    Returns general information about the API including version, author, and available endpoints.
    This is typically the first endpoint users encounter when exploring the API.
    """
    return {
        "message": settings.app_name,
        "version": settings.app_version,
        "author": settings.app_author,
        "email": settings.app_email,
        "license": settings.app_license,
        "url": settings.app_url,
        "status": settings.app_status,
        "docs": settings.docs_url,
        "health": "/health",
        "environment": settings.environment,
    }


@router.get("/info")
async def api_info():
    """
    Detailed API information endpoint

    Returns comprehensive information about the API including all available endpoints,
    version details, and service capabilities.
    """
    return {
        "api": {
            "name": settings.app_name,
            "version": settings.app_version,
            "description": settings.app_description,
            "author": settings.app_author,
            "email": settings.app_email,
            "license": settings.app_license,
            "url": settings.app_url,
            "status": settings.app_status,
        },
        "service": {
            "environment": settings.environment,
            "debug": settings.debug,
            "host": settings.host,
            "port": settings.port,
        },
        "endpoints": {
            "documentation": {
                "swagger_ui": settings.docs_url,
                "redoc": settings.redoc_url,
                "openapi_json": "/openapi.json",
            },
            "health": "/health",
            "netlist": {
                "upload": "/api/netlist/upload",
                "list": "/api/netlist",
                "get": "/api/netlist/{submission_id}",
                "validate": "/api/netlist/validate",
            },
        },
    }


@router.post("/kill")
async def kill_server():
    """
    Kill the server (development only)

    This endpoint shuts down the server gracefully. Only available in development mode.
    Useful for testing and development workflows.

    **WARNING**: This will terminate the server process!
    """
    # Only allow in development mode
    if settings.environment != "development":
        raise HTTPException(
            status_code=403,
            detail="Kill endpoint is only available in development mode",
        )

    # Send SIGTERM to the current process
    os.kill(os.getpid(), signal.SIGTERM)

    return {
        "message": "Server shutdown initiated",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.environment,
    }
