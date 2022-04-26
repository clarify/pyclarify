"""
Copyright 2022 Searis AS

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from datetime import datetime, timedelta


def timedelta_isoformat(td: timedelta) -> str:
    """
    ISO 8601 encoding for timedeltas.
    """
    minutes, seconds = divmod(td.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    result = "P"
    if td.days > 0:
        result += f"{td.days}D"
    result += "T" + "".join(
        [
            f"{n:d}{l}"
            for l, n in zip(["H", "M", "S"], [hours, minutes, seconds])
            if n > 0
        ]
    )
    return result


def rfc3339_to_timedelta(rfc):
    # if timedelta is none or edge condition
    if not rfc or rfc == "window":
        return timedelta(seconds=0)

    # split RFC to days and time of day
    days, time = rfc.split("T")
    # create kwargs for timedelta
    kwargs = {}

    # Filter out number of days
    days = "".join(filter(str.isdigit, days))
    if days != "":
        # add number of days to kwargs
        kwargs["days"] = eval(days)

    # translate RFC3339 lingo to datetime.timedelta jargon
    translate = {"h": "hours", "m": "minutes", "s": "seconds"}
    tmp = ""
    # iterate through time of day portion
    for c in time:
        if c.isalpha():
            kwargs[translate[c.lower()]] = eval(tmp)
            tmp = ""
        else:
            tmp += c

    return timedelta(**kwargs)


# Convenient method to time to string from datetime and vice versa
time_syntax = "%Y-%m-%dT%H:%M:%SZ"


def time_to_string(time):
    return datetime.strftime(time, time_syntax)


def string_to_time(string):
    return datetime.strptime(string, time_syntax)


def parse_to_datetime(time):
    if not time:
        return time
    elif isinstance(time, datetime):
        return time
    elif isinstance(time, str):
        time = string_to_time(time)
    elif isinstance(time, int):
        time = datetime.fromtimestamp(time)
    else:
        print(f"could not parse time: {time}")  # TODO: Throw exception
    return time


def compute_iso_timewindow(start_time, end_time):
    start_time = parse_to_datetime(start_time)
    end_time = parse_to_datetime(end_time)

    if not start_time and end_time:
        start_time = end_time - timedelta(days=40)
    elif start_time and not end_time:
        end_time = start_time + timedelta(days=40)
    elif not start_time and not end_time:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=40)

    return time_to_string(start_time), time_to_string(end_time)


def compute_timedelta(start_time, end_time):
    start_time = parse_to_datetime(start_time)
    end_time = parse_to_datetime(end_time)
    return end_time - start_time


def datetime_to_str(o):
    date = datetime.strftime(o, "%Y-%m-%dT%H:%M:%SZ")
    return date
