import pytest
from mongomock_motor import AsyncMongoMockClient
from modules.database import Database
from modules.data import Data
from modules.timestamp import Timestamp


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


@pytest.mark.asyncio
async def test_create_data(database):
    """
    Test creating a new Data object in the database.
    """
    data = await database.create_data("user", 123)
    assert data is not None
    assert data.get_value("id") == 123
    assert data.get_value("type") == "user"


@pytest.mark.asyncio
async def test_get_data(database):
    """
    Test retrieving a single document or a list of documents.
    """
    # Create a Data object and upsert it into the mock DB
    data = await database.create_data("user", 123)
    await database.upsert_data(data)

    # Test fetching a single document
    fetched_data = await database.get_data("user", 123)
    assert fetched_data is not None
    assert fetched_data.get_value("id") == 123

    # Test fetching a paginated list of documents
    data2 = await database.create_data("user", 124)
    await database.upsert_data(data2)
    data_list = await database.get_data("user", page=1, limit=1)
    assert len(data_list) == 1


@pytest.mark.asyncio
async def test_get_linked_data(database):
    """
    Test retrieving linked data from another collection.
    """
    data1 = await database.create_data("user", 123)
    data2 = await database.create_data("post", 1)
    data1.set_value("posts", [1])
    await database.upsert_data(data1)
    await database.upsert_data(data2)

    linked_data = await database.get_linked_data("post", data1)
    assert len(linked_data) == 1
    assert linked_data[0].get_value("id") == 1


@pytest.mark.asyncio
async def test_search_data(database):
    """
    Test searching for data based on criteria.
    """
    data1 = await database.create_data("user", 123)
    data2 = await database.create_data("user", 124)
    await database.upsert_data(data1)
    await database.upsert_data(data2)

    # Search for data where ID is 123
    criteria = {"id": 123}
    search_results = await database.search_data("user", criteria)
    assert len(search_results) == 1
    assert search_results[0].get_value("id") == 123


@pytest.mark.asyncio
async def test_data_exists(database):
    """
    Test checking if a document exists in the database.
    """
    data = await database.create_data("user", 123)
    await database.upsert_data(data)
    exists = await database.data_exists(data)
    assert exists is True

    non_existing_data = await database.create_data("user", 999)
    exists = await database.data_exists(non_existing_data)
    assert exists is False


@pytest.mark.asyncio
async def test_id_exists(database):
    """
    Test checking if a document with a specific ID exists in a collection.
    """
    data = await database.create_data("user", 123)
    await database.upsert_data(data)
    exists = await database.id_exists("user", 123)
    assert exists is True

    exists = await database.id_exists("user", 999)
    assert exists is False


@pytest.mark.asyncio
async def test_upsert_data(database):
    """
    Test upserting data into the database.
    """
    data = await database.create_data("user", 123)
    await database.upsert_data(data)
    fetched_data = await database.get_data("user", 123)
    assert fetched_data is not None
    assert fetched_data.get_value("id") == 123


@pytest.mark.asyncio
async def test_upsert_bulk_data(database):
    """
    Test bulk upsert of data into the database.
    """
    data1 = await database.create_data("user", 123)
    data2 = await database.create_data("user", 124)
    await database.upsert_bulk_data("user", [data1, data2])

    # Check that both records are upserted
    data_list = await database.get_data("user", page=1, limit=2)
    assert len(data_list) == 2
    assert data_list[0].get_value("id") in [123, 124]
    assert data_list[1].get_value("id") in [123, 124]


@pytest.mark.asyncio
async def test_soft_delete(database):
    """
    Test soft deleting data in the database.
    """
    data = await database.create_data("user", 123)
    await database.upsert_data(data)
    await database.soft_delete("user", data)

    # Check if the data is marked as deleted
    deleted_data = await database.get_data("user", 123, deleted=True)
    assert deleted_data is not None
    assert deleted_data.get_value("is_deleted") is True


@pytest.mark.asyncio
async def test_restore(database):
    """
    Test restoring soft-deleted data in the database.
    """
    data = await database.create_data("user", 123)
    await database.upsert_data(data)
    await database.soft_delete("user", data)
    await database.restore("user", data)

    # Check if the data is restored
    restored_data = await database.get_data("user", 123, deleted=False)
    assert restored_data is not None
    assert restored_data.get_value("is_deleted") is False


@pytest.mark.asyncio
async def test_hard_delete(database):
    """
    Test permanently deleting data from the database.
    """
    data = await database.create_data("user", 123)
    await database.upsert_data(data)
    await database.hard_delete("user", data)

    # Check if the data is removed
    deleted_data = await database.get_data("user", 123)
    assert deleted_data is None


@pytest.mark.asyncio
async def test_hard_delete_by_cutoff(database):
    """
    Test deleting documents by cutoff date.
    """
    timestamp = Timestamp.now()
    data = await database.create_data("user", 123)
    await database.upsert_data(data)

    await database.hard_delete_by_cutoff("user", timestamp)
    deleted_data = await database.get_data("user", 123)
    assert deleted_data is None


@pytest.mark.asyncio
async def test_backup_table(database, tmp_path):
    """
    Test backing up a table to a JSON file.
    """
    data = await database.create_data("user", 123)
    await database.upsert_data(data)

    backup_file = tmp_path / "backup.json"
    await database.backup_table("user", str(backup_file))

    # Check if the file exists and contains the expected data
    assert backup_file.exists()
    with open(backup_file, "r") as f:
        backup_data = json.load(f)
    assert len(backup_data) > 0


@pytest.mark.asyncio
async def test_restore_table(database, tmp_path):
    """
    Test restoring a table from a JSON file.
    """
    data = await database.create_data("user", 123)
    await database.upsert_data(data)

    backup_file = tmp_path / "backup.json"
    await database.backup_table("user", str(backup_file))

    # Create a new database instance for restore
    new_database = Database(client=AsyncMongoMockClient())
    await new_database.restore_table("user", str(backup_file))

    restored_data = await new_database.get_data("user", 123)
    assert restored_data is not None
    assert restored_data.get_value("id") == 123
