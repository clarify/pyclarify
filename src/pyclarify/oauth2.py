import requests
import datetime
import logging
import json
from os import path

from pyclarify.models.auth import OAuthResponse, OAuthRequestBody, ClarifyCredential


class GetToken:
    def __init__(self, clarify_credentials_path: str):
        """
        Initialiser of auth class

        Parameters
        ----------
        clarify_credentials_path : str
            The path to the clarify_credentials.json downloaded from the Clarify app
        """
        self.api_url = None
        self.access_token = None
        self.integration_id = None
        self.headers = {"content-type": "application/x-www-form-urlencoded"}
        self.credentials = self.read_credentials(clarify_credentials_path)
        self.api_url = self.credentials.audience
        self.auth_endpoint = f"{self.api_url}oauth/token"
        self._expire_token = None

    def read_credentials(self, clarify_credentials_path):
        """
        Read user credentials.

        Returns
        -------
        dict
            Dictionary of the user credentials.
        """
        if isinstance(clarify_credentials_path, str):
            if path.exists(clarify_credentials_path):
                f = open(clarify_credentials_path)
                clarify_credentials = json.load(f)
                f.close()
            else:
                try:
                    clarify_credentials = json.loads(clarify_credentials_path)
                except:
                    logging.error(
                        f"{clarify_credentials_path} is of type string, but is not a valid path or credentials"
                    )
                    return False

        if isinstance(clarify_credentials_path, dict):
            clarify_credentials = clarify_credentials_path

        oauth_request_body = OAuthRequestBody(
            client_id=clarify_credentials["credentials"]["clientId"],
            client_secret=clarify_credentials["credentials"]["clientSecret"],
            audience=clarify_credentials["apiUrl"],
        )
        self.integration_id = clarify_credentials["integration"]
        return oauth_request_body

    def get_new_token(self):
        """
        Get a new token using the users credentials.

        Returns
        -------
        str
            User token.
        """
        response = requests.post(
            url=self.auth_endpoint,
            headers=self.headers,
            data=self.credentials.dict(),
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
            User token.
        """
        if (self._expire_token is None) or (
            self._expire_token <= datetime.datetime.now()
        ):
            return self.get_new_token()
        elif self._expire_token > datetime.datetime.now():
            return self.access_token


class AuthError(Exception):
    def __init__(self, error, error_description):
        self.error = error
        self.error_description = error_description

    def __str__(self):
        return (
            f"Authentication error: {self.error}. Description: {self.error_description}"
        )
