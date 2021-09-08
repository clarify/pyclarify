import requests
from pyclarify.models.auth import OAuthResponse, OAuthRequestBody, ClarifyCredential
import datetime
import json


class GetToken:
    def __init__(self, clarify_credentials_path: str):
        """
        Initialiser of auth class

        Parameters
        ----------
        clarify_credentials_path : str
            The path to the clarify_credentials.json downloaded from the Clarify app
        """
        self.access_token = None
        self.headers = {"content-type": "application/x-www-form-urlencoded"}
        self.credentials = self.read_credentials(clarify_credentials_path)
        self.auth_endpoint = "https://login.clarify.us/oauth/token"
        self._expire_token = None

    def read_credentials(self, clarify_credentials_path):
        """
        Read user credentials.

        Returns
        -------
        dict
            Dictionary of the user credentials.
        """
        f = open(clarify_credentials_path)
        clarify_credentials = json.load(f)
        f.close()
        oauth_request_body = OAuthRequestBody(
            client_id=clarify_credentials["credentials"]["clientId"],
            client_secret=clarify_credentials["credentials"]["clientSecret"],
            audience=clarify_credentials["apiUrl"],
        )
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
            url=self.auth_endpoint, headers=self.headers, data=self.credentials,
        )

        token_obj = OAuthResponse(**response.json())
        self._expire_token = datetime.datetime.now() + token_obj.expires_in
        self.access_token = token_obj.access_token
        return self.access_token

    def get_token(self):
        """
        Check if token exists or has expired, if yes get a new one, else return the old one.

        Returns
        -------
        str
            User token.
        """
        if (self._expire_token == None) or (
            self._expire_token <= datetime.datetime.now()
        ):
            return self.get_new_token()
        elif self._expire_token > datetime.datetime.now():
            return self.access_token
