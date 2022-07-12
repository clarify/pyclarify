import unittest
import sys
import json
from pydantic.error_wrappers import ValidationError


sys.path.insert(1, "src/")
from pyclarify.fields.error import Error, ErrorData
from pyclarify.views.generics import Response
from pyclarify.views.dataframe import InsertResponse
from pyclarify.views.items import (
    SelectItemsResponse,
    PublishSignalsResponse,
)
from pyclarify.views.signals import (
    SelectSignalsResponse,
    SaveSignalsResponse,
)

class TestError(unittest.TestCase):
    # TODO: Make more thorough
    def setUp(self):
        with open("./tests/data/mock-models-response.json") as f:
            self.mock_data = json.load(f)
        self.error_data = self.mock_data["error_data"]
        self.error = self.mock_data["error"]

    def test_error_data(self):
        error_data = ErrorData(**self.error_data)
        self.assertEqual(
            error_data.json(),
            json.dumps(self.error_data),
        )

    def test_error(self):
        error = Error(**self.error)
        self.assertEqual(
            error.json(),
            json.dumps(self.error),
        )


class TestMaps(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-models-response.json") as f:
            self.mock_data = json.load(f)
        self.insert_response = self.mock_data["insert_response"]
        self.save_signal_response = self.mock_data["save_signal_response"]
        self.publish_signal_response = self.mock_data["publish_signal_response"]
        self.select_items_response = self.mock_data["select_items_response"]
        self.select_signals_response = self.mock_data["select_signals_response"]

    def test_insert_map(self):
        try:
            InsertResponse(**self.insert_response)
        except ValidationError:
            self.fail("InsertResponse raised ValidationError unexpectedly!")

    def test_save_signals_map(self):
        try:
            SaveSignalsResponse(**self.save_signal_response)
        except ValidationError:
            self.fail("SaveSignalsResponse raised ValidationError unexpectedly!")

    def test_select_items_map(self):
        try:
            SelectItemsResponse(**self.select_items_response)
        except ValidationError:
            self.fail("SelectItemsResponse raised ValidationError unexpectedly!")

    def test_select_signals_map(self):
        try:
            SelectSignalsResponse(**self.select_signals_response)
        except ValidationError:
            self.fail("SelectSignalsResponse raised ValidationError unexpectedly!")

    def test_publish_signals_map(self):
        try:
            PublishSignalsResponse(**self.publish_signal_response)
        except ValidationError:
            self.fail("PublishSignalsResponse raised ValidationError unexpectedly!")


class TestResponse(unittest.TestCase):
    def setUp(self):
        with open("./tests/data/mock-models-response.json") as f:
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
        self.assertIsInstance(res.result, SelectItemsResponse)

    def test_select_signals_response(self):
        response = self.generic_response
        response["result"] = self.select_signals_response
        try:
            res = Response(**response)
        except ValidationError:
            self.fail("Response raised ValidationError unexpectedly!")

        # Assert correct response type
        self.assertIsInstance(res.result, SelectSignalsResponse)


if __name__ == "__main__":
    unittest.main()
