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

from pydantic import BaseModel, Extra
from copy import deepcopy

from pydantic.fields import Optional
from typing import List, Union, Dict
from .data import (
    InputID,
    InsertSummary,
    SaveSummary,
    SignalInfo,
    DataFrame,
    merge,
    ResourceID,
    Signal,
)
from pyclarify.__utils__.exceptions import TypeError


class ErrorData(BaseModel):
    trace: str
    params: Optional[Dict[str, List[str]]]


class Error(BaseModel):
    code: str
    message: str
    data: Optional[Union[ErrorData, str]]


class InsertResponse(BaseModel, extra=Extra.forbid):
    signalsByInput: Dict[InputID, InsertSummary]


class SaveSignalsResponse(BaseModel, extra=Extra.forbid):
    signalsByInput: Dict[InputID, SaveSummary]


class SelectItemsResponse(BaseModel, extra=Extra.forbid):
    items: Optional[Dict[InputID, SignalInfo]]
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


class SelectSignalsResponse(BaseModel, extra=Extra.forbid):
    signals: Optional[Dict[ResourceID, Signal]]
    items: Optional[Dict[ResourceID, SignalInfo]]


class PublishSignalsResponse(BaseModel, extra=Extra.forbid):
    itemsBySignal: Dict[ResourceID, SaveSummary]


class GenericResponse(BaseModel, extra=Extra.forbid):
    jsonrpc: str = "2.0"
    id: str
    result: Optional[Dict]
    error: Union[Error, List[Error], None]

    def __add__(self, other):
        try:
            results = None
            errors = None
            if self.result:
                results = self.result
                if other.result:
                    results += other.result
            elif other.result:
                results = other.result

            if self.error:
                errors = self.error
                if other.error:
                    if isinstance(self.error, List):
                        if isinstance(other.error, List):
                            errors = self.error + other.error
                        else:
                            errors = self.error + [other.error]
                    elif isinstance(other.error, List):
                        errors = [self.error] + other.error
                    else:
                        errors = [self.error, other.error]
            elif other.error:
                errors = other.error

            return Response(
                jsonrpc=self.jsonrpc, id=self.id, result=results, error=errors
            )
        except TypeError as e:
            raise TypeError(source=self, other=other) from e


class Response(GenericResponse, extra=Extra.forbid):
    result: Optional[
        Union[
            InsertResponse,
            SaveSignalsResponse,
            SelectItemsResponse,
            SelectSignalsResponse,
            PublishSignalsResponse,
        ]
    ]
