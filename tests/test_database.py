import pytest
from mongomock_motor import AsyncMongoMockClient
from modules.database import Database
from modules.data import Data


@pytest.fixture(scope="function")
def database():
    """
    Create and provide a Database instance with a mock client for testing.

    Returns:
        Database: Instance of Database with a mock MongoDB client.
    """
    mock_client = AsyncMongoMockClient()
    return Database(client=mock_client)


@pytest.mark.asyncio
async def test_database_creation(database):
    """
    Test the creation of a Database instance with a mock client.
    """
    assert database is not None
    assert isinstance(database, Database)
