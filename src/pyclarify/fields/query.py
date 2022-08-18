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


from pyclarify.__utils__.exceptions import FilterError
from pydantic.fields import Optional
from pydantic import BaseModel, Extra
from enum import Enum
from typing import Union, List, Dict
from pydantic.class_validators import root_validator
from datetime import datetime


class Operators(str, Enum):
    NE = "$ne"
    REGEX = "$regex"
    IN = "$in"
    NIN = "$nin"
    LT = "$lt"
    GT = "$gt"
    GTE = "$gte"


class Comparison(BaseModel):
    value: Union[str, List[str], int, List[int], float, List[float], bool, None] = None
    operator: Optional[Operators]

    @root_validator(pre=False, allow_reuse=True)
    def field_must_reflect_operator(cls, values):
        value = values["value"]
        operator = values["operator"] if "operator" in values.keys() else None
        if operator:
            # Field value should be list
            if operator in [Operators.IN, Operators.NIN]:
                if not isinstance(value, list):
                    raise FilterError(operator, list, value)

            # Field value should not be list
            if operator not in [Operators.IN, Operators.NIN]:
                if isinstance(value, list):
                    raise FilterError(operator, list, value)

        # No operator means Equals
        else:
            if isinstance(value, list):
                raise FilterError("Equals (None)", list, value)
        return values

    class Config:
        use_enum_values = True
        extra = Extra.forbid


class Equal(Comparison):
    pass


class NotEqual(Comparison):
    operator = Operators.NE


class Regex(Comparison):
    operator = Operators.REGEX


class In(Comparison):
    operator = Operators.IN


class NotIn(Comparison):
    operator = Operators.NIN


class LessThan(Comparison):
    operator = Operators.LT


class GreaterThan(Comparison):
    operator = Operators.GT


class GreaterThanOrEqual(Comparison):
    operator = Operators.GTE


class DateField(BaseModel):
    operator: Optional[Operators]
    time: Optional[Union[str, datetime]]
    query: Dict = {}

    @root_validator(pre=True, allow_reuse=True)
    def refomat_payload(cls, values):
        op = values["operator"]
        time = values["time"]
        values["query"] = {op.value: time}

        return values

    class Config:
        extra = Extra.forbid
