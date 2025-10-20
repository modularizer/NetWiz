"""
Authentication decorators for different access levels
"""

from collections.abc import Callable
from typing import Any, Literal, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class DuplicateTagError(Exception):
    pass


def tag(**attributes) -> F:
    """Generic decorator for tagging attributes on functions.
    Useful for decorating a function without actually wrapping it or modifying its functionality.
    """

    def decorator(func: F) -> F:
        func.__tagged__ = True
        tags = func.__dict__.get("__tags__", [])
        for t in attributes:
            if t in tags and attributes[t] != func.__dict__.get(t):
                raise DuplicateTagError(f"Duplicate tag: {t}")
        tags.extend(list(attributes.keys()))
        func.__tags__ = tags
        func.__dict__.update(**attributes)
        return func

    return decorator


def get_tags(func: F) -> dict[str, Any]:
    return {t: getattr(func, t) for t in func.__dict__.get("__tags__", [])}


def get_tag(func: F, tag: str, _default: Any = None) -> Any:
    return getattr(func, tag, _default)


AuthTag = Literal["public", "optional", "user", "admin"]


def auth_tag(auth_level: AuthTag) -> F:
    return tag(
        __auth_level__=auth_level, __auth_required__=auth_level in ["user", "admin"]
    )


def PUBLIC(func: F) -> F:
    """
    Decorator for public endpoints that don't require authentication.

    Usage:
        @PUBLIC
        async def public_endpoint():
            return {"message": "Anyone can access this"}
    """
    return auth_tag("public")(func)


def AUTH(func: F) -> F:
    """
    Decorator for authenticated endpoints that require a valid user.

    Usage:
        @AUTH
        async def protected_endpoint(current_user: User = Depends(get_current_active_user)):
            return {"user": current_user.username}
    """
    return auth_tag("user")(func)


def ADMIN(func: F) -> F:
    """
    Decorator for admin-only endpoints that require admin privileges.

    Usage:
        @ADMIN
        async def admin_endpoint(current_user: User = Depends(get_current_active_user)):
            return {"admin_action": "performed"}
    """
    return auth_tag("admin")(func)


def OPTIONAL_AUTH(func: F) -> F:
    """
    Decorator for endpoints that work with or without authentication.

    Usage:
        @OPTIONAL_AUTH
        async def flexible_endpoint(current_user: User | None = Depends(get_optional_current_user)):
            if current_user:
                return {"message": f"Hello {current_user.username}"}
            return {"message": "Hello anonymous user"}
    """
    return auth_tag("optional")(func)


# Helper functions to inspect decorators
def requires_auth(func: Callable) -> bool:
    """Check if a function requires authentication"""
    return get_tag(func, "__auth_required__", True)  # Default to True for security


def get_auth_level(func: Callable) -> str:
    """Get the authentication level required by a function"""
    return get_tag(func, "__auth_level__", "user")  # Default to 'user' for security


def is_admin_required(func: Callable) -> bool:
    """Check if a function requires admin privileges"""
    return get_auth_level(func) == "admin"
