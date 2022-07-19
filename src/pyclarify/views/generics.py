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
from pydantic.fields import Optional
from typing import List, Dict, Union
from pyclarify.fields.constraints import ApiMethod
from pyclarify.fields.error import Error
from .dataframe import InsertParams, InsertResponse, SelectDataFrameParams, SelectDataFrameResponse
from .items import (
    SelectItemsParams,
    SelectItemsResponse,
    PublishSignalsParams,
    PublishSignalsResponse,
)
from .signals import (
    SelectSignalsParams,
    SelectSignalsResponse,
    SaveSignalsParams,
    SaveSignalsResponse,
)


class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: ApiMethod = ApiMethod.select_items
    id: str = "1"
    params: Dict = {}

    class Config:
        json_encoders = {
            timedelta: timedelta_isoformat,
            datetime: time_to_string
        }


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
        elif values["method"] == ApiMethod.select_dataframe:
            values["params"] = SelectDataFrameParams(**values["params"])
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


class Response(GenericResponse, extra=Extra.forbid):
    result: Optional[
        Union[
            InsertResponse,
            SaveSignalsResponse,
            SelectItemsResponse,
            SelectDataFrameResponse,
            SelectSignalsResponse,
            PublishSignalsResponse,
        ]
    ]
