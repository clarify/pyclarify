"""
Shared machinery for the API version compatibility suite.

Classes decorated with @for_each_api_version run once per version in API_VERSIONS. They use
the real Client, with ``requests.post`` replaced by FakeClarify: it records every request the
SDK sends and answers from the fixtures of the version under test.
"""

import copy
import json
import os
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

from pyclarify import Calculation, Client, DataFrame, Item, ItemAggregation, Signal
from pyclarify.views.evaluate import GroupAggregation

from .contracts import CONTRACTS

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
MOCK_CREDENTIALS = HERE.parent / "mock_data" / "mock-clarify-credentials.json"
MOCK_TOKEN = "token1234567890"

API_VERSIONS = tuple(
    version.strip()
    for version in os.environ.get("PYCLARIFY_API_VERSIONS", ",".join(CONTRACTS)).split(",")
    if version.strip()
)
_unknown = [version for version in API_VERSIONS if version not in CONTRACTS]
if _unknown:
    raise ValueError(f"PYCLARIFY_API_VERSIONS has versions without a contract: {_unknown}")

# JSON-RPC method (1.1 and 1.2 names) -> fixture name. Compared case-insensitively, because
# the SDK and the API reference disagree on the casing of some method names.
FIXTURE_BY_METHOD = {
    "integration.insert": "insert",
    "integration.savesignals": "save_signals",
    "integration.signals.save": "save_signals",
    "admin.publishsignals": "publish_signals",
    "admin.signals.publish": "publish_signals",
    "admin.selectsignals": "select_signals",
    "admin.signals.select": "select_signals",
    "clarify.selectitems": "select_items",
    "clarify.items.select": "select_items",
    "clarify.dataframe": "data_frame",
    "clarify.evaluate": "evaluate",
    "admin.signals.connect": "connect_signals",
    "admin.connectsignals": "connect_signals",  # 1.2 pre-release name
    "admin.signals.disconnect": "disconnect_signals",
    "admin.disconnectsignals": "disconnect_signals",  # 1.2 pre-release name
}

# Inputs shared by the tests. IDs match the fixtures.
TIMES = ["2024-01-01T00:00:00Z", "2024-01-01T01:00:00Z"]
GTE = "2024-01-01T00:00:00Z"
LT = "2024-01-02T00:00:00Z"
INPUT_ID = "input-a"
SIGNAL_ID = "c618rbfqfsj7mjkj0ss1"
ITEM_ID = "cbpmaq6rpn52969vfl00"

# One representative call per public Client method. Methods a version lacks are skipped for it,
# see VersionedCase.sdk_calls.
SDK_CALLS = {
    "connect_signals": lambda client: client.connect_signals(item=ITEM_ID, filter={"input": INPUT_ID}, dry_run=True),
    "disconnect_signals": lambda client: client.disconnect_signals(filter={"input": INPUT_ID}, dry_run=True),
    "insert": lambda client: client.insert(DataFrame(series={INPUT_ID: [1.0, None]}, times=TIMES)),
    "save_signals": lambda client: client.save_signals(input_ids=[INPUT_ID], signals=[Signal(name="Signal A")]),
    "publish_signals": lambda client: client.publish_signals(signal_ids=[SIGNAL_ID], items=[Item(name="Item A")]),
    "select_signals": lambda client: client.select_signals(include=["item"]),
    "select_items": lambda client: client.select_items(),
    "data_frame": lambda client: client.data_frame(gte=GTE, lt=LT, include=["item"]),
    "evaluate": lambda client: client.evaluate(
        rollup="PT1H",
        gte=GTE,
        lt=LT,
        items=[ItemAggregation(id=ITEM_ID, aggregation="avg", alias="i1")],
        calculations=[Calculation(formula="i1 * 2", alias="c1")],
    ),
}


