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

from datetime import timedelta
from pydantic.datetime_parse import parse_datetime, parse_duration


class TimeIterator:
    """
    Computes the total time window off an API call and chucks it into legal segments as constrained by the API. The 
    iterator returns the next legal chunk of time and separates them into notBefore and before parameters.

    Parameters
    ----------
    start_time: str/datetime 
        The global start time of the API call. This is the time that the user put in the notBefore parameter.
        It is the first date to be returned from the API.

    end_time: str/datetime
        The global end time of the API call. This is the time that the user put in the before parameter. 
        It is the final date to be returned from the API.

    rollup: RFC 3339 duration or "window", default None
                    If RFC 3339 duration is specified, roll-up the values into either the full time window
                    (`notBefore` -> `before`) or evenly sized buckets.
                    
    Returns
    -------
    current_start_time
        The notBefore parameter to be used in an API call.
    current_end_time 
        The before parameter to be used in an API call
    """

    def __init__(self, start_time, end_time, rollup=None):
        self.current_start_time = parse_datetime(start_time).replace(tzinfo=None)
        self.GLOBAL_END_TIME = parse_datetime(end_time).replace(tzinfo=None)

        # CONSTRAINT: Timewindow from an API call cannot be longer than 40 days if rollup is smaller than 1 minute
        self.API_LIMIT = timedelta(days=40)
        if rollup:
            if rollup == "window":
                self.rollup = rollup
            else:
                self.rollup = parse_duration(rollup)
                # CONSTRAINT: 400 days contraint if rollup is larger than 1 minute
                if self.rollup > timedelta(minutes=1):
                    self.API_LIMIT = timedelta(days=400)
        else:
            self.rollup = rollup
        

    def __iter__(self):
        self.ending_condition = False
        return self

    def __next__(self):
        if self.ending_condition:
            raise StopIteration
        
        # EDGE CONDITION: if rollup = "window" the API call should just return 1 timestamp
        if self.rollup == "window":
            self.ending_condition = True
            return self.current_start_time, self.GLOBAL_END_TIME

        # compute time window of current timestamps
        time_window = self.GLOBAL_END_TIME - self.current_start_time

        if time_window > self.API_LIMIT:
            self.current_start_time += self.API_LIMIT

            return self.current_start_time - self.API_LIMIT, self.current_start_time
        else:
            # If timewindow is smaller than API limit we end iterator
            self.ending_condition = True
            return self.current_start_time, self.GLOBAL_END_TIME


class ItemIterator:
    """
    The iterator chucks items into legal segments as constrained by the API. The iterator returns the next legal chunk 
    of items and separates them into the starting point(skip) and how many items to retrieve (limit).

    Parameters
    ----------
    user_limit: int 
        The number describing how many items the user wants to be returned.

    limit_per_call: int
        An int desribing the limit of how many items can be returned by the API.
    
    skip: int
        How many items to skip starting from the beginning of the returned list of items. 
        Think of this as the starting point.

    Returns
    -------
    skip
        The starting point of where to retrieve items
    limit 
        The number of items to retrieve
    """

    def __init__(self, user_limit, limit_per_call, skip):
        self.remaining_items = user_limit
        self.LIMIT_PER_CALL = limit_per_call
        self.skip = skip

    def __iter__(self):
        self.ending_condition = False
        return self

    def __next__(self):
        if self.ending_condition:
            raise StopIteration
        if self.remaining_items > self.LIMIT_PER_CALL:
            self.remaining_items -= self.LIMIT_PER_CALL
            self.skip += self.LIMIT_PER_CALL
            return self.skip - self.LIMIT_PER_CALL, self.LIMIT_PER_CALL
        else:
            self.ending_condition = True
            return self.skip, self.remaining_items
