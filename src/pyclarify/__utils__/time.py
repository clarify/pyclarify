"""
Copyright 2023 Searis AS

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
from pydantic.datetime_parse import parse_datetime
from datetime import datetime, timedelta
import re


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
