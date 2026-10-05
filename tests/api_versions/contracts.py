"""
The documented Clarify API contract for each API version, as far as PyClarify uses it.

Tests read what to expect from here instead of hard-coding it, so supporting a new API
version means adding a Contract (and fixtures/<version>/) rather than editing tests.

Sources:

- 1.1: https://docs.clarify.io/api/1.1 (methods and types pages).
- 1.2: https://docs.clarify.io/api/1.2 (reviewed on a pre-release preview), including its
  release notes.

Where the live API behaves differently from its reference, the contract follows the API and
says so in a comment. Checked on 2026-09-29 against 1.1.2 (production and dev) and 1.2.0 (dev).
"""

from dataclasses import dataclass, field
from datetime import timedelta

# Leaf markers for parameter schemas.
ANY = "any"  # a value this contract does not constrain further
NOT_NULL = "not-null"  # the documented type is not nullable, so null must not be sent


@dataclass(frozen=True)
class MapOf:
    """An object with arbitrary keys (input IDs, signal IDs) whose values follow `value`."""

    value: object


@dataclass(frozen=True)
class ListOf:
    """An array whose entries follow `item`."""

    item: object


@dataclass(frozen=True)
class Method:
    names: tuple  # documented JSON-RPC method names: the canonical name, then its aliases
    params: dict  # documented params: field -> ANY | NOT_NULL | dict | MapOf | ListOf
    # Required params. A tuple entry means "one of", for documented aliases.
    required: tuple = ()

    @property
    def name(self):
        return self.names[0]


@dataclass(frozen=True)
class Limits:
    select_items: int  # max query.limit per items select call
    select_signals: int  # max query.limit per signals select call
    data_frame: int  # max query.limit per clarify.dataFrame call
    raw_window: timedelta  # max time window when rollup is null or < PT1M
    rollup_window: timedelta  # max time window when rollup >= PT1M
    daily_rollup_window: timedelta  # max time window when rollup >= PT24H
    data_frame_monthly_rollup_window: timedelta  # clarify.dataFrame only: max time window when rollup >= P30D


@dataclass(frozen=True)
class Contract:
    version: str
    methods: dict  # SDK method name (e.g. "select_items") -> Method
    limits: Limits
    features: frozenset = field(default_factory=frozenset)  # optional features, e.g. "groups"


# API 1.1

FORMAT = {"dataAsArray": NOT_NULL, "groupIncludedByType": NOT_NULL}
RESOURCE_QUERY = {"filter": ANY, "sort": ANY, "limit": ANY, "skip": ANY, "total": ANY}
DATA_QUERY = {
    "filter": ANY,
    "rollup": ANY,
    "timeZone": NOT_NULL,
    "firstDayOfWeek": NOT_NULL,
    "origin": ANY,
    "last": NOT_NULL,
    "outsidePoints": NOT_NULL,  # not in the 1.1 or 1.2 reference, but accepted by 1.1.2 and 1.2.0
}
SIGNAL_SAVE = {
    "annotations": NOT_NULL,
    "name": NOT_NULL,
    "description": NOT_NULL,
    "labels": NOT_NULL,
    "sourceType": NOT_NULL,
    "valueType": NOT_NULL,
    "engUnit": NOT_NULL,
    "enumValues": NOT_NULL,
    "sampleInterval": ANY,
    "gapDetection": ANY,
}
ITEM_SAVE = {**SIGNAL_SAVE, "visible": NOT_NULL}
ITEM_AGGREGATION = {
    "id": NOT_NULL,
    "aggregation": NOT_NULL,
    "state": NOT_NULL,
    "lead": NOT_NULL,
    "lag": NOT_NULL,
    "alias": NOT_NULL,
}
CALCULATION = {"formula": NOT_NULL, "alias": NOT_NULL}
# The 1.1 reference only lists the daily window for clarify.dataFrame; 1.1.2 accepts it for
# clarify.evaluate too. Neither version rejected longer windows when checked.
LIMITS = Limits(
    select_items=1000,
    select_signals=1000,
    data_frame=50,
    raw_window=timedelta(days=40),
    rollup_window=timedelta(days=400),
    daily_rollup_window=timedelta(days=1900),
    data_frame_monthly_rollup_window=timedelta(days=3660),
)

V1_1 = Contract(
    version="1.1",
    methods={
        "insert": Method(
            names=("integration.insert",),
            params={"integration": NOT_NULL, "data": {"times": NOT_NULL, "series": NOT_NULL}},
            required=("integration", "data"),
        ),
        "save_signals": Method(
            names=("integration.saveSignals",),
            params={
                "integration": NOT_NULL,
                "signalsByInput": MapOf(SIGNAL_SAVE),
                # The reference names the alias "input", but 1.1.2 and 1.2.0 reject "input"
                # and accept "inputs".
                "inputs": MapOf(SIGNAL_SAVE),
                "createOnly": NOT_NULL,
            },
            required=("integration", ("signalsByInput", "inputs")),
        ),
        "publish_signals": Method(
            names=("admin.publishSignals",),
            params={"integration": NOT_NULL, "itemsBySignal": MapOf(ITEM_SAVE), "createOnly": NOT_NULL},
            required=("integration", "itemsBySignal"),
        ),
        "select_signals": Method(
            names=("admin.selectSignals",),
            params={"integration": NOT_NULL, "query": RESOURCE_QUERY, "include": ANY, "format": FORMAT},
            required=("integration",),
        ),
        "select_items": Method(
            names=("clarify.selectItems",),
            params={"query": RESOURCE_QUERY, "include": ANY, "format": FORMAT},
        ),
        "data_frame": Method(
            names=("clarify.dataFrame",),
            params={"query": RESOURCE_QUERY, "data": DATA_QUERY, "include": ANY, "format": FORMAT},
        ),
        "evaluate": Method(
            names=("clarify.evaluate",),
            params={
                "items": ListOf(ITEM_AGGREGATION),
                "calculations": ListOf(CALCULATION),
                "data": DATA_QUERY,
                "include": ANY,
                "format": FORMAT,
            },
        ),
    },
    limits=LIMITS,
    features=frozenset({"outsidePoints"}),
)

