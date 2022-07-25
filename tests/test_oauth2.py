"""
Copyright 2021 Clarify

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import unittest
import json
from unittest.mock import patch

sys.path.insert(1, "src/")

from pyclarify.jsonrpc.oauth2 import Authenticator


class TestAuthenticator(unittest.TestCase):
    def setUp(self):
        self.credentials_path = "./tests/data/mock-clarify-credentials.json"

        with open(self.credentials_path) as f:
            self.credentials_dict = json.load(f)

        with open("./tests/data/mock-authentication.json") as f:
            self.mock_authentication = json.load(f)

        self.mock_token = self.mock_authentication["mock_token"]
        self.mock_token2 = self.mock_token
        self.mock_token2["access_token"] = "<YOUR_ACCESS_TOKEN2>"

        self.oauth_request_body = self.mock_authentication["oauth_request_body"]
        self.gettoken = Authenticator(self.credentials_path)

    def test_read_credentials_path(self):
        """
        Test that it can read the credentials from folder path
        """

        token_client = Authenticator(self.credentials_path)
        self.assertEqual(token_client.credentials, self.oauth_request_body)

    def test_read_credentials_string(self):
        """
        Test that it can read the credentials from string
        """
        credentials_string = json.dumps(self.credentials_dict)
        token_client = Authenticator(credentials_string)
        self.assertEqual(token_client.credentials, self.oauth_request_body)

    def test_read_credentials_dict(self):
        """
        Test that it can read the credentials from a dictionary
        """
        token_client = Authenticator(self.credentials_dict)
        self.assertEqual(token_client.credentials, self.oauth_request_body)

    def test_no_input(self):
        """
        Test that it gets a TypeError when not providing an input
        """
        self.assertRaises(TypeError, Authenticator)

    @patch("pyclarify.jsonrpc.oauth2.requests.post")
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
