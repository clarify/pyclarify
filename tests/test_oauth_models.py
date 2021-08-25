import unittest
import sys
import json
import requests

sys.path.insert(1, "src/pyclarify")
import models


class TestModels(unittest.TestCase):
    def test_load_file(self):
        with open("clarify-credentials.json") as f:
            data = json.load(f)
            self.assertEqual(data["apiUrl"], "https://api.clarify.us/v1/")

    def test_populate_auth_objs(self):
        with open("clarify-credentials.json") as f:
            data = json.load(f)
            credential_obj = models.auth.ClarifyCredential(**data)
            self.assertEqual(credential_obj.credentials.type, "client-credentials")
            oauth_request_obj = models.auth.OAuthRequestBody(client_id=credential_obj.credentials.clientId,
                                                             client_secret=credential_obj.credentials.clientSecret)
            self.assertEqual(oauth_request_obj.client_id, credential_obj.credentials.clientId)

    def populate_auth_token(self):
        with open("clarify-credentials.json") as f:
            data = json.load(f)
            credential_obj = models.auth.ClarifyCredential(**data)
            self.assertEqual(credential_obj.credentials.type, "client-credentials")
            oauth_request_obj = models.auth.OAuthRequestBody(client_id=credential_obj.credentials.clientId,
                                                             client_secret=credential_obj.credentials.clientSecret,
                                                             audience=credential_obj.apiUrl)
            response = requests.post(url='https://login.clarify.us/oauth/token',
                                     headers={'content-type': 'application/x-www-form-urlencoded'},
                                     data=oauth_request_obj.dict())

            if response.ok:
                token_obj = models.auth.OAuthResponse(**response.json())
                print(token_obj)
                self.assertEqual(token_obj.token_type, "Bearer")
            else:
                print(response.content)



if __name__ == '__main__':
    unittest.main()