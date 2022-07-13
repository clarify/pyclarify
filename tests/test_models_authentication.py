import unittest
import sys
import json

sys.path.insert(1, "src/")
from pyclarify.fields.authentication import OAuthRequestBody, ClarifyCredential


class TestOauthModels(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-clarify-credentials.json") as f:
            self.credentials_dict = json.load(f)

    def test_populate_auth_objs(self):
        credential_obj = ClarifyCredential(**self.credentials_dict)
        self.assertEqual(credential_obj.credentials.type, "client-credentials")
        oauth_request_obj = OAuthRequestBody(
            client_id=credential_obj.credentials.clientId,
            client_secret=credential_obj.credentials.clientSecret,
        )
        self.assertEqual(
            oauth_request_obj.client_id, credential_obj.credentials.clientId
        )


if __name__ == "__main__":
    unittest.main()
