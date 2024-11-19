import pytest
from modules.data import Data, templates
from unittest.mock import patch
from modules.timestamp import Timestamp


# Fixtures for mock template
@pytest.fixture
def mock_user_template():
    """
    Mock the user template to simulate a real environment.
    """
    templates["user"] = {
        "_id": None,
        "_collection": "user",
        "first_name": "",
        "last_name": "",
        "school_email": "",
        "student_id": "",
        "major": [],
        "graduation_year": None,
        "guild": [],
        "event": [],
        "updated_at": "",
        "created_at": "",
    }


@pytest.fixture
def user_data(mock_user_template):
    """
    Create a Data object using the user template.
    """
    return Data.from_template("user", _id=1)


# Test Initialization
def test_user_template_initialization(mock_user_template):
    """
    Ensure the user template is initialized without errors.
    """
    data = Data("user")
    assert data is not None


# Test Data Creation
def test_user_data_creation(user_data):
    """
    Validate creation of user data.
    """
    assert user_data.get_value("id") == 1
    assert user_data.get_value("type") == "user"
    assert user_data.get_value("first_name") == ""
    assert user_data.get_value("graduation_year") is None


# Test Setting and Getting Single Values
def test_user_set_get_value(user_data):
    """
    Test setting and getting single values for the user data.
    """
    user_data.set_value("first_name", "John")
    user_data.set_value("last_name", "Doe")
    user_data.set_value("graduation_year", 2025)

    assert user_data.get_value("first_name") == "John"
    assert user_data.get_value("last_name") == "Doe"
    assert user_data.get_value("graduation_year") == 2025


# Test List Operations
def test_user_major_operations(user_data):
    """
    Test list operations for the 'major' field.
    """
    user_data.append_to_list("major", "Computer Science")
    user_data.append_to_list("major", "Electronic Arts")
    assert user_data.get_list("major") == ["Computer Science", "Electronic Arts"]

    user_data.remove_from_list("major", "Computer Science")
    assert user_data.get_list("major") == ["Electronic Arts"]

    popped_major = user_data.pop_from_list("major", 0)
    assert popped_major == "Electronic Arts"
    assert user_data.get_list("major") == []


# Test Guild List Operations
def test_user_guild_operations(user_data):
    """
    Test list operations for the 'guild' field.
    """
    user_data.append_to_list("guild", "Art Guild")
    user_data.append_to_list("guild", "Tech Guild")
    assert user_data.get_list("guild") == ["Art Guild", "Tech Guild"]

    user_data.clear_list("guild")
    assert user_data.get_list("guild") == []


# Test Event List Operations
def test_user_event_operations(user_data):
    """
    Test list operations for the 'event' field.
    """
    user_data.append_to_list("event", "Hackathon")
    user_data.append_to_list("event", "Art Showcase")
    assert user_data.get_list("event") == ["Hackathon", "Art Showcase"]

    user_data.remove_from_list("event", "Hackathon")
    assert user_data.get_list("event") == ["Art Showcase"]


# Test Invalid Field Access
def test_user_invalid_field_access(user_data):
    """
    Ensure accessing or modifying an invalid field raises appropriate errors.
    """
    with pytest.raises(KeyError):
        user_data.get_value("nonexistent_field")

    with pytest.raises(TypeError):
        user_data.append_to_list("first_name", "Invalid Operation")  # Not a list


# Test Timestamps
@patch("modules.timestamp.now", return_value="2024-11-19T12:00:00")
def test_user_timestamps(mock_now, user_data):
    """
    Ensure timestamps are properly set.
    """
    assert user_data.get_value("created_at") == "2024-11-19T12:00:00"
    user_data.set_value("updated_at", "2024-11-20T12:00:00")
    assert user_data.get_value("updated_at") == "2024-11-20T12:00:00"
