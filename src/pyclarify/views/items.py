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
    TypeSignal,
    SourceTypeSignal,
    LabelsKey,
    AnnotationKey,
    ResourceID,
    IntegrationID,
    ResourceMetadata,
)


class ItemInfo(BaseModel):
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


class ItemSelectView(BaseModel):
    type: str
    id: str
    meta: ResourceMetadata
    attributes: Item
    relationships: Dict = {}


class ItemSaveView(Item):
    annotations: Optional[Dict[AnnotationKey, str]] = {}


class PublishSignalsParams(BaseModel):
    integration: IntegrationID
    itemsBySignal: Dict[ResourceID, ItemSaveView]
    createOnly: Optional[bool] = False


class SaveSummary(BaseModel, extra=Extra.forbid):
    id: ResourceID
    created: bool
    updated: bool


class PublishSignalsResponse(BaseModel, extra=Extra.forbid):
    itemsBySignal: Dict[ResourceID, SaveSummary]
