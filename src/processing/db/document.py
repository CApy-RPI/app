import json
import typing

from processing.modules import Timestamp

from .collection import Collection
from .templates import templates


class Document:
    def __init__(self):
        pass

    @classmethod
    def from_template(cls, collection: Collection, id: typing.Optional[int] = None):
        """
        Create a new Data object using a template for the specified collection.

        Args:
            collection (str): The name of the data collection.
            id (int): The unique identifier for this data instance.

        Returns:
            Data: A new Data instance initialized with the template data.
        """
        it = cls()
        it.__data = templates[collection].copy()
        it.__data["created_at"] = Timestamp.now()
        it.__data["_id"] = id
        return it

    @classmethod
    def from_dict(cls, collection: Collection, data: dict):
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
        self.__data[key] = value

    def __str__(self) -> str:
        """
        Convert the Data object into a string representation.

        Returns:
        str: A string representation of the Data object.
        """
        return json.dumps(self.__data)
