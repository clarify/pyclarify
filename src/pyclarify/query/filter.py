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

from pyclarify.fields.query import Comparison, DateField, Operators
from pydantic.class_validators import root_validator
from pydantic import BaseModel
from pydantic.fields import Optional
from typing import ForwardRef, Union, List, Dict
from datetime import datetime


Filter = ForwardRef("Filter")


class Filter(BaseModel):
    """
    Pydantic model for handling filtering. The filter supports pythons built in "&" and "|" operators for chaining filters.
    The model has a to_query() method used internally to convert model to MongoDB format.
    
    Parameters
    ----------
    fields : dict[str, Comparison]
        A dictionary of the key to be filtered on and a logical comparison.

    Example
    -------
    >>> from pyclarify import query
    >>> f1 = query.Filter(fields={"name": query.NotEqual(value="Lufttemperatur")})
    >>> f2 = query.Filter(fields={"labels.unit-type": query.NotIn(value=["Flåte", "Merde 5"])})
    >>> f1.to_query()
    ... {'name': {'$ne': 'Lufttemperatur'}}
    >>> f3 = f1 & f2
    >>> f3.to_query()
    ... {
    ...     '$and': [
    ...         {'name': {'$ne': 'Lufttemperatur'}},
    ...         {'labels.unit-type': {'$nin': ['Flåte', 'Merde 5']}}
    ...     ]
    ... }

    Complete list of operators
    --------------------------
    - Equal
    - NotEqual
    - Regex
    - In
    - NotIn
    - LessThan
    - Greater
    - GreaterOrEqual
    """

    and_list: Optional[List[Filter]]
    or_list: Optional[List[Filter]]
    fields: Optional[Dict[str, Union[str, Comparison]]]


    def __and__(self, other):
        _tmp = []

        if self.and_list is not None:
            _tmp += self.and_list

        if self.or_list is not None or self.fields is not None:
            _tmp.append(self)

        if other.and_list is not None:
            _tmp += other.and_list

        if other.or_list is not None or other.fields is not None:
            _tmp.append(other)

        return Filter(and_list=_tmp)

    def __or__(self, other):
        _tmp = []

        if self.or_list is not None:
            _tmp += self.or_list

        if self.and_list is not None or self.fields is not None:
            _tmp.append(self)

        if other.or_list is not None:
            _tmp += other.or_list
        if other.and_list is not None or other.fields is not None:
            _tmp.append(other)

        return Filter(or_list=_tmp)

    def field_to_query(self, field):
        field, comparison = list(field.items())[0]
        if isinstance(comparison, Comparison):
            comparison = comparison.dict()
        else:
            comparison = {"operator": None, "value": comparison}
        if comparison["operator"]:
            return {field: {comparison["operator"]: comparison["value"]}}
        return {field: comparison["value"]}

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


class DataFilter(BaseModel):
    """
    Pydantic model for handeling filtering. The model has a to_query() method used internally to convert model to MongoDB format.
    
    Parameters
    ----------
    gte: string(`ISO 8601 timestamp <https://docs.clarify.io/api/1.1beta2/types/fields#datetime>`__) or python datetime, optional, default <now - 7 days>
        An RFC3339 time describing the inclusive start of the window.

    lt: string(`ISO 8601 timestamp <https://docs.clarify.io/api/1.1beta2/types/fields#datetime>`__) or python datetime, optional, default <now + 7 days>
        An RFC3339 time describing the exclusive end of the window.

    Example
    -------
    >>> from pyclarify import query
    >>> data_filter = query.DataFilter(gte='2022-08-01T16:00:20Z',lt='2022-08-02T16:00:20Z')
    >>> data_filter.to_query()
    ... {'times': {'$gte': '2022-08-01T16:00:20Z', '$lt': '2022-08-02T16:00:20Z'}}
    """

    gte: Optional[Union[str, datetime]] = None
    lt: Optional[Union[str, datetime]] = None

    @root_validator(pre=False, allow_reuse=True)
    def field_must_reflect_operator(cls, values):
        gte = values["gte"] if "gte" in values.keys() else None
        lt = values["lt"] if "lt" in values.keys() else None

        if gte:
            values["gte"] = DateField(operator=Operators.GTE, time=gte)
        if lt:
            values["lt"] = DateField(operator=Operators.LT, time=lt)

        return values

    def to_query(self):
        q = {}
        if self.gte:
            gte = self.gte.dict()["query"]
            q.update(gte)
        if self.lt:
            lt = self.lt.dict()["query"]
            q.update(lt)
        return {"times": q}
