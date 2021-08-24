from pydantic import BaseModel, constr
from pydantic.fields import Optional
from typing import List, Union, Dict
from datetime import datetime, timedelta
from enum import Enum

# constrained string defined by the API
InputId = constr(regex=r"^[a-z0-9_-]{1,40}$")
LabelsKey = constr(regex=r"^[A-Za-z0-9-_/]{1,40}$")
AnnotationKey = constr(regex=r"^[A-Za-z0-9-_/]{1,40}$")


class ClarifyDataFrame(BaseModel):
    times: List[datetime] = None
    series: Dict[InputId,
                 List[Union[float, int, None]]] = None


class TypeSignal(str, Enum):
    numeric = 'numeric'
    enum = 'enum'


class SourceTypeSignal(str, Enum):
    measurement = "measurement"
    aggregation = "aggregation"
    prediction = "prediction"


class Signal(BaseModel):
    name: InputId
    type: TypeSignal = TypeSignal.numeric
    description: str = ""
    labels: Dict[LabelsKey, str] = {}
    annotations: Dict[AnnotationKey, str] = {}
    engUnit: str = ""
    enumValues: Dict[str, str] = {}
    sourceType: SourceTypeSignal = SourceTypeSignal.measurement
    sampleInterval: Optional[timedelta] = None
    gapDetection: Optional[timedelta] = None
