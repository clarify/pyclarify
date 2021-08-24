from pydantic import BaseModel
from pydantic.fields import Optional
from typing import List, Union, Dict
from datetime import datetime
from enum import Enum, IntEnum
from .data import ClarifyDataFrame


class ApiMethod(str, Enum):
    select = 'item.Select'
    insert = 'integration.Insert'
    save_signals = 'integration.SaveSignals'


class InsertParams(BaseModel):
    integration: str = ""
    data: ClarifyDataFrame


class JsonRPCRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: ApiMethod = ApiMethod.select
    id: str = "1"
    params: Dict = {}
