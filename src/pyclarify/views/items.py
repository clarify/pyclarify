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

from datetime import timedelta, datetime
from pydantic import BaseModel, Extra
from pydantic.json import timedelta_isoformat
from pydantic.fields import Optional
from typing import List, Dict, Union
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
from pyclarify.fields.resource import BaseResource
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
    sampleInterval: timedelta = None
    gapDetection: timedelta = None

    class Config:
        json_encoders = {timedelta: timedelta_isoformat}
        extra = Extra.forbid


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

    annotations: Optional[Annotations]
    visible: bool = False


class SelectItemsDataParams(BaseModel, extra=Extra.forbid):
    """
    :meta private:
    """
    include: Optional[bool] = False
    notBefore: Optional[datetime]
    before: Optional[datetime]
    rollup: Optional[Union[timedelta, Literal["window"]]]


class SelectItemsParams(BaseModel, extra=Extra.forbid):
    """
    :meta private:
    """
    query: Optional[ResourceQuery] = {}
    include: Optional[List[str]] = []
    groupIncludedByType: bool = True


class ItemSelectView(BaseResource):
    """
    :meta private:
    """
    attributes: Item


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


{'jsonrpc': '2.0', 'id': '1', 'result': {'meta': {'total': -1, 'groupIncludedByType': True}, 'data': [{'type': 'signals', 'id': 'cbpmaq6rpn52969vfk70', 'meta': {'attributesHash': '7db601f42a56ae88ef93328038578c0119611b9b', 'relationshipsHash': 'ac55c70f73c20e38394fb64d7b7fb2e848ae568b', 'annotations': {}, 'createdAt': '2022-08-10T07:59:36.018Z', 'updatedAt': '2022-10-03T13:43:23.452Z'}, 'attributes': {'name': 'Signal 39', 'description': '', 'valueType': 'numeric', 'sourceType': 'measurement', 'engUnit': '', 'sampleInterval': None, 'gapDetection': None, 'labels': {}, 'enumValues': {}, 'input': 'test_signal_39'}, 'relationships': {'item': {'data': {'type': 'items', 'id': 'cbpmaq6rpn52969vfl00'}}}}]}}
