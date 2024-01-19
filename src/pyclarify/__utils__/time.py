# Copyright 2023 Searis AS

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime, timedelta
import re


"""
Functions to parse datetime objects.

We're using regular expressions rather than time.strptime because:
- They provide both validation and parsing.
- They're more flexible for datetimes.
- The date/datetime/time constructors produce friendlier error messages.

Stolen from https://raw.githubusercontent.com/django/django/main/django/utils/dateparse.py at
9718fa2e8abe430c3526a9278dd976443d4ae3c6

Changed to:
* use standard python datetime types not django.utils.timezone
* raise ValueError when regex doesn't match rather than returning None
* support parsing unix timestamps for dates and datetimes

Yoinked from pydantic V1.10 after they removed it in V2
"""
import re
from datetime import date, datetime, time, timedelta, timezone
from typing import Dict, Optional, Type, Union

date_expr = r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})'
time_expr = (
    r'(?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
    r'(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$'
)

date_re = re.compile(f'{date_expr}$')
time_re = re.compile(time_expr)
datetime_re = re.compile(f'{date_expr}[T ]{time_expr}')

standard_duration_re = re.compile(
    r'^'
    r'(?:(?P<days>-?\d+) (days?, )?)?'
    r'((?:(?P<hours>-?\d+):)(?=\d+:\d+))?'
    r'(?:(?P<minutes>-?\d+):)?'
    r'(?P<seconds>-?\d+)'
    r'(?:\.(?P<microseconds>\d{1,6})\d{0,6})?'
    r'$'
)

# Support the sections of ISO 8601 date representation that are accepted by timedelta
iso8601_duration_re = re.compile(
    r'^(?P<sign>[-+]?)'
    r'P'
    r'(?:(?P<days>\d+(.\d+)?)D)?'
    r'(?:T'
    r'(?:(?P<hours>\d+(.\d+)?)H)?'
    r'(?:(?P<minutes>\d+(.\d+)?)M)?'
    r'(?:(?P<seconds>\d+(.\d+)?)S)?'
    r')?'
    r'$'
)

EPOCH = datetime(1970, 1, 1)
# if greater than this, the number is in ms, if less than or equal it's in seconds
# (in seconds this is 11th October 2603, in ms it's 20th August 1970)
MS_WATERSHED = int(2e10)
# slightly more than datetime.max in ns - (datetime.max - EPOCH).total_seconds() * 1e9
MAX_NUMBER = int(3e20)
StrBytesIntFloat = Union[str, bytes, int, float]


def get_numeric(value: StrBytesIntFloat, native_expected_type: str) -> Union[None, int, float]:
    if isinstance(value, (int, float)):
        return value
    try:
        return float(value)
    except ValueError:
        return None
    except TypeError:
        raise TypeError(f'invalid type; expected {native_expected_type}, string, bytes, int or float')


def from_unix_seconds(seconds: Union[int, float]) -> datetime:
    if seconds > MAX_NUMBER:
        return datetime.max
    elif seconds < -MAX_NUMBER:
        return datetime.min

    while abs(seconds) > MS_WATERSHED:
        seconds /= 1000
    dt = EPOCH + timedelta(seconds=seconds)
    return dt.replace(tzinfo=timezone.utc)


def _parse_timezone(value: Optional[str], error: Type[Exception]) -> Union[None, int, timezone]:
    if value == 'Z':
        return timezone.utc
    elif value is not None:
        offset_mins = int(value[-2:]) if len(value) > 3 else 0
        offset = 60 * int(value[1:3]) + offset_mins
        if value[0] == '-':
            offset = -offset
        try:
            return timezone(timedelta(minutes=offset))
        except ValueError:
            raise error()
    else:
        return None


def parse_date(value: Union[date, StrBytesIntFloat]) -> date:
    """
    Parse a date/int/float/string and return a datetime.date.

    Raise ValueError if the input is well formatted but not a valid date.
    Raise ValueError if the input isn't well formatted.
    """
    if isinstance(value, date):
        if isinstance(value, datetime):
            return value.date()
        else:
            return value

    number = get_numeric(value, 'date')
    if number is not None:
        return from_unix_seconds(number).date()

    if isinstance(value, bytes):
        value = value.decode()

    match = date_re.match(value)  # type: ignore
    if match is None:
        raise ValueError

    kw = {k: int(v) for k, v in match.groupdict().items()}

    try:
        return date(**kw)
    except ValueError:
        raise 


