"""
Repository for netlist operations using dependency injection
"""


from motor.core import AgnosticDatabase
from pydantic import UUID4

from netwiz_backend.models import PaginationParams
from netwiz_backend.netlist.models import NetlistSubmission


class NetlistRepository:
    """Repository for netlist operations with dependency injection"""

    def __init__(self, database: AgnosticDatabase):
        self.collection = database.netlists

    async def create(self, submission: NetlistSubmission) -> str:
        """Create a new netlist submission"""
        doc = submission.model_dump()
        result = await self.collection.insert_one(doc)
        return str(result.inserted_id)

    async def get_by_id(self, submission_id: str) -> NetlistSubmission | None:
        """Get netlist by submission ID"""
        doc = await self.collection.find_one({"id": submission_id})
        if doc is not None:
            doc = NetlistSubmission(**doc)
        return doc

    async def list_by_user(
        self, user_id: str, limit: int = 10
    ) -> list[NetlistSubmission]:
        """List netlists for a user"""
        cursor = self.collection.find({"user_id": user_id}).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [NetlistSubmission(**doc) for doc in docs]

    async def list_all(self, limit: int = 10) -> list[NetlistSubmission]:
        """List all netlists"""
        cursor = self.collection.find({}).limit(limit)
        docs = await cursor.to_list(length=limit)
        return [NetlistSubmission(**doc) for doc in docs]

    async def list(
        self, user_id: UUID4 | None = None, pagination: PaginationParams | None = None
    ):
        if user_id:
            # Filter by user_id
            submissions = await self.list_by_user(user_id, pagination.page_size)
            total_count = await self.count_by_user(user_id)
        elif pagination:
            # Get all submissions
            submissions = await self.list_all(pagination.page_size)
            total_count = await self.count()
        else:
            submissions = await self.list_all()
            total_count = await self.count()

        return submissions, total_count

    async def count(self) -> int:
        """Count total netlists"""
        return await self.collection.count_documents({})

    async def count_by_user(self, user_id: str) -> int:
        """Count netlists for a specific user"""
        return await self.collection.count_documents({"user_id": user_id})


def get_netlist_repository(database: AgnosticDatabase) -> NetlistRepository:
    """Factory function to create repository with database dependency"""
    return NetlistRepository(database)
