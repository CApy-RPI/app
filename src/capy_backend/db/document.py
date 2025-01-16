import os
import json
import enum
import typing

from .timestamp import Timestamp
from config import DATA_TEMPLATE_PATH


class DocumentTypes(enum.Enum):
    USER = "user"
    GUILD = "guild"
    EVENT = "event"


templates: dict[DocumentTypes, dict[str, typing.Any]] = {
    DocumentTypes.USER: {},
    DocumentTypes.GUILD: {},
    DocumentTypes.EVENT: {},
}

for file in os.listdir(DATA_TEMPLATE_PATH):
    if not file.endswith(".json"):
        continue
    filename = file[:-5]
    with open(f"{DATA_TEMPLATE_PATH}/{file}", "r") as f:
        templates[DocumentTypes[filename.upper()]] = json.load(f)


class Document:
    def __init__(self):
        self.__data: dict[str, typing.Any] = {}

    @classmethod
    def from_template(cls, collection: DocumentTypes, id: typing.Optional[int] = None):
        """
        Create a new Data object using a template for the specified collection.

        Args:
            collection (str): The name of the data collection.
            id (int): The unique identifier for this data instance.

        Returns:
            Data: A new Data instance initialized with the template data.
        """
        if collection not in templates:
            raise ValueError(f"Invalid collection type: {collection}")
        it = cls()
        it.__data = templates[collection].copy()
        it.__data["created_at"] = Timestamp()
        it.__data["updated_at"] = Timestamp()
        it.__data["_id"] = id
        return it

    @classmethod
    def from_dict(cls, collection: DocumentTypes, data: dict[str, typing.Any]):
        """
        Create a new Data object from a dictionary representation.

        Args:
            data (dict): A dictionary containing the data to initialize the Data object.

        Returns:
            Data: A new Data instance initialized with the provided dictionary data.
        """
        it = Document.from_template(collection)
        for key, value in data.items():
            it.__data[key] = value
        return it

    def __getitem__(self, key: str) -> typing.Any:
        """
        Get a value from the Data object.

        Args:
            key (str): The key to retrieve from the Data object.

        Returns:
            typing.Any: The value associated with the specified key.
        """
        return self.__data[key]

    def __setitem__(self, key: str, value: typing.Any):
        """
        Set a value in the Data object.

        Args:
            key (str): The key to set in the Data object.
            value (typing.Any): The value to set for the specified key.
        """
        self.__data["updated_at"] = Timestamp()
        self.__data[key] = value

    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in the Data object.

        Args:
            key (str): The key to check in the Data object.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return key in self.__data

    def __delitem__(self, key: str):
        """
        Delete a key-value pair from the Data object.

        Args:
            key (str): The key to delete from the Data object.
        """
        del self.__data[key]

    def __len__(self) -> int:
        """
        Get the number of items in the Data object.

        Returns:
            int: The number of items in the Data object.
        """
        return len(self.__data)

    def __iter__(self):
        """
        Get an iterator over the keys of the Data object.

        Returns:
            iterator: An iterator over the keys of the Data object.
        """
        return iter(self.__data)

    def __str__(self) -> str:
        """
        Convert the Data object into a string representation.

        Returns:
        str: A string representation of the Data object.
        """

        def default_serializer(obj):
            if isinstance(obj, Timestamp):
                return obj.to_json()
            raise TypeError(f"Type {type(obj)} not serializable")

        return json.dumps(self.__data, default=default_serializer)

    def __setattr__(self, name, value):
        if name.startswith("_Document__"):
            super().__setattr__(name, value)
        else:
            raise AttributeError(
                "Direct attribute modification is not allowed. Use item assignment instead."
            )

    def __delattr__(self, name):
        if name.startswith("_Document__"):
            super().__delattr__(name)
        else:
            raise AttributeError(
                f"Direct attribute deletion is not allowed. Use item deletion instead: {name}"
            )

    def keys(self):
        """
        Get all keys in the Data object.

        Returns:
            list: A list of keys in the Data object.
        """
        return self.__data.keys()

    def values(self):
        """
        Get all values in the Data object.

        Returns:
            list: A list of values in the Data object.
        """
        return self.__data.values()

    def items(self):
        """
        Get all key-value pairs in the Data object.

        Returns:
            list: A list of key-value pairs in the Data object.
        """
        return self.__data.items()

    def get_value(self, key: str) -> typing.Any:
        """
        Get a value from the Data object.

        Args:
            key (str): The key to retrieve from the Data object.

        Returns:
            typing.Any: The value associated with the specified key.
        """
        if key not in self.__data:
            raise KeyError(f"Key not found: {key}")
        return self.__data[key]

    def set_value(self, key: str, value: typing.Any):
        """
        Set a value in the Data object.

        Args:
            key (str): The key to set in the Data object.
            value (typing.Any): The value to set for the specified key.
        """
        if key not in self.__data:
            raise KeyError(f"Key not found: {key}")
        self[key] = value
