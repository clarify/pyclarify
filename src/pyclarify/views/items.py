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


from datetime import timedelta, datetime
from pydantic import ConfigDict, BaseModel, Extra
from pydantic.json import timedelta_isoformat
from typing import List, Dict, Union, Optional
from typing_extensions import Literal
from pyclarify.fields.constraints import (
    Annotations,
    TypeSignal,
    SourceTypeSignal,
    LabelsKey,
    AnnotationKey,
    ResourceID,
    IntegrationID,
)
from pyclarify.fields.query import SelectionFormat
from pyclarify.fields.resource import BaseResource, RelationshipsDictItem
from pyclarify.query.query import ResourceQuery


class ItemInfo(BaseModel):
    """
    Base attributes shared by most item structures.

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
    visible: bool = False
    # TODO[pydantic]: The following keys were removed: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(json_encoders={timedelta: timedelta_isoformat}, extra="forbid")


class Item(ItemInfo):
    """
    Item model for sending Item meta data to Clarify.

    Parameters
    ----------
    name: string(len:1-128)
        A human-readable name for the resource.

    description: string(len:0-1000)
        A free-form description of the resource.

    labels: Dict[LabelsKey, List[str]]
        A map of custom classification attributes. Filtering is done on label keys (labels.<key>).
        LabelsKey is alphanumeric string up to 128 chars. 

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

    visible: bool
        Whether the item should be visible for your entire organization within Clarify or not.

    annotations: Dict[AnnotationKey, str]
        A key-value store where integrations can store programmatic meta-data about the resource instance. Filtering is done one member fields.
        AnnotationKey is alphanumeric string up to 128 chars.

    Example
    -------
    
        >>> from pyclarify import Item
    
        Creating a minimal item.

        >>> item = Item(name="My new item")

        Creating a item with all attributes set.

        >>> item = Item(
        ...     name="My new item"
        ...     description="This item is an example."
        ...     labels={
        ...         "environment": ["dev", "mocking"],
        ...         "unit":["cloud"]
        ...     }
        ...     engUnit="℃"
        ...     sampleInterval="PT30S"
        ...     gapDetection="PT5M"   
        ... )

        Creating an enum item.

        >>> item = Item(
        ...     name="My new enum item"
        ...     description="This enum item is an example."
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

    Tip
    ---

        Items are hidden by default. If you want them to be visible you can add the attribute ``visible`` and set it to ``True``

        >>> item = Item(name="My new item", visible=True) 
    """

class SelectItemsDataParams(BaseModel, extra=Extra.forbid):
    """
    :meta private:
    """
    include: Optional[bool] = False
    notBefore: Optional[datetime] = None
    before: Optional[datetime] = None
    rollup: Optional[Union[timedelta, Literal["window"]]] = None


class SelectItemsParams(BaseModel, extra=Extra.forbid):
    """
    :meta private:
    """
    query: Optional[ResourceQuery] = {}
    include: Optional[List[str]] = []
    format: SelectionFormat = SelectionFormat()


class ItemSelectView(BaseResource):
    # Note BaseResource (Not BaseModel)
    """
    :meta private:
    """
    attributes: Item
    relationships: Optional[RelationshipsDictItem] = None

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.id == other.id


class ItemSaveView(Item):
    """
    :meta private:
    """
    annotations: Optional[Dict[AnnotationKey, str]] = {}


class PublishSignalsParams(BaseModel):
    """
    :meta private:
    """
    integration: IntegrationID
    itemsBySignal: Dict[ResourceID, Item]
    createOnly: Optional[bool] = False


class SaveSummary(BaseModel, extra=Extra.forbid):
    """
    :meta private:
    """
    id: ResourceID
    created: bool
    updated: bool


class PublishSignalsResponse(BaseModel, extra=Extra.forbid):
    """
    :meta private:
    """
    itemsBySignal: Dict[ResourceID, SaveSummary]
