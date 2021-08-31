import requests
from models.auth import OAuthResponse, OAuthRequestBody, ClarifyCredential
import datetime


class GetToken:
    def __init__(self, url, credential_file: ClarifyCredential):

        self.access_token = None
        self.content_type = "application/x-www-form-urlencoded"
        self.credential_file = credential_file
        self._expire_date = datetime.datetime.now()
        self._expire_token = None
        self.url = url

    def read_credentials(self):
        """
        Read user credentials.

        Returns
        -------
        dict
            Dictionary of the user credentials.
        """
        data = self.credential_file
        oauth_request_body = OAuthRequestBody(
            client_id=data["credentials"]["clientId"],
            client_secret=data["credentials"]["clientSecret"],
        )
        return oauth_request_body.dict()

    def new_token(self, url: str):
        """
        Get a new token using the users credentials.

        Parameters
        ----------
        url : str, default "https://login.clarify.us/oauth/token"
            URL to make the post request to the Clarify API.

        Returns
        -------
        str
            User token.
        """
        data = self.read_credentials()
        response = requests.post(
            url=url,
            headers={"content-type": self.content_type},
            data=data,
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
            return self.new_token(self.url)
        elif self._expire_token > datetime.datetime.now():
            return self.access_token
