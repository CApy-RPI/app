import re
import pytz
from datetime import datetime, timedelta
from functools import wraps

STRFTIME_FORMAT = "%m/%d/%y %I:%M %p %Z %z"


class Timestamp:
    # * * * * * Initialization * * * * * #
    def __init__(self, datetime_str: str):
        """
        Initializes the Timestamp object by parsing the given datetime string
        into UTC for internal storage.

        Args:
            datetime_str (str): The date in the format MM/DD/YY HH:MM {AM/PM} with an optional timezone.
        """
        self.__timezone = self.get_default_timezone()  # Default timezone
        self.set_datetime_and_timezone(datetime_str)

    # * * * * * Helpers * * * * * #
    @staticmethod
    def get_default_timezone() -> str:
        """
        Determines the default timezone between Eastern Standard Time (EST)
        and Eastern Daylight Time (EDT) based on the current date.

        Returns:
            str: The appropriate timezone ("EST" or "EDT").
        """
        # Determine the current timezone in New York to check for daylight savings
        current_time = datetime.now(pytz.timezone("America/New_York"))
        return current_time.strftime("%Z")

    # * * * * * Validators * * * * * #
    @staticmethod
    def is_valid_timezone(timezone: str) -> bool:
        """Validates if the given timezone string is in the list of all available timezones."""
        return timezone in pytz.all_timezones

    @staticmethod
    def is_valid_datetime(datetime_str: str) -> bool:
        """Validates if the given datetime string is in the correct format."""
        try:
            datetime.strptime(datetime_str, "%m/%d/%y %I:%M %p")
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_datetime_and_timezone(datetime_str: str) -> bool:
        """Validates if the given datetime string is in the correct format."""
        try:
            datetime.strptime(datetime_str, "%m/%d/%y %I:%M %p %Z")
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_timezone(func):
        """
        Decorator to validate the timezone string before executing the decorated function.

        Args:
            func (function): The function to be decorated.

        Raises:
            ValueError: If the timezone string is not in the list of all available timezones.
        """

        @wraps(func)
        def wrapper(self, timezone: str, *args, **kwargs):
            if not self.is_valid_timezone(timezone):
                raise ValueError(
                    f"Invalid timezone: {timezone}. Must be one of {pytz.all_timezones}."
                )
            return func(self, timezone, *args, **kwargs)

        return wrapper

    @staticmethod
    def validate_datetime(func):
        """
        Decorator to validate the datetime format of a given string before executing the decorated function.

        Args:
            func (function): The function to be decorated.

        Raises:
            ValueError: If the datetime string does not match the expected format MM/DD/YY HH:MM AM/PM.
        """

        @wraps(func)
        def wrapper(self, datetime_str: str, *args, **kwargs):
            if not self.is_valid_datetime(datetime_str):
                raise ValueError(
                    f"Invalid datetime format: {datetime_str}. Expected format: MM/DD/YY HH:MM AM/PM"
                )
            return func(self, datetime_str, *args, **kwargs)

        return wrapper

    @staticmethod
    def validate_datetime_and_timezone(func):
        """
        Decorator to validate the datetime format of a given string before executing the decorated function.

        Args:
            func (function): The function to be decorated.

        Raises:
            ValueError: If the datetime string does not match the expected format MM/DD/YY HH:MM AM/PM.
        """

        @wraps(func)
        def wrapper(self, datetime_str: str, *args, **kwargs):
            if not self.is_valid_datetime_and_timezone(datetime_str):
                raise ValueError(
                    f"Invalid datetime format: {datetime_str}. Expected format: MM/DD/YY HH:MM AM/PM Timezone"
                )
            return func(self, datetime_str, *args, **kwargs)

        return wrapper

    # * * * * * Constructors * * * * * #
    @classmethod
    @validate_timezone
    def now(cls, timezone: str = None) -> "Timestamp":
        """
        Returns the current time in the specified timezone as a Timestamp object.

        Args:
            timezone (str): The timezone to get the current time in.

        Returns:
            Timestamp: A Timestamp object representing the current time.
        """
        timezone = timezone or Timestamp.get_default_timezone()

        # Get the current time in the specified timezone
        current_time = datetime.now(pytz.timezone(timezone))
        return cls(current_time.strftime(STRFTIME_FORMAT))

    @classmethod
    def from_epoch(cls, epoch: float) -> "Timestamp":
        """
        Creates a Timestamp object from a Unix epoch time.

        Args:
            epoch (float): The Unix timestamp representing the number of seconds since
                            January 1, 1970, 00:00:00 (UTC).

        Returns:
            Timestamp: A Timestamp object initialized with the given epoch time.
        """
        utc_datetime = datetime.fromtimestamp(epoch, tz=pytz.utc)
        return cls(utc_datetime.strftime(STRFTIME_FORMAT))

    @classmethod
    def from_iso8601(cls, iso8601: str) -> "Timestamp":
        """
        Creates a Timestamp object from a ISO 8601 datetime string.

        Args:
            iso8601 (str): The ISO 8601 datetime string in the format
                            YYYY-MM-DDTHH:MM:SS.ssssssZ.

        Returns:
            Timestamp: A Timestamp object initialized with the given ISO 8601 datetime string.
        """
        utc_datetime = datetime.fromisoformat(iso8601)
        return cls(utc_datetime.strftime(STRFTIME_FORMAT))

    # * * * * * String Representation * * * * * #
    def to_epoch(self) -> float:
        """Returns the stored datetime as a Unix epoch time."""
        return self.__utc_datetime.timestamp()

    def to_iso8601(self) -> str:
        """Returns the stored datetime in ISO 8601 format."""
        return self.__utc_datetime.isoformat()

    def to_utc(self) -> str:
        """
        Returns the stored UTC datetime in ISO 8601 format.
        """
        return self.__utc_datetime.strftime(STRFTIME_FORMAT)

    def to_timezone(self, timezone: str = None) -> str:
        """
        Converts the stored UTC datetime to the specified timezone.
        If no timezone is specified, it defaults to the object's timezone.

        Args:
            timezone (str): The desired timezone to convert to.

        Returns:
            str: The converted datetime in the specified or default timezone.
        """
        if timezone is None:
            timezone = self.__timezone

        target_tz = pytz.timezone(timezone)
        localized_datetime = self.__utc_datetime.astimezone(target_tz)
        return localized_datetime.strftime(STRFTIME_FORMAT)

    def to_default_timezone(self) -> str:
        """
        Converts the stored UTC datetime to the default timezone (America/New_York).
        """
        return self.to_timezone(self.get_default_timezone())

    def __str__(self):
        raise NotImplementedError(
            "Use to_utc(), to_timezone(), or to_default_timezone() explicitly instead."
        )

    def __ret__(self):
        return self.__str__()

    # * * * * * Getter and Setter Methods * * * * * #
    def get_timezone(self) -> str:
        """Gets the current timezone."""
        return self.__timezone

    @validate_timezone
    def get_datetime(self, timezone: str = None) -> str:
        """Gets the stored datetime in the current timezone."""
        return self.to_timezone(timezone)

    @validate_timezone
    def set_timezone(self, new_timezone: str):
        """
        Sets a new timezone and updates the stored UTC time accordingly.

        Args:
            new_timezone (str): The new timezone to set.
        """
        # Store the current time in the new timezone
        local_tz = pytz.timezone(new_timezone)
        localized_datetime = self.__utc_datetime.astimezone(local_tz)

        # Update the timezone and store the new UTC time
        self.__timezone = new_timezone
        self.__utc_datetime = localized_datetime.astimezone(pytz.utc)

    @validate_datetime
    def set_datetime(self, datetime_str: str):
        """
        Sets a new datetime and updates the stored UTC time accordingly.

        Args:
            datetime_str (str): The new datetime in the format MM/DD/YY HH:MM {AM/PM}.
        """
        # Parse the datetime string to get a naive datetime object
        naive_datetime = datetime.strptime(datetime_str, STRFTIME_FORMAT)

        # Localize the naive datetime to UTC
        self.__utc_datetime = naive_datetime.astimezone(pytz.utc)

        return self.__utc_datetime

    @validate_datetime_and_timezone
    def set_datetime_and_timezone(self, datetime_str: str):
        """
        Sets the datetime and timezone, converting to UTC for internal storage.

        Args:
            datetime_str (str): The date in the format MM/DD/YY HH:MM {AM/PM} with an optional timezone.
        """
        # Regular expression to check for timezone in the datetime string
        timezone_pattern = r"\b(UTC|EST|EDT|CST|CDT|PST|PDT|MST|MDT)\b"

        # Check for timezone in the datetime string
        if tz_match := re.search(timezone_pattern, datetime_str, re.IGNORECASE):
            self.__timezone = tz_match.group(0).upper()
            datetime_str = re.sub(
                timezone_pattern, "", datetime_str
            ).strip()  # Remove timezone from string
        else:
            # Default to system timezone if none is specified
            self.__timezone = self.get_default_timezone()

        # Parse the datetime string to get a naive datetime object
        naive_datetime = self.set_datetime(datetime_str)

        # Localize the naive datetime to the specified timezone
        local_tz = pytz.timezone(
            "America/New_York"
            if self.__timezone == self.get_default_timezone()
            else self.__timezone
        )
        localized_datetime = local_tz.localize(naive_datetime)

        # Convert to UTC and store
        self.__utc_datetime = localized_datetime.astimezone(pytz.utc)

    # * * * * * Time Arithmetic * * * * * #
    def add_days(self, days: int):
        """Adds a specified number of days to the current time."""
        self.__utc_datetime += timedelta(days=days)

    def subtract_days(self, days: int):
        """Subtracts a specified number of days from the current time."""
        self.__utc_datetime -= timedelta(days=days)

    def add_hours(self, hours: int):
        """Adds a specified number of hours to the current time."""
        self.__utc_datetime += timedelta(hours=hours)

    def subtract_hours(self, hours: int):
        """Subtracts a specified number of hours from the current time."""
        self.__utc_datetime -= timedelta(hours=hours)

    def add_minutes(self, minutes: int):
        """Adds a specified number of minutes to the current time."""
        self.__utc_datetime += timedelta(minutes=minutes)

    def subtract_minutes(self, minutes: int):
        """Subtracts a specified number of minutes from the current time."""
        self.__utc_datetime -= timedelta(minutes=minutes)

    # * * * * * Comparison Operators * * * * * #
    def _lt__(self, other: "Timestamp") -> bool:
        """Checks if the current time is before an_other Timestamp object."""
        return self.__utc_datetime < other.__utc_datetime

    def _le__(self, other: "Timestamp") -> bool:
        """Checks if the current time is before or equal to an_other Timestamp object."""
        return self.__utc_datetime <= other.__utc_datetime

    def _eq__(self, other: "Timestamp") -> bool:
        """Checks if the current time is equal to an_other Timestamp object."""
        return self.__utc_datetime == other.__utc_datetime

    def _ne__(self, other: "Timestamp") -> bool:
        """Checks if the current time is not equal to an_other Timestamp object."""
        return self.__utc_datetime != other.__utc_datetime

    def _gt__(self, other: "Timestamp") -> bool:
        """Checks if the current time is after an_other Timestamp object."""
        return self.__utc_datetime > other.__utc_datetime

    def _ge__(self, other: "Timestamp") -> bool:
        """Checks if the current time is after or equal to an_other Timestamp object."""
        return self.__utc_datetime >= other.__utc_datetime

    # * * * * * Utility Methods * * * * * #
    def time_difference(self, other: "Timestamp") -> str:
        """Returns a human-readable string showing the difference between two Timestamp objects."""
        delta = self.__utc_datetime - other.__utc_datetime
        return f"{delta.days} days, {delta.seconds // 3600} hours, {delta.seconds // 60 % 60} minutes"
