"""
Copyright 2023 Clarify

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
from pyclarify.client import JSONRPCClient
from pyclarify.views.generics import Response
from pyclarify.jsonrpc.oauth2 import Authenticator

class TestJSONRPCClient(unittest.TestCase):
    def setUp(self):
        with open("./tests/mock_data/jsonrpc-client.json") as f:
            self.mock_data = json.load(f)

        self.client = JSONRPCClient(base_url=self.mock_data["mock_url"])
        self.content_type_headers = {"content-type": "application/json"}

        with open("./tests/mock_data/mock-client-common.json") as f:
            self.mock_access_token = json.load(f)["mock_access_token"]

    def test_update_header(self):
        """
        Test for updating request headers of client
        """
        # assert initialisation
        self.assertEqual(self.client.headers, self.content_type_headers)

        # assert direct overwrite
        self.client.headers = {}
        self.assertEqual(self.client.headers, {})

        # assert update_header method working
        self.client.update_headers(self.content_type_headers)
        self.assertEqual(self.client.headers, self.content_type_headers)

        # assert update_header method working with existing headers
        self.client.update_headers(self.content_type_headers)
        self.assertEqual(self.client.headers, self.content_type_headers)

        # assert update_header method working with new headers
        self.client.update_headers({"X-API-Version": "1.0"})

        self.assertEqual(
            self.client.headers,
            {"content-type": "application/json", "X-API-Version": "1.0"},
        )

    def test_create_payload(self):
        VALID_RPC_PAYLOAD = json.dumps(self.mock_data["mock_RPC_payload"])

        payload = self.client.create_payload(
            self.mock_data["mock_method"], self.mock_data["mock_params"]
        )

        # assert correct creation
        self.assertEqual(payload, VALID_RPC_PAYLOAD)

        # assert incrementation of id
        payload_2 = self.client.create_payload(
            self.mock_data["mock_method"], self.mock_data["mock_params"]
        )
        payload_2 = json.loads(payload_2)
        self.assertEqual(payload_2["id"], 2)

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_request_no_iteration(self, client_req_mock, get_token_mock):

        payload = self.client.create_payload(
            "clarify.selectItems", self.mock_data["no_iterations"]["args"]
        )
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data["no_iterations"][
            "response"
        ]

        response = self.client.make_request(payload).json()
        payload = json.loads(payload)


        # assert is JSONRPC
        self.assertEqual(response["jsonrpc"], "2.0")

        # assert is correct id
        self.assertEqual(response["id"], str(payload["id"]))

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_request_one_iteration(self, client_req_mock, get_token_mock):

        payload = self.client.create_payload(
            "clarify.selectItems", self.mock_data["one_iterations"]["args"]
        )
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data["one_iterations"][
            "response"
        ]

        response = self.client.make_request(payload).json()
        payload = json.loads(payload)


        # assert is JSONRPC
        self.assertEqual(response["jsonrpc"], "2.0")

        # assert is correct id
        self.assertEqual(response["id"], str(payload["id"]))

    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_send_request_many_iteration(self, client_req_mock, get_token_mock):

        payload = self.client.create_payload(
            "clarify.selectItems", self.mock_data["many_iterations"]["args"]
        )
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data["many_iterations"][
            "response"
        ]

        response = self.client.make_request(payload).json()
        payload = json.loads(payload)


        # assert is JSONRPC
        self.assertEqual(response["jsonrpc"], "2.0")

        # assert is correct id
        self.assertEqual(response["id"], str(payload["id"]))
    
    @patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token")
    @patch("pyclarify.client.requests.post")
    def test_get_error(self, client_req_mock, get_token_mock):

        payload = self.client.create_payload(
            "clarify.selectItems", self.mock_data["error"]["args"]
        )
        get_token_mock.return_value = self.mock_access_token
        client_req_mock.return_value.ok = True
        client_req_mock.return_value.json = lambda: self.mock_data["error"][
            "response"
        ]

        response = self.client.make_request(payload).json()
        payload = json.loads(payload)


        # assert is JSONRPC
        self.assertEqual(response["jsonrpc"], "2.0")

        # assert is correct id
        self.assertEqual(response["id"], str(payload["id"]))


    def test_authentication(self):
        self.client.authenticate("./tests/mock_data/mock-clarify-credentials.json")
        self.assertIsInstance(self.client.authentication, Authenticator)
    


if __name__ == "__main__":
    unittest.main()
