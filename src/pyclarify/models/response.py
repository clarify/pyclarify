from pydantic import BaseModel, Extra

from pydantic.fields import Optional
from typing import List, Union, Dict
from .data import (
    InputID,
    InsertSummary,
    SaveSummary,
    SignalInfo,
    DataFrame,
    ResourceID,
    Signal,
)


class ErrorData(BaseModel):
    trace: str
    params: Optional[Dict[str, List[str]]]


class Error(BaseModel):
    code: str
    message: str
    data: Optional[Union[ErrorData, str]]


class InsertResponse(BaseModel, extra=Extra.forbid):
    signalsByInput: Dict[InputID, InsertSummary]


class SaveSignalsResponse(BaseModel, extra=Extra.forbid):
    signalsByInput: Dict[InputID, SaveSummary]


class SelectItemsResponse(BaseModel, extra=Extra.forbid):
    items: Optional[Dict[InputID, SignalInfo]]
    data: Optional[DataFrame]


class SelectSignalsResponse(BaseModel, extra=Extra.forbid):
    signals: Optional[Dict[ResourceID, Signal]]
    items: Optional[Dict[ResourceID, SignalInfo]]



class PublishSignalsResponse(BaseModel, extra=Extra.forbid):
    itemsBySignal: Dict[ResourceID, SaveSummary]


class GenericResponse(BaseModel, extra=Extra.forbid):
    jsonrpc: str = "2.0"
    id: str
    result: Optional[Dict]
    error: Optional[Error]


class Response(GenericResponse, extra=Extra.forbid):
    result: Optional[
        Union[
            InsertResponse,
            SaveSignalsResponse,
            SelectItemsResponse,
            SelectSignalsResponse,
            PublishSignalsResponse,
        ]
    ]
