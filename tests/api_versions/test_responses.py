"""
How PyClarify reads responses, checked against the fixtures of each API version.

Assertions compare the parsed result with the raw fixture rather than with hard-coded values,
so they keep working when a placeholder fixture is replaced with a recorded response.
"""

from enum import Enum

from pydantic import ValidationError

from pyclarify import DataFrame, Item
from pyclarify.__utils__.time import parse_datetime, parse_duration
from pyclarify.fields.constraints import SourceTypeSignal, TypeSignal

from .harness import GTE, LT, FakeHTTPResponse, VersionedCase, for_each_api_version, group_aggregation

DURATIONS = ("sampleInterval", "gapDetection")


@for_each_api_version
class ResponseParsing(VersionedCase):
    def assertAttributesMatch(self, parsed, raw):
        for key, raw_value in raw.items():
            self.assertTrue(
                hasattr(parsed, key), f"{type(parsed).__name__} drops the {key!r} attribute returned by API {self.api_version}"
            )
            value = getattr(parsed, key)
            if key in DURATIONS and raw_value is not None:
                raw_value = parse_duration(raw_value)
            if isinstance(value, Enum):
                value = value.value
            self.assertEqual(value, raw_value, key)

    def assertFrameMatches(self, frame, raw):
        self.assertIsInstance(frame, DataFrame)
        self.assertEqual(frame.times, [parse_datetime(t) for t in raw["times"]])
        self.assertEqual(frame.series, raw["series"])
        df = frame.to_pandas()
        self.assertEqual(sorted(df.columns), sorted(raw["series"]))
        self.assertEqual(len(df), len(raw["times"]))

    def test_insert(self):
        raw = self.fixture("insert")["result"]["signalsByInput"]
        result = self.call("insert").result
        self.assertEqual(
            {key: (summary.id, summary.created) for key, summary in result.signalsByInput.items()},
            {key: (summary["id"], summary["created"]) for key, summary in raw.items()},
        )

    def test_save_signals(self):
        raw = self.fixture("save_signals")["result"]["signalsByInput"]
        result = self.call("save_signals").result
        self.assertEqual(
            {key: (s.id, s.created, s.updated) for key, s in result.signalsByInput.items()},
            {key: (s["id"], s["created"], s["updated"]) for key, s in raw.items()},
        )

    def test_publish_signals(self):
        raw = self.fixture("publish_signals")["result"]["itemsBySignal"]
        result = self.call("publish_signals").result
        self.assertEqual(
            {key: (s.id, s.created, s.updated) for key, s in result.itemsBySignal.items()},
            {key: (s["id"], s["created"], s["updated"]) for key, s in raw.items()},
        )

    def test_select_items(self):
        raw = self.fixture("select_items")["result"]
        response = self.call("select_items")
        self.assertIsNone(response.error)
        self.assertEqual(response.result.meta.total, raw["meta"]["total"])
        self.assertEqual([item.id for item in response.result.data], [item["id"] for item in raw["data"]])
        for item, raw_item in zip(response.result.data, raw["data"]):
            # Backward compatibility: attributes are Items, and known enum values enum members.
            self.assertIsInstance(item.attributes, Item)
            self.assertIsInstance(item.attributes.valueType, TypeSignal)
            self.assertEqual(item.type, raw_item["type"])
            self.assertEqual(item.meta.annotations, raw_item["meta"]["annotations"])
            self.assertEqual(item.meta.updatedAt, parse_datetime(raw_item["meta"]["updatedAt"]))
            self.assertAttributesMatch(item.attributes, raw_item["attributes"])

    def test_select_signals(self):
        raw = self.fixture("select_signals")["result"]
        response = self.call("select_signals")
        self.assertIsNone(response.error)
        self.assertEqual([signal.id for signal in response.result.data], [signal["id"] for signal in raw["data"]])
        for signal, raw_signal in zip(response.result.data, raw["data"]):
            self.assertIsInstance(signal.attributes.sourceType, SourceTypeSignal)
            self.assertAttributesMatch(signal.attributes, raw_signal["attributes"])
            linked = signal.relationships.item.data
            self.assertEqual(linked.id if linked else None, (raw_signal["relationships"]["item"]["data"] or {}).get("id"))
        self.assertEqual(
            sorted(item.id for item in response.result.included.items),
            sorted(item["id"] for item in raw["included"]["items"]),
        )

    def test_data_frame(self):
        raw = self.fixture("data_frame")["result"]
        response = self.call("data_frame")
        self.assertIsNone(response.error)
        self.assertFrameMatches(response.result.data, raw["data"])
        self.assertEqual(
            sorted(item.id for item in response.result.included.items),
            sorted(item["id"] for item in raw["included"]["items"]),
        )

    def test_evaluate(self):
        raw = self.fixture("evaluate")["result"]
        response = self.call("evaluate")
        self.assertIsNone(response.error)
        self.assertFrameMatches(response.result.data, raw["data"])

    def test_evaluate_with_groups(self):
        if "groups" not in self.contract.features:
            self.skipTest(f"API {self.api_version} has no group aggregation")
        raw = self.fixture("evaluate_groups")
        self.server.reply_with(raw)
        group = group_aggregation({}, timeAggregation="avg", groupAggregation="sum", alias="g1")
        response = self.client.evaluate(rollup="PT10M", gte=GTE, lt=LT, groups=[group])
        self.assertIsNone(response.error)
        self.assertFrameMatches(response.result.data, raw["result"]["data"])

    def test_connect_and_disconnect_signals(self):
        methods = [method for method in ("connect_signals", "disconnect_signals") if method in self.contract.methods]
        if not methods:
            self.skipTest(f"API {self.api_version} cannot connect signals")
        for sdk_method in methods:
            with self.subTest(sdk_method):
                raw = self.fixture(sdk_method)["result"]
                response = self.call(sdk_method)
                self.assertIsNone(response.error)
                self.assertEqual([signal.id for signal in response.result.data], [signal["id"] for signal in raw["data"]])
                linked = response.result.data[0].relationships.item.data
                self.assertEqual(linked.id if linked else None, (raw["data"][0]["relationships"]["item"]["data"] or {}).get("id"))

    def returned_error(self, sdk_method):
        """The error the SDK returns for `sdk_method`, failing the test if the SDK raises instead."""
        try:
            error = self.call(sdk_method).error
        except ValidationError as exc:
            self.fail(f"{sdk_method} raises instead of returning the error:\n{exc}")
        return error[0] if isinstance(error, list) else error

    def test_json_rpc_error(self):
        raw = self.fixture("error")["error"]
        self.server.reply_with(self.fixture("error"))
        for sdk_method in self.sdk_calls():
            with self.subTest(sdk_method):
                error = self.returned_error(sdk_method)
                self.assertEqual((error.code, error.message), (raw["code"], raw["message"]))
                self.assertEqual(error.data.trace, raw["data"]["trace"])
                self.assertEqual(error.data.params, raw["data"]["params"])

    def test_json_rpc_error_with_path_errors(self):
        """The shape the production API returns for invalid params: pathErrors, and no trace."""
        raw = self.fixture("error_path_errors")["error"]
        self.server.reply_with(self.fixture("error_path_errors"))
        for sdk_method in self.sdk_calls():
            with self.subTest(sdk_method):
                error = self.returned_error(sdk_method)
                self.assertEqual((error.code, error.message), (raw["code"], raw["message"]))
                self.assertIn(raw["data"]["pathErrors"][0]["path"], str(error.data), "the path errors are dropped")

    def test_http_error(self):
        self.server.reply_with(FakeHTTPResponse(status_code=503, reason="Service Unavailable", text="upstream timeout"))
        for sdk_method in self.sdk_calls():
            with self.subTest(sdk_method):
                error = self.call(sdk_method).error
                error = error[0] if isinstance(error, list) else error
                self.assertEqual(error.code, 503)
                self.assertEqual(error.message, "HTTP Response Error: Service Unavailable")
                self.assertEqual(error.data, "upstream timeout")
