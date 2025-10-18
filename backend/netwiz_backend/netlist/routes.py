"""
Core netlist functionality router

This router contains all the core business logic for:
- Netlist upload and validation
- Netlist retrieval and management
- Validation operations
- Submission tracking
"""

import uuid

import pydantic_core
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.requests import Request as FastAPIRequest
from fastapi.responses import JSONResponse
from motor.core import AgnosticDatabase
from pydantic import UUID4

from netwiz_backend.database import get_database
from netwiz_backend.json_tracker import TrackedJson, TrackedJSONDecodeError
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
)
from netwiz_backend.netlist.repository import get_netlist_repository
from netwiz_backend.tools import get_pagination_params

# Create core netlist router
router = APIRouter(prefix="/netlist", tags=["netlist"])


async def get_raw_json(request: FastAPIRequest) -> str:
    """Get raw JSON text from request, bypassing Pydantic validation"""
    body = await request.body()
    return body.decode("utf-8")


async def get_unvalidated_request(request: FastAPIRequest) -> ValidationRequest:
    """Get ValidationRequest with custom pre-validation"""

    from netwiz_backend.netlist.core.validation import (
        ValidationError,
        ValidationErrorType,
        ValidationHTTPError,
    )

    body = await request.body()
    json_text = body.decode("utf-8")

    # Step 1: Parse JSON using TrackedJson (primary and only JSON parser)
    try:
        tracked_json = TrackedJson.loads(json_text, raise_on_error=True)
        data = tracked_json.data
    except TrackedJSONDecodeError as e:
        # JSON syntax error - TrackedJson provides detailed location info
        raise ValidationHTTPError(
            validation_errors=[
                ValidationError(
                    message=f"JSON syntax error: {e.msg}",
                    error_type=ValidationErrorType.INVALID_JSON,
                    location=e.error_loc,
                )
            ],
            applied_rules=[ValidationErrorType.INVALID_JSON],
        ) from e
    except Exception as e:
        # Unexpected error during JSON parsing
        raise ValidationHTTPError(
            validation_errors=[
                ValidationError(
                    message=f"Unexpected error parsing JSON: {e!s}",
                    error_type=ValidationErrorType.INVALID_JSON,
                    location=None,
                )
            ],
            applied_rules=[ValidationErrorType.INVALID_JSON],
        ) from e

    # Step 2: Check if data is a dict
    if not isinstance(data, dict):
        raise ValidationHTTPError(
            validation_errors=[
                ValidationError(
                    message="Request data must be an object",
                    error_type=ValidationErrorType.INVALID_JSON,
                    location=None,
                )
            ],
            applied_rules=[ValidationErrorType.INVALID_JSON],
        )

    missing_field_validation_errors = []
    for f in ["components", "nets"]:
        if f not in data:
            missing_field_validation_errors.append(
                ValidationError(
                    message=f"Missing required field: {f}",
                    error_type=ValidationErrorType.MISSING_FIELD,
                    location=None,
                )
            )

    if missing_field_validation_errors:
        raise ValidationHTTPError(
            validation_errors=missing_field_validation_errors,
            applied_rules=[ValidationErrorType.MISSING_FIELD],
        )

    # Step 7: Now that basic structure is validated, we already have tracked_json
    # from the initial parsing step above

    # print("parsed", parse_result)
    # Create Netlist object using the validated data
    from netwiz_backend.netlist.core.models import Netlist

    try:
        netlist_obj = Netlist(**data)
    except pydantic_core.ValidationError as e:
        validation_errors = []
        for pydantic_error in e.errors():
            msg = pydantic_error["msg"]
            path: list[str | int] = list(pydantic_error["loc"])

            # Convert Pydantic path to TrackedJson path format
            # Pydantic paths are like ['components', 0, 'name']
            # TrackedJson paths are like "$.components.0.name"
            location_info = None
            if tracked_json:
                try:
                    # Try progressively removing the last part of the path
                    for i in range(len(path), 0, -1):
                        partial_path = path[:i]
                        location_key = "$." + ".".join(str(p) for p in partial_path)

                        if location_key in tracked_json.locations:
                            loc = tracked_json.locations[location_key]
                            location_info = loc
                            print(
                                f"Found location for path {path} at partial path {partial_path}: {location_info}"
                            )
                            break
                except Exception as e:
                    print(f"Error finding location for path {path}: {e}")

            if not location_info:
                print(f"No location found for path {path}")

            validation_errors.append(
                ValidationError(
                    message=msg,
                    error_type=ValidationErrorType.INVALID_FORMAT,
                    location=location_info,
                )
            )

        raise ValidationHTTPError(
            validation_errors=validation_errors,
            applied_rules=[ValidationErrorType.INVALID_FORMAT],
        ) from e

    # Create ValidationRequest without validation
    return ValidationRequest(netlist=netlist_obj)


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
    user_id: UUID4 | None = Query(default=None, description="Filter by user ID"),
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


@router.post("/validate")
async def validate_netlist(
    request: ValidationRequest = Depends(get_unvalidated_request)
) -> JSONResponse:
    """
    Validate a netlist without storing it

    This endpoint performs validation on a netlist without storing it in the database.
    Useful for real-time validation in frontend applications.

    Uses custom pre-validation to check JSON structure and return ValidationErrors with
    line/character numbers, then runs business logic validation if structure is valid.
    """
    try:
        # Use our custom validation
        validation_result = validate_netlist_internal(request.netlist)
        return JSONResponse(
            status_code=200,
            content={"validation_result": validation_result.model_dump(mode="json")},
        )

    except HTTPException as e:
        # This is our pre-validation error from the dependency
        if "validation_result" in e.detail:
            return JSONResponse(status_code=e.status_code, content=e.detail)
        else:
            # Fallback for other HTTP exceptions
            from netwiz_backend.netlist.core.validation import (
                ValidationError,
                ValidationErrorType,
                ValidationResult,
            )

            error_result = ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(
                        message=f"Validation failed: {e.detail}",
                        error_type=ValidationErrorType.BLANK_COMPONENT_NAME,
                        location=None,
                    )
                ],
                warnings=[],
                applied_rules=[],
            )
            return JSONResponse(
                status_code=e.status_code,
                content={"validation_result": error_result.model_dump(mode="json")},
            )

    except Exception as e:
        # If there's an unexpected error, return it as a validation error
        from netwiz_backend.netlist.core.validation import (
            ValidationError,
            ValidationErrorType,
            ValidationHTTPError,
        )

        raise ValidationHTTPError(
            validation_errors=[
                ValidationError(
                    message=f"Validation failed: {e!s}",
                    error_type=ValidationErrorType.BLANK_COMPONENT_NAME,
                    location=None,
                )
            ],
            applied_rules=[ValidationErrorType.BLANK_COMPONENT_NAME],
            status_code=500,
        ) from e
