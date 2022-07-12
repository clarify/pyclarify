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


from .constraints import LimitSelectItems, LimitSelectSignals
from pydantic.fields import Optional
from pydantic import BaseModel, Extra
from typing_extensions import Literal
from typing import Union
from datetime import datetime, timedelta


class QueryParams(BaseModel):
    include: Optional[bool] = False
    filter: Optional[dict] = {}
    skip: Optional[int] = 0


class SelectSignalsSignalsParams(QueryParams, extra=Extra.forbid):
    limit: Optional[LimitSelectSignals] = 50


class SelectItemsItemsParams(QueryParams, extra=Extra.forbid):
    limit: Optional[LimitSelectItems] = 10


class DataQuery(BaseModel, extra=Extra.forbid):
    include: bool = False
    notBefore: Optional[datetime]
    before: Optional[datetime]
    rollup: Union[timedelta, Literal["window"]] = None


class ResourceQuery(BaseModel, extra=Extra.forbid):
    include: bool = False
    filter: dict  # TODO: ResourceFilter (https://docs.clarify.io/v1.1/reference/filtering)
    limit: int = (
        0  # select_items: max=50, default=10 | select_signal: max=1000, default=50
    )
    skip: int = 0
