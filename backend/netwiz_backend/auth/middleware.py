"""
Authentication middleware and dependencies
"""


from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.core import AgnosticDatabase

from netwiz_backend.auth.jwt_utils import verify_token
from netwiz_backend.auth.models import User
from netwiz_backend.auth.repository import get_auth_repository
from netwiz_backend.database import get_database

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    database: AgnosticDatabase = Depends(get_database),
) -> User:
    """
    Get current authenticated user from JWT token

    This dependency extracts the JWT token from the Authorization header,
    verifies it, and returns the corresponding user from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise credentials_exception

    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception

    auth_repo = get_auth_repository(database)
    user = await auth_repo.get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user

    This dependency ensures the user account is active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    database: AgnosticDatabase = Depends(get_database),
) -> User | None:
    """
    Get current user if authenticated, otherwise return None

    This dependency is useful for endpoints that work with or without authentication.
    """
    if credentials is None:
        return None

    try:
        token_data = verify_token(credentials.credentials)
        if token_data is None:
            return None

        auth_repo = get_auth_repository(database)
        user = await auth_repo.get_user_by_username(token_data.username)
        return user
    except HTTPException:
        return None
