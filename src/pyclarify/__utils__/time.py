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
from pydantic.datetime_parse import parse_datetime
from datetime import datetime, timedelta

# Convenient method to time to string from datetime and vice versa
def time_to_string(time):
    time_syntax = "%Y-%m-%dT%H:%M:%SZ"
    return datetime.strftime(time, time_syntax)

def compute_iso_timewindow(start_time, end_time):
    if not start_time and end_time:
        end_time = parse_datetime(end_time)
        start_time = end_time - timedelta(days=40)
    elif start_time and not end_time:
        start_time = parse_datetime(start_time)
        end_time = start_time + timedelta(days=40)
    elif not start_time and not end_time:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=40)
    else:
        end_time = parse_datetime(end_time)
        start_time = parse_datetime(start_time)
    return time_to_string(start_time), time_to_string(end_time)
