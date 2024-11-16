import unittest
from modules.timestamp import Timestamp


class TestTimestamp(unittest.TestCase):
    def setUp(self):
        """Set up the initial conditions for each test case."""
        self.timestamp = Timestamp(
            "12/31/23 11:00 PM"
        )  # No timezone specified, default to America/New_York
        self.longMessage = True

    # Test Initialization without timezone
    def test_initialization_without_timezone(self):
        """Test initializing without specifying a timezone defaults to America/New_York."""
        # The default should be America/New_York (EST/EDT)
        # We are testing the default conversion to EST
        self.assertEqual(self.timestamp.get_datetime(), "12/31/23 11:00 PM EST")

    # Test Invalid DateTime String
    def test_invalid_datetime_format_raises_error(self):
        """Test that initializing with an invalid datetime format raises a ValueError."""
        with self.assertRaises(ValueError):
            Timestamp("31-12-23 11:00 PM")  # Invalid format

    # Test Constructors
    #! These two don't look like useful tests...
    def test_constructor_from_epoch(self):
        """Test creating a Timestamp from an epoch time."""
        timestamp = Timestamp.from_epoch(
            1704067200
        )  # Known epoch time for 01/01/24 00:00 UTC
        self.assertEqual(timestamp.to_utc(), "01/01/24 12:00 AM UTC")

    def test_constructor_from_iso8601(self):
        """Test creating a Timestamp from an ISO 8601 string."""
        timestamp = Timestamp.from_iso8601("2024-01-01T00:00:00+00:00")
        self.assertEqual(timestamp.to_utc(), "01/01/24 12:00 AM UTC")

    # Test Arithmetic Operations
    def test_add_days(self):
        """Test adding days to the timestamp."""
        self.timestamp.add_days(2)
        self.assertEqual(self.timestamp.to_est(), "01/02/24 11:00 PM EST")
        self.assertEqual(self.timestamp.to_utc(), "01/03/24 04:00 AM UTC")

    def test_subtract_days(self):
        """Test subtracting days from the timestamp."""
        self.timestamp.subtract_days(1)
        self.assertEqual(self.timestamp.to_est(), "12/30/23 11:00 PM EST")
        self.assertEqual(self.timestamp.to_utc(), "12/31/23 04:00 AM UTC")

    def test_add_hours(self):
        """Test adding hours to the timestamp."""
        self.timestamp.add_hours(5)
        self.assertEqual(self.timestamp.to_est(), "01/01/24 04:00 AM EST")
        self.assertEqual(self.timestamp.to_utc(), "01/01/24 09:00 AM UTC")

    def test_subtract_hours(self):
        """Test subtracting hours from the timestamp."""
        self.timestamp.subtract_hours(3)
        self.assertEqual(self.timestamp.to_est(), "12/31/23 08:00 PM EST")
        self.assertEqual(self.timestamp.to_utc(), "01/01/24 01:00 AM UTC")

    def test_add_minutes(self):
        """Test adding minutes to the timestamp."""
        self.timestamp.add_minutes(30)
        self.assertEqual(self.timestamp.to_est(), "12/31/23 11:30 PM EST")
        self.assertEqual(self.timestamp.to_utc(), "01/01/24 04:30 AM UTC")

    def test_subtract_minutes(self):
        """Test subtracting minutes from the timestamp."""
        self.timestamp.subtract_minutes(15)
        self.assertEqual(self.timestamp.to_est(), "12/31/23 10:45 PM EST")
        self.assertEqual(self.timestamp.to_utc(), "01/01/24 03:45 AM UTC")

    # Test Comparison Operations
    def test_comparison_less_than(self):
        """Test that a timestamp is less than a later timestamp."""
        earlier = Timestamp("12/31/23 10:00 PM")  # Default timezone (America/New_York)
        self.assertTrue(earlier < self.timestamp)

    def test_comparison_less_than_or_equal(self):
        """Test that a timestamp is less than or equal to another timestamp."""
        same_time = Timestamp("12/31/23 11:00 PM")
        self.assertTrue(self.timestamp <= same_time)

    def test_comparison_equal(self):
        """Test that a timestamp is equal to another timestamp."""
        same_time = Timestamp("12/31/23 11:00 PM")
        self.assertTrue(self.timestamp == same_time)

    def test_comparison_not_equal(self):
        """Test that a timestamp is not equal to a different timestamp."""
        different_time = Timestamp("01/01/24 12:00 AM")
        self.assertTrue(self.timestamp != different_time)

    def test_comparison_greater_than(self):
        """Test that a timestamp is greater than an earlier timestamp."""
        later = Timestamp("01/01/24 01:00 AM")
        self.assertTrue(later > self.timestamp)

    def test_comparison_greater_than_or_equal(self):
        """Test that a timestamp is greater than or equal to another timestamp."""
        same_time = Timestamp("12/31/23 11:00 PM")
        self.assertTrue(self.timestamp >= same_time)

    # Test Time Difference
    def test_time_difference(self):
        """Test the difference in days and hours between two timestamps."""
        other = Timestamp("12/30/23 11:00 PM")
        self.assertEqual(
            self.timestamp.time_difference(other), "1 days, 0 hours, 0 minutes"
        )
