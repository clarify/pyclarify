# Copyright 2023 Searis AS

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import Dict, List, Optional
from pydantic import BaseModel, Extra
from pyclarify.fields.constraints import (
    Alias,
    BucketOffset,
    TimeAggregationMethod,
    GroupAggregationMethod,
    ResourceID,
    State,
)

from pyclarify.fields.query import SelectionFormat
from pyclarify.query.query import (
    DataQuery,
    ResourceQuery,
)


class ItemAggregation(BaseModel):
    """
    Model for creating an item aggregation to be used with the `clarify.evaluate` method.

    Parameters
    ----------

    id: ResourceID
        The ID of the item to be aggregated.

    aggregation: str
        The aggregation type to be done. Current legal aggregations are found `here <https://docs.clarify.io/api/1.1/types/fields#data-aggregation>`__.

    state: int[0:9999]
        The integer denoting the state to be used in the aggregation. Only necessary when using state based aggregation.

    lead: int[-1000:1000]
        Shift buckets backwards by N.

    lag: int[-1000:1000]
        Shift buckets forwards by N.

    alias: string
        A short alias to use in formulas as well as in the data frame results.


    Example
    -------

        >>> from pyclarify import ItemAggregation

        Creating a minimal item aggregation.

        >>> item_aggregation = ItemAggregation(
        ...     id="cbpmaq6rpn52969vfl0g",
        ...     aggregation="avg",
        ...     alias="i2"
        ... )

        Creating an item aggregation with all attributes set.

        >>> item_aggregation = ItemAggregation(
        ...     id="cbpmaq6rpn52969vfl00",
        ...     aggregation="max",
        ...     state=1,
        ...     lead=1,
        ...     lag=1,
        ...     alias="i1"
        ... )
    """

    id: ResourceID
    aggregation: TimeAggregationMethod
    state: Optional[State] = None
    lead: Optional[BucketOffset] = None
    lag: Optional[BucketOffset] = None
    alias: Alias


class GroupAggregation(BaseModel):
    """
    Model for creating a group aggregation to be used with the `clarify.evaluate` method.

    Parameters
    ----------

    query: ResourceQuery
        A query matching items in an integration to be added to the group.

    timeAggregation: str
        The time aggregation type to be done within items. Current legal aggregations are found `here <https://docs.clarify.io/api/1.2/types/fields#time-aggregation>`__.

    groupAggregation: str
        The group aggregation type to be done across groups. Current legal aggregations are found `here <https://docs.clarify.io/api/1.2/types/fields#group-aggregation>`__.

    state: int[0:9999]
        The integer denoting the state to be used in the aggregation. Only necessary when using state based aggregation. This only applies to time aggregations of type `state-seconds`, `state-percent`, and `state-rate`.

    lead: int[-1000:1000]
        Shift buckets backwards by N.

    lag: int[-1000:1000]
        Shift buckets forwards by N.

    alias: string
        A short alias to use in formulas as well as in the data frame results.


    Example
    -------

        >>> from pyclarify import GroupAggregation

        Creating a minimal group aggregation.

        >>> group_aggregation = GroupAggregation(
        ...     query=ResourceQuery(filter={}),
        ...     timeAggregation="avg",
        ...     groupAggregationMethod="avg"
        ...     alias="g1"
        ... )

        Creating a group aggregation with all attributes set.

        >>> group_aggregation = GroupAggregation(
        ...     query=ResourceQuery(filter={}),
        ...     timeAggregationMethod="max",
        ...     groupAggregationMethod="avg",
        ...     state=1,
        ...     lead=1,
        ...     lag=1,
        ...     alias="g1"
        ... )
    """

    query: ResourceQuery
    timeAggregation: TimeAggregationMethod
    groupAggregation: GroupAggregationMethod
    state: Optional[State] = None
    lead: Optional[BucketOffset] = None
    lag: Optional[BucketOffset] = None
    alias: Alias


class Calculation(BaseModel):
    """
    Model for creating a calculation to be used in evaluate endpoint.

    Parameters
    ----------

    formula: str
        The formula to be applied. Current legal calculations are found `here <https://docs.clarify.io/users/admin/items/calculated-items#formula>`__.

    alias: string
        A short alias to use in formulas as well as in the data frame results.


    Example
    -------

        >>> from pyclarify import Calculation

        Creating a calculation assuming we have items with aliases "i1" and "i2".

        >>> calculation = Calculation(
        ...     formula="i1 + i2"
        ...     alias="c1"
        ... )

        Creating a calculation using other calculations.

        >>> calc1 = Calculation(
        ...     formula="i1 + i2"
        ...     alias="c1"
        ... )
        >>> calc2 = Calculation(
        ...     formula="c1**2 + i1"
        ...     alias="c1"
        ... )
    """

    # TODO: constraints for formula?
    formula: str
    alias: Alias


class EvaluateParams(BaseModel):
    """
    :meta private:
    """

    items: Optional[List[ItemAggregation]] = []
    groups: Optional[List[GroupAggregation]] = []
    calculations: List[Calculation]
    data: DataQuery
    include: List
    format: Optional[SelectionFormat] = SelectionFormat(dataAsArray=False)


# Evaluate uses DataFrame as response
