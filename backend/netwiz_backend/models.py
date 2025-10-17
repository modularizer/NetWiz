from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response model"""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: dict[str, Any] | None = Field(None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment (development/production)")


# Query Parameters


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints"""

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(
        default=10, ge=1, le=100, description="Number of items per page"
    )
