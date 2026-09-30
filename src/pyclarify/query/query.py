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

from pydantic import BaseModel, ConfigDict, Field
from typing import ClassVar, FrozenSet, Union, List, Dict, Optional
from datetime import datetime, timedelta
from typing_extensions import Literal

from pyclarify.fields.constraints import CalendarDuration, TimeZone, IntWeekDays
from pyclarify.fields.request import OmitNoneModel


class DataQuery(OmitNoneModel):
    # Left out when unset, so the API applies its own defaults.
    omit_if_none: ClassVar[FrozenSet[str]] = frozenset({"outsidePoints", "timeZone", "firstDayOfWeek"})

    outsidePoints: Optional[bool] = None
    filter: Optional[Dict] = {}
    # Durations given as RFC 3339 strings are sent unchanged; other forms, such as a timedelta
    # or a number of seconds, are converted as before.
    rollup: Optional[Union[Literal["window"], CalendarDuration, timedelta]] = Field(union_mode="left_to_right")
    timeZone: Optional[TimeZone] = "UTC"
    firstDayOfWeek: Optional[IntWeekDays] = 1
    origin: Optional[Union[str, datetime]] = None
    last: Optional[int] = -1

    model_config = ConfigDict(extra="forbid")


class ResourceQuery(BaseModel):
    filter: Optional[Dict] = {}
    sort: Optional[List[str]] = None
    limit: Optional[int] = None
    skip: Optional[int] = None
    total: Optional[bool] = None

    model_config = ConfigDict(extra="forbid")
