import pytz
from datetime import datetime, timedelta
from functools import wraps

DATETIME_FORMAT = "%m/%d/%y %I:%M %p"
DATETIME_TZ_FORMAT = "%m/%d/%y %I:%M %p %Z"  # Format with timezone abbreviation


class Timestamp:
    # * * * * * Initialization * * * * * #
    def __init__(self, datetime_str: str):
        """
        Initializes the Timestamp object by parsing the given datetime string
        into America/New_York timezone for internal storage.

        Args:
            datetime_str (str): The date in the format MM/DD/YY HH:MM {AM/PM}.
        """
        self.set_datetime(datetime_str)

    # * * * * * Validators * * * * * #
    @staticmethod
    def is_valid_datetime(datetime_str: str) -> bool:
        """Validates if the given datetime string is in the correct format."""
        try:
            datetime.strptime(datetime_str, DATETIME_FORMAT)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_datetime(func):
        """
        Decorator to validate the datetime format of a given string before executing the decorated function.
        """

        @wraps(func)
        def wrapper(self, datetime_str: str, *args, **kwargs):
            if not self.is_valid_datetime(datetime_str):
                raise ValueError(
                    f"Invalid datetime format: {datetime_str}. Expected format: MM/DD/YY HH:MM AM/PM"
                )
            return func(self, datetime_str, *args, **kwargs)

        return wrapper

    # * * * * * Constructors * * * * * #
    @classmethod
    def now(cls) -> "Timestamp":
        """
        Returns the current time in America/New_York as a Timestamp object.

        Returns:
            Timestamp: A Timestamp object representing the current time in America/New_York.
        """
        # Get the current time in America/New_York
        current_time = datetime.now(pytz.timezone("America/New_York"))
        return cls(current_time.strftime(DATETIME_FORMAT))

    @classmethod
    def from_epoch(cls, epoch: float) -> "Timestamp":
        """
        Creates a Timestamp object from a Unix epoch time.

        Args:
            epoch (float): The Unix timestamp representing the number of seconds since
                            January 1, 1970, 00:00:00 UTC.

        Returns:
            Timestamp: A Timestamp object initialized with the given epoch time, adjusted to America/New_York.
        """
        est_datetime = datetime.fromtimestamp(
            epoch, tz=pytz.timezone("America/New_York")
        )
        return cls(est_datetime.strftime(DATETIME_FORMAT))

    @classmethod
    def from_iso8601(cls, iso8601: str) -> "Timestamp":
        """
        Creates a Timestamp object from an ISO 8601 datetime string.

        Args:
            iso8601 (str): The ISO 8601 datetime string in the format
                            YYYY-MM-DDTHH:MM:SS.ssssssZ.

        Returns:
            Timestamp: A Timestamp object initialized with the given ISO 8601 datetime string, adjusted to America/New_York.
        """
        est_datetime = datetime.fromisoformat(iso8601).astimezone(
            pytz.timezone("America/New_York")
        )
        return cls(est_datetime.strftime(DATETIME_FORMAT))

    # * * * * * String Representation * * * * * #
    def to_epoch(self) -> float:
        """Returns the stored datetime as a Unix epoch time."""
        # Convert the stored datetime to UTC first, then to epoch time
        return self.__est_datetime.astimezone(pytz.utc).timestamp()

    def to_iso8601(self) -> str:
        """Returns the stored datetime in ISO 8601 format."""
        # Convert the stored datetime to UTC before converting to ISO 8601
        return self.__est_datetime.astimezone(pytz.utc).isoformat()

    def to_utc(self) -> str:
        """
        Returns the stored datetime in UTC format.
        """
        return self.__est_datetime.astimezone(pytz.utc).strftime(DATETIME_TZ_FORMAT)

    def to_est(self) -> str:
        """
        Returns the stored datetime in America/New_York format.
        """
        return self.__est_datetime.strftime(DATETIME_TZ_FORMAT)

    def __str__(self):
        return self.to_est()

    # Example of using the custom to_dict method
    def __repr__(self):
        return self.to_est()

    # * * * * * Getter and Setter Methods * * * * * #
    def get_datetime(self) -> str:
        """Gets the stored datetime in America/New_York."""
        return self.to_est()

    @validate_datetime
    def set_datetime(self, datetime_str: str):
        """
        Sets a new datetime and stores it in America/New_York.

        Args:
            datetime_str (str): The new datetime in the format MM/DD/YY HH:MM {AM/PM}.
        """
        # Parse the datetime string to get a naive datetime object
        naive_datetime = datetime.strptime(datetime_str, DATETIME_FORMAT)

        # Localize the naive datetime to America/New_York timezone
        ny_timezone = pytz.timezone("America/New_York")
        localized_datetime = ny_timezone.localize(naive_datetime)

        # Store the datetime in America/New_York
        self.__est_datetime = localized_datetime

    # * * * * * Time Arithmetic * * * * * #
    def add_days(self, days: int):
        """Adds a specified number of days to the current time."""
        self.__est_datetime += timedelta(days=days)

    def subtract_days(self, days: int):
        """Subtracts a specified number of days from the current time."""
        self.__est_datetime -= timedelta(days=days)

    def add_hours(self, hours: int):
        """Adds a specified number of hours to the current time."""
        self.__est_datetime += timedelta(hours=hours)

    def subtract_hours(self, hours: int):
        """Subtracts a specified number of hours from the current time."""
        self.__est_datetime -= timedelta(hours=hours)

    def add_minutes(self, minutes: int):
        """Adds a specified number of minutes to the current time."""
        self.__est_datetime += timedelta(minutes=minutes)

    def subtract_minutes(self, minutes: int):
        """Subtracts a specified number of minutes from the current time."""
        self.__est_datetime -= timedelta(minutes=minutes)

    # * * * * * Comparison Operators * * * * * #
    def __lt__(self, other: "Timestamp") -> bool:
        """Checks if the current time is before another Timestamp object."""
        return self.__est_datetime < other.__est_datetime

    def __le__(self, other: "Timestamp") -> bool:
        """Checks if the current time is before or equal to another Timestamp object."""
        return self.__est_datetime <= other.__est_datetime

    def __eq__(self, other: "Timestamp") -> bool:
        """Checks if the current time is equal to another Timestamp object."""
        return self.__est_datetime == other.__est_datetime

    def __ne__(self, other: "Timestamp") -> bool:
        """Checks if the current time is not equal to another Timestamp object."""
        return self.__est_datetime != other.__est_datetime

    def __gt__(self, other: "Timestamp") -> bool:
        """Checks if the current time is after another Timestamp object."""
        return self.__est_datetime > other.__est_datetime

    def __ge__(self, other: "Timestamp") -> bool:
        """Checks if the current time is after or equal to another Timestamp object."""
        return self.__est_datetime >= other.__est_datetime

    # * * * * * Utility Methods * * * * * #
    def time_difference(self, other: "Timestamp") -> str:
        """Returns a human-readable string showing the difference between two Timestamp objects."""
        delta = self.__est_datetime - other.__est_datetime
        return f"{delta.days} days, {delta.seconds // 3600} hours, {delta.seconds // 60 % 60} minutes"
