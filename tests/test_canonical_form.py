# Copyright 2026 Quantum Pipes Technologies, LLC
# SPDX-License-Identifier: Apache-2.0

"""
Canonical JSON serialization tests.

Validates the CPS v1.0 canonical form rules (spec Section 2):
    2.1 Lexicographic key ordering (recursive)
    2.2 Zero whitespace
    2.3 Float-typed fields preserve decimal point
    2.4 DateTime format (Python isoformat with +00:00)
    2.5 UUID lowercase with hyphens
    2.6 String escaping (RFC 8259)
    2.7 Null, boolean, and empty collections
"""

import json
from datetime import UTC, datetime

from qp_capsule.capsule import (
    Capsule,
    ReasoningOption,
    ReasoningSection,
    TriggerSection,
)
from qp_capsule.seal import compute_hash

FIXED_TIME = datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC)


def _canonicalize(d: dict) -> str:
    return json.dumps(d, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _make_capsule(**kwargs) -> Capsule:
    """Create a minimal Capsule with a fixed timestamp for deterministic output."""
    defaults = dict(trigger=TriggerSection(timestamp=FIXED_TIME))
    defaults.update(kwargs)
    return Capsule(**defaults)


# ─── 2.1 Key Ordering ────────────────────────────────────────────


class TestKeyOrdering:
    """CPS 2.1: All keys sorted lexicographically by Unicode code point, recursively."""

    def test_top_level_keys_sorted(self) -> None:
        """Top-level Capsule keys appear in lexicographic order."""
        capsule = _make_capsule()
        canonical = _canonicalize(capsule.to_dict())
        parsed = json.loads(canonical)
        keys = list(parsed.keys())
        assert keys == sorted(keys)

    def test_nested_section_keys_sorted(self) -> None:
        """Keys within each section are sorted."""
        capsule = _make_capsule()
        canonical = _canonicalize(capsule.to_dict())
        parsed = json.loads(canonical)
        sections = ("trigger", "context", "reasoning", "authority", "execution", "outcome")
        for section_name in sections:
            section = parsed[section_name]
            if isinstance(section, dict):
                keys = list(section.keys())
                assert keys == sorted(keys), f"Keys in '{section_name}' not sorted: {keys}"

    def test_environment_dict_keys_sorted(self) -> None:
        """Keys within context.environment are sorted."""
        from qp_capsule.capsule import ContextSection

        capsule = _make_capsule()
        capsule.context = ContextSection(environment={"zebra": 1, "alpha": 2, "middle": 3})
        canonical = _canonicalize(capsule.to_dict())
        env_keys = list(json.loads(canonical)["context"]["environment"].keys())
        assert env_keys == ["alpha", "middle", "zebra"]

    def test_nested_option_keys_sorted(self) -> None:
        """Keys within reasoning.options[] elements are sorted."""
        capsule = _make_capsule(
            reasoning=ReasoningSection(
                options=[ReasoningOption(id="opt_0", description="test", feasibility=0.5)],
                selected_option="test",
            ),
        )
        canonical = _canonicalize(capsule.to_dict())
        option = json.loads(canonical)["reasoning"]["options"][0]
        keys = list(option.keys())
        assert keys == sorted(keys)

    def test_input_key_order_does_not_affect_output(self) -> None:
        """Canonical form is identical regardless of input key order."""
        dict_a = {"z": 1, "a": 2, "m": {"z": 3, "a": 4}}
        dict_b = {"a": 2, "m": {"a": 4, "z": 3}, "z": 1}
        assert _canonicalize(dict_a) == _canonicalize(dict_b)


# ─── 2.2 Whitespace ──────────────────────────────────────────────


class TestWhitespace:
    """CPS 2.2: Zero whitespace. No spaces after : or , and no newlines."""

    def test_no_spaces_after_colon(self) -> None:
        canonical = _canonicalize(_make_capsule().to_dict())
        assert ": " not in canonical

    def test_no_spaces_after_comma(self) -> None:
        canonical = _canonicalize(_make_capsule().to_dict())
        assert ", " not in canonical

    def test_no_newlines(self) -> None:
        canonical = _canonicalize(_make_capsule().to_dict())
        assert "\n" not in canonical
        assert "\r" not in canonical


# ─── 2.3 Float-Typed Fields ──────────────────────────────────────


class TestFloatFields:
    """CPS 2.3: Float-typed fields always serialize with a decimal point."""

    def test_confidence_zero_is_zero_point_zero(self) -> None:
        """confidence: 0.0 serializes as 0.0, not 0."""
        capsule = _make_capsule(reasoning=ReasoningSection(confidence=0.0))
        canonical = _canonicalize(capsule.to_dict())
        assert '"confidence":0.0' in canonical

    def test_confidence_one_is_one_point_zero(self) -> None:
        """confidence: 1.0 serializes as 1.0, not 1."""
        capsule = _make_capsule(reasoning=ReasoningSection(confidence=1.0))
        canonical = _canonicalize(capsule.to_dict())
        assert '"confidence":1.0' in canonical

    def test_confidence_fractional_preserved(self) -> None:
        """confidence: 0.95 serializes as 0.95."""
        capsule = _make_capsule(reasoning=ReasoningSection(confidence=0.95))
        canonical = _canonicalize(capsule.to_dict())
        assert '"confidence":0.95' in canonical

    def test_feasibility_zero_is_zero_point_zero(self) -> None:
        """feasibility: 0.0 in options serializes as 0.0, not 0."""
        capsule = _make_capsule(
            reasoning=ReasoningSection(
                options=[ReasoningOption(id="opt_0", description="x", feasibility=0.0)],
                selected_option="x",
            ),
        )
        canonical = _canonicalize(capsule.to_dict())
        assert '"feasibility":0.0' in canonical

    def test_integer_fields_have_no_decimal(self) -> None:
        """Integer fields (sequence, duration_ms) serialize without decimal."""
        capsule = _make_capsule()
        d = capsule.to_dict()
        canonical = _canonicalize(d)
        assert '"sequence":0' in canonical
        assert '"duration_ms":0' in canonical
        assert '"sequence":0.' not in canonical


# ─── 2.4 DateTime Format ─────────────────────────────────────────


class TestDateTimeFormat:
    """CPS 2.4: trigger.timestamp uses Python isoformat() with +00:00."""

    def test_timestamp_uses_plus_offset_not_z(self) -> None:
        """Timestamps end with +00:00, never Z."""
        capsule = _make_capsule()
        canonical = _canonicalize(capsule.to_dict())
        assert "+00:00" in canonical
        assert '"timestamp"' in canonical
        # Z suffix must not appear
        assert "T12:00:00Z" not in canonical

    def test_timestamp_no_fractional_seconds_when_absent(self) -> None:
        """No .000000 appended when source has no fractional seconds."""
        capsule = _make_capsule(trigger=TriggerSection(timestamp=FIXED_TIME))
        canonical = _canonicalize(capsule.to_dict())
        assert "12:00:00+00:00" in canonical
        assert "12:00:00.0" not in canonical


# ─── 2.5 UUID Format ─────────────────────────────────────────────


class TestUUIDFormat:
    """CPS 2.5: UUIDs are lowercase hex with hyphens."""

    def test_id_is_lowercase_with_hyphens(self) -> None:
        capsule = _make_capsule()
        d = capsule.to_dict()
        capsule_id = d["id"]
        assert capsule_id == capsule_id.lower()
        assert len(capsule_id.split("-")) == 5


# ─── 2.7 Null, Boolean, Empty Collections ────────────────────────


class TestSpecialValues:
    """CPS 2.7: null, true, false, [], {} serialize correctly."""

    def test_null_values(self) -> None:
        capsule = _make_capsule()
        canonical = _canonicalize(capsule.to_dict())
        assert "null" in canonical

    def test_empty_array(self) -> None:
        capsule = _make_capsule()
        canonical = _canonicalize(capsule.to_dict())
        assert "[]" in canonical

    def test_empty_object(self) -> None:
        capsule = _make_capsule()
        canonical = _canonicalize(capsule.to_dict())
        assert "{}" in canonical

    def test_boolean_lowercase(self) -> None:
        """Booleans serialize as lowercase true/false."""
        capsule = _make_capsule(
            reasoning=ReasoningSection(
                options=[ReasoningOption(id="opt_0", description="x", selected=True)],
                selected_option="x",
            ),
        )
        canonical = _canonicalize(capsule.to_dict())
        assert "true" in canonical


# ─── Hash Determinism ─────────────────────────────────────────────


class TestHashDeterminism:
    """Hash output is deterministic across identical Capsule content."""

    def test_identical_capsules_produce_identical_hashes(self) -> None:
        c1 = _make_capsule()
        c2 = _make_capsule()
        c2.id = c1.id
        assert compute_hash(c1.to_dict()) == compute_hash(c2.to_dict())

    def test_hash_is_64_hex_characters(self) -> None:
        capsule = _make_capsule()
        h = compute_hash(capsule.to_dict())
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)
