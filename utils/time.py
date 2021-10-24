import time

SECONDS_TO_MILLIS: int = 1000
MINUTES_TO_MILLIS: int = 60 * SECONDS_TO_MILLIS
HOURS_TO_MILLIS: int = 60 * MINUTES_TO_MILLIS
DAYS_TO_MILLIS: int = 24 * HOURS_TO_MILLIS

def current_time_millis():
    return int(time.time() * 1000)
