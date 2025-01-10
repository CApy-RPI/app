# modules/database.py - handles all database interactions

import os
import json
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCursor
from pymongo import UpdateOne
from typing import List, Dict, Optional, Any, Union

from modules.timestamp import Timestamp
from modules.data import Data


class Database:
    def __init__(self, client: Optional[AsyncIOMotorClient] = None):
        """
        Initialize a new Database object with MongoDB.

        Args:
            client (Optional[AsyncIOMotorClient], optional): MongoDB client to connect to. Defaults to None (creates a new client).

        Raises:
            AssertionError: If MONGODB_URI environment variable is not set.
        """
        mongodb_uri = os.environ.get("MONGODB_URI")
        if not mongodb_uri:
            raise AssertionError("MONGODB_URI environment variable is not set.")
        mongodb_name = os.environ.get("MONGODB_NAME")
        if not mongodb_name:
            raise AssertionError("MONGODB_NAME environment variable is not set.")
        
        self.__client = client or AsyncIOMotorClient(mongodb_uri)
        self.__db = self.__client.get_database(mongodb_name)

    # * * * * * Internal Helpers * * * * * #
    @staticmethod
    def _documents_to_data(
        _collection_name: str, documents: List[Dict[str, Any]]
    ) -> List[Data]:
        """
        Convert a list of documents to a list of Data objects.

        Args:
            _collection_name (str): The name of the collection from which the documents were retrieved.
            documents (List[Dict[str, Any]]): The list of documents to convert.

        Returns:
            List[Data]: A list of Data objects corresponding to the given documents.
        """
        return [Data(_collection_name, doc) for doc in documents]

    @staticmethod
    def _extract_ids(items: Union[int, List[int], Data, List[Data]]) -> List[int]:
        """
        Helper function to extract IDs from mixed input.

        Args:
            items (Union[int, List[int], Data, List[Data]]): Input data that could contain IDs or Data objects.

        Returns:
            List[int]: A list of extracted IDs.
        """
        if isinstance(items, int):
            return [items]
        elif isinstance(items, Data):
            return [items.get_value("id")]
        elif isinstance(items, list):
            return [
                item if isinstance(item, int) else item.get_value("id")
                for item in items
            ]
        return []

    @staticmethod
    def _apply_pagination(
        cursor: AsyncIOMotorCursor,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> AsyncIOMotorCursor:
        """
        Apply pagination to a database cursor.

        Args:
            cursor (AsyncIOMotorCursor): The cursor to apply pagination to.
            page (Optional[int]): The page number to retrieve (1-indexed).
            limit (Optional[int]): The number of items per page.

        Returns:
            AsyncIOMotorCursor: The cursor with pagination applied.
        """
        if page and limit:
            skip = (page - 1) * limit
            return cursor.skip(skip).limit(limit)

        return cursor.limit(limit) if limit else cursor

    # * * * * * Create Data * * * * * #
    async def create_data(self, collection_name: str, id: int):
        """
        Create a new Data object with the given collection and id.

        Args:
            collection_name (str): The type of data to create (e.g., user, guild).
            id (int): The id of the data to create.

        Returns:
            Data: A new Data object with the given type and id.
        """
        return Data.from_template(collection_name, id=id)

    # * * * * * Get Data * * * * * #
    async def get_data(
        self,
        collection_name: str,
        id: Optional[int] = None,
        page: Optional[int] = 1,
        limit: Optional[int] = None,
        deleted: Optional[bool] = False,
    ) -> Union[Optional[Data], List[Data]]:
        """
        Retrieve a document or a paginated list of documents from the specified collection.

        Args:
            collection_name (str): The name of the collection to retrieve the data from.
            id (int, optional): The ID of a specific document to retrieve. If provided, pagination is ignored.
            page (int, optional): The page number to retrieve (1-indexed). Default is 1.
            limit (int, optional): The number of items to retrieve per page. Only used when id is not specified.
            deleted (bool, optional): Whether to include deleted records in the search. Default is False.

        Returns:
            Union[Optional[Data], List[Data]]: A single Data object if `id` is provided; otherwise, a list of Data objects.
        """
        # If id is provided, we will fetch a single document
        if id is not None:
            criteria = {"id": id, "is_deleted": deleted}
            document = await self.search_data(collection_name, criteria)
            return document[0] if document else None

        # If no id is provided, we will fetch a paginated list of documents
        criteria = {"is_deleted": deleted}  # Include or exclude deleted records
        return await self.search_data(collection_name, criteria, page=page, limit=limit)

    async def get_linked_data(
        self,
        collection_name: str,
        data: Data,
        page: Optional[int] = 1,
        limit: Optional[int] = None,
        deleted: Optional[bool] = False,
    ) -> List[Data]:
        """
        Retrieve documents from the specified collection that are linked to the given Data object, with optional pagination.

        Args:
            collection_name (str): The name of the collection to retrieve the documents from.
            data (Data): The Data object to retrieve the linked documents for.
            limit (Optional[int]): The maximum number of results to return. If None, returns all matching results.
            page (Optional[int]): The page number to retrieve, with the default being 1. Used for pagination.
            deleted (Optional[bool]): Whether to include deleted records in the search. Default is False.

        Returns:
            list[Data]: A list of Data objects representing the linked documents from the database.
        """

        # Prepare search criteria for linked IDs and non-deleted records
        linked_ids = data.get_value(collection_name)
        search_criteria = {"id": {"$in": linked_ids}, "is_deleted": deleted}

        # Reuse search_data for pagination and retrieval
        return await self.search_data(
            collection_name, search_criteria, page, limit, deleted
        )

    # * * * * * Search and Find Data * * * * * #
    async def search_data(
        self,
        collection_name: str,
        criteria: Dict[str, Any],
        limit: Optional[int] = None,
        page: Optional[int] = 1,
        deleted: Optional[bool] = False,
    ) -> List[Data]:
        """
        Search for Data objects in the specified collection by multiple fields and values, with optional pagination.

        Args:
            collection_name (str): The name of the collection to search in.
            criteria (Dict[str, any]): A dictionary of field-value pairs to search by.
            limit (Optional[int]): The maximum number of results to return. If None, returns all matching results.
            page (Optional[int]): The page number to retrieve, with the default being 1. Used for pagination.
            deleted (Optional[bool]): Flag to include deleted documents (if True) or exclude them (if False). Default is False.

        Returns:
            List[Data]: A list of Data objects that match the search criteria.
        """
        # Include deleted status in criteria
        criteria["is_deleted"] = deleted

        # Build query with criteria, limit, and skip
        cursor = self.__db[collection_name].find(criteria)
        cursor = self._apply_pagination(cursor, page, limit)
        documents = await cursor.to_list(length=None)
        return self._documents_to_data(collection_name, documents)

    async def data_exists(self, data: Data, deleted: Optional[bool] = False) -> bool:
        """
        Check if a document exists in the database with the given Data object.

        Args:
            data (Data): The Data object to check for existence.
            deleted (Optional[bool]): Flag to include deleted documents (if True) or exclude them (if False). Default is False.

        Returns:
            bool: True if the document exists in the database, False otherwise.
        """
        criteria = {"id": data.get_value("id"), "is_deleted": deleted}
        document = await self.__db[data.get_value("type")].find_one(criteria)
        return document is not None

    async def id_exists(
        self, collection_name: str, id: int, deleted: Optional[bool] = False
    ) -> bool:
        """
        Check if a document with the given ID exists in the specified collection.

        Args:
            collection_name (str): The name of the collection to search in.
            id (int): The ID of the document to check for existence.
            deleted (Optional[bool]): Flag to include deleted documents (if True) or exclude them (if False). Default is False.

        Returns:
            bool: True if a document with the given ID exists, False otherwise.
        """
        criteria = {"id": id, "is_deleted": deleted}
        document = await self.__db[collection_name].find_one(criteria)
        return document is not None

    # * * * * * Update and Upsert Data * * * * * #
    async def upsert_data(self, data: Data):
        """
        Update or insert a document in the database with the given Data object.

        Args:
            data (Data): The Data object to upsert in the database.
        """
        data.set_value("updated_at", Timestamp.now())
        await self.__db[data.get_value("type")].update_one(
            {"id": data.get_value("id")},
            {"$set": data.to_dict()},
            upsert=True,
        )

    async def upsert_bulk_data(self, collection_name: str, data_list: list[Data]):
        """
        Upsert a list of Data objects into the given collection.

        Args:
            collection_name (str): The name of the collection to upsert the data into.
            data_list (list[Data]): The list of Data objects to upsert into the collection.
        """
        updates = [
            {
                "updateOne": {
                    "filter": {"id": data.get_value("id")},
                    "update": {"$set": data.to_dict()},
                    "upsert": True,
                }
            }
            for data in data_list
        ]
        await self.__db[collection_name].bulk_write(updates)

    # * * * * * Delete and Restore Data * * * * * #
    async def soft_delete(
        self, collection_name: str, items: Union[int, List[int], Data, List[Data]]
    ):
        """
        Soft delete one or more documents by marking them as deleted.

        Args:
            collection_name (str): The name of the collection.
            items (Union[int, List[int], Data, List[Data]]): Single ID, list of IDs, Data object, or list of Data objects.
        """
        ids = self._extract_ids(items)
        await self.__db[collection_name].update_many(
            {"id": {"$in": ids}},
            {"$set": {"is_deleted": True, "deleted_at": Timestamp.now()}},
        )

    async def restore(
        self, collection_name: str, items: Union[int, List[int], Data, List[Data]]
    ):
        """
        Restore one or more documents by marking them as not deleted.

        Args:
            collection_name (str): The name of the collection.
            items (Union[int, List[int], Data, List[Data]]): Single ID, list of IDs, Data object, or list of Data objects.
        """
        ids = self._extract_ids(items)
        await self.__db[collection_name].update_many(
            {"id": {"$in": ids}}, {"$set": {"is_deleted": False, "deleted_at": None}}
        )

    async def hard_delete(
        self, collection_name: str, items: Union[int, List[int], Data, List[Data]]
    ):
        """
        Permanently delete one or more documents.

        Args:
            collection_name (str): The name of the collection.
            items (Union[int, List[int], Data, List[Data]]): Single ID, list of IDs, Data object, or list of Data objects.
        """
        ids = self._extract_ids(items)
        await self.__db[collection_name].delete_many({"id": {"$in": ids}})

    async def hard_delete_by_cutoff(
        self, collection_name: str, cutoff_date: Timestamp, older: bool = True
    ):
        """
        Permanently delete soft-deleted documents based on a cutoff date.

        Args:
            collection_name (str): The name of the collection.
            cutoff_date (Timestamp): The cutoff date as a Timestamp object.
            older (bool): If True, delete documents older than the cutoff date; otherwise, delete newer documents.
        """
        # Determine comparison operator based on whether we're deleting older or newer documents
        operator = "$lt" if older else "$gt"

        # Convert Timestamp to UTC datetime for database comparison
        utc_cutoff_date = cutoff_date.to_utc()

        await self.__db[collection_name].delete_many(
            {"is_deleted": True, "deleted_at": {operator: utc_cutoff_date}}
        )

    # * * * * * Backup and Restore Tablets * * * * * #
    async def backup_table(self, collection_name: str, output_file: str):
        """
        Back up the data in the specified collection to a JSON file.

        Args:
            collection_name (str): The name of the collection to back up.
            output_file (str): The file to write the data to.
        """
        # Retrieve all documents in the collection
        cursor = self.db[collection_name].find()
        documents = await cursor.to_list(length=None)

        # Write documents to a file in JSON format
        with open(output_file, "w") as f:
            json.dump(documents, f, default=str, indent=4)

    async def restore_table(
        self, collection_name: str, input_file: str, drop_existing: bool = False
    ):
        """
        Restore the data in the specified collection from a JSON file.

        Args:
            collection_name (str): The name of the collection to restore data into.
            input_file (str): The file to read the data from.
            drop_existing (bool): If True, the collection will be dropped before restoring (full drop restore).
                                If False, documents will be upserted (upsert restore).
        """
        # Load data from the JSON file
        with open(input_file, "r") as f:
            data = json.load(f)

        if drop_existing:
            # Drop the existing collection for a full restore
            await self.db[collection_name].drop()
            await self.db[collection_name].insert_many(data)
            return

        # Perform an upsert restore without dropping the collection
        bulk_operations = []
        for document in data:
            # Ensure each document has an '_id' field for upsert purposes
            if "_id" not in document:
                raise ValueError(
                    "Each document must have an '_id' field for upsert restore."
                )

            # Prepare update or insert operation (upsert)
            bulk_operations.append(
                UpdateOne({"_id": document["_id"]}, {"$set": document}, upsert=True)
            )

        # Execute bulk upsert operation
        if bulk_operations:
            await self.db[collection_name].bulk_write(bulk_operations)
