from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, constr

# Response Models


class ErrorResponse(BaseModel):
    """Standard error response model"""

    error: constr(strip_whitespace=True) = Field(..., description="Error type")
    message: constr(strip_whitespace=True) = Field(
        ..., description="Human-readable error message"
    )
    details: dict[str, Any] | None = Field(None, description="Additional error details")


class HealthResponse(BaseModel):
    """Health check response model"""

    status: constr(strip_whitespace=True) = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: constr(strip_whitespace=True) = Field(..., description="API version")
    environment: constr(strip_whitespace=True) = Field(
        ..., description="Environment (development/production)"
    )


# Query Parameters


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints"""

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(
        default=10, ge=1, le=100, description="Number of items per page"
    )
