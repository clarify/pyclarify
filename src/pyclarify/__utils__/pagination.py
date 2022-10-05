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
from pyclarify.query.filter import DataFilter

from pyclarify.views.generics import Request
from .time import compute_iso_timewindow
from .payload import unpack_params


class SegmentIterator:
    """
    The iterator chucks resources into legal segments as constrained by the API. The iterator returns the next legal chunk
    of resources and separates them into the starting point(skip) and how many resources to retrieve (limit).

    Parameters
    ----------
    user_limit: int
        The number describing how many resources the user wants to be returned.

    limit_per_call: int
        An int describing the limit of how many resources can be returned by the API.

    skip: int
        How many resources to skip starting from the beginning of the returned list of resources.
        Think of this as the starting point.

    Returns
    -------
    skip
        The starting point of where to retrieve resources
    limit
        The number of resources to retrieve
    """

    def __init__(self, user_limit, limit_per_call, skip):
        self.remaining_resources = user_limit
        self.LIMIT_PER_CALL = limit_per_call
        self.skip = skip

    def __iter__(self):
        self.ending_condition = False
        return self

    def __next__(self):
        if self.ending_condition:
            raise StopIteration
        if self.remaining_resources > self.LIMIT_PER_CALL:
            self.remaining_resources -= self.LIMIT_PER_CALL
            self.skip += self.LIMIT_PER_CALL
            return self.skip - self.LIMIT_PER_CALL, self.LIMIT_PER_CALL
        else:
            self.ending_condition = True
            return self.skip, self.remaining_resources


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

    rollup: `RFC3339 duration <https://docs.clarify.io/api/1.1beta2/types/fields#fixed-duration>`__ or "window", default None
                    If `RFC3339 duration <https://docs.clarify.io/api/1.1beta2/types/fields#fixed-duration>`__ is specified, roll-up the values into either the full time window
                    (`notBefore` -> `before`) or evenly sized buckets.

    window_size: `RFC3339 duration <https://docs.clarify.io/api/1.1beta2/types/fields#fixed-duration>`__, default None
                If `RFC3339 duration <https://docs.clarify.io/api/1.1beta2/types/fields#fixed-duration>`__ is specified, the iterator will use the specified window as a paging size instead
                of default API limits. This is commonly used when resolution of data is too high to be packaged with default
                values.

    Returns
    -------
    current_start_time
        The notBefore parameter to be used in an API call.
    current_end_time
        The before parameter to be used in an API call
    """

    def __init__(self, start_time=None, end_time=None, rollup=None, window_size=None):
        start_time, end_time = compute_iso_timewindow(start_time, end_time)
        self.current_start_time = parse_datetime(start_time)
        self.GLOBAL_END_TIME = parse_datetime(end_time)

        # CONSTRAINT: Time window from an API call cannot be longer than 40 days if rollup is smaller than 1 minute
        self.API_LIMIT = timedelta(days=40)
        if rollup:
            if rollup == "window":
                self.rollup = rollup
            else:
                self.rollup = parse_duration(rollup)
                # CONSTRAINT: 400 days constraint if rollup is larger than 1 minute
                if self.rollup > timedelta(minutes=1):
                    self.API_LIMIT = timedelta(days=400)
        else:
            self.rollup = rollup
        if window_size:
            self.API_LIMIT = parse_duration(window_size)


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
            # If time window is smaller than API limit we end iterator
            self.ending_condition = True
            return self.current_start_time, self.GLOBAL_END_TIME



class SelectIterator:
    """
    Computes the next request for select queries. 

    Parameters
    ----------
    request: dict/Request

    Returns
    -------
    request: dict/Request
    """

    def __init__(self, request: Request, window_size=None):
        self.request = request
        self.window_size = window_size
        (
            self.API_LIMIT, 
            self.user_limit, 
            self.skip, 
            self.user_gte, 
            self.user_lt, 
            self.rollup
        ) = unpack_params(self.request)

        # support None inputs
        if self.user_limit == None:
            self.user_limit = float("inf")

        self.segment_iterator = iter(SegmentIterator(
                user_limit=self.user_limit, 
                limit_per_call=self.API_LIMIT, 
                skip=self.skip
        ))
        self.current_time_iterator = iter(TimeIterator(
            start_time=self.user_gte, 
            end_time=self.user_lt, 
            rollup=self.rollup, 
            window_size=self.window_size
        ))


    def __iter__(self):
        self.stopping_condition = False
        self.first_iteration = True
        self.skip, self.limit = next(self.segment_iterator)
        return self

    def __next__(self):
        self.request.params.query.skip = self.skip
        self.request.params.query.limit = self.limit
        try:
            start_time, end_time = next(self.current_time_iterator)
            dq = DataFilter(gte=start_time, lt=end_time)
            self.request.params.data.filter = dq.to_query()
        except:            
            try:
                self.skip, self.limit = next(self.segment_iterator)
                self.current_time_iterator = iter(TimeIterator(
                    start_time=self.user_gte, 
                    end_time=self.user_lt, 
                    rollup=self.rollup, 
                    window_size=self.window_size
                ))
            except:
                self.stopping_condition = True
        if self.stopping_condition and not self.first_iteration:
            raise StopIteration
        else:
            self.first_iteration = False
            return self.request
