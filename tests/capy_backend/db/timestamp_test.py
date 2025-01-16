from datetime import datetime, timezone
import pytz
from capy_backend.db.timestamp import Timestamp


def test_timestamp_creation():
    ts = Timestamp()
    assert isinstance(ts.get_utc_time(), datetime)


def test_timestamp_from_utc():
    utc_time = datetime.now(timezone.utc)
    ts = Timestamp.from_utc(utc_time)
    assert ts.get_utc_time() == utc_time


def test_timestamp_str():
    ts = Timestamp()
    ny_tz = pytz.timezone("America/New_York")
    est_time = ts.get_utc_time().astimezone(ny_tz)
    assert str(ts) == est_time.strftime("%Y-%m-%d %H:%M:%S %Z")


def test_timestamp_to_json():
    ts = Timestamp()
    assert ts.to_json() == ts.get_utc_time().isoformat()
