"""
Copyright 2023 Searis AS

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
from typing import List, Dict, Union, Optional
from pyclarify.fields.constraints import ApiMethod, IntegrationID
from pyclarify.fields.error import Error
from pyclarify.fields.resource import SelectionMeta
from pyclarify.views.evaluate import EvaluateParams
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
        elif values["method"] == ApiMethod.evaluate:
            values["params"] = EvaluateParams(**values["params"])
            return values
        return values


class IncludedField(BaseModel):
    def __add__(self, other):
        data = {}
        keys = set(list(self.dict().keys()) + list(other.dict().keys()))
        for key in keys:
            data[key] = []
            self_object = getattr(self, key) if hasattr(self, key) else None
            other_object = getattr(other, key) if hasattr(other, key) else None
            if self_object:
                data[key] += self_object
            if other_object:
                data[key] += other_object
            if self_object is None and other_object is None:
                data.pop(key)
            else:
                data[key] = list(set(data[key]))
        if hasattr(data, "integration"):
            data["integration"] = data["integration"][0]
        return self.__class__(**data)

class IncludedFieldSignals(IncludedField, extra=Extra.ignore):
    items: Optional[List[ItemSelectView]]


class IncludedFieldItems(IncludedField, extra=Extra.ignore):
    integration: Optional[IntegrationID]
    signals: Optional[List[SignalSelectView]]




class Selection(BaseModel):
    meta: SelectionMeta

    def __add__(self, other):
        try:
            data = {}
            data["meta"] = self.meta
            data["data"] = self.data + other.data
            if self.included is not None:
                data["included"] = self.included
            if other.included is not None:
                if data["included"] is not None:
                    data["included"] += other.included
                else:
                    data["included"] = other.included
            if self.included is None and other.included is None:
                data.pop("included", None)

            return self.__class__(**data)
        except TypeError as e:
            raise TypeError(source=self, other=other) from e

class DataSelection(Selection):
    data:  DataFrame
    included: Optional[IncludedFieldSignals]


class ItemSelection(Selection):
    data: List[ItemSelectView]
    included: Optional[IncludedFieldItems]

class SignalSelection(Selection):
    data:  List[SignalSelectView]
    included: Optional[IncludedFieldSignals]


class GenericResponse(BaseModel, extra=Extra.forbid):
    jsonrpc: str = "2.0"
    id: str
    result: Optional[Union[InsertResponse,SaveSignalsResponse,DataSelection,ItemSelection,SignalSelection,PublishSignalsResponse]]
    error: Union[Error, List[Error], None]


class Response(GenericResponse):
    method: Optional[ApiMethod]
    
    @pydantic.root_validator()
    def use_correct_response_based_on_method(cls, values):
        #TODO: Not happy with this resolution flow
        result = values.get("result")
        method = values.get("method")
        if result:
            if method == ApiMethod.insert:
                if not isinstance(result, InsertResponse):
                    values["result"] = InsertResponse(**result.dict())

            elif method == ApiMethod.save_signals:
                if not isinstance(result, SaveSignalsResponse):
                    values["result"] = SaveSignalsResponse(**result.dict())
            
            elif method == ApiMethod.data_frame or method == ApiMethod.evaluate:
                if not isinstance(result, DataSelection):
                    values["result"] = DataSelection(**result.dict())
            
            elif method == ApiMethod.select_items:
                if not isinstance(result, ItemSelection):
                    values["result"] = ItemSelection(**result.dict())

            elif method == ApiMethod.select_signals:
                if not isinstance(result, SignalSelection):
                    values["result"] = SignalSelection(**result.dict())

            elif method == ApiMethod.publish_signals:
                if not isinstance(result, PublishSignalsResponse):
                    values["result"] = PublishSignalsResponse(**result.dict())
        else:
            pass #TODO: Possible error state 
        values.pop("method") # no need anymore for declaring method
        return values
    
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
