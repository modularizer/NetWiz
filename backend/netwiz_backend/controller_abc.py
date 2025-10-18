from abc import ABC, abstractmethod

from fastapi import APIRouter


class RouteControllerABC(ABC):
    """
    Class-organized FastAPI controller for /netlist endpoints.
    Keeps router + handlers + reusable deps together.
    """

    tags: list[str]

    def __init__(self, prefix: str = "/netlist"):
        self.prefix = prefix
        self.router = APIRouter(prefix=self.prefix, tags=self.tags)
        self._register_routes(self.router)

    def register(self, app):
        app.include_router(self.router)
        return app

    @abstractmethod
    def _register_routes(self, router: APIRouter):
        pass

    @abstractmethod
    def get_endpoints(self):
        pass
