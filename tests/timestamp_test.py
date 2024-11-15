import unittest
from modules.timestamp import Timestamp


class TestTimestamp(unittest.TestCase):
    def setUp(self):
        """Set up the initial conditions for each test case."""
        self.timestamp = Timestamp("12/31/23 11:00 PM EST")

    # Test Initialization and Default Timezone Detection
    def test_initialization_with_est(self):
        """Test initializing with an EST datetime string."""
        self.assertEqual(self.timestamp.get_timezone(), "EST")

    def test_initialization_without_timezone(self):
        """Test initializing without specifying a timezone defaults to system timezone."""
        timestamp = Timestamp("12/31/23 11:00 PM")
        self.assertEqual(timestamp.get_timezone(), Timestamp.get_default_timezone())

    # Test Setting and Getting Timezone
    def test_set_timezone_utc(self):
        """Test setting timezone to UTC and retrieving it."""
        self.timestamp.set_timezone("UTC")
        self.assertEqual(self.timestamp.get_timezone(), "UTC")

    def test_set_timezone_to_pst(self):
        """Test setting timezone to PST."""
        self.timestamp.set_timezone("America/Los_Angeles")
        self.assertEqual(self.timestamp.get_timezone(), "PST")

    def test_invalid_timezone_raises_error(self):
        """Test that setting an invalid timezone raises a ValueError."""
        with self.assertRaises(ValueError):
            self.timestamp.set_timezone("INVALID/TIMEZONE")

    # Test Invalid DateTime String
    def test_invalid_datetime_format_raises_error(self):
        """Test that initializing with an invalid datetime format raises a ValueError."""
        with self.assertRaises(ValueError):
            Timestamp("31-12-23 11:00 PM")

    # Test Time Conversion
    def test_time_conversion_to_utc(self):
        """Test that the time converts correctly to UTC."""
        self.timestamp.set_timezone("UTC")
        expected_utc_time = "01/01/24 04:00 AM UTC +0000"  # EST (UTC-5) to UTC
        self.assertEqual(self.timestamp.to_utc(), expected_utc_time)

    def test_time_conversion_to_pst(self):
        """Test that the time converts correctly to PST."""
        self.timestamp.set_timezone("America/Los_Angeles")
        expected_pst_time = "12/31/23 08:00 PM PST -0800"  # PST is UTC-8
        self.assertEqual(
            self.timestamp.to_timezone("America/Los_Angeles"), expected_pst_time
        )

    def test_time_conversion_to_default_timezone(self):
        """Test conversion to the default timezone."""
        expected_default_time = (
            "12/31/23 11:00 PM EST -0500"  # Assuming default timezone is EST
        )
        self.assertEqual(self.timestamp.to_default_timezone(), expected_default_time)

    # Test Constructors
    def test_constructor_from_epoch(self):
        """Test creating a Timestamp from an epoch time."""
        timestamp = Timestamp.from_epoch(
            1672444800
        )  # Known epoch time for 01/01/24 00:00 UTC
        self.assertEqual(timestamp.to_utc(), "01/01/24 12:00 AM UTC +0000")

    def test_constructor_from_iso8601(self):
        """Test creating a Timestamp from an ISO 8601 string."""
        timestamp = Timestamp.from_iso8601("2024-01-01T00:00:00+00:00")
        self.assertEqual(timestamp.to_utc(), "01/01/24 12:00 AM UTC +0000")

    # Test Arithmetic Operations
    def test_add_days(self):
        """Test adding days to the timestamp."""
        self.timestamp.add_days(2)
        self.assertEqual(self.timestamp.to_utc(), "01/02/24 11:00 PM UTC +0000")

    def test_subtract_days(self):
        """Test subtracting days from the timestamp."""
        self.timestamp.subtract_days(1)
        self.assertEqual(self.timestamp.to_utc(), "12/30/23 11:00 PM UTC +0000")

    def test_add_hours(self):
        """Test adding hours to the timestamp."""
        self.timestamp.add_hours(5)
        self.assertEqual(self.timestamp.to_utc(), "01/01/24 04:00 AM UTC +0000")

    def test_subtract_hours(self):
        """Test subtracting hours from the timestamp."""
        self.timestamp.subtract_hours(3)
        self.assertEqual(self.timestamp.to_utc(), "12/31/23 08:00 PM UTC +0000")

    def test_add_minutes(self):
        """Test adding minutes to the timestamp."""
        self.timestamp.add_minutes(30)
        self.assertEqual(self.timestamp.to_utc(), "12/31/23 11:30 PM UTC +0000")

    def test_subtract_minutes(self):
        """Test subtracting minutes from the timestamp."""
        self.timestamp.subtract_minutes(15)
        self.assertEqual(self.timestamp.to_utc(), "12/31/23 10:45 PM UTC +0000")

    # Test Comparison Operations
    def test_comparison_less_than(self):
        """Test that a timestamp is less than a later timestamp."""
        earlier = Timestamp("12/31/23 10:00 PM EST")
        self.assertTrue(earlier < self.timestamp)

    def test_comparison_less_than_or_equal(self):
        """Test that a timestamp is less than or equal to another timestamp."""
        same_time = Timestamp("12/31/23 11:00 PM EST")
        self.assertTrue(self.timestamp <= same_time)

    def test_comparison_equal(self):
        """Test that a timestamp is equal to another timestamp."""
        same_time = Timestamp("12/31/23 11:00 PM EST")
        self.assertTrue(self.timestamp == same_time)

    def test_comparison_not_equal(self):
        """Test that a timestamp is not equal to a different timestamp."""
        different_time = Timestamp("01/01/24 12:00 AM EST")
        self.assertTrue(self.timestamp != different_time)

    def test_comparison_greater_than(self):
        """Test that a timestamp is greater than an earlier timestamp."""
        later = Timestamp("01/01/24 01:00 AM EST")
        self.assertTrue(later > self.timestamp)

    def test_comparison_greater_than_or_equal(self):
        """Test that a timestamp is greater than or equal to another timestamp."""
        same_time = Timestamp("12/31/23 11:00 PM EST")
        self.assertTrue(self.timestamp >= same_time)

    # Test Time Difference
    def test_time_difference(self):
        """Test the difference in days and hours between two timestamps."""
        other = Timestamp("12/30/23 11:00 PM EST")
        self.assertEqual(
            self.timestamp.time_difference(other), "1 days, 0 hours, 0 minutes"
        )
