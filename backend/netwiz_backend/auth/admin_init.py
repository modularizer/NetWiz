"""
Admin account initialization service
"""

from netwiz_backend.auth.jwt_utils import get_password_hash
from netwiz_backend.auth.models import User, UserType
from netwiz_backend.auth.repository import AuthRepository
from netwiz_backend.config import settings


async def ensure_admin_account_exists(auth_repo: AuthRepository) -> None:
    """
    Ensure admin account exists, create it if it doesn't.

    This function checks if an admin user exists, and if not, creates one
    with the configured temporary password.
    """
    # Check if admin user already exists
    admin_user = await auth_repo.get_user_by_username("admin")

    if admin_user is None:
        # Create admin user
        admin_password_hash = get_password_hash(settings.admin_temp_password)

        admin_user = User(
            username="admin",
            hashed_password=admin_password_hash,
            user_type=UserType.ADMIN,
        )

        await auth_repo.create_user(admin_user)
        print(
            f"✅ Admin account created with temporary password: {settings.admin_temp_password}"
        )
        print("⚠️  IMPORTANT: Change the admin password immediately after first login!")
    else:
        print("✅ Admin account already exists")
