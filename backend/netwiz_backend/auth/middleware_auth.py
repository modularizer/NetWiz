"""
Authentication middleware that enforces decorator-based access control
"""

from collections.abc import Callable

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from netwiz_backend.auth.decorators import (
    get_auth_level,
    is_admin_required,
    requires_auth,
)
from netwiz_backend.auth.middleware import (
    get_current_active_user,
    get_optional_current_user,
)
from netwiz_backend.auth.models import UserType


async def auth_middleware(request: Request, call_next: Callable):
    """
    Middleware that enforces authentication based on decorator attributes.

    This middleware checks if the endpoint has authentication decorators
    and enforces the appropriate access control.
    """
    # Skip auth middleware for FastAPI internal routes
    internal_routes = {
        "/docs",
        "/redoc",
        "/openapi.json",
        "/docs/oauth2-redirect",
        "/redoc/oauth2-redirect",
    }

    if request.url.path in internal_routes:
        return await call_next(request)

    # Get the route handler
    route = request.scope.get("route")
    if not route or not hasattr(route, "endpoint"):
        return await call_next(request)

    handler = route.endpoint

    # Check if authentication is required
    if not requires_auth(handler):
        return await call_next(request)

    # Get authentication level
    auth_level = get_auth_level(handler)

    try:
        if auth_level == "optional":
            # Optional auth - get user if available
            current_user = await get_optional_current_user()
        else:
            # Required auth - get authenticated user
            current_user = await get_current_active_user()
            print(
                f"DEBUG: Got user {current_user.username}, is_active: {current_user.is_active}, user_type: {current_user.user_type}"
            )

            # Check admin requirement
            if is_admin_required(handler) and current_user.user_type != UserType.ADMIN:
                print("user not admin", current_user.user_type)
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Admin privileges required"},
                )

        # Add user to request state for use in handlers
        request.state.current_user = current_user

    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

    return await call_next(request)
