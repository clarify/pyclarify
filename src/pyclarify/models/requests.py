"""
Copyright 2021 Clarify

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

from pydantic import BaseModel, constr, conint, Extra, validate_arguments
from pydantic.fields import Optional
import pydantic
from typing import List, Union, Dict
from typing_extensions import Literal
from datetime import datetime
from enum import Enum
from .data import DataFrame, InputID, SignalInfo, Signal, Item
from pyclarify.__utils__.convert import timedelta_isoformat, time_to_string
from pyclarify.__utils__.pagination import GetDates
from datetime import timedelta

IntegrationID = constr(regex=r"^[a-v0-9]{20}$")
ResourceID = constr(regex=r"^[a-v0-9]{20}$")
LimitSelectItems = conint(ge=0)
LimitSelectSignals = conint(ge=0, le=1000)

### PARAMETERS ###

# Generic Query Parameters #
class QueryParams(BaseModel):
    include: Optional[bool] = False
    filter: dict = {}
    skip: Optional[int] = 0


class SelectSignalsSignalsParams(QueryParams, extra=Extra.forbid):
    limit: Optional[LimitSelectSignals] = 50


class SelectItemsItemsParams(QueryParams, extra=Extra.forbid):
    limit: Optional[LimitSelectItems] = 10


# Generic Inclusion Parameters #
class InclusionParams(BaseModel):
    include: Optional[bool] = False


class SelectItemsDataParams(InclusionParams, extra=Extra.forbid):
    notBefore: Optional[datetime]
    before: Optional[datetime]
    rollup: Optional[Union[timedelta, Literal["window"]]]


class SelectSignalsItemsParams(InclusionParams, extra=Extra.forbid):
    pass


# Generic Request Parameter
class RequestParams(BaseModel):
    pass


# Clarify Namespace
class ClarifyParams(RequestParams):
    pass


class SelectItemsParams(ClarifyParams, extra=Extra.forbid):
    items: SelectItemsItemsParams
    data: SelectItemsDataParams


# Integration Namespace
class IntegrationParams(RequestParams):
    integration: IntegrationID


class InsertParams(IntegrationParams):
    data: DataFrame


class SaveSignalsParams(IntegrationParams, extra=Extra.forbid):
    inputs: Dict[InputID, SignalInfo]
    createOnly: Optional[bool] = False


# Admin Namespace
class AdminParams(RequestParams):
    integration: IntegrationID


class PublishSignalsParams(AdminParams):
    itemsBySignal: Dict[ResourceID, Item]
    createOnly: Optional[bool] = False


class SelectSignalsParams(AdminParams):
    signals: SelectSignalsSignalsParams
    items: SelectSignalsItemsParams


### REQUESTS ###
class ApiMethod(str, Enum):
    insert = "integration.Insert"
    save_signals = "integration.SaveSignals"
    select_items = "clarify.SelectItems"
    select_signals = "admin.SelectSignals"
    publish_signals = "admin.PublishSignals"


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

    @pydantic.root_validator()
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
        return values
