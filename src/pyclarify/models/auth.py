from pydantic import BaseModel, constr
from pydantic.fields import Optional
from typing import List, Union, Dict
from datetime import datetime, timedelta


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
