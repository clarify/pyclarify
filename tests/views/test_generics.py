import unittest
import sys
import json
from pydantic.error_wrappers import ValidationError

sys.path.insert(1, "src/")
from pyclarify.fields.constraints import ApiMethod
from pyclarify.views.generics import Request, Response, Selection
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


class TestRequest(unittest.TestCase):
    def setUp(self):
        with open("./tests/mock_data/generics.json") as f:
            generic_data = json.load(f)
            self.generic_request = generic_data["generic_request"]
            self.methods = generic_data["methods"]

        with open("./tests/mock_data/dataframe.json") as f:
            dataframe_data = json.load(f)
            self.insert_args = dataframe_data["insert"]["args"]

        with open("./tests/mock_data/items.json") as f:
            item_data = json.load(f)
            select_items_args = item_data["select_items"]["args"]
            self.select_items_params = {"query": select_items_args}

            self.publish_signals_args = item_data["publish_signals"]["args"]

        with open("./tests/mock_data/signals.json") as f:
            signals_data = json.load(f)
            select_signals_args = signals_data["select_signals"]["args"]
            include = select_signals_args.pop("include")
            self.select_signals_params = {"query": select_signals_args}
            self.select_signals_params["integration"] = "c618rbfqfsj7mjkj0ss1"
            self.select_signals_params["include"] = include
            
            self.save_signals_args = signals_data["save_signals"]["args"]

    def test_insert_creation(self):
        try:
            req = Request(method=ApiMethod.insert, params=self.insert_args)
        except ValidationError:
            self.fail("Request raised ValidationError unexpectedly!")

        self.assertIsInstance(req.params, InsertParams)

    def test_save_signals_creation(self):
        try:
            req = Request(
                method=ApiMethod.save_signals, params=self.save_signals_args
            )
        except ValidationError:
            self.fail("Request raised ValidationError unexpectedly!")

        self.assertIsInstance(req.params, SaveSignalsParams)

    def test_select_items_creation(self):
        try:
            req = Request(
                method=ApiMethod.select_items, params=self.select_items_params
            )
        except ValidationError:
            self.fail("Request raised ValidationError unexpectedly!")

        self.assertIsInstance(req.params, SelectItemsParams)

    def test_select_signals_creation(self):
        try:
            req = Request(
                method=ApiMethod.select_signals, params=self.select_signals_params
            )
        except ValidationError:
            self.fail("Request raised ValidationError unexpectedly!")

        self.assertIsInstance(req.params, SelectSignalsParams)

    def test_publish_signals_creation(self):
        try:
            req = Request(
                method=ApiMethod.publish_signals, params=self.publish_signals_args
            )
        except ValidationError:
            self.fail("Request raised ValidationError unexpectedly!")

        self.assertIsInstance(req.params, PublishSignalsParams)


class TestMaps(unittest.TestCase):
    def setUp(self):
        with open("./tests/mock_data/items.json") as f:
            mock_data = json.load(f)
            self.select_items_response = mock_data["select_items"]["response"]["result"]

        with open("./tests/mock_data/signals.json") as f:
            mock_data = json.load(f)
            self.select_signals_response = mock_data["select_signals"]["response"]["result"]

        with open("./tests/mock_data/dataframe.json") as f:
            mock_data = json.load(f)
            self.data_frame_response = mock_data["data_frame"]["response"]["result"]

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

    def test_data_frame_map(self):
        try:
            Selection(**self.data_frame_response)
        except ValidationError:
            self.fail("Selection raised ValidationError unexpectedly!")


class TestResponse(unittest.TestCase):
    def setUp(self):

        with open("./tests/mock_data/items.json") as f:
            mock_data = json.load(f)
            self.select_items_response = mock_data["select_items"]["response"]["result"]
            self.publish_signal_response = mock_data["publish_signals"]["response"]


        with open("./tests/mock_data/signals.json") as f:
            mock_data = json.load(f)
            self.select_signals_response = mock_data["select_signals"]["response"]["result"]
            self.save_signal_response = mock_data["save_signals"]["response"]


        with open("./tests/mock_data/dataframe.json") as f:
            mock_data = json.load(f)
            self.data_frame_response = mock_data["data_frame"]["response"]["result"]
            self.insert_response = mock_data["insert"]["response"]

        with open("./tests/mock_data/generics.json") as f:
            mock_data = json.load(f)
            self.generic_response = mock_data["generic_response"]

    def test_insert_response(self):
        response = self.generic_response
        response["result"] = self.insert_response
        try:
            res = Response(**self.insert_response)
        except ValidationError:
            self.fail("Response raised ValidationError unexpectedly!")

        self.assertIsInstance(res.result, InsertResponse)

    def test_signal_save_response(self):
        response = self.generic_response
        response["result"] = self.save_signal_response
        try:
            res = Response(**response)
        except ValidationError:
            self.fail("Response raised ValidationError unexpectedly!")

        self.assertIsInstance(res.result, SaveSignalsResponse)

    def test_signal_publish_response(self):
        response = self.generic_response
        response["result"] = self.publish_signal_response
        try:
            res = Response(**response)
        except ValidationError:
            self.fail("Response raised ValidationError unexpectedly!")

        self.assertIsInstance(res.result, PublishSignalsResponse)

    def test_select_items_response(self):
        response = self.generic_response
        response["result"] = self.select_items_response
        try:
            res = Response(**response)
        except ValidationError:
            self.fail("Response raised ValidationError unexpectedly!")

        self.assertIsInstance(res.result, Selection)

    def test_select_signals_response(self):
        response = self.generic_response
        response["result"] = self.select_signals_response
        try:
            res = Response(**response)
        except ValidationError:
            self.fail("Response raised ValidationError unexpectedly!")

        self.assertIsInstance(res.result, Selection)


if __name__ == "__main__":
    unittest.main()
