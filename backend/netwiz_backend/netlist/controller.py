# netwiz_backend/netlist/controller.py
import uuid
from typing import ClassVar

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.requests import Request as FastAPIRequest
from fastapi.responses import JSONResponse
from motor.core import AgnosticDatabase
from pydantic import UUID4

from netwiz_backend.controller_abc import RouteControllerABC
from netwiz_backend.database import get_database
from netwiz_backend.models import PaginationParams
from netwiz_backend.netlist.core.validation.prevalidation import validate_basic_format
from netwiz_backend.netlist.core.validation.types import (
    ValidationError,
    ValidationErrorType,
    ValidationHTTPError,
    ValidationResult,
)
from netwiz_backend.netlist.core.validation.validation import validate_netlist_internal
from netwiz_backend.netlist.models import (
    NetlistEndpoints,
    NetlistGetResponse,
    NetlistListResponse,
    NetlistSubmission,
    NetlistUploadRequest,
    NetlistUploadResponse,
    ValidationRequest,
)
from netwiz_backend.netlist.repository import get_netlist_repository
from netwiz_backend.tools import get_pagination_params


class NetlistController(RouteControllerABC):
    """
    Class-organized FastAPI controller for /netlist endpoints.
    Keeps router + handlers + reusable deps together.
    """

    tags: ClassVar[list[str]] = ["netlist"]

    def _register_routes(self, router: APIRouter):
        # Register routes
        router.add_api_route(
            "/{submission_id}",
            self.get_netlist,
            methods=["GET"],
            response_model=NetlistGetResponse,
        )

        router.add_api_route(
            "",
            self.list_netlists,
            methods=["GET"],
            response_model=NetlistListResponse,
        )

        router.add_api_route(
            "/upload",
            self.upload_netlist,
            methods=["POST"],
            response_model=NetlistUploadResponse,
            status_code=status.HTTP_201_CREATED,
        )

        # Note: to inject a custom dependency result (ValidationRequest) into the handler
        # we keep the dependency in the function signature via Depends(...)
        router.add_api_route(
            "/validate",
            self.validate_netlist,
            methods=["POST"],
        )

    def get_endpoints(self) -> NetlistEndpoints:
        """Generate netlist endpoints based on the configured prefix."""
        return NetlistEndpoints(
            upload=f"{self.prefix}/upload",
            list=self.prefix,
            get=f"{self.prefix}/{{submission_id}}",
            validate=f"{self.prefix}/validate",
        )

    # ── Shared dependency (kept on the class) ──────────────────────────────────
    @staticmethod
    async def get_unvalidated_request(request: FastAPIRequest) -> ValidationRequest:
        """
        Custom pre-validation: parse body as text, run structural validation to
        produce a ValidationRequest or raise ValidationHTTPError.
        """
        body = await request.body()
        json_text = body.decode("utf-8")

        tracked_netlist, vres = validate_basic_format(json_text)
        if vres is not None:
            raise ValidationHTTPError(
                validation_errors=vres.errors + vres.warnings,
                applied_rules=vres.applied_rules,
            )
        return ValidationRequest(netlist=tracked_netlist)

    # ── Handlers ───────────────────────────────────────────────────────────────
    async def get_netlist(
        self,
        submission_id: str,
        database: AgnosticDatabase = Depends(get_database),
    ) -> NetlistGetResponse:
        repo = get_netlist_repository(database)
        submission = await repo.get_by_id(submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Netlist submission with ID '{submission_id}' not found",
            )
        return NetlistGetResponse(submission=submission)

    async def list_netlists(
        self,
        pagination: PaginationParams = Depends(get_pagination_params),
        database: AgnosticDatabase = Depends(get_database),
        user_id: UUID4 | None = Query(default=None, description="Filter by user ID"),
    ) -> NetlistListResponse:
        repo = get_netlist_repository(database)
        submissions, total_count = await repo.list(
            user_id=user_id, pagination=pagination
        )
        return NetlistListResponse(
            submissions=submissions,
            total_count=total_count,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    async def upload_netlist(
        self,
        request: NetlistUploadRequest,
        database: AgnosticDatabase = Depends(get_database),
    ) -> NetlistUploadResponse:
        try:
            submission_id = str(uuid.uuid4())
            validation_result = validate_netlist_internal(request.netlist)

            submission = NetlistSubmission(
                id=submission_id,
                netlist=request.netlist,
                user_id=request.user_id,
                filename=request.filename,
                validation_result=validation_result,
            )

            repo = get_netlist_repository(database)
            await repo.create(submission)

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

    async def validate_netlist(
        self,
        request: ValidationRequest = Depends(
            get_unvalidated_request.__func__
        ),  # staticmethod ref
    ) -> JSONResponse:
        """
        Validate a netlist without storing it.
        """
        try:
            validation_result = validate_netlist_internal(request.netlist)
            return JSONResponse(
                status_code=200,
                content={
                    "validation_result": validation_result.model_dump(mode="json")
                },
            )
        except ValidationHTTPError as e:
            return JSONResponse(status_code=e.status_code, content=e.detail)
        except HTTPException as e:
            error_result = ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(
                        message=f"Validation failed: {e.detail}",
                        error_type=ValidationErrorType.INVALID_FORMAT,
                        location=None,
                    )
                ],
                warnings=[],
                applied_rules=[ValidationErrorType.INVALID_FORMAT],
            )
            return JSONResponse(
                status_code=e.status_code,
                content={"validation_result": error_result.model_dump(mode="json")},
            )
        except Exception as e:
            raise ValidationHTTPError(
                validation_errors=[
                    ValidationError(
                        message=f"Validation failed: {e!s}",
                        error_type=ValidationErrorType.INVALID_FORMAT,
                        location=None,
                    )
                ],
                applied_rules=ValidationErrorType.INVALID_FORMAT,
                status_code=500,
            ) from e
