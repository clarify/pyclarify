from pydantic import BaseModel, constr, conint, Extra
from pydantic.fields import Optional
from typing import List, Union, Dict
from typing_extensions import Literal
from datetime import datetime
from enum import Enum
from .data import DataFrame, InputID, SignalInfo, Signal
from pyclarify.__utils__.convert import timedelta_isoformat
from datetime import timedelta

IntegrationID = constr(regex=r"^[a-v0-9]{20}$")
LimitSelectItems = conint(ge=0, le=50)
LimitSelectSignals = conint(ge=0, le=1000)


class ApiMethod(str, Enum):
    insert = "integration.Insert"
    save_signals = "integration.SaveSignals"
    select_items = "clarify.SelectItems"
    select_signal = "admin.SelectSignals"
    publish_signals = "admin.PublishSignals"


class JSONRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: ApiMethod = ApiMethod.select_items
    id: str = "1"
    params: Dict = {}

    class Config:
        json_encoders = {timedelta: timedelta_isoformat}


class InsertParams(BaseModel, extra=Extra.forbid):
    integration: IntegrationID
    data: DataFrame


class InsertRequest(JSONRPCRequest):
    method: ApiMethod = ApiMethod.insert
    params: InsertParams


class SaveParams(BaseModel, extra=Extra.forbid):
    integration: IntegrationID
    inputs: Dict[InputID, SignalInfo]
    createdOnly: Optional[bool] = False


class PublishParams(BaseModel):
    integration: IntegrationID
    itemsBySignal: Dict[InputID, SignalInfo]
    createOnly: Optional[bool] = False


class SaveRequest(JSONRPCRequest):
    method: ApiMethod = ApiMethod.save_signals
    params: SaveParams

class PublishRequest(JSONRPCRequest):
    method: ApiMethod = ApiMethod.publish_signals
    params: PublishParams


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


class GenericSummary(BaseModel, extra=Extra.forbid):
    id: str
    created: bool

class InsertSummary(GenericSummary, extra=Extra.forbid):
    pass

class SaveSummary(GenericSummary, extra=Extra.forbid):
    updated: bool


class SignalSaveMap(BaseModel):
    signalsByInput: Dict[InputID, Union[SaveSummary, InsertSummary]]


class SignalPublishMap(BaseModel):
    itemsBySignal: Dict[InputID, Union[SaveSummary, InsertSummary]]


class SaveResponse(GenericResponse):
    result: Optional[Union[SignalSaveMap, SignalPublishMap]]


class SelectItemsParams(BaseModel, extra=Extra.forbid):
    include: Optional[bool] = False
    filter: dict = {}                   # https://docs.clarify.io/v1.1/reference/filtering
    limit: Optional[LimitSelectItems] = 10
    skip: Optional[int] = 0


class SelectDataParams(BaseModel, extra=Extra.forbid):
    include: Optional[bool] = False
    notBefore: Optional[datetime]
    before: Optional[datetime]
    rollup: Optional[Union[timedelta, Literal["window"]]]


class ItemSelect(BaseModel, extra=Extra.forbid):
    items: SelectItemsParams
    data: SelectDataParams


class SelectItemRequest(JSONRPCRequest):
    method: ApiMethod = ApiMethod.select_items
    params: ItemSelect


class SelectSignalParams(BaseModel, extra=Extra.forbid):
    include: Optional[bool] = False
    filter: dict = {}
    limit: Optional[LimitSelectSignals] = 50
    skip: Optional[int] = 0


class SignalItemParams(BaseModel, extra=Extra.forbid):
    include: Optional[bool] = False


class SignalSelect(BaseModel, extra=Extra.forbid):
    integration: IntegrationID
    signals: SelectSignalParams
    items: SignalItemParams


class SelectSignalRequest(JSONRPCRequest):
    method: ApiMethod = ApiMethod.select_signal
    params: SignalSelect


class SelectMapResult(BaseModel, extra=Extra.forbid):
    items: Optional[Dict[InputID, SignalInfo]]
    signals: Optional[Dict[InputID, Signal]]
    data: Optional[DataFrame]


class SelectSignalsMapResult(BaseModel, extra=Extra.forbid):
    items: Optional[Dict[InputID, SignalInfo]]


class SelectResponse(GenericResponse):
    result: Optional[SelectMapResult] 





