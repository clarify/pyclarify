import sys
import unittest
import json
from unittest.mock import patch

sys.path.insert(1, "src/")

from pyclarify.oauth2 import GetToken

URL = "https://api.clarify.us/v1/"


class TestGetToken(unittest.TestCase):
    def setUp(self):

        self.url = URL
        self.mock_token = {
            "access_token": "<YOUR_ACCESS_TOKEN>",
            "scope": "invoke:integration",
            "expires_in": 86400,
            "token_type": "Bearer",
        }

        self.mock_token2 = {
            "access_token": "<YOUR_ACCESS_TOKEN2>",
            "scope": "invoke:integration",
            "expires_in": 86400,
            "token_type": "Bearer",
        }

        self.oauth_request_body_model = dict(
            {
                "grant_type": "client_credentials",
                "client_id": "test_id_123",
                "client_secret": "test_pass_123",
                "audience": "https://api.clarify.us/v1/",
            }
        )
        f = open("./tests/test-clarify-credentials.json")
        clarify_credentials = json.load(f)
        self.example_credentials = clarify_credentials

        self.gettoken = GetToken(self.url, self.example_credentials)

    def test_read_credentials(self):
        """
        Test that it can read the credentials
        """
        req = self.gettoken.read_credentials()
        self.assertEqual(req, self.oauth_request_body_model)

    @patch("pyclarify.oauth2.requests.post")
    def test_get_token(self, mock_request):
        """
        Test that it can get and update the token
        """
        mock_request.return_value.json = lambda: self.mock_token
        response = self.gettoken.get_token()
        self.assertEqual(response, self.mock_token["access_token"])

        mock_request.return_value.json = lambda: self.mock_token2
        response = self.gettoken.get_token()
        self.assertEqual(response, self.mock_token["access_token"])

        self.gettoken._expire_token = None
        response = self.gettoken.get_token()
        self.assertEqual(response, self.mock_token2["access_token"])


if __name__ == "__main__":
    unittest.main()
