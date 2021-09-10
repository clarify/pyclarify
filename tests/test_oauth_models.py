import unittest
import sys
import json
import requests
from unittest.mock import patch

sys.path.insert(1, "src/")
import pyclarify.models as models


class TestModels(unittest.TestCase):
    def setUp(self):
        f = open("./tests/data/test-clarify-credentials.json")
        self.credentials_dict = json.load(f)
        f.close()

        f = open("./tests/data/mock-token.json")
        self.mock_token = json.load(f)
        f.close()

    def test_populate_auth_objs(self):
        credential_obj = models.auth.ClarifyCredential(**self.credentials_dict)
        self.assertEqual(credential_obj.credentials.type, "client-credentials")
        oauth_request_obj = models.auth.OAuthRequestBody(
            client_id=credential_obj.credentials.clientId,
            client_secret=credential_obj.credentials.clientSecret,
        )
        self.assertEqual(
            oauth_request_obj.client_id, credential_obj.credentials.clientId
        )

    @patch("requests.post")
    def test_populate_auth_token(self, mock_request):
        mock_request.return_value.ok = True
        mock_request.return_value.status_code = 200
        mock_request.return_value.json = lambda: self.mock_token
        credential_obj = models.auth.ClarifyCredential(**self.credentials_dict)
        self.assertEqual(credential_obj.credentials.type, "client-credentials")
        oauth_request_obj = models.auth.OAuthRequestBody(
            client_id=credential_obj.credentials.clientId,
            client_secret=credential_obj.credentials.clientSecret,
            audience=credential_obj.apiUrl,
        )
        response = requests.post(
            url="https://login.clarify.us/oauth/token",
            headers={"content-type": "application/x-www-form-urlencoded"},
            data=oauth_request_obj.dict(),
        )

        if response.ok:
            token_obj = models.auth.OAuthResponse(**response.json())
            self.assertEqual(token_obj.token_type, "Bearer")
            self.assertEqual(token_obj.access_token, "<YOUR_ACCESS_TOKEN>")
        else:
            self.assertEqual(401, response.status_code)

    @patch("requests.post")
    def test_populate_auth_token_fail(self, mock_request):
        mock_request.return_value.ok = False
        mock_request.return_value.status_code = 401
        mock_request.return_value.json = lambda: self.mock_token
        credential_obj = models.auth.ClarifyCredential(**self.credentials_dict)
        self.assertEqual(credential_obj.credentials.type, "client-credentials")
        oauth_request_obj = models.auth.OAuthRequestBody(
            client_id=credential_obj.credentials.clientId,
            client_secret=credential_obj.credentials.clientSecret,
            audience=credential_obj.apiUrl,
        )
        response = requests.post(
            url="https://login.clarify.us/oauth/token",
            headers={"content-type": "application/x-www-form-urlencoded"},
            data=oauth_request_obj.dict(),
        )

        if response.ok:
            token_obj = models.auth.OAuthResponse(**response.json())
            self.assertEqual(token_obj.token_type, "Bearer")
            self.assertEqual(token_obj.access_token, "<YOUR_ACCESS_TOKEN>")
        else:
            self.assertEqual(401, response.status_code)


if __name__ == "__main__":
    unittest.main()
