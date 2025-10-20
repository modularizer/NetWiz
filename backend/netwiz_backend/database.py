"""
MongoDB database service for NetWiz using dependency injection
"""

from collections.abc import AsyncGenerator

from motor.core import AgnosticClient, AgnosticDatabase
from motor.motor_asyncio import AsyncIOMotorClient

from .config import settings


class DatabaseManager:
    """MongoDB connection manager with context manager support"""

    def __init__(self):
        self._client: AgnosticClient | None = None
        self._database: AgnosticDatabase | None = None

    async def connect(self) -> None:
        """Initialize database connection"""
        if self._client is None:
            try:
                self._client = AsyncIOMotorClient(settings.mongodb_uri)
                self._database = self._client[settings.mongodb_database]

                # Actually test the connection by pinging the server
                await self._client.admin.command("ping")
                print(f"✅ Connected to MongoDB: {settings.mongodb_database}")
            except Exception as e:
                print(f"❌ Failed to connect to MongoDB: {e}")
                # Clean up failed connection
                if self._client:
                    self._client.close()
                    self._client = None
                    self._database = None
                # Don't raise - let the application continue without database

    async def disconnect(self) -> None:
        """Close database connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            print("✅ MongoDB connection closed")

    @property
    def database(self) -> AgnosticDatabase:
        """Get database instance"""
        if self._database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._database

    @property
    def client(self) -> AgnosticClient:
        """Get client instance"""
        if self._client is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._client

    async def __aenter__(self) -> "DatabaseManager":
        """Async context manager entry - ensures connection is established"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit - does NOT disconnect for app lifetime connections"""
        # Note: We don't disconnect here as the connection should persist
        # during the application lifetime. Only disconnect on app shutdown.
        pass

    def __enter__(self) -> "DatabaseManager":
        """Sync context manager entry (for compatibility)"""
        # Note: This won't work with async operations, but provides compatibility
        raise RuntimeError("Use 'async with' for async database operations")

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Sync context manager exit (for compatibility)"""
        # Note: This won't work with async operations, but provides compatibility
        raise RuntimeError("Use 'async with' for async database operations")

    async def temporary_connection(self) -> "TemporaryConnection":
        """
        Create a temporary connection that will be closed on exit

        Use this for testing or short-lived operations where you want
        to ensure the connection is closed after use.
        """
        return TemporaryConnection(self)


class TemporaryConnection:
    """Temporary database connection that closes on exit"""

    def __init__(self, manager: DatabaseManager):
        self._manager = manager
        self._was_connected = manager._client is not None

    async def __aenter__(self) -> DatabaseManager:
        """Ensure connection is established"""
        await self._manager.connect()
        return self._manager

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close connection if it wasn't connected before"""
        if not self._was_connected:
            await self._manager.disconnect()


# Global instance for dependency injection
_db_manager = DatabaseManager()


async def get_database() -> AsyncGenerator[AgnosticDatabase, None]:
    """
    FastAPI dependency to get database instance

    This is the recommended pattern for FastAPI:
    - Simple and clean
    - Proper lifecycle management
    - Easy to test and mock
    """
    await _db_manager.connect()
    try:
        yield _db_manager.database
    finally:
        # Note: We don't disconnect here as the connection should persist
        # during the application lifetime. Disconnect happens on app shutdown.
        pass


async def init_database() -> None:
    """Initialize database connection (called at app startup)"""
    await _db_manager.connect()


async def close_database() -> None:
    """Close database connection (called at app shutdown)"""
    await _db_manager.disconnect()
