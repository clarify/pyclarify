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

"""
Oauth2 module for authentication client.

The module provides a class for setting reading clarify credentials used to authenticate
the API client. This module also handles getting access tokens with expiry date.
"""

import requests
import datetime
import json
from os import path

from pyclarify.fields.authentication import OAuthResponse, OAuthRequestBody
from pyclarify.__utils__.exceptions import AuthError, CredentialError


class Authenticator:
    def __init__(self, clarify_credentials):
        """
        Initialiser of auth class.

        Parameters
        ----------
        clarify_credentials : str/dict
            The path to the clarify_credentials.json downloaded from the Clarify app,
            or json/dictionary of the content in clarify_credentials.json
        """
        self.api_url = None
        self.access_token = None
        self.integration_id = None
        self.headers = {"content-type": "application/x-www-form-urlencoded"}
        self.credentials = self.read_credentials(clarify_credentials)
        self.api_url = self.credentials.audience
        self.auth_endpoint = f"{self.api_url}oauth/token"
        self._expire_token = None

    def read_credentials(self, clarify_credentials):
        """
        Read user credentials.

        Parameters
        ----------
        clarify_credentials : str/dict
            The path to the clarify_credentials.json downloaded from the Clarify app,
            or json/dictionary of the content in clarify_credentials.json


        Returns
        -------
        dict
            Dictionary of the user credentials.
        """
        if isinstance(clarify_credentials, str):
            if path.exists(clarify_credentials):
                with open(clarify_credentials) as f:
                    clarify_credentials = json.load(f)
            else:
                try:
                    clarify_credentials = json.loads(clarify_credentials)
                except:
                    raise CredentialError("String not valid", 
                    f"Could not read credentials from: {clarify_credentials}. Make sure the path exists"
                    " or that the string is in valid json format."
                    )
        if isinstance(clarify_credentials, dict):
            clarify_credentials_object = clarify_credentials
        try:
            oauth_request_body = OAuthRequestBody(
                client_id=clarify_credentials_object["credentials"]["clientId"],
                client_secret=clarify_credentials_object["credentials"]["clientSecret"],
                audience=clarify_credentials_object["apiUrl"],
            )
            self.integration_id = clarify_credentials_object["integration"]
        except:
            raise CredentialError("Content not found", 
                    f"Could not read credentials from: {clarify_credentials}. Make sure the object is a"
                    " valid Clarify Credentials file."
                    )
        return oauth_request_body

    def refresh_token(self):
        """
        Get a new token using the users credentials.

        Returns
        -------
        str
            Access token.
        """
        response = requests.post(
            url=self.auth_endpoint, headers=self.headers, data=self.credentials.dict(),
        )

        if response.ok:
            token_obj = OAuthResponse(**response.json())
            self._expire_token = datetime.datetime.now() + token_obj.expires_in
            self.access_token = token_obj.access_token
            return self.access_token
        else:
            raise AuthError(**response.json())

    def get_token(self):
        """
        Check if token exists or has expired, if yes get a new one, else return the old one.

        Returns
        -------
        str
            Access token.
        """
        if (self._expire_token is None) or (
            self._expire_token <= datetime.datetime.now()
        ):
            return self.refresh_token()
        elif self._expire_token > datetime.datetime.now():
            return self.access_token