def parse_time(value: Union[time, StrBytesIntFloat]) -> time:
    """
    Parse a time/string and return a datetime.time.

    Raise ValueError if the input is well formatted but not a valid time.
    Raise ValueError if the input isn't well formatted, in particular if it contains an offset.
    """
    if isinstance(value, time):
        return value

    number = get_numeric(value, 'time')
    if number is not None:
        if number >= 86400:
            # doesn't make sense since the time time loop back around to 0
            raise ValueError
        return (datetime.min + timedelta(seconds=number)).time()

    if isinstance(value, bytes):
        value = value.decode()

    match = time_re.match(value)  # type: ignore
    if match is None:
        raise ValueError

    kw = match.groupdict()
    if kw['microsecond']:
        kw['microsecond'] = kw['microsecond'].ljust(6, '0')

    tzinfo = _parse_timezone(kw.pop('tzinfo'), ValueError)
    kw_: Dict[str, Union[None, int, timezone]] = {k: int(v) for k, v in kw.items() if v is not None}
    kw_['tzinfo'] = tzinfo

    try:
        return time(**kw_)  # type: ignore
    except ValueError:
        raise ValueError


def parse_datetime(value: Union[datetime, StrBytesIntFloat]) -> datetime:
    """
    Parse a datetime/int/float/string and return a datetime.datetime.

    This function supports time zone offsets. When the input contains one,
    the output uses a timezone with a fixed offset from UTC.

    Raise ValueError if the input is well formatted but not a valid datetime.
    Raise ValueError if the input isn't well formatted.
    """
    if isinstance(value, datetime):
        return value

    number = get_numeric(value, 'datetime')
    if number is not None:
        return from_unix_seconds(number)

    if isinstance(value, bytes):
        value = value.decode()

    match = datetime_re.match(value)  # type: ignore
    if match is None:
        raise ValueError

    kw = match.groupdict()
    if kw['microsecond']:
        kw['microsecond'] = kw['microsecond'].ljust(6, '0')

    tzinfo = _parse_timezone(kw.pop('tzinfo'), ValueError)
    kw_: Dict[str, Union[None, int, timezone]] = {k: int(v) for k, v in kw.items() if v is not None}
    kw_['tzinfo'] = tzinfo

    try:
        return datetime(**kw_)  # type: ignore
    except ValueError:
        raise ValueError


def parse_duration(value: StrBytesIntFloat) -> timedelta:
    """
    Parse a duration int/float/string and return a datetime.timedelta.

    The preferred format for durations in Django is '%d %H:%M:%S.%f'.

    Also supports ISO 8601 representation.
    """
    if isinstance(value, timedelta):
        return value

    if isinstance(value, (int, float)):
        # below code requires a string
        value = f'{value:f}'
    elif isinstance(value, bytes):
        value = value.decode()

    try:
        match = standard_duration_re.match(value) or iso8601_duration_re.match(value)
    except TypeError:
        raise TypeError('invalid type; expected timedelta, string, bytes, int or float')

    if not match:
        raise ValueError

    kw = match.groupdict()
    sign = -1 if kw.pop('sign', '+') == '-' else 1
    if kw.get('microseconds'):
        kw['microseconds'] = kw['microseconds'].ljust(6, '0')

    if kw.get('seconds') and kw.get('microseconds') and kw['seconds'].startswith('-'):
        kw['microseconds'] = '-' + kw['microseconds']

    kw_ = {k: float(v) for k, v in kw.items() if v is not None}

    return sign * timedelta(**kw_)

def time_to_string(time):
    return time.astimezone().isoformat()


def compute_iso_timewindow(start_time, end_time):
    if not start_time and end_time:
        end_time = parse_datetime(end_time)
        start_time = end_time - timedelta(days=40)
    elif start_time and not end_time:
        start_time = parse_datetime(start_time)
        end_time = start_time + timedelta(days=40)
    elif not start_time and not end_time:
        end_time = datetime.now() + timedelta(days=7)
        start_time = end_time - timedelta(days=14)
    else:
        end_time = parse_datetime(end_time)
        start_time = parse_datetime(start_time)
    return start_time, end_time

def is_datetime(value):
    if isinstance(value, str):
        parts = re.findall(r'\d+', value)
        if len(parts) == 3:
            parts = [int(p) for p in parts]

            # Assuming middle value is month
            month = parts[1]

            # Assuming the biggest number is the year
            if parts[0] > parts[-1]:
                year = parts[0]
                day = parts[-1]
            else:
                year = parts[-1]
                day = parts[0]
            value = datetime(year=year, month=month, day=day)
    try:
        # if value is bigger than 1973 and less than 2122 (should be good for 99% of use cases)
        lower_threshold = parse_datetime(100000000).timestamp()
        upper_threshold = parse_datetime(4800000000).timestamp()
        v = parse_datetime(value).timestamp()

        return  (v > lower_threshold) and (v < upper_threshold)
    except:
        return False
