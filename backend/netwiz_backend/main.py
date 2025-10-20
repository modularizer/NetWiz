# netwiz_backend/main.py
from __future__ import annotations

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from netwiz_backend.config import settings
from netwiz_backend.database import close_database, init_database
from netwiz_backend.models import ErrorResponse
from netwiz_backend.netlist.controller import NetlistController
from netwiz_backend.system.controller import SystemController


class NetwizApp:
    """Top-level FastAPI application manager (static/class methods where sensible)."""

    # ── construction ───────────────────────────────────────────────────────────
    def __init__(self) -> None:
        self.app = self._create_app()
        self._configure_middleware()
        self._register_controllers()
        self._register_lifecycle()
        self._register_exception_handlers()
        self._register_openapi_endpoint()

    @staticmethod
    def _create_app() -> FastAPI:
        return FastAPI(
            title=settings.app_name,
            description=settings.app_description,
            version=settings.app_version,
            docs_url="/docs",
            redoc_url="/redoc",
            debug=settings.debug,
            openapi_url="/openapi.json",
            openapi_tags=[
                {"name": "netlist", "description": "Manage PCB netlists"},
                {"name": "system", "description": "System and health endpoints"},
            ],
        )

    def _configure_middleware(self) -> None:
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _register_controllers(self) -> None:
        netlist_controller = NetlistController(prefix="/netlist")
        netlist_controller.register(self.app)
        SystemController(prefix="", netlist_controller=netlist_controller).register(
            self.app
        )

    def _register_lifecycle(self) -> None:
        # static: they don’t depend on instance state
        self.app.add_event_handler("startup", NetwizApp.on_startup)
        self.app.add_event_handler("shutdown", NetwizApp.on_shutdown)

    def _register_exception_handlers(self) -> None:
        # static: don’t depend on instance state
        self.app.add_exception_handler(HTTPException, NetwizApp.http_exception_handler)
        self.app.add_exception_handler(Exception, NetwizApp.general_exception_handler)

    def _register_openapi_endpoint(self) -> None:
        self.app.get("/openapi.json", tags=["system"])(self.app.openapi)

    # ── lifecycle (static) ─────────────────────────────────────────────────────
    @staticmethod
    async def on_startup() -> None:
        await init_database()

    @staticmethod
    async def on_shutdown() -> None:
        await close_database()

    # ── exception handlers (static) ────────────────────────────────────────────
    @staticmethod
    async def http_exception_handler(
        request: Request, exc: HTTPException
    ) -> JSONResponse:
        if isinstance(exc.detail, dict) and "validation_result" in exc.detail:
            return JSONResponse(status_code=exc.status_code, content=exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=str(exc.detail),
                message=str(exc.detail),
                details={"status_code": exc.status_code},
            ).model_dump(),
        )

    @staticmethod
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="internal_server_error",
                message="An internal server error occurred",
                details={"exception": str(exc)},
            ).model_dump(),
        )

    # ── public factories/runners (class methods) ───────────────────────────────
    @classmethod
    def get_app(cls) -> FastAPI:
        return cls().app

    @classmethod
    def run(cls) -> None:
        uvicorn.run(
            "netwiz_backend.main:app",  # or "netwiz_backend.main:NetwizApp.get_app"
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
        )


# ASGI entrypoint
app: FastAPI = NetwizApp.get_app()


def main():
    NetwizApp.run()


if __name__ == "__main__":
    main()
