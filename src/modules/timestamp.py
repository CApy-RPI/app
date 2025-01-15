import re
import pytz
from datetime import datetime, timezone


def now():
    """
    Returns the current time in the America/New_York timezone in the format
    %Y-%m-%d %H:%M:%S %Z %z.

    Returns:
        The current time in the America/New_York timezone.
    """
    return str(datetime.now(timezone.utc))


def format_time(_datetime: str) -> str:
    """
    Formats the given date and time into the same format as the now() function in UTC.

    Args:
        _datetime (str): The date in the format MM/DD/YY HH:MM {AM/PM} with an optional timezone.

    Returns:
        str: The formatted time in UTC.
    """
    # Regular expression to check if the datetime contains a timezone (like EST, PST, UTC, etc.)
    datetime_tz = get_timezone(_datetime)

    # Remove the timezone from the original datetime string if it exists
    _datetime = re.sub(datetime_tz, "", _datetime).strip()

    # Parse the datetime string to a naive datetime object (without timezone)
    naive_datetime = datetime.strptime(_datetime, "%m/%d/%y %I:%M %p")

    # Convert the naive datetime to the appropriate timezone
    local_tz = pytz.timezone(get_full_timezone(datetime_tz))
    localized_datetime = local_tz.localize(naive_datetime)

    # Convert to UTC
    utc_datetime = localized_datetime.astimezone(pytz.utc)

    # Return the formatted datetime in UTC (ISO 8601 format)
    return utc_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")


def get_timezone(input_str: str) -> str:

    # Regular expression to check if the datetime contains a timezone (like EST, PST, UTC, etc.)
    timezone_pattern = r"\b(UTC|EST|EDT|CST|CDT|PST|PDT|MST|MDT)\b"

    if tz_match := re.search(timezone_pattern, input_str, re.IGNORECASE):
        # Extract the timezone if it exists
        return tz_match.group(0).upper()
    else:
        # Assume EDT if no timezone is provided
        return "EDT"


def get_full_timezone(timezone_str: str) -> str:
    """
    Maps a timezone short form to its full timezone name.

    Args:
        timezone_str (str): The short form of the timezone (e.g., 'EST', 'PST').

    Returns:
        str: The full timezone name (e.g., 'America/New_York').
    """
    # Dictionary to map timezone short forms to full timezone names
    timezone_mapping = {
        "EST": "America/New_York",
        "EDT": "America/New_York",
        "CST": "America/Chicago",
        "CDT": "America/Chicago",
        "MST": "America/Denver",
        "MDT": "America/Denver",
        "PST": "America/Los_Angeles",
        "PDT": "America/Los_Angeles",
        "UTC": "UTC",
    }

    # Check if the provided timezone_str is in the mapping, if not, default to "America/New_York"
    return timezone_mapping.get(timezone_str, "America/New_York")


def localize_datetime(utc_datetime: str, timezone_str: str) -> str:
    """
    Localizes a given UTC datetime string to the specified timezone.

    Args:
        utc_datetime (str): The UTC datetime string in ISO 8601 format.
        timezone_str (str): The timezone to localize to (e.g., 'America/New_York').

    Returns:
        str: The localized datetime string in the specified timezone.
    """
    # Get the full timezone string using the new function
    full_timezone_str = get_full_timezone(timezone_str)

    # Parse the UTC datetime string to a datetime object
    utc_dt = datetime.strptime(utc_datetime, "%Y-%m-%d %H:%M:%S %Z")

    # Convert the UTC datetime to the specified timezone
    local_tz = pytz.timezone(full_timezone_str)
    localized_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)

    # Return the localized datetime in 12-hour format
    return localized_dt.strftime("%Y-%m-%d %I:%M %p %Z")
