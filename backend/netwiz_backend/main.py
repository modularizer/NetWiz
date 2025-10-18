"""
FastAPI application for PCB Netlist Visualizer + Validator
"""

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import app metadata and configuration
from netwiz_backend.config import settings
from netwiz_backend.database import close_database, init_database
from netwiz_backend.models import ErrorResponse
from netwiz_backend.netlist import netlist_router
from netwiz_backend.system import router as system_router

# Load environment variables
load_dotenv()

# Initialize database (will be called in startup event)

# Create FastAPI app using metadata from __init__.py via settings
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    debug=settings.debug,
    # OpenAPI configuration
    openapi_url="/openapi.json",
    openapi_tags=[
        {
            "name": "netlist",
            "description": "Operations with netlists. Upload, validate, and manage PCB netlist data.",
        },
        {
            "name": "health",
            "description": "Health check endpoints for monitoring service status.",
        },
    ],
)

# Add CORS middleware using settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(netlist_router)
app.include_router(system_router)


# Database lifecycle events
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_database()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database on shutdown"""
    await close_database()


# Root endpoint is now handled by system_router


# OpenAPI schema generation endpoint
@app.get("/openapi.json")
async def get_openapi_schema():
    """
    Get the OpenAPI schema as JSON

    This endpoint returns the complete OpenAPI 3.0 specification for the API,
    including all endpoints, request/response models, and validation rules.
    """
    return app.openapi()


# Note: OpenAPI schema generation is handled by the netwiz-generate-openapi script


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with consistent error format"""
    # Check if this is our custom validation response
    if isinstance(exc.detail, dict) and "validation_result" in exc.detail:
        # Return our custom validation response directly
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail,
        )
    else:
        # Handle regular HTTP exceptions
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=str(exc.detail),
                message=str(exc.detail),
                details={"status_code": exc.status_code},
            ).model_dump(),
        )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions with consistent error format"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="internal_server_error",
            message="An internal server error occurred",
            details={"exception": str(exc)},
        ).model_dump(),
    )


def main():
    """Main entry point for the application"""
    uvicorn.run(
        "netwiz_backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )


if __name__ == "__main__":
    main()
