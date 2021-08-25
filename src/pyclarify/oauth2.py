import requests
from models.auth import OAuthResponse, OAuthRequestBody
import json

class GetToken():

    def __init__(
        self, 
        access_token=None,
        ):
        """
        [summary]

        Parameters
        ----------
        client_id : [type]
            [description]
        client_secret : [type]
            [description]
        access_token : [type], optional
            [description], by default None
        """
        self._access_token = access_token


    def load_file(self):
        """
        [summary]

        Returns
        -------
        [type]
            [description]
        """
        with open("clarify-credentials.json") as f:
            data = json.load(f)
            oauth_request_obj = OAuthRequestBody(client_id=data["credentials"]["clientId"],
                                                client_secret=data["credentials"]["clientSecret"])
        return oauth_request_obj

    def get_token(self, url:str,):
        data = self.load_file()
        print(dict(data))
        response = requests.post(url, dict(data))

        if response.ok:
            token_obj = OAuthResponse(**response.json())
        else:
            print(response.content)
        return token_obj