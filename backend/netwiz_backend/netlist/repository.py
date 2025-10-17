"""
Repository for netlist operations using dependency injection
"""


from motor.core import AgnosticDatabase

from .models import NetlistSubmission


class NetlistRepository:
    """Repository for netlist operations with dependency injection"""

    def __init__(self, database: AgnosticDatabase):
        self.collection = database.netlists

    async def create(self, submission: NetlistSubmission) -> str:
        """Create a new netlist submission"""
        doc = submission.model_dump()
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)

    async def get_by_id(self, submission_id: str) -> dict | None:
        """Get netlist by submission ID"""
        return await self.collection.find_one({"id": submission_id})

    async def list_by_user(self, user_id: str, limit: int = 10) -> list[dict]:
        """List netlists for a user"""
        cursor = self.collection.find({"user_id": user_id}).limit(limit)
        return await cursor.to_list(length=limit)

    async def list_all(self, limit: int = 10) -> list[dict]:
        """List all netlists"""
        cursor = self.collection.find({}).limit(limit)
        return await cursor.to_list(length=limit)

    async def count(self) -> int:
        """Count total netlists"""
        return await self.collection.count_documents({})

    async def count_by_user(self, user_id: str) -> int:
        """Count netlists for a specific user"""
        return await self.collection.count_documents({"user_id": user_id})


def get_netlist_repository(database: AgnosticDatabase) -> NetlistRepository:
    """Factory function to create repository with database dependency"""
    return NetlistRepository(database)
