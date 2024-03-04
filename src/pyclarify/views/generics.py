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


from datetime import datetime, timedelta
from pydantic import ConfigDict, BaseModel, validate_arguments, model_validator
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
    id: Union[str,int] = "1"
    params: Union[
        dict,
        InsertParams, 
        SaveSignalsParams, 
        SelectItemsParams, 
        SelectSignalsParams, 
        PublishSignalsParams, 
        DataFrameParams, 
        EvaluateParams] = {}
    # TODO[pydantic]: The following keys are deprecated: `json_encoders`.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-config for more information.
    model_config = ConfigDict(json_encoders={timedelta: timedelta_isoformat, datetime: time_to_string})


class Request(JSONRPCRequest):
    method: ApiMethod

    @model_validator(mode='after')
    @classmethod
    def use_correct_params_based_on_method(cls, values):
        if values.method == ApiMethod.insert:
           values.params = InsertParams(**values.params)
        elif values.method == ApiMethod.save_signals:
           values.params = SaveSignalsParams(**values.params)
        elif values.method == ApiMethod.select_items:
           values.params = SelectItemsParams(**values.params)
        elif values.method == ApiMethod.select_signals:
           values.params = SelectSignalsParams(**values.params)
        elif values.method == ApiMethod.publish_signals:
           values.params = PublishSignalsParams(**values.params)
        elif values.method == ApiMethod.data_frame:
           values.params = DataFrameParams(**values.params)
        elif values.method == ApiMethod.evaluate:
           values.params = EvaluateParams(**values.params)
        return values


class IncludedField(BaseModel):
    def __add__(self, other):
        data = {}
        keys = set(list(self.model_dump().keys()) + list(other.model_dump().keys()))
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


class IncludedFieldSignals(IncludedField):
    items: Optional[List[ItemSelectView]] = None
    model_config = ConfigDict(extra="ignore")


class IncludedFieldItems(IncludedField):
    integration: Optional[IntegrationID] = None
    signals: Optional[List[SignalSelectView]] = None
    model_config = ConfigDict(extra="forbid")


class Selection(BaseModel):
    meta: SelectionMeta

    def __add__(self, other):
        try:
            self.data += other.data
            if self.included:
                if other.included:
                    self.included += other.included
            elif other.included:
                self.included = other.included
            
            return self
        except TypeError as e:
            raise TypeError(source=self, other=other) from e

class DataSelection(Selection):
    data: DataFrame
    included: Optional[IncludedFieldSignals] = None


class ItemSelection(Selection):
    data: Optional[List[ItemSelectView]] = None
    included: Optional[IncludedFieldItems] = None


class SignalSelection(Selection):
    data:  Optional[List[SignalSelectView]] = None
    included: Optional[IncludedFieldSignals] = None
    

class GenericResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Union[str,int] = "1"
    result: Optional[Union[DataSelection, SignalSelection, InsertResponse,SaveSignalsResponse,ItemSelection,PublishSignalsResponse]] = None
    error: Union[Error, List[Error], None] = None

    model_config = ConfigDict(extra="forbid")


class Response(GenericResponse):
    method: Optional[ApiMethod] = None
    
    @model_validator(mode='after')
    def use_correct_response_based_on_method(cls, values):
        #TODO: Not happy with this resolution flow
        result = values.result
        method = values.method
        error = values.error
        if result:
            if method == ApiMethod.insert:
                if not isinstance(result, InsertResponse):
                    values.result = InsertResponse(**result.model_dump())
            elif method == ApiMethod.save_signals:
                if not isinstance(result, SaveSignalsResponse):
                    values.result  = SaveSignalsResponse(**result.model_dump())
            elif method == ApiMethod.data_frame or method == ApiMethod.evaluate:
                if not isinstance(result, DataSelection):
                    values.result  = DataSelection(**result.model_dump())
            elif method == ApiMethod.select_items:
                if not isinstance(result, ItemSelection):
                    values.result  = ItemSelection(**result.model_dump())
            elif method == ApiMethod.select_signals:
                if not isinstance(result, SignalSelection):
                    values.result  = SignalSelection(**result.model_dump())
            elif method == ApiMethod.publish_signals:
                if not isinstance(result, PublishSignalsResponse):
                    values.result  = PublishSignalsResponse(**result.model_dump())
            else:
                # If has no method signature, assume its a valid object type
                return values
        elif error:          
            pass #TODO: Possible error state 
        values.method = None # no need anymore for declaring method
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
            if results:
                self.result = results

            if self.error:
                errors = self.error
                if other.error:
                    if isinstance(self.error, List):
                        errors = self.error + [other.error]
                    else:
                        errors = [self.error, other.error]
            elif other.error:
                errors = other.error
            if errors:
                self.error = errors
            
            return self
        except TypeError as e:
            raise TypeError(source=self, other=other) from e
