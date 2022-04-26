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

from pydantic import BaseModel
from pydantic.fields import Optional
from datetime import timedelta


class OAuthRequestBody(BaseModel):
    grant_type: str = "client_credentials"
    client_id: str
    client_secret: str
    audience: str = "https://api.clarify.io/v1/"


class OAuthResponse(BaseModel):
    access_token: str
    scope: Optional[str]
    expires_in: timedelta
    token_type: str = "Bearer"


class Credential(BaseModel):
    type: str
    clientId: str
    clientSecret: str


class ClarifyCredential(BaseModel):
    apiUrl: str
    integration: str
    credentials: Credential
