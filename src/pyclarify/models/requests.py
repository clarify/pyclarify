from pydantic import BaseModel, constr
from pydantic.fields import Optional
from typing import List, Union, Dict, TypedDict
from datetime import datetime
from enum import Enum
from .data import ClarifyDataFrame, InputId, Signal

IntegrationId = constr(regex=r"^[a-v0-9]{20}$")


class ApiMethod(str, Enum):
    select = 'item.Select'
    insert = 'integration.Insert'
    save_signals = 'integration.SaveSignals'


class JsonRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: ApiMethod = ApiMethod.select
    id: str = "1"
    params: Dict = {}


class ParamsInsert(BaseModel):
    integration: IntegrationId
    data: ClarifyDataFrame


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
    code: int
    message: str
    data: Optional[ErrorData]


class ResponseGeneric(BaseModel):
    jsonrpc: str = "2.0"
    id: str
    result: Optional[Dict]
    error: Optional[Error]


class SaveResult(TypedDict, total=True):
    id: str
    created: bool


class SignalSaveMap(TypedDict, total=True):
    signalsByInput: Dict[InputId, SaveResult]


class ResponseSave(ResponseGeneric):
    result: SignalSaveMap
