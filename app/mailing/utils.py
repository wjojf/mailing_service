import pytz
from datetime import datetime

TIMEZONES_LIST = pytz.all_timezones
TIMEZONES_CHOICES = tuple(zip(TIMEZONES_LIST, TIMEZONES_LIST))
DEFAULT_TIMEZONE = [x[0] for x in TIMEZONES_LIST if x.lower().strip() == "universal"][0]
ERROR_TIMEZONE_MESSAGE = "Not a valid timezone"


def get_timezone_current_time(timezone: str, tz_list=TIMEZONES_LIST) -> datetime:
    assert timezone in tz_list, ERROR_TIMEZONE_MESSAGE
    return datetime.now(tz=pytz.timezone(timezone))


def alter_datetime_timezone(dt: datetime, timezone: str, tz_list=TIMEZONES_LIST) -> datetime:
    assert timezone in tz_list, ERROR_TIMEZONE_MESSAGE
    return dt.replace(tzinfo=pytz.timezone(timezone))


def get_closer_date(start_time: datetime, timezone: str, tz_list=TIMEZONES_LIST) -> datetime:
    assert timezone in tz_list, ERROR_TIMEZONE_MESSAGE
    return max(start_time, datetime.now(tz=pytz.timezone(timezone)))


def get_utc_start_time(start_time: datetime):
    return start_time.astimezone(pytz.timezone("UTC"))