from typing import Any

from pydantic import BaseModel, Field, constr

# Response Models


class ErrorResponse(BaseModel):
    """Standard error response model"""

    error: constr(strip_whitespace=True) = Field(..., description="Error type")
    message: constr(strip_whitespace=True) = Field(
        ..., description="Human-readable error message"
    )
    details: dict[str, Any] | None = Field(
        default=None, description="Additional error details"
    )


# Query Parameters


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints"""

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(
        default=10, ge=1, le=100, description="Number of items per page"
    )


class PaginatedResponse(BaseModel):
    """Response model for listing netlists"""

    total_count: int = Field(..., description="Total number of submissions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
