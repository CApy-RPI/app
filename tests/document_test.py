import pytest
from processing.db import Document
from processing.modules import Timestamp


@pytest.fixture
def user_data():
    return {
        "_id": 1,
        "profile": {
            "name": {"first": "John", "middle": "A", "last": "Doe"},
            "school_email": "john.doe@example.com",
            "student_id": "123456",
            "major": ["Computer Science"],
            "graduation_year": 2023,
            "phone": "123-456-7890",
        },
        "guilds": [],
        "events": [],
        "created_at": Timestamp.now(),
    }


@pytest.fixture
def data(user_data):
    return Document.from_dict("user", user_data)


def test_get_value(data):
    assert data.get_value("_id") == 1
    assert data.get_value("profile")["name"]["first"] == "John"


def test_set_value(data):
    data.set_value("profile", {"name": {"first": "Jane"}})
    assert data.get_value("profile")["name"]["first"] == "Jane"


def test_append_to_list(data):
    data.append_to_list("guilds", "guild_1")
    assert "guild_1" in data.get_list("guilds")


def test_remove_from_list(data):
    data.append_to_list("guilds", "guild_1")
    data.remove_from_list("guilds", "guild_1")
    assert "guild_1" not in data.get_list("guilds")


def test_pop_from_list(data):
    data.append_to_list("guilds", "guild_1")
    popped_value = data.pop_from_list("guilds", 0)
    assert popped_value == "guild_1"
    assert "guild_1" not in data.get_list("guilds")


def test_clear_list(data):
    data.append_to_list("guilds", "guild_1")
    data.clear_list("guilds")
    assert data.get_list("guilds") == []


def test_to_dict(data):
    data_dict = data.to_dict()
    assert data_dict["_id"] == 1
    assert data_dict["profile"]["name"]["first"] == "John"
