"""
Authentication repository for user operations using dependency injection
"""

from motor.core import AgnosticDatabase

from netwiz_backend.auth.models import User


class AuthRepository:
    """Repository for authentication operations with dependency injection"""

    def __init__(self, database: AgnosticDatabase):
        self.collection = database.users

    async def create_user(self, user: User) -> str:
        """Create a new user"""
        doc = user.model_dump()
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)

    async def get_user_by_id(self, user_id: str) -> User | None:
        """Get user by ID"""
        doc = await self.collection.find_one({"id": user_id})
        if doc is not None:
            doc = User(**doc)
        return doc

    async def get_user_by_username(self, username: str) -> User | None:
        """Get user by username"""
        doc = await self.collection.find_one({"username": username})
        if doc is not None:
            doc = User(**doc)
        return doc

    async def update_user(self, user_id: str, update_data: dict) -> bool:
        """Update user data"""
        result = await self.collection.update_one(
            {"id": user_id}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_user(self, user_id: str) -> bool:
        """Delete user by ID"""
        result = await self.collection.delete_one({"id": user_id})
        return result.deleted_count > 0

    async def user_exists(self, username: str) -> bool:
        """Check if user exists by username"""
        doc = await self.collection.find_one({"username": username})
        return doc is not None

    async def count_users(self) -> int:
        """Count total users"""
        return await self.collection.count_documents({})


def get_auth_repository(database: AgnosticDatabase) -> AuthRepository:
    """Factory function to create auth repository with database dependency"""
    return AuthRepository(database)
