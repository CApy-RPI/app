import pytest
from modules.timestamp import Timestamp


@pytest.fixture
def timestamp():
    """Fixture to provide a default Timestamp object."""
    return Timestamp("12/31/23 11:00 PM")  # Default timezone: America/New_York


# Test Initialization without timezone
def test_initialization_without_timezone(timestamp):
    """Test initializing without specifying a timezone defaults to America/New_York."""
    assert timestamp.get_datetime() == "12/31/23 11:00 PM EST"


# Test Invalid DateTime String
def test_invalid_datetime_format_raises_error():
    """Test that initializing with an invalid datetime format raises a ValueError."""
    with pytest.raises(ValueError):
        Timestamp("31-12-23 11:00 PM")  # Invalid format


# Test Constructors
def test_constructor_from_epoch():
    """Test creating a Timestamp from an epoch time."""
    timestamp = Timestamp.from_epoch(1704067200)  # Epoch for 01/01/24 00:00 UTC
    assert timestamp.to_utc() == "01/01/24 12:00 AM UTC"


def test_constructor_from_iso8601():
    """Test creating a Timestamp from an ISO 8601 string."""
    timestamp = Timestamp.from_iso8601("2024-01-01T00:00:00+00:00")
    assert timestamp.to_utc() == "01/01/24 12:00 AM UTC"


# Test Arithmetic Operations
def test_add_days(timestamp):
    """Test adding days to the timestamp."""
    timestamp.add_days(2)
    assert timestamp.to_est() == "01/02/24 11:00 PM EST"
    assert timestamp.to_utc() == "01/03/24 04:00 AM UTC"


def test_subtract_days(timestamp):
    """Test subtracting days from the timestamp."""
    timestamp.subtract_days(1)
    assert timestamp.to_est() == "12/30/23 11:00 PM EST"
    assert timestamp.to_utc() == "12/31/23 04:00 AM UTC"


def test_add_hours(timestamp):
    """Test adding hours to the timestamp."""
    timestamp.add_hours(5)
    assert timestamp.to_est() == "01/01/24 04:00 AM EST"
    assert timestamp.to_utc() == "01/01/24 09:00 AM UTC"


def test_subtract_hours(timestamp):
    """Test subtracting hours from the timestamp."""
    timestamp.subtract_hours(3)
    assert timestamp.to_est() == "12/31/23 08:00 PM EST"
    assert timestamp.to_utc() == "01/01/24 01:00 AM UTC"


def test_add_minutes(timestamp):
    """Test adding minutes to the timestamp."""
    timestamp.add_minutes(30)
    assert timestamp.to_est() == "12/31/23 11:30 PM EST"
    assert timestamp.to_utc() == "01/01/24 04:30 AM UTC"


def test_subtract_minutes(timestamp):
    """Test subtracting minutes from the timestamp."""
    timestamp.subtract_minutes(15)
    assert timestamp.to_est() == "12/31/23 10:45 PM EST"
    assert timestamp.to_utc() == "01/01/24 03:45 AM UTC"


# Test Comparison Operations
def test_comparison_less_than(timestamp):
    """Test that a timestamp is less than a later timestamp."""
    earlier = Timestamp("12/31/23 10:00 PM")
    assert earlier < timestamp


def test_comparison_less_than_or_equal(timestamp):
    """Test that a timestamp is less than or equal to another timestamp."""
    same_time = Timestamp("12/31/23 11:00 PM")
    assert timestamp <= same_time


def test_comparison_equal(timestamp):
    """Test that a timestamp is equal to another timestamp."""
    same_time = Timestamp("12/31/23 11:00 PM")
    assert timestamp == same_time


def test_comparison_not_equal(timestamp):
    """Test that a timestamp is not equal to a different timestamp."""
    different_time = Timestamp("01/01/24 12:00 AM")
    assert timestamp != different_time


def test_comparison_greater_than(timestamp):
    """Test that a timestamp is greater than an earlier timestamp."""
    later = Timestamp("01/01/24 01:00 AM")
    assert later > timestamp


def test_comparison_greater_than_or_equal(timestamp):
    """Test that a timestamp is greater than or equal to another timestamp."""
    same_time = Timestamp("12/31/23 11:00 PM")
    assert timestamp >= same_time


# Test Time Difference
def test_time_difference(timestamp):
    """Test the difference in days and hours between two timestamps."""
    other = Timestamp("12/30/23 11:00 PM")
    assert timestamp.time_difference(other) == "1 days, 0 hours, 0 minutes"
