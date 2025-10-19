import os
import signal
from datetime import datetime, timezone
from typing import ClassVar

from fastapi import APIRouter, HTTPException

from netwiz_backend.config import settings
from netwiz_backend.controller_abc import RouteControllerABC
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

    def __init__(self, prefix: str = "", netlist_controller=None):
        super().__init__(prefix=prefix)
        self.netlist_controller = netlist_controller

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
        )

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
