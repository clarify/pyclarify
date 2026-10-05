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


from datetime import timedelta
from pydantic import AliasChoices, ConfigDict, BaseModel, Field
from pydantic.json import timedelta_isoformat
from typing import ClassVar, FrozenSet, List, Dict, Optional, Union
from pyclarify.fields.constraints import (
    TypeSignal,
    SourceTypeSignal,
    LabelsKey,
    InputID,
    ResourceID,
    IntegrationID,
    Annotations,
)
from pyclarify.fields.query import SelectionFormat
from pyclarify.fields.request import OmitNoneModel
from pyclarify.fields.resource import BaseResource, RelationshipsDictSignal
from pyclarify.query.query import ResourceQuery


class SignalInfo(OmitNoneModel):
    """
    Base attributes shared by most signal structures.

    Parameters
    ----------
    name: string(len:1-128)
        A human-readable name for the resource.

    description: string(len:0-1000)
        A free-form description of the resource.

    labels: Labels
        A map of custom classification attributes. Filtering is done on label keys (labels.<key>).

    sourceType: string(enum)
        Classification of the data source. The value must be "aggregate", "measurement" or "prediction".

    valueType: string(enum)
        How to interpret time-series data points. The value must be "enum" or "numeric".

    engUnit: string
        Engineering unit for time-series data in numeric representations.

    enumValues: map(string => string(len:1-128))
        Map of numeric values to display text in enum representations. The key must represent an integer in range 0-9999.

    sampleInterval: Fixed Duration, null
        The expected distance between data points.

    gapDetection: Fixed Duration, null
        The maximum distance between two data-points before considering it to be a gap.

    :meta private:
    """

    name: str
    description: str = ""
    labels: Dict[LabelsKey, List[str]] = {}
    sourceType: SourceTypeSignal = SourceTypeSignal.measurement
    valueType: TypeSignal = TypeSignal.numeric
    engUnit: str = ""
    enumValues: Dict[str, str] = {}
    sampleInterval: Optional[timedelta] = None
    gapDetection: Optional[timedelta] = None
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(json_encoders={timedelta: timedelta_isoformat}, extra="forbid")


class Signal(SignalInfo):
    """
    Model for sending Signal metadata to Clarify.

    Parameters
    ----------

    name: string(len:1-128)
        A human-readable name for the resource.

    description: string(len:0-1000)
        A free-form description of the resource.

    labels: Labels
        A map of custom classification attributes. Filtering is done on label keys (labels.<key>).

    sourceType: string(enum)
        Classification of the data source. The value must be "aggregate", "measurement" or "prediction".

    valueType: string(enum)
        How to interpret time-series data points. The value must be "enum" or "numeric".

    engUnit: string
        Engineering unit for time-series data in numeric representations.

    enumValues: map(string => string(len:1-128))
        Map of numeric values to display text in enum representations. The key must represent an integer in range 0-9999.

    sampleInterval: Fixed Duration, null
        The expected distance between data points.

    gapDetection: Fixed Duration, null
        The maximum distance between two data-points before considering it to be a gap.

    annotations: Annotations
        A key-value store where integrations can store programmatic meta-data about the resource instance.
        Filtering is done on member fields.

    
    Example
    -------
    
        >>> from pyclarify import Signal
    
        Creating a signal a minimal signal.

        >>> signal = Signal(name="My new signal")

        Creating a signal with all attributes set.

        >>> signal = Signal(
        ...     name="My new signal"
        ...     description="This signal is an example."
        ...     labels={
        ...         "environment": ["dev", "mocking"],
        ...         "unit":["cloud"]
        ...     }
        ...     engUnit="℃"
        ...     sampleInterval="PT30S"
        ...     gapDetection="PT5M"   
        ... )

        Creating an enum signal.

        >>> signal = Signal(
        ...     name="My new enum signal"
        ...     description="This enum signal is an example."
        ...     labels={
        ...         "environment": ["dev", "mocking"],
        ...         "unit":["cloud"]
        ...     }
        ...     valueType="enum"
        ...     enumValues={
        ...         "0" : "Wind",
        ...         "1" : "Rain",
        ...         "2" : "Cloudy"
        ...     }
        ...     sampleInterval="PT30S"
        ...     gapDetection="PT5M"
        ... )
    """

    # Annotations are merged, so leaving them out keeps the existing ones. sampleInterval and
    # gapDetection are still sent as null when unset, as in 0.6.
    omit_if_none: ClassVar[FrozenSet[str]] = frozenset({"annotations"})

    annotations: Optional[Annotations] = None


class SavedSignal(SignalInfo):
    """
    Signal attributes as returned by the API. Unlike Signal, it keeps fields it does not know
    and accepts enum values added by newer API versions.

    :meta private:
    """
    sourceType: Union[SourceTypeSignal, str] = Field(SourceTypeSignal.measurement, union_mode="left_to_right")
    valueType: Union[TypeSignal, str] = Field(TypeSignal.numeric, union_mode="left_to_right")
    input: str
    integration: Optional[IntegrationID] = None
    item: Optional[ResourceID] = None
    model_config = ConfigDict(extra="allow")


class SignalSelectView(BaseResource):
    """
    :meta private:
    """
    attributes: SavedSignal
    relationships: RelationshipsDictSignal


class SelectSignalsParams(BaseModel):
    """
    :meta private:
    """
    integration: IntegrationID
    query: ResourceQuery
    include: List[str] = []
    format: SelectionFormat = SelectionFormat()


class ConnectSignalsParams(BaseModel):
    """
    :meta private:
    """
    integration: IntegrationID
    query: ResourceQuery
    item: ResourceID
    dryRun: bool = False
    include: List[str] = []
    format: SelectionFormat = SelectionFormat()


class DisconnectSignalsParams(BaseModel):
    """
    :meta private:
    """
    integration: IntegrationID
    query: ResourceQuery
    dryRun: bool = False
    include: List[str] = []
    format: SelectionFormat = SelectionFormat()


class SaveSignalsParams(BaseModel):
    """
    :meta private:
    """
    integration: IntegrationID
    # "inputs" is the API 1.0 name, still accepted when building the params.
    signalsByInput: Dict[InputID, Signal] = Field(validation_alias=AliasChoices("signalsByInput", "inputs"))
    createOnly: Optional[bool] = False
    model_config = ConfigDict(extra="forbid")



class SaveSummary(BaseModel):
    """
    :meta private:
    """
    id: ResourceID
    created: bool
    updated: bool
    model_config = ConfigDict(extra="allow")


class SaveSignalsResponse(BaseModel):
    """
    :meta private:
    """
    signalsByInput: Dict[InputID, SaveSummary]
    model_config = ConfigDict(extra="allow")
