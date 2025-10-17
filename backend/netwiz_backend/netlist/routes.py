"""
Core netlist functionality router

This router contains all the core business logic for:
- Netlist upload and validation
- Netlist retrieval and management
- Validation operations
- Submission tracking
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.core import AgnosticDatabase

from netwiz_backend.database import get_database
from netwiz_backend.models import PaginationParams
from netwiz_backend.netlist.core.validation import (
    validate_netlist_internal,
)
from netwiz_backend.netlist.models import (
    NetlistGetResponse,
    NetlistListResponse,
    NetlistSubmission,
    NetlistUploadRequest,
    NetlistUploadResponse,
    ValidationRequest,
    ValidationResponse,
)
from netwiz_backend.netlist.repository import get_netlist_repository
from netwiz_backend.tools import get_pagination_params

# Create core netlist router
router = APIRouter(prefix="/api/netlist", tags=["netlist"])

# MongoDB storage via repository


@router.post(
    "/upload", response_model=NetlistUploadResponse, status_code=status.HTTP_201_CREATED
)
async def upload_netlist(
    request: NetlistUploadRequest, database: AgnosticDatabase = Depends(get_database)
):
    """
    Upload and validate a netlist

    This endpoint accepts a netlist in JSON format, validates it according to business rules,
    and stores it in the database. The validation result is returned immediately.

    **Validation Rules:**
    - Component names must not be blank
    - Net names must not be blank
    - All component IDs must be unique
    - All net IDs must be unique
    - GND net must be connected to all relevant components
    - Each net must have at least one connection
    """
    try:
        # Generate unique submission ID
        submission_id = str(uuid.uuid4())

        # Perform validation
        validation_result = validate_netlist_internal(request.netlist)

        # Create submission record
        submission = NetlistSubmission(
            id=submission_id,
            netlist=request.netlist,
            user_id=request.user_id,
            filename=request.filename,
            validation_result=validation_result,
        )

        # Store in MongoDB using dependency injection
        repository = get_netlist_repository(database)
        await repository.create(submission)

        return NetlistUploadResponse(
            submission_id=submission_id,
            message="Netlist uploaded and validated successfully",
            validation_result=validation_result,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to upload netlist: {e!s}",
        ) from e


@router.get("/{submission_id}", response_model=NetlistGetResponse)
async def get_netlist(
    submission_id: str, database: AgnosticDatabase = Depends(get_database)
):
    """
    Retrieve a specific netlist submission by ID

    Returns the complete netlist submission data including the original netlist,
    validation results, and metadata.
    """
    # Find submission in MongoDB using dependency injection
    repository = get_netlist_repository(database)
    submission_doc = await repository.get_by_id(submission_id)

    if not submission_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Netlist submission with ID '{submission_id}' not found",
        )

    # Convert MongoDB document to NetlistSubmission
    submission = NetlistSubmission(**submission_doc)
    return NetlistGetResponse(submission=submission)


@router.get("", response_model=NetlistListResponse)
async def list_netlists(
    pagination: PaginationParams = Depends(get_pagination_params),
    database: AgnosticDatabase = Depends(get_database),
    user_id: str | None = Query(None, description="Filter by user ID"),
):
    """
    List netlist submissions with pagination

    Returns a paginated list of netlist submissions. Can be filtered by user ID
    and supports pagination for large result sets.
    """
    # Get submissions from MongoDB using dependency injection
    repository = get_netlist_repository(database)

    if user_id:
        # Filter by user_id
        submissions_docs = await repository.list_by_user(user_id, pagination.page_size)
        total_count = await repository.count_by_user(user_id)
    else:
        # Get all submissions
        submissions_docs = await repository.list_all(pagination.page_size)
        total_count = await repository.count()

    # Convert MongoDB documents to NetlistSubmission objects
    submissions = [NetlistSubmission(**doc) for doc in submissions_docs]

    return NetlistListResponse(
        submissions=submissions,
        total_count=total_count,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.post("/validate", response_model=ValidationResponse)
async def validate_netlist(request: ValidationRequest) -> ValidationResponse:
    """
    Validate a netlist without storing it

    This endpoint performs validation on a netlist without storing it in the database.
    Useful for real-time validation in frontend applications.
    """
    try:
        validation_result = validate_netlist_internal(request.netlist)
        return ValidationResponse(validation_result=validation_result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Validation failed: {e!s}"
        ) from e
