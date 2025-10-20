"""
Authentication controller for NetWiz backend
"""

from typing import ClassVar

from fastapi import APIRouter, Depends, HTTPException, status
from motor.core import AgnosticDatabase

from netwiz_backend.auth.decorators import AUTH, PUBLIC
from netwiz_backend.auth.jwt_utils import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    get_refresh_token_expiration_time,
    get_token_expiration_time,
    verify_password,
    verify_refresh_token,
)
from netwiz_backend.auth.middleware_auth import get_current_active_user
from netwiz_backend.auth.models import (
    AuthEndpoints,
    ChangePasswordRequest,
    RefreshTokenRequest,
    Token,
    User,
    UserCreate,
    UserLogin,
    UsernameCheckRequest,
    UsernameCheckResponse,
    UserResponse,
    UserType,
)
from netwiz_backend.auth.repository import get_auth_repository
from netwiz_backend.controller_abc import RouteControllerABC
from netwiz_backend.database import get_database


class AuthController(RouteControllerABC):
    """
    Class-organized FastAPI controller for /auth endpoints.
    Handles user authentication including sign-up, sign-in, and sign-out.
    """

    tags: ClassVar[list[str]] = ["auth"]

    def _register_routes(self, router: APIRouter):
        # Register authentication routes
        router.add_api_route(
            "/signup",
            self.signup,
            methods=["POST"],
            response_model=UserResponse,
            status_code=status.HTTP_201_CREATED,
        )

        router.add_api_route(
            "/signin",
            self.signin,
            methods=["POST"],
            response_model=Token,
        )

        router.add_api_route(
            "/signout",
            self.signout,
            methods=["POST"],
            response_model=dict,
            dependencies=[Depends(get_current_active_user)],
        )

        router.add_api_route(
            "/refresh",
            self.refresh_token,
            methods=["POST"],
            response_model=Token,
        )

        router.add_api_route(
            "/change-password",
            self.change_password,
            methods=["POST"],
            response_model=dict,
            dependencies=[Depends(get_current_active_user)],
        )

        router.add_api_route(
            "/me",
            self.get_current_user,
            methods=["GET"],
            response_model=UserResponse,
            dependencies=[Depends(get_current_active_user)],
        )
        router.add_api_route(
            "/user/{user_id}",
            self.get_user_by_id,
            methods=["GET"],
            response_model=UserResponse,
            dependencies=[Depends(get_current_active_user)],
        )

        router.add_api_route(
            "/check-username",
            self.check_username_availability,
            methods=["POST"],
            response_model=UsernameCheckResponse,
        )

    def get_endpoints(self) -> AuthEndpoints:
        """Generate auth endpoints based on the configured prefix."""
        return AuthEndpoints(
            signup=f"{self.prefix}/signup",
            signin=f"{self.prefix}/signin",
            signout=f"{self.prefix}/signout",
            refresh=f"{self.prefix}/refresh",
            change_password=f"{self.prefix}/change-password",
            me=f"{self.prefix}/me",
            check_username=f"{self.prefix}/check-username",
        )

    @PUBLIC
    async def signup(
        self,
        user_create: UserCreate,
        database: AgnosticDatabase = Depends(get_database),
    ) -> UserResponse:
        """
        Create a new user account.

        Registers a new user with the provided username and password.
        The password is hashed before storage for security.
        """
        auth_repo = get_auth_repository(database)

        # Check if user already exists
        if await auth_repo.user_exists(user_create.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )

        # Create new user
        hashed_password = get_password_hash(user_create.password)

        # Set user type: admin if username is "admin", otherwise user
        user_type = (
            UserType.ADMIN if user_create.username.lower() == "admin" else UserType.USER
        )

        user = User(
            username=user_create.username,
            hashed_password=hashed_password,
            user_type=user_type,
        )

        await auth_repo.create_user(user)

        return UserResponse(
            id=user.id,
            username=user.username,
            user_type=user.user_type,
            created_at=user.created_at,
            is_active=user.is_active,
        )

    @PUBLIC
    async def signin(
        self,
        user_login: UserLogin,
        database: AgnosticDatabase = Depends(get_database),
    ) -> Token:
        """
        Authenticate user and return JWT token.

        Validates user credentials and returns a JWT access token
        if authentication is successful.
        """
        auth_repo = get_auth_repository(database)

        # Get user by username
        user = await auth_repo.get_user_by_username(user_login.username)
        print(user_login.model_dump(), user.model_dump())
        if not user:
            print("user not found => incorrect username or password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Verify password
        if not verify_password(user_login.password, user.hashed_password):
            print("incorrect password => incorrect username or password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check if user is active
        if not user.is_active:
            print("user not active")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )

        # Create access and refresh tokens
        token_data = {"sub": user.username, "user_id": user.id}
        access_token = create_access_token(data=token_data)
        refresh_token = create_refresh_token(data=token_data)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=get_token_expiration_time(),
            refresh_expires_in=get_refresh_token_expiration_time(),
        )

    @AUTH
    async def signout(
        self,
        current_user: User = Depends(get_current_active_user),
    ) -> dict:
        """
        Sign out the current user.

        Since JWT tokens are stateless, this endpoint primarily serves
        as a way to inform the client to discard the token.
        """
        return {"message": "Successfully signed out"}

    @PUBLIC
    async def refresh_token(
        self,
        refresh_request: RefreshTokenRequest,
        database: AgnosticDatabase = Depends(get_database),
    ) -> Token:
        """
        Refresh access token using refresh token.

        Validates the refresh token and returns a new access token
        if the refresh token is valid.
        """
        # Verify refresh token
        token_data = verify_refresh_token(refresh_request.refresh_token)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user to ensure they still exist and are active
        auth_repo = get_auth_repository(database)
        user = await auth_repo.get_user_by_username(token_data.username)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create new access and refresh tokens
        token_data_dict = {"sub": user.username, "user_id": user.id}
        access_token = create_access_token(data=token_data_dict)
        refresh_token = create_refresh_token(data=token_data_dict)

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=get_token_expiration_time(),
            refresh_expires_in=get_refresh_token_expiration_time(),
        )

    @AUTH
    async def change_password(
        self,
        change_request: ChangePasswordRequest,
        current_user: User = Depends(get_current_active_user),
        database: AgnosticDatabase = Depends(get_database),
    ) -> dict:
        """
        Change the current user's password.

        Validates the current password and updates it with the new password.
        """
        # Verify current password
        if not verify_password(
            change_request.current_password, current_user.hashed_password
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect",
            )

        # Hash new password
        new_password_hash = get_password_hash(change_request.new_password)

        # Update password in database
        auth_repo = get_auth_repository(database)
        success = await auth_repo.update_user(
            current_user.id, {"hashed_password": new_password_hash}
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update password",
            )

        return {"message": "Password changed successfully"}

    @AUTH
    async def get_current_user(
        self,
        current_user: User = Depends(get_current_active_user),
    ) -> UserResponse:
        """
        Get current authenticated user information.

        Returns the profile information of the currently authenticated user.
        """
        return UserResponse(
            id=current_user.id,
            username=current_user.username,
            user_type=current_user.user_type,
            created_at=current_user.created_at,
            is_active=current_user.is_active,
        )

    @AUTH
    async def get_user_by_id(
        self,
        user_id: str,
        current_user: User = Depends(get_current_active_user),
        database: AgnosticDatabase = Depends(get_database),
    ) -> UserResponse:
        """
        Get user information by ID.

        Only admins can access other users' information.
        Regular users can only access their own information.
        """
        # Check if user is trying to access their own info or is admin
        if current_user.id != user_id and current_user.user_type != UserType.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this user's information",
            )

        # Get user from database
        repo = get_auth_repository(database)
        user = await repo.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return UserResponse(
            id=user.id,
            username=user.username,
            user_type=user.user_type,
            created_at=user.created_at,
            is_active=user.is_active,
        )

    @PUBLIC
    async def check_username_availability(
        self,
        username_check: UsernameCheckRequest,
        database: AgnosticDatabase = Depends(get_database),
    ) -> UsernameCheckResponse:
        """
        Check if a username is available for registration.

        Returns whether the username is available and a descriptive message.
        """
        auth_repo = get_auth_repository(database)

        # Check if user already exists
        user_exists = await auth_repo.user_exists(username_check.username)

        if user_exists:
            return UsernameCheckResponse(
                username=username_check.username,
                available=False,
                message=f"Username '{username_check.username}' is already taken",
            )
        else:
            return UsernameCheckResponse(
                username=username_check.username,
                available=True,
                message=f"Username '{username_check.username}' is available",
            )
