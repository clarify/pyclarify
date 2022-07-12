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

from pydantic import BaseModel, Extra
from typing import Dict
from pyclarify.fields.constraints import InputID, ResourceID, IntegrationID
from pyclarify.fields.dataframe import DataFrame


class InsertParams(BaseModel):
    integration: IntegrationID
    data: DataFrame

class InsertSummary(BaseModel, extra=Extra.forbid):
    id: ResourceID
    created: bool


class InsertResponse(BaseModel, extra=Extra.forbid):
    signalsByInput: Dict[InputID, InsertSummary]
