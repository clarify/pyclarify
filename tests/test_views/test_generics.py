import unittest
import sys
import json
from pydantic.error_wrappers import ValidationError

sys.path.insert(1, "src/")
from pyclarify.fields.constraints import ApiMethod
from pyclarify.views.generics import Request, JSONRPCRequest, Response, Selection
from pyclarify.views.dataframe import InsertParams, InsertResponse
from pyclarify.views.items import (
    SelectItemsParams,
    PublishSignalsParams,
    PublishSignalsResponse
)
from pyclarify.views.signals import (
    SelectSignalsParams,
    SaveSignalsParams,
    SaveSignalsResponse
)


class TestJSONRPCRequest(unittest.TestCase):
    def setUp(self):
        with open("./tests/mock_data/request.json") as f:
            self.mock_data = json.load(f)

    def test_creation(self):
        empty_request = JSONRPCRequest()
        self.assertEqual(
            empty_request.json(),
            json.dumps(self.mock_data["select_items"]),
        )

    def test_creation_insert(self):
        empty_request = JSONRPCRequest(method=ApiMethod.insert)
        self.assertEqual(
            empty_request.json(),
            json.dumps(self.mock_data["insert"]),
        )

    def test_creation_save(self):
        empty_request = JSONRPCRequest(method=ApiMethod.save_signals)
        self.assertEqual(
            empty_request.json(),
            json.dumps(self.mock_data["save_signals"]),
        )

    def test_creation_params_1(self):
        empty_request = JSONRPCRequest(params={})
        self.assertEqual(
            empty_request.json(),
            json.dumps(self.mock_data["select_items"]),
        )


class TestRequest(unittest.TestCase):
    def setUp(self):
        with open("./tests/mock_data/request.json") as f:
            self.mock_data = json.load(f)

        with open("./tests/mock_data/signals.json") as f:
            signals_data = json.load(f)
            select_signals_args = signals_data["select_signals"]["args"]
            include = select_signals_args.pop("include")
            self.select_signals_params = {"query": select_signals_args}
            self.select_signals_params["integration"] = "c618rbfqfsj7mjkj0ss1"
            self.select_signals_params["include"] = include
            
            self.save_signals_params = signals_data["save_signals"]["args"]


        self.insert_params = self.mock_data["insert_params"]
        self.select_items_params = self.mock_data["select_items_params"]
        self.publish_signals_params = self.mock_data["publish_signals_params"]

    def test_insert_creation(self):
        try:
            req = Request(method=ApiMethod.insert, params=self.insert_params)
        except ValidationError:
            self.fail("Request raised ValidationError unexpectedly!")

        # assert correct params type
        self.assertIsInstance(req.params, InsertParams)

    def test_save_signals_creation(self):
        try:
            req = Request(
                method=ApiMethod.save_signals, params=self.save_signals_params
            )
        except ValidationError:
            self.fail("Request raised ValidationError unexpectedly!")

        # assert correct params type
        self.assertIsInstance(req.params, SaveSignalsParams)

    def test_select_items_creation(self):
        try:
            req = Request(
                method=ApiMethod.select_items, params=self.select_items_params
            )
        except ValidationError:
            self.fail("Request raised ValidationError unexpectedly!")

        # assert correct params type
        self.assertIsInstance(req.params, SelectItemsParams)

    def test_select_signals_creation(self):
        try:
            req = Request(
                method=ApiMethod.select_signals, params=self.select_signals_params
            )
        except ValidationError:
            self.fail("Request raised ValidationError unexpectedly!")

        # assert correct params type
        self.assertIsInstance(req.params, SelectSignalsParams)

    def test_publish_signals_creation(self):
        try:
            req = Request(
                method=ApiMethod.publish_signals, params=self.publish_signals_params
            )
        except ValidationError:
            self.fail("Request raised ValidationError unexpectedly!")

        # assert correct params type
        self.assertIsInstance(req.params, PublishSignalsParams)


class TestMaps(unittest.TestCase):
    def setUp(self):
        with open("./tests/mock_data/response.json") as f:
            self.mock_data = json.load(f)
        self.select_items_response = self.mock_data["select_items_response"]
        self.select_signals_response = self.mock_data["select_signals_response"]
        self.select_dataframe_response = self.mock_data["select_dataframe_response"]

    def test_select_items_map(self):
        try:
            Selection(**self.select_items_response)
        except ValidationError:
            self.fail("Selection raised ValidationError unexpectedly!")

    def test_select_signals_map(self):
        try:
            Selection(**self.select_signals_response)
        except ValidationError:
            self.fail("Selection raised ValidationError unexpectedly!")

    def test_select_dataframe_map(self):
        try:
            Selection(**self.select_dataframe_response)
        except ValidationError:
            self.fail("Selection raised ValidationError unexpectedly!")


class TestResponse(unittest.TestCase):
    def setUp(self):
        with open("./tests/mock_data/response.json") as f:
            self.mock_data = json.load(f)
        self.insert_response = self.mock_data["insert_response"]
        self.save_signal_response = self.mock_data["save_signal_response"]
        self.publish_signal_response = self.mock_data["publish_signal_response"]
        self.select_items_response = self.mock_data["select_items_response"]
        self.select_signals_response = self.mock_data["select_signals_response"]
        self.generic_response = self.mock_data["generic_response"]

    def test_insert_response(self):
        response = self.generic_response
        response["result"] = self.insert_response
        try:
            res = Response(**response)
        except ValidationError:
            self.fail("Response raised ValidationError unexpectedly!")

        # Assert correct response type
        self.assertIsInstance(res.result, InsertResponse)

    def test_signal_save_response(self):
        response = self.generic_response
        response["result"] = self.save_signal_response
        try:
            res = Response(**response)
        except ValidationError:
            self.fail("Response raised ValidationError unexpectedly!")

        # Assert correct response type
        self.assertIsInstance(res.result, SaveSignalsResponse)

    def test_signal_publish_response(self):
        response = self.generic_response
        response["result"] = self.publish_signal_response
        try:
            res = Response(**response)
        except ValidationError:
            self.fail("Response raised ValidationError unexpectedly!")

        # Assert correct response type
        self.assertIsInstance(res.result, PublishSignalsResponse)

    def test_select_items_response(self):
        response = self.generic_response
        response["result"] = self.select_items_response
        try:
            res = Response(**response)
        except ValidationError:
            self.fail("Response raised ValidationError unexpectedly!")

        # Assert correct response type
        self.assertIsInstance(res.result, Selection)

    def test_select_signals_response(self):
        response = self.generic_response
        response["result"] = self.select_signals_response
        try:
            res = Response(**response)
        except ValidationError:
            self.fail("Response raised ValidationError unexpectedly!")

        # Assert correct response type
        self.assertIsInstance(res.result, Selection)


if __name__ == "__main__":
    unittest.main()
