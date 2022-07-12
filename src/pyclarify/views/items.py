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
from copy import deepcopy
import pydantic
from pydantic import BaseModel, constr, conint, Extra
from pydantic.json import timedelta_isoformat
from pydantic.fields import Optional
from typing import List, Dict, Union
from typing_extensions import Literal
from pyclarify.__utils__.auxiliary import local_import
from pyclarify.fields.constraints import (
    ApiMethod,
    TypeSignal,
    SourceTypeSignal,
    LabelsKey,
    AnnotationKey,
    NumericalValuesType,
    InputID,
    ResourceID,
    IntegrationID,
)
from pyclarify.fields.error import Error
from pyclarify.fields.dataframe import DataFrame
from pyclarify.fields.query import SelectItemsItemsParams


class ItemInfo(BaseModel):
    name: str
    type: TypeSignal = TypeSignal.numeric
    description: str = ""
    labels: Dict[LabelsKey, List[str]] = {}
    annotations: Optional[Dict[AnnotationKey, str]] = {}
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
    items: SelectItemsItemsParams
    data: SelectItemsDataParams


class SelectItemsResponse(BaseModel, extra=Extra.forbid):
    items: Optional[Dict[InputID, ItemInfo]]
    data: Optional[DataFrame]

    def __add__(self, other):
        try:
            if isinstance(other, SelectItemsResponse):
                main_items = None
                main_df = None
                if self.items:
                    source_items = self.items
                    main_items = deepcopy(source_items)
                    if other.items:
                        for key, value in other.items.items():
                            main_items[key] = value
                if other.items and not self.items:
                    main_items = deepcopy(other.items)

                if other.data:
                    other_data = other.data
                    main_df = other_data
                    if self.data:
                        main_df = merge([self.data, other_data])
                if self.data and not other.data:
                    main_df = self.data

            return SelectItemsResponse(items=main_items, data=main_df)

        except TypeError as e:
            raise TypeError(source=self, other=other) from e


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



