import os
import signal
from datetime import datetime, timezone
from typing import ClassVar

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from motor.core import AgnosticDatabase

from netwiz_backend.auth.decorators import ADMIN, PUBLIC
from netwiz_backend.auth.jwt_utils import create_access_token, verify_password
from netwiz_backend.auth.middleware import get_current_active_user
from netwiz_backend.auth.repository import get_auth_repository
from netwiz_backend.config import settings
from netwiz_backend.controller_abc import RouteControllerABC
from netwiz_backend.database import get_database
from netwiz_backend.git_metadata import get_git_metadata
from netwiz_backend.system.models import (
    ApiInfo,
    ApiInfoResponse,
    DocumentationInfo,
    EndpointsInfo,
    HealthResponse,
    KillServerResponse,
    RootResponse,
    ServiceInfo,
)


class SystemController(RouteControllerABC):
    """System and health endpoints controller."""

    tags: ClassVar[list[str]] = ["system"]

    def __init__(self, prefix: str = "", netlist_controller=None, auth_controller=None):
        super().__init__(prefix=prefix)
        self.netlist_controller = netlist_controller
        self.auth_controller = auth_controller

    def _register_routes(self, router: APIRouter) -> None:
        router.add_api_route(
            "/health", self.health_check, methods=["GET"], response_model=HealthResponse
        )
        router.add_api_route(
            "/", self.root, methods=["GET"], response_model=RootResponse
        )
        router.add_api_route(
            "/info", self.api_info, methods=["GET"], response_model=ApiInfoResponse
        )
        router.add_api_route(
            "/kill",
            self.kill_server,
            methods=["POST"],
            response_model=KillServerResponse,
            dependencies=[Depends(get_current_active_user)],
            openapi_extra={
                "x-admin-only": True,
                "description": "Kill the server (admin only). Only available in development mode.",
            },
        )
        router.add_api_route(
            "/token",
            self.login_for_access_token,
            methods=["POST"],
            response_model=dict,
            tags=["auth"],
            summary="OAuth2 compatible token endpoint",
            description="Get access token for Swagger UI authorization",
        )

    def get_endpoints(self) -> EndpointsInfo:
        return EndpointsInfo(
            documentation=DocumentationInfo(
                swagger_ui=f"{self.prefix}/docs",
                redoc=f"{self.prefix}/redoc",
                openapi_json=f"{self.prefix}/openapi.json",
            ),
            health=f"{self.prefix}/health",
            netlist=self.netlist_controller.get_endpoints()
            if self.netlist_controller
            else None,
            auth=self.auth_controller.get_endpoints() if self.auth_controller else None,
        )

    @PUBLIC
    async def health_check(self) -> HealthResponse:
        """
        Health check endpoint for monitoring and load balancers.

        Provides basic health status information for the API service.
        Used by monitoring systems and load balancers to verify service availability.
        """
        # Check MongoDB connectivity
        mongodb_status = "unknown"
        overall_status = "healthy"

        try:
            if self.netlist_controller and hasattr(self.netlist_controller, "database"):
                # Test MongoDB connection
                await self.netlist_controller.database.client.admin.command("ping")
                mongodb_status = "connected"
            else:
                mongodb_status = "not_configured"
        except Exception as e:
            mongodb_status = f"error: {str(e)[:50]}"
            overall_status = "unhealthy"

        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now(timezone.utc),
            version=settings.app_version,
            environment=settings.environment,
            mongodb=mongodb_status,
        )

    @PUBLIC
    async def root(self) -> RootResponse:
        """
        Root endpoint with basic API information.

        Provides essential metadata about the API service including name, version,
        author, and links to documentation and health check endpoints.
        """
        git_metadata = get_git_metadata()

        return RootResponse(
            message=settings.app_name,
            version=settings.app_version,
            author=settings.app_author,
            email=settings.app_email,
            license=settings.app_license,
            url=settings.app_url,
            status=settings.app_status,
            docs=f"{self.prefix}/docs",
            health=f"{self.prefix}/health",
            environment=settings.environment,
            git=git_metadata,
        )

    @PUBLIC
    async def api_info(self) -> ApiInfoResponse:
        """
        Detailed API information endpoint.

        Provides comprehensive information about the API service including detailed
        metadata, service configuration, and available endpoints for API discovery.
        """
        return ApiInfoResponse(
            api=ApiInfo(
                name=settings.app_name,
                version=settings.app_version,
                description=settings.app_description,
                author=settings.app_author,
                email=settings.app_email,
                license=settings.app_license,
                url=settings.app_url,
                status=settings.app_status,
            ),
            service=ServiceInfo(
                environment=settings.environment,
                debug=settings.debug,
                host=settings.host,
                port=settings.port,
            ),
            endpoints=self.get_endpoints(),
        )

    @PUBLIC
    async def login_for_access_token(
        self,
        form_data: OAuth2PasswordRequestForm = Depends(),
        database: AgnosticDatabase = Depends(get_database),
    ) -> dict:
        """
        OAuth2 compatible token endpoint for Swagger UI.

        This endpoint provides username/password authentication that integrates
        seamlessly with Swagger UI's authorization modal.
        """
        auth_repo = get_auth_repository(database)
        user = await auth_repo.get_user_by_username(form_data.username)

        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = create_access_token(
            data={"sub": user.username, "user_id": str(user.id)}
        )
        return {"access_token": access_token, "token_type": "bearer"}

    @ADMIN
    async def kill_server(self) -> KillServerResponse:
        """
        Kill the server (development only).

        Initiates a graceful shutdown of the API server. Only available in development
        mode for safety reasons. Returns 403 Forbidden in production environments.
        """
        if settings.environment != "development":
            raise HTTPException(
                status_code=403,
                detail="Kill endpoint is only available in development mode",
            )

        os.kill(os.getpid(), signal.SIGTERM)
        return KillServerResponse(
            message="Server shutdown initiated",
            timestamp=datetime.now(timezone.utc).isoformat(),
            environment=settings.environment,
        )
