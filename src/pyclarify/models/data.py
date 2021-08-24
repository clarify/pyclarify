from pydantic import BaseModel, constr
from pydantic.fields import Optional
from typing import List, Union, Dict
from datetime import datetime, timedelta
from enum import Enum

class ClarifyDataFrame(BaseModel):
    times: List[datetime] = None
    series: Dict[constr(regex=r"^[a-z0-9_-]{1,40}$"),
                 List[Union[float, int, None]]] = None


class TypeSignal(str, Enum):
    numeric = 'numeric'
    enum = 'enum'


class SourceTypeSignal(str, Enum):
    measurement = "measurement"
    aggregation = "aggregation"
    prediction = "prediction"


class Signal(BaseModel):
    name: constr(regex=r"^[a-z0-9_-]{1,40}$")  # constrained string defined by the API
    type: TypeSignal = TypeSignal.numeric
    description: str = ""
    labels: Dict[str, str] = {}
    annotations: Dict[str, str] = {}
    engUnit: str = ""
    enumValues: Dict[str, str] = {}
    sourceType: SourceTypeSignal = SourceTypeSignal.measurement
    sampleInterval: Optional[timedelta] = None
    gapDetection: Optional[timedelta] = None
