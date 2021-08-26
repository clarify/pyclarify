import requests
from models.auth import OAuthResponse, OAuthRequestBody
import json
import datetime

class GetToken():

    def __init__(self):
        self.access_token = None
        self._expire_date = datetime.datetime.now()
        self._expire_token = None

    def load_file(self):
        with open("clarify-credentials.json") as f:
            data = json.load(f)
            oauth_request_obj = OAuthRequestBody(client_id=data["credentials"]["clientId"],
                                                client_secret=data["credentials"]["clientSecret"])
        return oauth_request_obj.dict()

    def new_token(self, url:str):
        data = self.load_file()
        response = requests.post(url, data)
        token_obj = OAuthResponse(**response.json())
        self._expire_token = self._expire_date + token_obj.dict()["expires_in"]
        self.access_token = token_obj.dict()["access_token"]

        return self.access_token

    def get_token(self, url:str):
        if self._expire_token == None:
            self.new_token(url)

        elif self._expire_token > self._expire_date:
            return self.access_token
