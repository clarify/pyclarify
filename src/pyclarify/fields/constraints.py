# Copyright 2023-2024 Searis AS

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from pydantic import AfterValidator, Field, StringConstraints
from typing import List, Union, Dict
from enum import Enum
from typing_extensions import Annotated
from pyclarify.__utils__.time import is_calendar_duration


State = Annotated[int, Field(ge=0, lt=10000)]
BucketOffset = Annotated[int, Field(ge=-1000, le=1000)]


# constrained string defined by the API
InputID = Annotated[str, Field(pattern=r"^^[a-zA-Z0-9-_:.#+/]{1,128}$")]
ResourceID = Annotated[str, Field(pattern=r"^[a-v0-9]{20}$")]
LabelsKey = Annotated[str, Field(pattern=r"^[A-Za-z0-9-_/]{1,128}$")]
AnnotationKey = Annotated[str, Field(pattern=r"^[A-Za-z0-9-_/]{1,128}$")]
NumericalValuesType = List[Union[float, int, None]]
SHA1Hash = Annotated[str, Field(pattern=r"^[a-f0-9]{5,40}$")]
IntegrationID = Annotated[str, Field(pattern=r"^[a-v0-9]{20}$")]
LimitSelectItems = Annotated[int, Field(ge=0, le=1000)]
LimitSelectSignals = Annotated[int, Field(ge=0, le=1000)]
Annotations = Dict[AnnotationKey, str]
Alias = Annotated[str, Field(pattern="^[A-Za-z_][A-Za-z0-9_]{0,27}$")]
IntWeekDays = Annotated[int, Field(ge=1, le=7)]


def _check_calendar_duration(value: str) -> str:
    if not is_calendar_duration(value):
        raise ValueError(f"{value!r} is not an RFC 3339 duration such as 'PT1H' or 'P1M'")
    return value


# An RFC 3339 duration kept as given: months and years have no fixed length, so converting to
# a timedelta would change them (P1M would become P30D).
CalendarDuration = Annotated[str, AfterValidator(_check_calendar_duration)]


TimeZone = str


class ApiMethod(str, Enum):
    # The API 1.1 names, which API 1.2 keeps as aliases for its renamed methods.
    insert = "integration.insert"
    save_signals = "integration.saveSignals"
    select_items = "clarify.selectItems"
    data_frame = "clarify.dataFrame"
    evaluate = "clarify.evaluate"
    select_signals = "admin.selectSignals"
    publish_signals = "admin.publishSignals"
    # New in API 1.2.
    connect_signals = "admin.signals.connect"
    disconnect_signals = "admin.signals.disconnect"


class SourceTypeSignal(str, Enum):
    measurement = "measurement"
    aggregation = "aggregation"
    prediction = "prediction"


class TypeSignal(str, Enum):
    numeric = "numeric"
    enum = "enum"


class TimeAggregationMethod(Enum):
    count = "count"
    min = "min"
    max = "max"
    sum = "sum"
    avg = "avg"
    state_seconds = "state-seconds"
    state_percent = "state-percent"
    state_rate = "state-rate"
    first = "first"
    last = "last"
    # deprecated names for the same three methods as above
    state_histogram_seconds = "state-seconds"
    state_histogram_percent = "state-percent"
    state_histogram_rate = "state-rate"


class GroupAggregationMethod(Enum):
    count = "count"
    min = "min"
    max = "max"
    sum = "sum"
    avg = "avg"
