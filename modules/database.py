# modules/database.py - handles all database interactions

import os
import json
import pytz
from datetime import datetime
from supabase import create_client


def now():
    """
    Returns the current time in the America/New_York timezone in the format
    %Y-%m-%d %H:%M:%S %Z %z.

    Returns:
        The current time in the America/New_York timezone.
    """
    eastern = pytz.timezone("America/New_York")
    eastern_time = datetime.now(eastern)
    return eastern_time.strftime("%Y-%m-%d %H:%M:%S %Z %z")


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
                self.__data["created_at"] = now()
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
        self.__data["updated_at"] = now()

    def append(self, key, value):
        """
        Append a value to the end of the list associated with the given key.

        Args:
            key (str): The key to append the value to.
            value (object): The value to append.
        """
        assert key in self.__data
        self.__data[key].append(value)
        self.__data["updated_at"] = now()

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

    def create(self, type: str, id: int):
        """
        Create a new Data object with the given type and id.

        Args:
            type (str): The type of data to create (e.g. user, guild).
            id (int): The id of the data to create.

        Returns:
            Data: A new Data object with the given type and id.
        """

        return Data(type, id)

    def get(self, table_name: str, id: int):
        """
        Retrieve a row from the specified table by the given ID.

        Args:
            table_name (str): The name of the table to retrieve the row from.
            id (int): The ID of the row to retrieve.

        Returns:
            Data: The retrieved row from the database represented as a Data object.
        """
        response = (
            self.__client.table(table_name).select("data").eq("id", id).execute().data
        )
        print(response[0])

        return (
            Data(
                table_name,
                id,
                response[0],
            )
            if response
            else None
        )

    def __insert(self, data: Data):
        """
        Insert a new row into the database with the given Data object.

        Args:
            data (Data): The Data object to insert into the database.
        """

        self.__client.table(data.get("type")).insert(
            {"id": data.get("id"), "data": str(data)}
        ).execute()

    def update(self, data: Data):
        """
        Update a row in the database with the given Data object.

        If the row does not exist, it will be inserted into the database.

        Args:
            data (Data): The Data object to update in the database.
        """
        a = self.get(data.get("type"), data.get("id"))
        if not a:
            self.__insert(data)
        else:
            self.__client.table(data.get("type")).update({"data": str(data)}).eq(
                "id", data.get("id")
            ).execute()


# TODO supabase returns a dictionary by default, change all of db to use the returned dict and not a json
