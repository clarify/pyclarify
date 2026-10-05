"""
API version compatibility suite.

Runs the same behavioural tests once per Clarify API version, so swapping the version
PyClarify talks to cannot silently change what the SDK sends or how it reads responses.

- contracts.py: what each API version documents (method names, params, paging limits).
- fixtures/<version>/: a JSON-RPC response per method, with synthetic data in the shapes the
  reference documents and the production API returns. ``_provenance`` says where each came
  from; ``diff -r fixtures/1.1 fixtures/1.2`` shows how the responses differ per version.
- test_requests.py, test_responses.py, test_forward_compat.py, test_pagination.py: offline
  tests, run through the real Client with ``requests.post`` replaced by a fake server.
- test_live.py: opt-in tests against a real Clarify organisation.

Run the suite, optionally limited to some versions:

    python -m unittest discover -s tests/api_versions -t tests
    PYCLARIFY_API_VERSIONS=1.2 python -m unittest discover -s tests/api_versions -t tests

Adding an API version: add a Contract in contracts.py and a fixtures/<version>/ directory.
"""

import sys
from pathlib import Path

# Test the working tree, never an installed copy of pyclarify.
SRC = Path(__file__).resolve().parents[2] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pyclarify  # noqa: E402

if Path(pyclarify.__file__).resolve().parent != SRC / "pyclarify":
    raise ImportError(f"pyclarify was imported from {pyclarify.__file__}, expected {SRC / 'pyclarify'}")
