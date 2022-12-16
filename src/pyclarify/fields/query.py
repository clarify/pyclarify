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


import warnings
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
    LTE = "$lte"
    GT = "$gt"
    GTE = "$gte"


class Comparison(BaseModel):
    value: Union[str, List[str], int, List[int], float, List[float], bool, None, List[None]] = None
    operator: Optional[Operators]

    @root_validator(pre=False, allow_reuse=True)
    def field_must_reflect_operator(cls, values):
        value = values["value"] if "value" in values.keys() else None
        operator = values["operator"] if "operator" in values.keys() else None
        if operator:
            # Field value should be list
            if operator in [Operators.IN, Operators.NIN]:
                if not isinstance(value, list):
                    raise FilterError(operator, list, value)
                elif None in value:
                    warnings.warn("You are using a null value as a filter. This will result in no results.", UserWarning)
        
            # Field value should not be list
            if operator not in [Operators.IN, Operators.NIN]:
                if isinstance(value, list):
                    raise FilterError(operator, list, value)
                elif not value:
                    warnings.warn("You are using a null value as a filter. This will result in no results.", UserWarning)
        # No operator means Equals
        else:
            if isinstance(value, list):
                raise FilterError("Equals (None)", list, value)

        return values

    class Config:
        use_enum_values = True
        extra = Extra.forbid


class Equal(Comparison):
    """
    Matches using equality.

    Example
    -------
    filter_value = Equal(value="foo")
    """
    pass

class NotEqual(Comparison):
    """
    Matches using negated equality.

    Example
    -------
    filter_value = NotEqual(value="bar")
    """
    operator = Operators.NE


class Regex(Comparison):
    """
    Matches all resources where the field value is match the specified regex.

    Example
    -------
    filter_value = Regex(value="fo[o]{1}")
    """
    operator = Operators.REGEX


class In(Comparison):
    """
    Matches all resources where the field value is present in the specified list.

    Example
    -------
    filter_value = In(value=["foo", "bar"])
    """
    operator = Operators.IN


class NotIn(Comparison):
    """
    Matches all resources where the field value is not present in the specified list.

    Example
    -------
    filter_value = NotIn(value=["baz", "qux"])
    """
    operator = Operators.NIN


class Less(Comparison):
    """
    Matches all resources where the field value is less than the specified value.

    Example
    -------
    filter_value = Less(value=10)
    """
    operator = Operators.LT


class LessOrEqual(Comparison):
    """
    Matches all resources where the field value is less than or equal to the specified value.

    Example
    -------
    filter_value = LessOrEqual(value=10)
    """
    operator = Operators.LTE


class Greater(Comparison):
    """
    Matches all resources where the field value is greater than the specified value.

    Example
    -------
    filter_value = Greater(value=10)
    """
    operator = Operators.GT


class GreaterOrEqual(Comparison):
    """
    Matches all resources where the field value is greater than or equal to the specified value.

    Example
    -------
    filter_value = GreaterOrEqual(value=10)
    """
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
