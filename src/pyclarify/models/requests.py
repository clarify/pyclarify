from pydantic import BaseModel, constr, conint
from pydantic.fields import Optional
from typing import List, Union, Dict
from datetime import datetime
from enum import Enum
from .data import DataFrame, InputID, Signal
from pyclarify.__utils__.convert import timedelta_isoformat
from datetime import timedelta

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

    class Config:
        json_encoders = {timedelta: timedelta_isoformat}


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


class GenericSummary(BaseModel):
    id: str
    created: bool

class InsertSummary(GenericSummary):
    pass

class SaveSummary(GenericSummary):
    updated: bool


class SignalSaveMap(BaseModel):
    signalsByInput: Dict[InputID, Union[SaveSummary, InsertSummary]]


class SaveResponse(GenericResponse):
    result: Optional[SignalSaveMap]


class SelectItemsParams(BaseModel):
    include: Optional[bool] = False
    filter: dict = {}                   # https://docs.clarify.io/v1.1/reference/filtering
    limit: Optional[LimitSelect] = 10
    skip: Optional[int] = 0


class SelectDataParams(BaseModel):
    include: Optional[bool] = False
    notBefore: Optional[datetime]
    before: Optional[datetime]
    rollup: Optional[timedelta] = None


class ItemSelect(BaseModel):
    items: SelectItemsParams
    data: SelectDataParams


class SelectRequest(JSONRPCRequest):
    method: ApiMethod = ApiMethod.select
    params: ItemSelect


class SelectMapResult(BaseModel):
    items: Optional[Dict[InputID, Signal]]
    data: Optional[DataFrame]


class SelectResponse(GenericResponse):
    result: Optional[SelectMapResult]
