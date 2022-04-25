"""
Copyright 2021 Clarify

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
from .exceptions import PyClarifyFilterError
from pydantic.class_validators import root_validator
from pydantic import BaseModel, Extra
from pydantic.fields import Optional
from typing import ForwardRef, Union, List, Dict
from enum import Enum

class LegalOperators(str, Enum):
    NE = "$ne"
    REGEX = "$regex"
    IN = "$in"
    NIN = "$nin"
    LT = "$lt"
    GT = "$gt"
    GTE = "$gte"


class Comparison(BaseModel):
    value: Union[
        str, 
        List[str], 
        int, 
        List[int], 
        float, 
        List[float], 
        bool,
        None
    ] = None
    operator: Optional[LegalOperators]

    @root_validator(pre=False)
    def field_must_reflect_operator(cls, values):
        value = values["value"]
        operator = values["operator"] if "operator" in values.keys() else None
        if operator:
            # Field value should be list
            if operator in [LegalOperators.IN, LegalOperators.NIN]:
                if not isinstance(value, list):
                    raise PyClarifyFilterError(operator, list, value)

            # Field value should not be list
            if operator not in [LegalOperators.IN, LegalOperators.NIN]:
                if isinstance(value, list):
                    raise PyClarifyFilterError(operator, list, value)

        # No operator means Equals
        else:
            if isinstance(value, list):
                raise PyClarifyFilterError("Equals (None)", list, value)
        return values

    class Config:
        use_enum_values = True
        extra=Extra.forbid


class Equal(Comparison):
    pass

class NotEqual(Comparison):
    operator = LegalOperators.NE

class Regex(Comparison):
    operator = LegalOperators.REGEX

class In(Comparison):
    operator = LegalOperators.IN

class NotIn(Comparison):
    operator = LegalOperators.NIN

class LessThan(Comparison):
    operator = LegalOperators.LT

class GreaterThan(Comparison):
    operator = LegalOperators.GT

class GreaterThanOrEqual(Comparison):
    operator = LegalOperators.GTE


Filter = ForwardRef('Filter')

class Filter(BaseModel):
    and_list: Optional[List[Filter]]
    or_list: Optional[List[Filter]]
    fields: Optional[Dict[str, Comparison]]

    def __and__(self, other):
        _tmp = []

        if self.and_list != None:
            _tmp += self.and_list

        if self.or_list != None or self.fields != None:
            _tmp.append(self)
        
        if other.and_list != None:
            _tmp += other.and_list

        if other.or_list != None or other.fields != None:
            _tmp.append(other)

        return Filter(and_list=_tmp)

    def __or__(self, other):
        _tmp = []

        if self.or_list != None:
            _tmp += self.or_list
    
        if self.and_list != None or self.fields != None:
            _tmp.append(self)
        
        if other.or_list != None:
            _tmp += other.or_list
        if other.and_list != None or other.fields != None:
            _tmp.append(other)
        
        return Filter(or_list=_tmp)
    
    def field_to_query(self, field):
        field, comparison = list(field.items())[0]
        comparison = comparison.dict()
        if comparison["operator"]:
            return {field: {comparison["operator"]: comparison["value"]}}
        return {field: {comparison["value"]}}
    
    def to_query(self):
        q = {}
        if self.and_list:
            q["$and"] = [f.to_query() for f in self.and_list]
        if self.or_list:
            q["$or"] = [f.to_query() for f in self.or_list]
        if not self.fields:
            return q
        
        if self.fields and q == {}:
            return self.field_to_query(self.fields)

        return q

Filter.update_forward_refs()
