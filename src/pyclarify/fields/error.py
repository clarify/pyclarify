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


from pydantic import BaseModel, ConfigDict, Field
from typing import Any, List, Union, Dict, Optional


class ErrorData(BaseModel):
    """
    Clarify specific error details. Fields the API adds, such as ``pathErrors``, are kept.
    """

    trace: Optional[str] = None
    params: Optional[Dict[str, List[str]]] = None
    model_config = ConfigDict(extra="allow")


class Error(BaseModel):
    code: int
    message: str
    # The API documents an object, but JSON RPC allows any value.
    data: Optional[Union[ErrorData, str, Any]] = Field(None, union_mode="left_to_right")
    model_config = ConfigDict(extra="allow")
