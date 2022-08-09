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
from datetime import datetime
from pydantic.fields import Optional

from pydantic import BaseModel

from pyclarify.fields.constraints import Annotations, SHA1Hash

class ResourceMetadata(BaseModel):
    annotations: Annotations
    attributesHash: SHA1Hash
    relationshipsHash: SHA1Hash
    updatedAt: datetime
    createdAt: datetime

class BaseResource(BaseModel):
    id: str
    type: str
    meta: ResourceMetadata

class SelectionMeta(BaseModel):
    total: int
    groupIncludedByType: bool


class RelationshipMetadata(BaseModel):
    type: str
    id: str


class RelationshipData(BaseModel):
    data: Optional[RelationshipMetadata]


class RelationshipsDict(BaseModel):
    integration: RelationshipData
    item: RelationshipData
