# modules/database.py - handles all database interactions

import os
import json
from supabase import create_client


class Data:
    def __init__(self, type: str, id: int, data: str = ""):
        """
        Initialize a new Data object with the given type, id, and data.

        Args:
            type (str): The type of data to load (e.g. user, guild).
            id (int): The id of the data to load.
            data (str): The data to load as a JSON string. If None, the default
                template for the given type will be used.

        Raises:
            FileNotFoundError: If the default template for the given type does
                not exist.
        """
        file_path = f"resources/data/template/{type}.json"
        assert os.path.exists(file_path)

        if not data:
            with open(file_path, "r") as f:
                self.__data = json.load(f)
                self.__data["id"] = id
        else:
            self.__data = json.load(data)

    def get(self, key):
        """
        Return the value associated with the given key.

        Args:
            key (str): The key to retrieve the value for.

        Returns:
            object: The value associated with the given key.
        """
        return self.__data[key]

    def set(self, key, value):
        """
        Set the value associated with the given key.

        Args:
            key (str): The key to set the value for.
            value: The value to set.

        """
        assert key in self.__data
        self.__data[key] = value

    def append(self, key, value):
        """
        Append a value to the end of the list associated with the given key.

        Args:
            key (str): The key to append the value to.
            value (object): The value to append.
        """
        assert key in self.__data
        self.__data[key].append(value)

    def commit(self):
        """
        Commit the current state of this Data object to the database.
        """

        Database().update(self)

    def __str__(self):
        """
        Return a string representation of this Data object as a JSON string.

        Returns:
            str: A JSON string representing this Data object.
        """
        return json.dumps(self.__data)


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

    def get(self, table_name: str, id: int):
        """
        Retrieve a row from the specified table by the given ID.

        Args:
            table_name (str): The name of the table to retrieve the row from.
            id (int): The ID of the row to retrieve.

        Returns:
            Data: The retrieved row from the database represented as a Data object.
            -1: If the retrieval fails.
        """
        return Data(
            table_name,
            id,
            self.__client.table(table_name).select("data").eq("id", id).execute().data,
        )

    def insert(self, data: Data):
        """
        Insert a new row into the database with the given Data object.

        Args:
            data (Data): The Data object to insert into the database.
        """

        self.__client.table(data.get("type")).insert({"data": str(data)}).execute()

    def update(self, data: Data):
        """
        Update a row in the database with the given Data object.

        If the row does not exist, it will be inserted into the database.

        Args:
            data (Data): The Data object to update in the database.
        """
        if not self.get(data.get("type"), data.get("id")):
            self.insert(data)
        else:
            self.__client.table(data.get("type")).update({"data": str(data)}).eq(
                "id", data.get("id")
            ).execute()


def create_user(id: int):
    """
    Create a new Data object for a user with the given ID.

    Args:
        id (int): The ID of the user.

    Returns:
        Data: The new Data object for the user.
    """
    return Data("user", id)


def create_guild(id: int):
    """
    Create a new Data object for a guild with the given ID.

    Args:
        id (int): The ID of the guild.

    Returns:
        Data: The new Data object for the guild.
    """
    return Data("guild", id)


def get_user(id: int):
    """
    Get the Data object for a user with the given ID.

    Args:
        id (int): The ID of the user.

    Returns:
        Data: The Data object for the user.
    """
    return Database().get("user", id)


def get_guild(id: int):
    """
    Get the Data object for a guild with the given ID.

    Args:
        id (int): The ID of the guild.

    Returns:
        Data: The Data object for the guild.
    """
    return Database().get("guild", id)


# TODO move create and get into db s.t. a new db doesn't have to be created each time
# TODO use db in main to access and change data
