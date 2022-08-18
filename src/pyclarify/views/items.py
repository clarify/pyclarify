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
    """

    name: str
    valueType: TypeSignal = TypeSignal.numeric
    description: str = ""
    labels: Dict[LabelsKey, List[str]] = {}
    engUnit: str = ""
    enumValues: Dict[str, str] = {}
    sourceType: SourceTypeSignal = SourceTypeSignal.measurement
    sampleInterval: timedelta = None
    gapDetection: timedelta = None

    class Config:
        json_encoders = {timedelta: timedelta_isoformat}
        extra = Extra.forbid


class Item(ItemInfo):
    """
    Extends ItemInfo class.

    Parameters
    ----------
    visible: bool
        Whether the item should be visible for your entire organization within Clarify or not.

    annotations: Annotations
        A key-value store where integrations can store programmatic meta-data about the resource instance. Filtering is done one member fields.
    """

    annotations: Optional[Annotations]
    visible: bool = False


class SelectItemsDataParams(BaseModel, extra=Extra.forbid):
    include: Optional[bool] = False
    notBefore: Optional[datetime]
    before: Optional[datetime]
    rollup: Optional[Union[timedelta, Literal["window"]]]


class SelectItemsParams(BaseModel, extra=Extra.forbid):
    query: Optional[ResourceQuery] = {}
    include: Optional[List[str]] = []
    groupIncludedByType: bool = True


class ItemSelectView(BaseResource):
    attributes: Item


class ItemSaveView(Item):
    annotations: Optional[Dict[AnnotationKey, str]] = {}


class PublishSignalsParams(BaseModel):
    integration: IntegrationID
    itemsBySignal: Dict[ResourceID, Item]
    createOnly: Optional[bool] = False


class SaveSummary(BaseModel, extra=Extra.forbid):
    id: ResourceID
    created: bool
    updated: bool


class PublishSignalsResponse(BaseModel, extra=Extra.forbid):
    itemsBySignal: Dict[ResourceID, SaveSummary]
