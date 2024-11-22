import os
import json
from typing import Optional, Union, List
from functools import wraps
from modules.timestamp import Timestamp

# Load templates dynamically from files in "resources/data/template"
templates = {}
filenames = []
for file in os.listdir("resources/data/template"):
    if file.endswith(".json"):
        filename = file[:-5]
        filenames.append(filename)
        with open(f"resources/data/template/{file}", "r") as f:
            templates[filename] = json.load(f)


class Data:
    # * * * * * Initializer * * * * * #
    def _init__(self):
        """
        Initializes a new Data object with the specified collection.

        Args:
            collection (str): The name of the data collection.
        """

    # * * * * * Constructors * * * * * #
    @classmethod
    def from_template(cls, collection: str, id: Optional[int] = None):
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
    def from_dict(cls, data: dict):
        """
        Create a new Data object from a dictionary representation.

        Args:
            data (dict): A dictionary containing the data to initialize the Data object.

        Returns:
            Data: A new Data instance initialized with the provided dictionary data.
        """
        it = cls()
        it.__data = data.copy()
        return it

    # * * * * * Validators * * * * * #
    def assert_template(self, collection: str, function: Optional[str] = None) -> bool:
        """
        Asserts that the specified collection exists in the templates.

        Args:
            collection (str): The name of the data collection to check.
            function (Optional[str]): The name of the function calling this assertion,
                                    used for error messaging.

        Raises:
            ValueError: If the collection does not exist in templates.

        Returns:
            bool: True if the collection exists, otherwise raises an error.
        """
        if collection not in templates:
            raise ValueError(
                f"Error in {function or 'assert_template'}: Collection '{collection}' does not exist in templates."
            )

    def validate_key_exists(method):
        """
        Decorator to ensure the specified key exists in the '__data' dictionary.

        Args:
            method (function): The method that requires key existence in '__data'.

        Raises:
            KeyError: If the key is not found in '__data'.
        """

        @wraps(method)
        def wrapper(self, key, *args, **kwargs):
            if key == "id":
                key = "_id"
            elif key == "type":
                key = "_collection"

            if key not in self.__data:
                raise KeyError(
                    f"Error in {method.__name__}: Key '{key}' not found in data."
                )
            return method(self, key, *args, **kwargs)

        return wrapper

    def validate_key_points_to_value(method):
        """
        Decorator to ensure the specified key points to a single, non-list, non-dict value.

        Args:
            method (function): The method that requires the key to point to a value.

        Raises:
            TypeError: If the key points to a list or dictionary, with details on the actual type.
        """

        @wraps(method)
        def wrapper(self, key, *args, **kwargs):
            if key == "id":
                key = "_id"
            elif key == "type":
                key = "_collection"

            if key not in self.__data:
                raise KeyError(
                    f"Error in {method.__name__}: Key '{key}' not found in data."
                )
            value = self.__data.get(key)
            if isinstance(value, (list, dict)):
                raise TypeError(
                    f"Error in {method.__name__}: Key '{key}' must point to a single value, "
                    f"but currently points to type '{type(value).__name__}'."
                )
            return method(self, key, *args, **kwargs)

        return wrapper

    def validate_key_points_to_list(method):
        """
        Decorator to ensure the specified key points to a list.

        Args:
            method (function): The method that requires the key to point to a list.

        Raises:
            TypeError: If the key does not point to a list, with details on the actual type.
        """

        @wraps(method)
        def wrapper(self, key, *args, **kwargs):
            if key == "id":
                key = "_id"
            elif key == "type":
                key = "_collection"

            if key not in self.__data:
                raise KeyError(
                    f"Error in {method.__name__}: Key '{key}' not found in data."
                )
            value = self.__data.get(key)
            if not isinstance(value, list):
                raise TypeError(
                    f"Error in {method.__name__}: Key '{key}' must point to a list, "
                    f"but currently points to type '{type(value).__name__}'."
                )
            return method(self, key, *args, **kwargs)

        return wrapper

    def validate_index_points_to_value_in_valid_list(method):
        """
        Decorator to ensure the specified index points to a value in a valid list.

        Args:
            method (function): The method that requires the index to point to a value in a valid list.

        Raises:
            IndexError: If the index points to a value that is not in the list, with details on the actual type.
        """

        @wraps(method)
        def wrapper(self, key, index, *args, **kwargs):
            if key == "id":
                key = "_id"
            elif key == "type":
                key = "_collection"

            value = self.__data.get(key)
            if not isinstance(value, list):
                raise TypeError(
                    f"Error in {method.__name__}: Key '{key}' must point to a list, "
                    f"but currently points to type '{type(value).__name__}'."
                )
            if index < 0 or index >= len(value):
                raise IndexError(
                    f"Error in {method.__name__}: Index '{index}' out of range for key '{key}'. List size: {len(value)}."
                )
            return method(self, key, index, *args, **kwargs)

        return wrapper

    @validate_key_exists
    def validate_key_points_to_dict(method):
        """
        Decorator to ensure the specified key points to a dictionary.

        Args:
            method (function): The method that requires the key to point to a dictionary.

        Raises:
            TypeError: If the key does not point to a dictionary, with details on the actual type.
        """

        @wraps(method)
        def wrapper(self, key, *args, **kwargs):
            if key == "id":
                key = "_id"
            elif key == "type":
                key = "_collection"

            value = self.__data.get(key)
            if not isinstance(value, dict):
                raise TypeError(
                    f"Error in {method.__name__}: Key '{key}' must point to a dictionary, "
                    f"but currently points to type '{type(value).__name__}'."
                )
            return method(self, key, *args, **kwargs)

        return wrapper

    # * * * * * Getters and Setters * * * * * #
    @validate_key_points_to_value
    def get_value(self, key: str):
        """
        Retrieve the value associated with the specified key.

        Args:
            key (str): The key for which to retrieve the value.

        Returns:
            object: The value associated with the key.
        """
        return self.__data[key]

    @validate_key_points_to_value
    def set_value(self, key: str, value):
        """
        Set the value for the specified key.

        Args:
            key (str): The key for which to set the value.
            value: The value to set.

        Raises:
            AttributeError: If attempting to set the '_collection' attribute.
        """
        if key == "id":
            self.__data["_id"] = value
            return
        elif key == "type":
            raise AttributeError(
                "Error in set_value: Setting '_collection' is not allowed."
            )

        self.__data[key] = value

    # * * * * * List Operations * * * * * #

    @validate_key_points_to_list
    def get_list(self, key: str) -> Optional[list]:
        """
        Get a copy of the list associated with the specified key.

        Args:
            key (str): The key for which to retrieve the list.

        Returns:
            list: A copy of the list associated with the key.
        """
        return self.__data[key].copy()

    @validate_index_points_to_value_in_valid_list
    def get_from_list(self, key: str, index: int) -> Optional[Union[None, object]]:
        """
        Get an item from the list associated with the specified key by index.

        Args:
            key (str): The key for which to retrieve the list item.
            index (int): The index of the item to retrieve.

        Returns:
            object: The item at the specified index.
        """
        return self._data[key][index]

    @validate_key_points_to_list
    def slice_list(
        self, key: str, start: Optional[int] = None, end: Optional[int] = None
    ) -> List[object]:
        """
        Get a copy of a slice of the list associated with the specified key.

        Args:
            key (str): The key for which to retrieve the list slice.
            start (Optional[int]): The starting index of the slice (default is 0).
            end (Optional[int]): The ending index of the slice (default is the length of the list).

        Returns:
            List[object]: A copy of the sliced list.

        Raises:
            IndexError: If the slice indices are out of range.
        """
        lst = self.__data[key]
        start = start if start is not None else 0
        end = end if end is not None else len(lst)

        if start < 0 or end < 0 or start >= len(lst) or end > len(lst) or start > end:
            raise IndexError(
                f"Error in slice_list: Slice indices '{start}:{end}' are out of range for key '{key}'. List size: {len(lst)}"
            )
        return lst[start:end]

    @validate_key_points_to_list
    def append_to_list(self, key: str, value: object):
        """
        Append a value to the list associated with the specified key.

        Args:
            key (str): The key for which to append the value.
            value: The value to append to the list.
        """
        self.__data[key].append(value)

    @validate_key_points_to_list
    def remove_from_list(self, key: str, value: object):
        """
        Remove the first occurrence of a matching value from the list associated with the specified key.

        Args:
            key (str): The key for which to remove the item.
            value: The value to remove from the list.

        """
        self.__data[key].remove(value)

    @validate_index_points_to_value_in_valid_list
    def pop_from_list(self, key: str, index: int) -> object:
        """
        Pop an item from the list associated with the specified key by index.

        Args:
            key (str): The key for which to pop the item.
            index (int): The index of the item to pop.

        Returns:
            object: The item that was removed from the list.
        """
        return self.__data[key].pop(index)

    @validate_key_points_to_list
    def clear_list(self, key: str):
        """
        Clear all items from the list associated with the specified key.

        Args:
            key (str): The key for which to clear the list.

        """
        self.__data[key].clear()

    # * * * * * Dictionary Operations * * * * * #
    def to_dict(self) -> dict:
        """
        Convert the Data object into a dictionary.

        Returns:
        dict: The Data object as a dictionary.
        """
        ret = self.__data.copy()
        ret["updated_at"] = self.__data["updated_at"].to_est()
        ret["created_at"] = self.__data["created_at"].to_est()
        return ret

    def __str__(self) -> str:
        """
        Convert the Data object into a string representation.

        Returns:
        str: A string representation of the Data object.
        """
        return json.dumps(self.__data)
