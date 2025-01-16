import pytest
from capy_backend.db.document import Document, DocumentTypes


@pytest.fixture
def user_template():
    return Document.from_template(DocumentTypes.USER)


@pytest.fixture
def guild_template():
    return Document.from_template(DocumentTypes.GUILD)


@pytest.fixture
def event_template():
    return Document.from_template(DocumentTypes.EVENT)


def test_from_template_user_id(user_template):
    assert user_template["_id"] is None


def test_from_template_user_profile_name_first(user_template):
    assert user_template["profile"]["name"]["first"] == ""


def test_from_template_user_created_at(user_template):
    assert "created_at" in user_template


def test_from_template_user_updated_at(user_template):
    assert "updated_at" in user_template


def test_from_template_guild_id(guild_template):
    assert guild_template["_id"] is None


def test_from_template_guild_channels_reports(guild_template):
    assert guild_template["channels"]["reports"] == ""


def test_from_template_guild_created_at(guild_template):
    assert "created_at" in guild_template


def test_from_template_guild_updated_at(guild_template):
    assert "updated_at" in guild_template


def test_from_template_event_id(event_template):
    assert event_template["_id"] is None


def test_from_template_event_data_name(event_template):
    assert event_template["data"]["name"] == ""


def test_from_template_event_created_at(event_template):
    assert "created_at" in event_template


def test_from_template_event_updated_at(event_template):
    assert "updated_at" in event_template


def test_from_dict_id():
    data = {
        "_id": 1,
        "profile": {
            "name": {"first": "John", "middle": "A", "last": "Doe"},
            "school_email": "john.doe@example.com",
            "student_id": "123456",
            "major": ["CS"],
            "graduation_year": 2023,
            "phone": "123-456-7890",
        },
    }
    doc = Document.from_dict(DocumentTypes.USER, data)
    assert doc["_id"] == 1


def test_from_dict_profile_name_first():
    data = {
        "_id": 1,
        "profile": {
            "name": {"first": "John", "middle": "A", "last": "Doe"},
            "school_email": "john.doe@example.com",
            "student_id": "123456",
            "major": ["CS"],
            "graduation_year": 2023,
            "phone": "123-456-7890",
        },
    }
    doc = Document.from_dict(DocumentTypes.USER, data)
    assert doc["profile"]["name"]["first"] == "John"


def test_from_dict_profile_school_email():
    data = {
        "_id": 1,
        "profile": {
            "name": {"first": "John", "middle": "A", "last": "Doe"},
            "school_email": "john.doe@example.com",
            "student_id": "123456",
            "major": ["CS"],
            "graduation_year": 2023,
            "phone": "123-456-7890",
        },
    }
    doc = Document.from_dict(DocumentTypes.USER, data)
    assert doc["profile"]["school_email"] == "john.doe@example.com"


def test_getitem_profile_name_first(user_template):
    assert user_template["profile"]["name"]["first"] == ""


def test_setitem_profile_name_first(user_template):
    user_template["profile"]["name"]["first"] = "Jane"
    assert user_template["profile"]["name"]["first"] == "Jane"


def test_setitem_updated_at(user_template):
    user_template["profile"]["name"]["first"] = "Jane"
    assert "updated_at" in user_template


def test_str(user_template):
    assert isinstance(str(user_template), str)


def test_keys(user_template):
    assert "profile" in user_template.keys()


def test_values(user_template):
    user_template.set_value("_id", 1)
    values = list(user_template.values())
    assert 1 in values


def test_items(user_template):
    assert ("_id", None) in user_template.items()


def test_len(user_template):
    assert len(user_template) > 0


def test_iter(user_template):
    keys = [key for key in user_template]
    assert "profile" in keys


def test_delitem(user_template):
    del user_template["profile"]
    assert "profile" not in user_template


def test_get_value(user_template):
    user_template.set_value("_id", 1)
    assert user_template.get_value("_id") == 1


def test_set_value(user_template):
    user_template.set_value(
        "profile", {"name": {"first": "Jane", "middle": "", "last": ""}}
    )
    assert user_template["profile"]["name"]["first"] == "Jane"


def test_contains(user_template):
    assert "profile" in user_template


def test_delattr(user_template):
    with pytest.raises(AttributeError):
        del user_template.__data


def test_setattr(user_template):
    with pytest.raises(AttributeError):
        user_template.__data = {}


def test_getattr(user_template):
    with pytest.raises(AttributeError):
        _ = user_template.__data


def test_invalid_collection():
    with pytest.raises(ValueError):
        Document.from_template("invalid_collection")


def test_getattr_invalid(user_template):
    with pytest.raises(AttributeError):
        _ = user_template.invalid_attribute


def test_delattr_invalid(user_template):
    with pytest.raises(AttributeError):
        del user_template.invalid_attribute


def test_get_value_invalid_key(user_template):
    with pytest.raises(KeyError):
        user_template.get_value("invalid_key")


def test_set_value_invalid_key(user_template):
    with pytest.raises(KeyError):
        user_template.set_value("invalid_key", "value")
