import unittest
import sys
import json
import requests
from unittest.mock import patch

sys.path.insert(1, "src/pyclarify")
import models


class TestModels(unittest.TestCase):
    def setUp(self):
        self.example_credentials = """ { "credentials": {
    "type": "client-credentials",
    "clientId": "test_id_123",
    "clientSecret": "test_pass_123"
  },
  "integration": "test_integration_123",
  "apiUrl": "https://api.clarify.us/v1/"
}"""
        self.mock_token = {
            "access_token": "<YOUR_ACCESS_TOKEN>",
            "scope": "invoke:integration",
            "expires_in": 86400,
            "token_type": "Bearer",
        }

    def test_populate_auth_objs(self):
        data = json.loads(self.example_credentials)
        credential_obj = models.auth.ClarifyCredential(**data)
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
        data = json.loads(self.example_credentials)
        credential_obj = models.auth.ClarifyCredential(**data)
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
        data = json.loads(self.example_credentials)
        credential_obj = models.auth.ClarifyCredential(**data)
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
