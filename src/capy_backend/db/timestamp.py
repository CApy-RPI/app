from datetime import datetime, timezone
import pytz


class Timestamp:
    def __init__(self) -> None:
        self.__utc_time: datetime = datetime.now(timezone.utc)

    @classmethod
    def from_utc(cls, utc_time: datetime) -> "Timestamp":
        instance = cls.__new__(cls)
        instance.__utc_time = utc_time
        return instance

    def get_utc_time(self) -> datetime:
        return self.__utc_time

    def to_json(self) -> str:
        return self.__utc_time.isoformat()

    def to_est(self) -> str:
        ny_tz = pytz.timezone("America/New_York")
        est_time = self.__utc_time.astimezone(ny_tz)
        return est_time.strftime("%Y-%m-%d %H:%M:%S %Z")

    def __str__(self) -> str:
        return self.to_est()