# API 1.2: renamed methods keep their 1.1 names as aliases, formats gain fields, save and
# publish can return resources, and evaluate gains group aggregations.

RESOURCE_FORMAT = {**FORMAT, "flattenResourceFields": NOT_NULL, "includeResourceHashFields": NOT_NULL}
DATA_FORMAT = {**RESOURCE_FORMAT, "usePathErrors": NOT_NULL}
SAVE_RESULT = {"result": NOT_NULL, "include": ANY, "format": RESOURCE_FORMAT}
ITEM_AGGREGATION_1_2 = {**ITEM_AGGREGATION, "timeAggregation": NOT_NULL, "engUnit": NOT_NULL}  # aggregation is an alias
# The clarify.evaluate page still lists "query"; 1.2.0 rejects it and accepts "filter", as the
# release notes say.
GROUP_AGGREGATION = {
    "filter": ANY,
    "timeAggregation": NOT_NULL,
    "groupAggregation": NOT_NULL,
    "state": NOT_NULL,
    "lead": NOT_NULL,
    "lag": NOT_NULL,
    "alias": NOT_NULL,
    "engUnit": NOT_NULL,
}
CALCULATION_1_2 = {**CALCULATION, "engUnit": NOT_NULL}

V1_2 = Contract(
    version="1.2",
    methods={
        "insert": V1_1.methods["insert"],
        "save_signals": Method(
            names=("integration.signals.save", "integration.saveSignals"),
            params={**V1_1.methods["save_signals"].params, **SAVE_RESULT},
            required=V1_1.methods["save_signals"].required,
        ),
        "publish_signals": Method(
            names=("admin.signals.publish", "admin.publishSignals"),
            params={**V1_1.methods["publish_signals"].params, **SAVE_RESULT},
            required=V1_1.methods["publish_signals"].required,
        ),
        "select_signals": Method(
            names=("admin.signals.select", "admin.selectSignals"),
            params={"integration": NOT_NULL, "query": RESOURCE_QUERY, "include": ANY, "format": RESOURCE_FORMAT},
            required=("integration",),
        ),
        "select_items": Method(
            names=("clarify.items.select", "clarify.selectItems"),
            params={"query": RESOURCE_QUERY, "include": ANY, "format": RESOURCE_FORMAT},
        ),
        "data_frame": Method(
            names=("clarify.dataFrame",),
            params={"query": RESOURCE_QUERY, "data": DATA_QUERY, "include": ANY, "format": DATA_FORMAT},
        ),
        "evaluate": Method(
            names=("clarify.evaluate",),
            params={
                "items": ListOf(ITEM_AGGREGATION_1_2),
                "groups": ListOf(GROUP_AGGREGATION),
                "calculations": ListOf(CALCULATION_1_2),
                "data": DATA_QUERY,
                "include": ANY,
                "format": DATA_FORMAT,
            },
        ),
        "connect_signals": Method(
            names=("admin.signals.connect",),
            params={
                "integration": NOT_NULL,
                "query": RESOURCE_QUERY,
                "item": NOT_NULL,
                "dryRun": NOT_NULL,
                "include": ANY,
                "format": RESOURCE_FORMAT,
            },
            required=("integration", "item"),
        ),
        "disconnect_signals": Method(
            names=("admin.signals.disconnect",),
            params={"integration": NOT_NULL, "query": RESOURCE_QUERY, "dryRun": NOT_NULL, "include": ANY, "format": RESOURCE_FORMAT},
            required=("integration",),
        ),
    },
    limits=LIMITS,
    features=frozenset({"groups", "outsidePoints"}),
)

CONTRACTS = {contract.version: contract for contract in (V1_1, V1_2)}


def violations(body, method):
    """
    Everything in a JSON-RPC request body that the documented `method` contract does not allow.

    Returns human-readable strings, empty when the request matches the contract.
    """
    found = []
    if body.get("method") not in method.names:
        documented = " or ".join(repr(name) for name in method.names)
        found.append(f"method: sent {body.get('method')!r}, documented {documented}")
    params = body.get("params") or {}
    for required in method.required:
        names = required if isinstance(required, tuple) else (required,)
        if not any(name in params for name in names):
            found.append(f"params.{' | '.join(names)}: required but not sent")
    found += _schema_violations(params, method.params, "params")
    return found


def _schema_violations(value, spec, path):
    if spec == ANY:
        return []
    if spec == NOT_NULL:
        return [f"{path}: sent as null, but the documented type is not nullable"] if value is None else []
    if value is None:
        return []
    if isinstance(spec, MapOf) and isinstance(value, dict):
        return [v for key, item in value.items() for v in _schema_violations(item, spec.value, f"{path}.{key}")]
    if isinstance(spec, ListOf) and isinstance(value, list):
        return [v for i, item in enumerate(value) for v in _schema_violations(item, spec.item, f"{path}[{i}]")]
    if isinstance(spec, dict) and isinstance(value, dict):
        found = [f"{path}.{key}: not in the documented contract" for key in value if key not in spec]
        for key, item in value.items():
            if key in spec:
                found += _schema_violations(item, spec[key], f"{path}.{key}")
        return found
    return []
