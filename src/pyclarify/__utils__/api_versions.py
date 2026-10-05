# Copyright 2026 Searis AS

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Differences between Clarify API versions that change what PyClarify sends.

Request models describe the newest API. ``adapt_request`` rewrites a serialized request for
the API version a client uses; currently only the 1.2 pre-releases need changes. Features a
version lacks are refused by the client before a request is built (see ``at_least``).
"""

import re

_VERSION = re.compile(r"^(\d+)\.(\d+)(?:(alpha|beta|rc)(\d+))?$")
_STAGES = ("alpha", "beta", "rc")

# The first versions with each feature.
GROUPS = "1.2alpha1"  # clarify.evaluate group aggregations
CONNECT_SIGNALS = "1.2alpha1"  # admin.signals.connect and admin.signals.disconnect
RELEASE_1_2 = "1.2"

# 1.2 methods under the names the 1.2 pre-releases use.
PRE_RELEASE_METHOD_NAMES = {
    "admin.signals.connect": "admin.connectSignals",
    "admin.signals.disconnect": "admin.disconnectSignals",
}


def version_key(version):
    """
    Sort key for an API version selector, where pre-releases come before their release:
    1.2alpha1 < 1.2beta1 < 1.2 < 1.3alpha1. None for selectors it does not know, like aliases.
    """
    match = _VERSION.match(version or "")
    if not match:
        return None
    major, minor, stage, number = match.groups()
    stage_rank = _STAGES.index(stage) if stage else len(_STAGES)
    return int(major), int(minor), stage_rank, int(number or 0)


def at_least(version, minimum):
    """Whether API `version` is `minimum` or newer. Unknown selectors count as the newest."""
    key = version_key(version)
    return key is None or key >= version_key(minimum)


def is_1_2_pre_release(version):
    """Whether `version` is a 1.2 pre-release, such as 1.2alpha1 (served as 1.2beta1)."""
    return at_least(version, GROUPS) and not at_least(version, RELEASE_1_2)


def adapt_request(payload, api_version):
    """Rewrite a serialized JSON RPC request, built for the newest API, for `api_version`."""
    if not is_1_2_pre_release(api_version):
        return payload
    payload["method"] = PRE_RELEASE_METHOD_NAMES.get(payload["method"], payload["method"])
    params = payload.get("params") or {}
    if params.get("groups"):
        # The pre-releases select group items with a resource query instead of a filter.
        params["groups"] = [
            {**{key: value for key, value in group.items() if key != "filter"}, "query": {"filter": group.get("filter", {})}}
            for group in params["groups"]
        ]
    query = params.get("query")
    if payload["method"] == "clarify.dataFrame" and isinstance(query, dict) and query.get("total") is False:
        # 1.2beta1 rejects query.total in clarify.dataFrame, even when false.
        del query["total"]
    return payload
