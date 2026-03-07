# Copyright 2026 Quantum Pipes Technologies, LLC
# SPDX-License-Identifier: Apache-2.0

"""
Golden fixture conformance tests.

Loads the CPS v1.0 golden test vectors from fixtures.json and verifies
the Python reference implementation produces byte-identical canonical
JSON and matching SHA3-256 hashes for every vector.

A conformant CPS implementation in any language must pass these fixtures.
"""

import hashlib
import json
from pathlib import Path

import pytest

# Fixtures live at specs/cps/fixtures.json relative to the repo root.
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_FIXTURES_PATH = _REPO_ROOT / "specs" / "cps" / "fixtures.json"


def _load_fixtures() -> list[dict]:
    if not _FIXTURES_PATH.exists():
        pytest.skip(
            f"fixtures.json not found at {_FIXTURES_PATH}",
            allow_module_level=True,
        )
    with open(_FIXTURES_PATH) as f:
        data = json.load(f)
    return data["fixtures"]


def _canonicalize(capsule_dict: dict) -> str:
    """Canonical JSON per CPS spec Section 2: sorted keys, literal UTF-8, zero whitespace."""
    return json.dumps(capsule_dict, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha3_256(canonical_json: str) -> str:
    """SHA3-256 per CPS spec Section 3.1."""
    return hashlib.sha3_256(canonical_json.encode("utf-8")).hexdigest()


FIXTURES = _load_fixtures()
FIXTURE_IDS = [f["name"] for f in FIXTURES]


@pytest.mark.parametrize("fixture", FIXTURES, ids=FIXTURE_IDS)
class TestGoldenFixtures:
    """
    Verify every golden test vector from the CPS v1.0 specification.

    Each vector contains a capsule_dict, the expected canonical_json,
    and the expected sha3_256_hash. The Python implementation must
    produce byte-identical output for all three fixtures.
    """

    def test_canonical_json_matches(self, fixture: dict) -> None:
        """Canonical JSON is byte-identical to the golden vector."""
        actual = _canonicalize(fixture["capsule_dict"])
        expected = fixture["canonical_json"]
        assert actual == expected, (
            f"Canonical JSON mismatch for fixture '{fixture['name']}'. "
            f"First divergence near position {_first_diff(actual, expected)}."
        )

    def test_sha3_256_hash_matches(self, fixture: dict) -> None:
        """SHA3-256 hash matches the golden vector."""
        canonical = _canonicalize(fixture["capsule_dict"])
        actual = _sha3_256(canonical)
        expected = fixture["sha3_256_hash"]
        assert actual == expected, (
            f"Hash mismatch for fixture '{fixture['name']}': "
            f"got {actual}, expected {expected}"
        )

    def test_hash_computed_from_canonical_json(self, fixture: dict) -> None:
        """Hash is derived from the canonical JSON, not from the raw dict."""
        expected_hash = _sha3_256(fixture["canonical_json"])
        assert expected_hash == fixture["sha3_256_hash"]


def _first_diff(a: str, b: str) -> int:
    """Return index of the first character where a and b differ."""
    for i, (ca, cb) in enumerate(zip(a, b)):
        if ca != cb:
            return i
    return min(len(a), len(b))
