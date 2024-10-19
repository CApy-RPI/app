# modules/database.py - handles all database interactions

import os
import json
from supabase import create_client

from modules.timestamp import now

# Import all templates into a dict
templates = {}
for filename in os.listdir("resources/data/template"):
    if filename.endswith(".json"):
        with open(f"resources/data/template/{filename}", "r") as f:
            templates[filename[:-5]] = json.load(f)


class Data:
    def __init__(self, _type: str, _data: dict = None, _id: int = None):
        """
        Initialize a new Data object with the given type, id, and data.

        Args:
            _type (str): The type of data to load (e.g. user, guild).
            _id (int): The id of the data to load.
            _data (str): The data to load as a JSON string. If None, the default
                template for the given type will be used.

        Raises:
            FileNotFoundError: If the default template for the given type does
                not exist.
        """
        file_path = f"resources/data/template/{_type}.json"
        assert os.path.exists(file_path)

        """ Deprecate - does not update old data with new template data keys
        if not _data:
            with open(file_path, "r") as f:
                self.__data = json.load(f)
                self.__data["id"] = _id
                self.__data["created_at"] = now()
        else:
            self.__data = json.loads(_data["data"])
        """

        # Return copied template data if no input data is provided
        if not _data:
            assert _id is not None
            self.__data = templates[_type].copy()
            self.__data["created_at"] = now()
            self.__id = _id
            return

        # Load fields from input data
        self.__data = json.loads(_data["data"])
        self.__id = _data["id"]

        # Check for any updates from template
        for key, value in templates[_type].items():
            if key not in self.__data:
                self.__data[key] = value

    def get_value(self, _key: str):
        """
        Return the value associated with the given key.

        Args:
            _key (str): The key to retrieve the value for.

        Returns:
            object: The value associated with the given key.
        """
        return self.__id if _key == "id" else self.__data[_key]

    def set_value(self, _key: str, _value):
        """
        Set the value associated with the given key.

        Args:
            _key (str): The key to set the value for.
            _value: The value to set.

        """
        if _key == "id":
            self.__id = _value

        assert _key in self.__data
        self.__data[_key] = _value

    def append_value(self, _key: str, _value):
        """
        Append a value to the end of the list associated with the given key.

        Args:
            _key (str): The key to append the value to.
            _value (object): The value to append.
        """

        assert _key in self.__data
        assert isinstance(self.__data[_key], list)
        self.__data[_key].append(_value)

    def remove_value(self, _key: str, _value):
        """
        Remove a value from the list associated with the given key.

        Args:
            _key (str): The key to remove the value from.
            _value (object): The value to remove.
        """

        assert _key in self.__data
        assert isinstance(self.__data[_key], list)
        self.__data[_key].remove(_value)

    def pop_value(self, _key: str, _index: int):
        """
        Pop a value from the list associated with the given key.

        Args:
            _key (str): The key to remove the element from.
            _index (int): The index of the element to pop.
        """

        assert _key in self.__data
        assert isinstance(self.__data[_key], list)
        assert _index < len(self.__data[_key])
        return self.__data[_key].pop(_index)

    def clear_value(self, _key: str):
        """
        Remove all values from the list associated with the given key.

        Args:
            _key (str): The key to remove all values from.
        """

        assert _key in self.__data
        assert isinstance(self.__data[_key], list)
        self.__data[_key] = []

    def __str__(self):
        """
        Return a string representation of this Data object as a JSON string.

        Returns:
            str: A JSON string representing this Data object.
        """
        return json.dumps(self.__data)

    def __ret__(self):
        """
        Use str(Data) instead to get the string representation of the Data object

        Raises:
            NotImplementedError: Always, as this method should not be used.
        """

        raise NotImplementedError(
            "Use str(Data) instead to get the string representation of the Data object"
        )


