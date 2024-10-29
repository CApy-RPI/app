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
    timezone_pattern = r"\b(UTC|EST|EDT|CST|CDT|PST|PDT|MST|MDT)\b"

    if tz_match := re.search(timezone_pattern, _datetime, re.IGNORECASE):
        # Extract the timezone if it exists
        tz_str = tz_match.group(0).upper()
    else:
        # Assume EDT if no timezone is provided
        tz_str = "EDT"

    # Remove the timezone from the original datetime string if it exists
    _datetime = re.sub(timezone_pattern, "", _datetime).strip()

    # Parse the datetime string to a naive datetime object (without timezone)
    naive_datetime = datetime.strptime(_datetime, "%m/%d/%y %I:%M %p")

    # Convert the naive datetime to the appropriate timezone
    local_tz = pytz.timezone("America/New_York" if tz_str == "EDT" else tz_str)
    localized_datetime = local_tz.localize(naive_datetime)

    # Convert to UTC
    utc_datetime = localized_datetime.astimezone(pytz.utc)

    # Return the formatted datetime in UTC (ISO 8601 format)
    return utc_datetime.strftime("%Y-%m-%d %H:%M:%S %Z")
