import sys
import unittest
import json
from unittest.mock import patch

sys.path.insert(1, "src/")

from pyclarify.oauth2 import GetToken


class TestGetToken(unittest.TestCase):
    def setUp(self):
        self.credentials_path = "./tests/data/test-clarify-credentials.json"

        f = open(self.credentials_path)
        self.credentials_dict = json.load(f)
        f.close()

        f = open("./tests/data/mock-token.json")
        self.mock_token = json.load(f)
        f.close()

        self.mock_token2 = self.mock_token
        self.mock_token2["access_token"] = "<YOUR_ACCESS_TOKEN2>"

        self.oauth_request_body_model = dict(
            {
                "grant_type": "client_credentials",
                "client_id": "test_id_123",
                "client_secret": "test_pass_123",
                "audience": "https://api.clarify.us/v1/",
            }
        )
        self.gettoken = GetToken(self.credentials_path)

    def test_read_credentials_path(self):
        """
        Test that it can read the credentials from folder path
        """

        token_client = GetToken(self.credentials_path)
        self.assertEqual(token_client.credentials, self.oauth_request_body_model)

    def test_read_credentials_string(self):
        """
        Test that it can read the credentials from string
        """
        credentials_string = json.dumps(self.credentials_dict)
        token_client = GetToken(credentials_string)
        self.assertEqual(token_client.credentials, self.oauth_request_body_model)

    def test_read_credentials_dict(self):
        """
        Test that it can read the credentials from a dictionary
        """
        token_client = GetToken(self.credentials_dict)
        self.assertEqual(token_client.credentials, self.oauth_request_body_model)

    def test_no_input(self):
        """
        Test that it gets a TypeError when not providing an input
        """
        self.assertRaises(TypeError, GetToken)

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
