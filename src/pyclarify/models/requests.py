from pydantic import BaseModel, constr, conint
from pydantic.fields import Optional
from typing import List, Union, Dict
from datetime import datetime
from enum import Enum
from .data import DataFrame, InputID, Signal

IntegrationID = constr(regex=r"^[a-v0-9]{20}$")
LimitSelect = conint(ge=0, le=20)


class ApiMethod(str, Enum):
    select = "clarify.SelectItems"
    insert = "integration.Insert"
    save_signals = "integration.SaveSignals"


class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: ApiMethod = ApiMethod.select
    id: str = "1"
    params: Dict = {}


class InsertParams(BaseModel):
    integration: IntegrationID
    data: DataFrame


class InsertRequest(JSONRPCRequest):
    method: ApiMethod = ApiMethod.insert
    params: InsertParams


class SaveParams(BaseModel):
    integration: IntegrationID
    inputs: Dict[InputID, Signal]
    createdOnly: Optional[bool] = False


class SaveRequest(JSONRPCRequest):
    method: ApiMethod = ApiMethod.save_signals
    params: SaveParams


class ErrorData(BaseModel):
    trace: str
    params: Optional[Dict[str, List[str]]]


class Error(BaseModel):
    code: str
    message: str
    data: Optional[Union[ErrorData, str]]


class GenericResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[str]
    result: Optional[Dict]
    error: Optional[Error]


class SaveResult(BaseModel):
    id: str
    created: bool


class SignalSaveMap(BaseModel):
    signalsByInput: Dict[InputID, SaveResult]


class SaveResponse(GenericResponse):
    result: Optional[SignalSaveMap]


class SelectItemsParams(BaseModel):
    include: Optional[bool] = False
    filter: dict = {}
    limit: Optional[LimitSelect] = 10
    skip: Optional[int] = 0


class SelectTimesParams(BaseModel):
    before: Optional[datetime]
    notBefore: Optional[datetime]


class SelectSeriesParams(BaseModel):
    items: Optional[bool] = False
    aggregates: Optional[bool] = False


class ItemSelect(BaseModel):
    items: SelectItemsParams
    times: SelectTimesParams
    series: SelectSeriesParams


class SelectRequest(JSONRPCRequest):
    method: ApiMethod = ApiMethod.select
    params: ItemSelect


class SelectMapResult(BaseModel):
    items: Optional[Dict[InputID, Signal]]
    data: Optional[DataFrame]


class SelectResponse(GenericResponse):
    result: Optional[SelectMapResult]
