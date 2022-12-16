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

from datetime import datetime, timedelta
import pydantic
from pydantic import BaseModel, validate_arguments, Extra
from pydantic.json import timedelta_isoformat
from pyclarify.__utils__.time import time_to_string
from pyclarify.__utils__.exceptions import TypeError
from pydantic.fields import Optional
from typing import List, Dict, Union
from pyclarify.fields.constraints import ApiMethod, IntegrationID
from pyclarify.fields.error import Error
from pyclarify.fields.resource import SelectionMeta
from .dataframe import InsertParams, InsertResponse, DataFrameParams
from .dataframe import DataFrame
from .items import (
    SelectItemsParams,
    PublishSignalsParams,
    PublishSignalsResponse,
    ItemSelectView,
)
from .signals import (
    SelectSignalsParams,
    SaveSignalsParams,
    SaveSignalsResponse,
    SignalSelectView,
)


class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: ApiMethod = ApiMethod.select_items
    id: str = "1"
    params: Dict = {}

    class Config:
        json_encoders = {timedelta: timedelta_isoformat, datetime: time_to_string}


@validate_arguments
class Request(JSONRPCRequest):
    method: ApiMethod

    @pydantic.root_validator(allow_reuse=True)
    @classmethod
    def use_correct_params_based_on_method(cls, values):
        if values["method"] == ApiMethod.insert:
            values["params"] = InsertParams(**values["params"])
            return values
        elif values["method"] == ApiMethod.save_signals:
            values["params"] = SaveSignalsParams(**values["params"])
            return values
        elif values["method"] == ApiMethod.select_items:
            values["params"] = SelectItemsParams(**values["params"])
            return values
        elif values["method"] == ApiMethod.select_signals:
            values["params"] = SelectSignalsParams(**values["params"])
            return values
        elif values["method"] == ApiMethod.publish_signals:
            values["params"] = PublishSignalsParams(**values["params"])
            return values
        elif values["method"] == ApiMethod.data_frame:
            values["params"] = DataFrameParams(**values["params"])
            return values
        return values


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


class IncludedField(BaseModel, extra=Extra.ignore):
    integration: Optional[IntegrationID]
    items: Optional[List[ItemSelectView]]

    def __add__(self, other):
        data = {}
        data["items"] = []
        if self.integration is not None:
            data["integration"] = self.integration
        if self.items is not None:
            data["items"] += self.items
        if other.items is not None:
            data["items"] += other.items
        if self.items is None and other.items is None:
            data.pop("items", None)
        return IncludedField(**data)


class Selection(BaseModel):
    meta: SelectionMeta
    data: Union[List[ItemSelectView], List[SignalSelectView], DataFrame]
    included: Optional[IncludedField]

    def __add__(self, other):
        try:
            data = {}
            data["meta"] = self.meta
            data["data"] = self.data + other.data
            data["included"] = IncludedField()
            if self.included is not None:
                data["included"] += self.included
            if other.included is not None:
                data["included"] += other.included
            if self.included is None and other.included is None:
                data.pop("included", None)
            return Selection(**data)
        except TypeError as e:
            raise TypeError(source=self, other=other) from e


class Response(GenericResponse, extra=Extra.forbid):
    result: Optional[
        Union[InsertResponse, SaveSignalsResponse, Selection, PublishSignalsResponse]
    ]
