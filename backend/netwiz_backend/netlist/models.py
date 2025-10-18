"""
Pydantic models for PCB Netlist Validator API

These models define the data structures for:
- Netlist components and nets
- API request/response schemas
- Validation results
"""

from datetime import datetime, timezone

from pydantic import UUID4, BaseModel, Field, constr

from netwiz_backend.netlist.core.models import Netlist
from netwiz_backend.netlist.core.validation import ValidationResult


class NetlistSubmission(BaseModel):
    """Represents a netlist submission with metadata"""

    id: UUID4 = Field(..., description="Unique submission ID")
    netlist: Netlist = Field(..., description="The netlist data")
    user_id: UUID4 | None = Field(None, description="User who submitted the netlist")
    submission_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When the netlist was submitted",
    )
    validation_result: ValidationResult | None = Field(
        None, description="Validation result for this submission"
    )
    filename: constr(strip_whitespace=True) | None = Field(
        None, description="Original filename if uploaded from file"
    )


# API Request/Response Models
class ValidationRequest(BaseModel):
    """Request model for validating a netlist"""

    netlist: Netlist = Field(..., description="The netlist data to validate")


class ValidationResponse(BaseModel):
    """Response model for netlist validation"""

    validation_result: ValidationResult = Field(
        ..., description="The validation result"
    )


class NetlistUploadRequest(BaseModel):
    """Request model for uploading a netlist"""

    netlist: Netlist = Field(..., description="The netlist data to upload")
    user_id: UUID4 | None = Field(None, description="User ID for tracking submissions")
    filename: constr(strip_whitespace=True) | None = Field(
        None, description="Original filename if uploaded from file"
    )


class NetlistUploadResponse(BaseModel):
    """Response model for netlist upload"""

    submission_id: UUID4 = Field(..., description="Unique ID for this submission")
    message: constr(strip_whitespace=True) = Field(..., description="Success message")
    validation_result: ValidationResult = Field(
        ..., description="Validation result for the uploaded netlist"
    )


class NetlistGetResponse(BaseModel):
    """Response model for retrieving a netlist"""

    submission: NetlistSubmission = Field(
        ..., description="The netlist submission data"
    )


class NetlistListResponse(BaseModel):
    """Response model for listing netlists"""

    submissions: list[NetlistSubmission] = Field(
        ..., description="List of netlist submissions"
    )
    total_count: int = Field(..., description="Total number of submissions")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")


class NetlistEndpoints(BaseModel):
    """Netlist endpoints information"""

    upload: constr(strip_whitespace=True) = Field(..., description="Upload endpoint")
    list: constr(strip_whitespace=True) = Field(..., description="List endpoint")
    get: constr(strip_whitespace=True) = Field(..., description="Get endpoint")
    validate: constr(strip_whitespace=True) = Field(
        ..., description="Validate endpoint"
    )