class Database:
    def __init__(self):
        """
        Initialize a new Database object with the given URL and key.

        Raises:
            AssertionError: If the SUPABASE_URL or SUPABASE_KEY environment variables are not set.
        """
        self.__client = create_client(
            os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")
        )

    #! Database data creation
    def create_data(self, _table_name: str, _id: int):
        """
        Create a new Data object with the given type and id.

        Args:
            _table_name (str): The type of data to create (e.g. user, guild).
            _id (int): The id of the data to create.

        Returns:
            Data: A new Data object with the given type and id.
        """

        return Data(_table_name, _id=_id)

    #! Database data retrieval
    def get_data(self, _table_name: str, _id: int):
        """
        Retrieve a row from the specified table by the given ID.

        Args:
            _table_name (str): The name of the table to retrieve the row from.
            _id (int): The ID of the row to retrieve.

        Returns:
            Data: The retrieved row from the database represented as a Data object.
        """
        response = (
            self.__client.table(_table_name)
            .select("*")
            .eq("id", _id)
            .eq("is_deleted", False)
            .execute()
            .data
        )

        return (
            Data(
                _table_name,
                response[0],
            )
            if response
            else None
        )

    def get_paginated_data(self, _table_name: str, _page: int, _limit: int):
        """
        Retrieve a paginated list of Data objects from the specified table.

        Args:
            _table_name (str): The name of the table to retrieve the data from.
            _page (int): The page number to retrieve (1-indexed).
            _limit (int): The number of items to retrieve per page.

        Returns:
            List[Data]: The retrieved Data objects.
        """
        offset = (_page - 1) * _limit
        return [
            Data(_table_name, item)
            for item in self.__client.table(_table_name)
            .select("*")
            .eq("is_deleted", False)
            .range(offset, offset + _limit - 1)
            .execute()
            .data
        ]

    def get_linked_data(
        self, _table_name: str, _data: Data, _warn_override: bool = False
    ):
        """
        Retrieve all rows from the specified table that are linked to the given Data object.

        The rows are linked if the id of the row is in the list of ids associated with the given Data object.

        Args:
            _table_name (str): The name of the table to retrieve the rows from.
            _data (Data): The Data object to retrieve the linked rows for.

        Returns:
            list[Data]: A list of Data objects representing the linked rows from the database.
        """

        if not _warn_override:
            raise ValueError(
                "If using this method for discord embed, use get_linked_paginated_data() instead. Otherwise, pass True to _warn_override."
            )

        return [
            Data(_table_name, item)
            for item in self.__client.table(_table_name)
            .select("*")
            .in_("id", _data.get_value(_table_name))
            .eq("is_deleted", False)
            .execute()
            .data
        ]

    def get_paginated_linked_data(
        self, _table_name: str, _data: Data, _page: int, _limit: int
    ):
        """
        Retrieve a paginated list of non-deleted rows from the specified table that are linked to the given Data object.

        The rows are linked if the id of the row is in the list of ids associated with the given Data object.

        Args:
            _table_name (str): The name of the table to retrieve the rows from.
            _data (Data): The Data object to retrieve the linked rows for.
            _page (int): The page number to retrieve (1-indexed).
            _limit (int): The number of items to retrieve per page.

        Returns:
            list[Data]: A paginated list of Data objects representing the linked rows from the database.
        """
        offset = (_page - 1) * _limit
        return [
            Data(_table_name, item)
            for item in self.__client.table(_table_name)
            .select("*")
            .in_("id", _data.get_value(_table_name))  # Only include linked rows
            .eq("is_deleted", False)  # Only include non-deleted rows
            .range(offset, offset + _limit - 1)  # Apply pagination
            .execute()
            .data
        ]

    #! Database data search and find
    def search_data(self, _table_name: str, _field: str, _value: any):
        """
        Search for Data objects in the specified table by the given field and value.

        Args:
            _table_name (str): The name of the table to search in.
            _field (str): The field to search by.
            _value (any): The value to search for.

        Returns:
            List[Data]: A list of Data objects that match the search criteria.
        """

        response = (
            self.__client.table(_table_name)
            .select("*")
            .eq(_field, _value)
            .eq("is_deleted", False)
            .execute()
        )
        return [Data(_table_name, item) for item in response.data]

    def exists_data(self, _data: Data):
        """
        Check if a row exists in the database with the given Data object.

        Args:
            _data (Data): The Data object to check if it exists in the database.

        Returns:
            bool: True if the row exists in the database, False otherwise.
        """
        return self.get_data(_data.get_value("type"), _data.get_value("id")) is not None

    #! Database data update and upsert
    """ Deprecate - replaced with upsert
    def __insert_data(self, _data: Data):
        '''
        DO NOT USE THIS FUNCTION PUBLICLY

        Insert a new row into the database with the given Data object.

        Args:
            _data (Data): The Data object to insert into the database.
        '''

        self.__client.table(_data.get_value("type")).insert(
            {"id": _data.get_value("id"), "data": str(_data)}
        ).execute()
    """

    def upsert_data(self, _data: Data):
        """
        Update a row in the database with the given Data object.

        If the row does not exist, it will be inserted into the database.

        Args:
            _data (Data): The Data object to upsert in the database.
        """

        # Update the updated_at field
        _data.set_value("updated_at", now())

        # Update the data in the database
        self.__client.table(_data.get_value("type")).upsert(
            {"id": _data.get_value("id"), "data": str(_data)}
        ).execute()

    def update_data(self, _data: Data):
        """
        Update a row in the database with the given Data object.

        If the row does not exist, it will not be inserted into the database.

        Args:
            _data (Data): The Data object to update in the database.

        Raises:
            NotImplementedError: This method should be removed in favor of upsert_data.
        """
        raise NotImplementedError(
            "Use upsert_data(Data()) instead of update_data(Data())"
        )

    def upsert_bulk_data(self, _table_name: str, _data_list: list[Data]):
        """
        Upsert a list of Data objects into the given table.

        If a Data object with the same id already exists in the table, its data will be updated.
        Otherwise, a new row will be inserted into the table.

        Args:
            _table_name (str): The name of the table to upsert the data into.
            _data_list (list[Data]): The list of Data objects to upsert into the table.
        """

        update_payload = [
            {"id": data.get_value("id"), "data": str(data)} for data in _data_list
        ]
        self.__client.table(_table_name).upsert(update_payload).execute()

    #! Database data delete and restore
    def soft_delete(self, _table_name: str, _id: int):
        """
        Soft delete a record by marking it as deleted and adding a timestamp.

        Args:
            _table_name (str): The name of the table to soft delete from.
            _id (int): The ID of the record to be soft deleted.
        """
        self.__client.table(_table_name).update(
            {"is_deleted": True, "deleted_at": now()}
        ).eq("id", _id).execute()

    def hard_delete(self, _table_name: str, _id: int, _warn_override: bool = False):
        """
        Permanently delete a record from the database.

        Args:
            _table_name (str): The table name to delete from.
            _id (int): The ID of the record to be hard deleted.
        """
        if not _warn_override:
            raise ValueError(
                "Unless you are absolutely sure you want to delete FOREVER, use soft_delete() instead. Otherwise, pass True to _warn_override."
            )

        self.__client.table(_table_name).delete().eq("id", _id).execute()

    def restore(self, _table_name: str, _id: int):
        """
        Restore a soft deleted record by marking the 'is_deleted' flag as False.

        Args:
            _table_name (str): The table name to restore from.
            _id (int): The ID of the record to restore.
        """
        self.__client.table(_table_name).update(
            {"is_deleted": False, "deleted_at": None}
        ).eq("id", _id).execute()

    def bulk_soft_delete_after_time(self, _table_name: str, _cutoff_time: str):
        """
        Soft delete all records in a table that are older than a specified time.

        Args:
            _table_name (str): The name of the table to soft delete from.
            _cutoff_time (str): The cutoff time to soft delete records older than this time.
        """
        self.__client.table(_table_name).update(
            {"is_deleted": True, "deleted_at": now()}
        ).lt("created_at", _cutoff_time).is_("is_deleted", False).execute()

    def bulk_soft_delete(self, _table_name: str, _ids: list[int]):
        """
        Soft delete multiple records by marking them as 'deleted'.

        Args:
            _table_name (str): The table name to soft delete from.
            ids (list[int]): The IDs of the records to be soft deleted.
        """
        self.__client.table(_table_name).update(
            {"is_deleted": True, "deleted_at": now()}
        ).in_("id", _ids).execute()

    def bulk_hard_delete(
        self, _table_name: str, _ids: list[int], _warn_override: bool = False
    ):
        """
        Permanently delete multiple records from the database.

        Args:
            _table_name (str): The table name to delete from.
            ids (list[int]): The IDs of the records to be hard deleted.
        """
        if not _warn_override:
            raise ValueError(
                "Unless you are absolutely sure you want to delete FOREVER, use soft_delete() instead. Otherwise, pass True to _warn_override."
            )
        self.__client.table(_table_name).delete().in_("id", _ids).execute()

    def bulk_restore(self, _table_name: str, _ids: list[int]):
        """
        Restore multiple soft deleted records by marking the 'is_deleted' flag as False.

        Args:
            _table_name (str): The table name to restore from.
            ids (list[int]): The IDs of the records to restore.
        """
        self.__client.table(_table_name).update(
            {"is_deleted": False, "deleted_at": None}
        ).in_("id", _ids).execute()

    def cleanup_soft_deleted(self, _table_name: str, _cutoff_date: str):
        """
        Permanently delete records that were soft deleted before a certain date.

        Args:
            _table_name (str): The table name to clean up.
            cutoff_date (str): The cutoff date to delete records older than this date.
        """
        self.__client.table(_table_name).delete().lt("deleted_at", _cutoff_date).eq(
            "is_deleted", True
        ).execute()

    #! Database table backup and restore
    def backup_table(self, _table_name: str, _output_file: str):
        """
        Back up the data in the given table to a file.

        Args:
            _table_name (str): The name of the table to backup.
            _output_file (str): The file to write the data to.
        """
        response = self.__client.table(_table_name).select("*").execute()
        with open(_output_file, "w") as f:
            json.dump(response.data, f, indent=4)

    def restore_table(self, _table_name: str, _input_file: str):
        """
        Restore the data in the given table from a file.

        Args:
            _table_name (str): The name of the table to restore data into.
            _input_file (str): The file to read the data from.
        """
        with open(_input_file, "r") as f:
            data = json.load(f)
        self.__client.table(_table_name).upsert(data).execute()
