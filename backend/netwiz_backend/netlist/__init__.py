"""
NetWiz Netlist Package

Core netlist functionality including:
- Pydantic models for netlist data structures
- API routes for netlist operations
- Validation logic and business rules
- Data models and schemas
"""

from .models import (
    Netlist,
    NetlistGetResponse,
    NetlistListResponse,
    NetlistSubmission,
    NetlistUploadRequest,
    NetlistUploadResponse,
    ValidationRequest,
    ValidationResponse,
    ValidationResult,
)
from .repository import get_netlist_repository
from .routes import router as netlist_router

__all__ = [
    # Models
    "Netlist",
    "NetlistGetResponse",
    "NetlistListResponse",
    "NetlistSubmission",
    "NetlistUploadRequest",
    "NetlistUploadResponse",
    "ValidationRequest",
    "ValidationResponse",
    "ValidationResult",
    # Router
    "netlist_router",
    # Repository
    "get_netlist_repository",
]
