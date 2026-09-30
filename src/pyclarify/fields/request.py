# Copyright 2026 Searis AS

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import ClassVar, FrozenSet
from pydantic import BaseModel, model_serializer


class OmitNoneModel(BaseModel):
    """
    Base for models sent to the API. Fields named in ``omit_if_none`` are left out of the
    request when they are None, so the API applies its own default: the API does not document
    null for those fields, and a stricter API version could reject it.

    :meta private:
    """

    omit_if_none: ClassVar[FrozenSet[str]] = frozenset()

    @model_serializer(mode="wrap")
    def serialize_without_none(self, serialize):
        data = serialize(self)
        for name in self.omit_if_none:
            if name in data and data[name] is None:
                del data[name]
        return data
