"""
Copyright 2023 Searis AS

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

from typing import Dict, List, Optional
from pydantic import BaseModel, Extra
from pyclarify.fields.constraints import Alias, BucketOffset, DataAggregation, ResourceID, State

from pyclarify.fields.query import SelectionFormat
from pyclarify.query.query import DataQuery



class ItemAggregation(BaseModel):
    """
    :meta private:
    """
    id: ResourceID
    aggregation: DataAggregation
    state: Optional[State]
    lead: Optional[BucketOffset]
    lag: Optional[BucketOffset]
    alias: Alias



class Calculation(BaseModel):
    """
    :meta private:
    """
    #TODO: constraints for formula?
    formula: str
    alias: Alias


class EvaluateParams(BaseModel):
    """
    :meta private:
    """
    items: List[ItemAggregation]
    calculations: List[Calculation]
    data: DataQuery
    include: List
    format: Optional[SelectionFormat] = SelectionFormat(dataAsArray=False)

# Evaluate uses DataFrame as response