def group_aggregation(filter, **fields):
    """
    A GroupAggregation over the items matching `filter`. API 1.2 names that field ``filter``;
    older SDK versions only accept it wrapped in a resource query as ``query``.
    """
    if "filter" in GroupAggregation.model_fields:
        return GroupAggregation(filter=filter, **fields)
    return GroupAggregation(query={"filter": filter}, **fields)


def make_client(api_version, credentials=MOCK_CREDENTIALS):
    """A Client that sends the given API version."""
    return Client(str(credentials), api_version=api_version)


def load_fixture(api_version, name):
    """The JSON-RPC response stored in fixtures/<api_version>/<name>.json."""
    with open(FIXTURES / api_version / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)["response"]


@dataclass
class RecordedRequest:
    url: str
    headers: dict
    body: dict

    @property
    def method(self):
        return self.body["method"]

    @property
    def params(self):
        return self.body["params"]


class FakeHTTPResponse:
    """The parts of requests.Response that the SDK reads."""

    def __init__(self, payload=None, status_code=200, reason="OK", text=None):
        self._payload = payload
        self.status_code = status_code
        self.ok = status_code < 400
        self.reason = reason
        self.text = json.dumps(payload) if text is None else text

    def json(self):
        return copy.deepcopy(self._payload)


class FakeClarify:
    """
    Stand-in for the Clarify RPC endpoint, installed over ``requests.post``.

    Answers each method with the matching fixture of its API version. Set `handler` to a
    function of the request body to simulate other behaviour; it returns a JSON-RPC response
    dict or a FakeHTTPResponse.
    """

    def __init__(self, api_version):
        self.api_version = api_version
        self.requests = []
        self.handler = self.reply_from_fixtures

    def __call__(self, url, data=None, headers=None, **kwargs):
        request = RecordedRequest(url=url, headers=dict(headers or {}), body=json.loads(data))
        self.requests.append(request)
        reply = self.handler(request.body)
        if isinstance(reply, FakeHTTPResponse):
            return reply
        return FakeHTTPResponse({**reply, "id": request.body["id"]})

    def reply_from_fixtures(self, body):
        return load_fixture(self.api_version, FIXTURE_BY_METHOD[body["method"].lower()])

    def reply_with(self, response):
        """Answer every following request with `response`."""
        self.handler = lambda body: response


class VersionedCase:
    """
    Base for tests that run once per API version, see for_each_api_version.

    Provides self.client (a Client sending self.api_version), self.server (the FakeClarify
    it talks to) and self.contract (the documented contract of self.api_version).
    """

    api_version = None
    __test__ = False  # only the generated per-version classes are collected

    def setUp(self):
        super().setUp()
        self.contract = CONTRACTS[self.api_version]
        self.server = FakeClarify(self.api_version)
        for patcher in (
            patch("pyclarify.jsonrpc.client.requests.post", new=self.server),
            patch("pyclarify.jsonrpc.oauth2.Authenticator.get_token", return_value=MOCK_TOKEN),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)
        self.client = make_client(self.api_version)

    def fixture(self, name):
        return load_fixture(self.api_version, name)

    def call(self, sdk_method):
        """Run the representative call of `sdk_method` and return the SDK's Response."""
        return SDK_CALLS[sdk_method](self.client)

    def sdk_calls(self):
        """The representative calls of the methods this API version has."""
        return {name: call for name, call in SDK_CALLS.items() if name in self.contract.methods}


def for_each_api_version(cls):
    """
    Class decorator that adds one unittest.TestCase per API version to the module of `cls`,
    named Test<cls>_v<version>, e.g. TestPagination_v1_2.
    """
    module = sys.modules[cls.__module__]
    for version in API_VERSIONS:
        name = f"Test{cls.__name__}_v{version.replace('.', '_')}"
        namespace = {"api_version": version, "__test__": True, "__module__": cls.__module__, "__qualname__": name}
        setattr(module, name, type(name, (cls, unittest.TestCase), namespace))
    return cls
