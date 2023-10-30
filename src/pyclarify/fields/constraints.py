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


from pydantic import constr, conint
from typing import List, Union, Dict
from enum import Enum


State = conint(ge=0, lt=10000)
BucketOffset = conint(ge=-1000, le=1000)


# constrained string defined by the API
InputID = constr(regex=r"^^[a-zA-Z0-9-_:.#+/]{1,128}$")
ResourceID = constr(regex=r"^[a-v0-9]{20}$")
LabelsKey = constr(regex=r"^[A-Za-z0-9-_/]{1,128}$")
AnnotationKey = constr(regex=r"^[A-Za-z0-9-_/]{1,128}$")
NumericalValuesType = List[Union[float, int, None]]
SHA1Hash = constr(regex=r"^[a-f0-9]{5,40}$")
IntegrationID = constr(regex=r"^[a-v0-9]{20}$")
LimitSelectItems = conint(ge=0, le=1000)
LimitSelectSignals = conint(ge=0, le=1000)
Annotations = Dict[AnnotationKey, str]
Alias = constr(regex="^[A-Za-z_][A-Za-z0-9_]{0,27}$")
IntWeekDays = conint(ge=0, le=6)


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


class DataAggregation(Enum):
    count = "count"
    min = "min"
    max = "max"
    sum = "sum"
    avg = "avg"
    state_histogram_seconds = "state-histogram-seconds"
    state_histogram_percent = "state-histogram-percent"
    state_histogram_rate = "state-histogram-rate"
