"""
JWT utilities for authentication
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from netwiz_backend.auth.models import TokenData
from netwiz_backend.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Add pepper to the plain password before verification
    peppered_password = settings.password_pepper + plain_password

    # Use bcrypt verification
    return bcrypt.checkpw(
        peppered_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt with application-specific pepper"""
    # Add the configured pepper to the password before hashing
    # This provides defense-in-depth: even with database access,
    # attackers need both the hash AND this secret pepper
    peppered_password = settings.password_pepper + password

    # Use bcrypt to hash the peppered password with a random salt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(peppered_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_refresh_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def verify_token(token: str) -> TokenData | None:
    """Verify and decode a JWT access token"""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        token_type = payload.get("type")
        if token_type != "access":
            return None
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if username is None or user_id is None:
            return None
        return TokenData(username=username, user_id=user_id)
    except jwt.PyJWTError:
        return None


def verify_refresh_token(token: str) -> TokenData | None:
    """Verify and decode a JWT refresh token"""
    try:
        payload = jwt.decode(
            token, settings.jwt_refresh_secret_key, algorithms=[settings.jwt_algorithm]
        )
        token_type = payload.get("type")
        if token_type != "refresh":
            return None
        username: str = payload.get("sub")
        user_id: str = payload.get("user_id")
        if username is None or user_id is None:
            return None
        return TokenData(username=username, user_id=user_id)
    except jwt.PyJWTError:
        return None


def get_token_expiration_time() -> int:
    """Get access token expiration time in seconds"""
    return settings.jwt_access_token_expire_minutes * 60


def get_refresh_token_expiration_time() -> int:
    """Get refresh token expiration time in seconds"""
    return settings.jwt_refresh_token_expire_days * 24 * 60 * 60
