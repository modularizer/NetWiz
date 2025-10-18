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
from netwiz_backend.netlist.core.validation.validation import (
    validate_basic_format,
    validate_netlist,
    validate_netlist_text,
)
from netwiz_backend.netlist.models import (
    NetlistEndpoints,
    NetlistGetResponse,
    NetlistListResponse,
    NetlistSubmission,
    NetlistUploadRequest,
    NetlistUploadResponse,
    TextValidationRequest,
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

        router.add_api_route(
            "/validate-text",
            self.validate_json_text,
            methods=["POST"],
        )

    def get_endpoints(self) -> NetlistEndpoints:
        """Generate netlist endpoints based on the configured prefix."""
        return NetlistEndpoints(
            upload=f"{self.prefix}/upload",
            list=self.prefix,
            get=f"{self.prefix}/{{submission_id}}",
            validate=f"{self.prefix}/validate",
            validate_text=f"{self.prefix}/validate-text",
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
            raise HTTPException(
                status_code=422,
                detail={"validation_result": vres.model_dump(mode="json")},
            )
        return ValidationRequest(netlist=tracked_netlist)

    # ── Handlers ───────────────────────────────────────────────────────────────
    async def get_netlist(
        self,
        submission_id: str,
        database: AgnosticDatabase = Depends(get_database),
    ) -> NetlistGetResponse:
        """
        Retrieve a specific netlist submission by ID.

        Fetches a previously uploaded netlist submission from the database using its
        unique submission ID. Includes netlist data, metadata, validation results,
        and submission timestamp.
        """
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
        """
        List netlist submissions with pagination and optional filtering.

        Retrieves a paginated list of netlist submissions from the database.
        Results can be filtered by user ID and include pagination metadata.
        """
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
        """
        Upload and validate a new netlist submission.

        Accepts a netlist submission, validates it according to PCB design rules,
        and stores it in the database. Validation includes component connectivity,
        net integrity, and design rule compliance checks.
        """
        try:
            submission_id = str(uuid.uuid4())
            validation_result = validate_netlist(request.netlist)

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
        """Validate a netlist without storing it in the database."""
        return await self._validate(lambda: validate_netlist(request.netlist))

    async def validate_json_text(
        self,
        request: TextValidationRequest,
    ) -> JSONResponse:
        return await self._validate(lambda: validate_netlist_text(request.json_text))

    async def _validate(self, func):
        """Validate JSON text directly with better location tracking."""
        # try:
        validation_result = func()
        if validation_result.is_valid:
            return JSONResponse(
                status_code=200,
                content={
                    "validation_result": validation_result.model_dump(mode="json")
                },
            )
        return JSONResponse(
            status_code=422,
            content={
                "detail": {
                    "validation_result": validation_result.model_dump(mode="json")
                }
            },
        )
        # except Exception as e:
        #     print(e)
        #     validation_result = ValidationResult(
        #         is_valid=False,
        #         errors=[
        #             ValidationError(
        #                 error_type=INVALID_FORMAT,
        #                 message="Unknown Internal Server Error",
        #                 severity="error",
        #             )
        #         ],
        #     )
        #     return JSONResponse(
        #         status_code=500,
        #         content={
        #             "detail": {
        #                 "validation_result": validation_result.model_dump(mode="json")
        #             }
        #         },
        #     )
