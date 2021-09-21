from pydantic import BaseModel, constr, conint
from pydantic.fields import Optional
from typing import List, Union, Dict
from datetime import datetime
from enum import Enum
from .data import DataFrame, InputId, Signal

IntegrationId = constr(regex=r"^[a-v0-9]{20}$")
LimitSelect = conint(ge=0, le=20)


class ApiMethod(str, Enum):
    select = "clarify.SelectItems"
    insert = "integration.Insert"
    save_signals = "integration.SaveSignals"


class JsonRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: ApiMethod = ApiMethod.select
    id: str = "1"
    params: Dict = {}


class ParamsInsert(BaseModel):
    integration: IntegrationId
    data: DataFrame


class InsertJsonRPCRequest(JsonRPCRequest):
    method: ApiMethod = ApiMethod.insert
    params: ParamsInsert


class ParamsSave(BaseModel):
    integration: IntegrationId
    inputs: Dict[InputId, Signal]
    createdOnly: Optional[bool] = False


class SaveJsonRPCRequest(JsonRPCRequest):
    method: ApiMethod = ApiMethod.save_signals
    params: ParamsSave


class ErrorData(BaseModel):
    trace: str
    params: Optional[Dict[str, List[str]]]


class Error(BaseModel):
    code: str
    message: str
    data: Optional[Union[ErrorData, str]]


class ResponseGeneric(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str]
    result: Optional[Dict]
    error: Optional[Error]


class SaveResult(BaseModel):
    id: str
    created: bool


class SignalSaveMap(BaseModel):
    signalsByInput: Dict[InputId, SaveResult]


class ResponseSave(ResponseGeneric):
    result: Optional[SignalSaveMap]


class ParamsSelectItems(BaseModel):
    include: Optional[bool] = False
    filter: dict = {}
    limit: Optional[LimitSelect] = 10
    skip: Optional[int] = 0


class ParamsSelectTimes(BaseModel):
    before: Optional[datetime]
    notBefore: Optional[datetime]


class ParamsSelectSeries(BaseModel):
    items: Optional[bool] = False
    aggregates: Optional[bool] = False


class ItemSelect(BaseModel):
    items: ParamsSelectItems
    times: ParamsSelectTimes
    series: ParamsSelectSeries


class SelectJsonRPCRequest(JsonRPCRequest):
    method: ApiMethod = ApiMethod.select
    params: ItemSelect


class ResultSelectMap(BaseModel):
    items: Optional[Dict[InputId, Signal]]
    data: Optional[DataFrame]


class ResponseSelect(ResponseGeneric):
    result: Optional[ResultSelectMap]
