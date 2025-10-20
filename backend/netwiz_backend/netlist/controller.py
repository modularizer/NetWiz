# netwiz_backend/netlist/controller.py
import uuid
from typing import ClassVar

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from motor.core import AgnosticDatabase
from pydantic import UUID4

from netwiz_backend.auth.decorators import AUTH, PUBLIC
from netwiz_backend.auth.middleware import get_current_active_user
from netwiz_backend.auth.models import User
from netwiz_backend.controller_abc import RouteControllerABC
from netwiz_backend.database import get_database
from netwiz_backend.models import PaginationParams
from netwiz_backend.netlist.core.models import Netlist, TrackedNetlist
from netwiz_backend.netlist.core.validation import validate_netlist
from netwiz_backend.netlist.models import (
    NetlistEndpoints,
    NetlistListResponse,
    NetlistSubmission,
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
            response_model=NetlistSubmission,
            dependencies=[Depends(get_current_active_user)],
            openapi_extra={
                "description": "Retrieve a specific netlist submission. Users can only access their own netlists unless they are admin."
            },
        )

        router.add_api_route(
            "",
            self.list_netlists,
            methods=["GET"],
            response_model=NetlistListResponse,
            dependencies=[Depends(get_current_active_user)],
            openapi_extra={
                "description": "List netlist submissions. Users see only their own netlists by default. Admins can use list_all=true or user_id parameter."
            },
        )

        router.add_api_route(
            "/upload",
            self.upload_netlist,
            methods=["POST"],
            response_model=NetlistSubmission,
            status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(get_current_active_user)],
            openapi_extra={
                "description": "Upload netlist as JSON file. Accepts multipart/form-data with file field."
            },
        )

    @PUBLIC
    def get_endpoints(self) -> NetlistEndpoints:
        """Generate netlist endpoints based on the configured prefix."""
        return NetlistEndpoints(
            upload=f"{self.prefix}/upload",
            upload_data=f"{self.prefix}/upload/data",
            upload_text=f"{self.prefix}/upload/text",
            list=self.prefix,
            get=f"{self.prefix}/{{submission_id}}",
        )

    # ── Handlers ───────────────────────────────────────────────────────────────
    @AUTH
    async def get_netlist(
        self,
        submission_id: str,
        database: AgnosticDatabase = Depends(get_database),
        current_user: User = Depends(get_current_active_user),
    ) -> NetlistSubmission:
        """
        Retrieve a specific netlist submission by ID.

        Fetches a previously uploaded netlist submission from the database using its
        unique submission ID. Users can only access their own netlists unless they are admin.
        """
        repo = get_netlist_repository(database)
        submission = await repo.get_by_id(submission_id)
        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Netlist submission with ID '{submission_id}' not found",
            )

        # Check access permissions: user must be owner or admin
        if (
            submission.user_id != current_user.id
            and current_user.user_type.value != "admin"
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view your own netlists",
            )

        return submission

    @AUTH
    async def list_netlists(
        self,
        pagination: PaginationParams = Depends(get_pagination_params),
        database: AgnosticDatabase = Depends(get_database),
        current_user: User = Depends(get_current_active_user),
        user_id: UUID4 | None = Query(
            default=None, description="Filter by user ID (admin only)"
        ),
        list_all: bool = Query(
            default=False, description="List all netlists (admin only)"
        ),
    ) -> NetlistListResponse:
        """
        List netlist submissions with pagination and optional filtering.

        Retrieves a paginated list of netlist submissions from the database.
        By default, users only see their own netlists. Admins can use list_all=true
        to see all netlists or user_id to filter by specific user.
        """

        # Determine which netlists to show based on user permissions
        if current_user.user_type.value != "admin" and (
            list_all or (user_id is not None and user_id != current_user.id)
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You can only view your own netlists",
            )
        elif list_all:
            # Admin can list all netlists
            filters = {}
        else:
            # Admin can filter by specific user
            filters = {"user_id": user_id or current_user.id}

        repo = get_netlist_repository(database)
        submissions, total_count = await repo.list(pagination=pagination, **filters)
        return NetlistListResponse(
            submissions=submissions,
            total_count=total_count,
            page=pagination.page,
            page_size=pagination.page_size,
        )

    @AUTH
    async def upload_netlist(
        self,
        file: UploadFile = File(..., description="JSON file containing netlist data"),
        database: AgnosticDatabase = Depends(get_database),
        current_user: User = Depends(get_current_active_user),
    ) -> NetlistSubmission:
        """
        Upload and validate a netlist from a JSON file.

        Accepts a JSON file upload via multipart/form-data.
        The file should contain valid netlist JSON data.
        """
        # Validate file type
        if not file.filename or not file.filename.lower().endswith(".json"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a JSON file (.json extension)",
            )

        # Read file content
        content = await file.read()
        json_text = content.decode("utf-8")
        filename = file.filename

        submission_id = str(uuid.uuid4())
        tracked_netlist, validation_result = validate_netlist(json_text)
        netlist = (
            Netlist(
                components=tracked_netlist.components,
                nets=tracked_netlist.nets,
                metadata=tracked_netlist.metadata,
            )
            if isinstance(tracked_netlist, TrackedNetlist)
            else tracked_netlist
            if isinstance(tracked_netlist, Netlist)
            else None
        )

        submission = NetlistSubmission(
            id=submission_id,
            json_text=json_text,
            netlist=netlist,
            user_id=current_user.id,
            filename=filename or "unnamed_netlist.json",
            validation_result=validation_result,
        )

        repo = get_netlist_repository(database)
        await repo.create(submission)

        return submission
