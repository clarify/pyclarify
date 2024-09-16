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


from pydantic import Field, StringConstraints
from typing import List, Union, Dict
from enum import Enum
from typing_extensions import Annotated


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
IntWeekDays = Annotated[int, Field(ge=0, le=6)]


TimeZone = str


class ApiMethod(str, Enum):
    insert = "integration.Insert"
    save_signals = "integration.SaveSignals"
    select_items = "clarify.SelectItems"
    data_frame = "clarify.dataFrame"
    evaluate = "clarify.evaluate"
    select_signals = "admin.SelectSignals"
    publish_signals = "admin.PublishSignals"


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
