import pytz


TIMEZONES = tuple(zip(pytz.all_timezones, pytz.all_timezones))
DEFAULT_TIMEZONE = [x[0] for x in TIMEZONES if x[0].lower().strip() == "universal"][0]