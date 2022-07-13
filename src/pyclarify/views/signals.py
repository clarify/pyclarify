"""
Copyright 2022 Searis AS

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

from datetime import timedelta
from pydantic import BaseModel, Extra
from pydantic.fields import Optional
from pydantic.json import timedelta_isoformat
from typing import List, Dict, Union
from pyclarify.fields.constraints import (
    ResourceMetadata,
    TypeSignal,
    SourceTypeSignal,
    LabelsKey,
    AnnotationKey,
    InputID,
    ResourceID,
    IntegrationID,
)
from pyclarify.fields.query import SelectSignalsSignalsParams


class SignalInfo(BaseModel):
    name: str
    type: TypeSignal = TypeSignal.numeric
    description: str = ""
    labels: Dict[LabelsKey, List[str]] = {}
    annotations: Optional[Dict[AnnotationKey, str]] = {}
    engUnit: str = ""
    enumValues: Dict[str, str] = {}
    sourceType: SourceTypeSignal = SourceTypeSignal.measurement
    sampleInterval: timedelta = None
    gapDetection: timedelta = None

    class Config:
        json_encoders = {timedelta: timedelta_isoformat}
        extra = Extra.forbid


class Signal(SignalInfo):
    item: Union[ResourceID, None]
    inputId: InputID
    meta: ResourceMetadata


class SelectSignalsItemsParams(BaseModel, extra=Extra.forbid):
    include: Optional[bool] = False


class SelectSignalsParams(BaseModel):
    integration: IntegrationID
    signals: SelectSignalsSignalsParams
    items: SelectSignalsItemsParams


class SelectSignalsResponse(BaseModel, extra=Extra.forbid):
    signals: Optional[Dict[ResourceID, Signal]]
    items: Optional[Dict[ResourceID, SignalInfo]]


class SaveSignalsParams(BaseModel, extra=Extra.forbid):
    integration: IntegrationID
    inputs: Dict[InputID, SignalInfo]
    createOnly: Optional[bool] = False


class SaveSummary(BaseModel, extra=Extra.forbid):
    id: ResourceID
    created: bool
    updated: bool


class SaveSignalsResponse(BaseModel, extra=Extra.forbid):
    signalsByInput: Dict[InputID, SaveSummary]
