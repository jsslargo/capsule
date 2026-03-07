---
title: "Capsule Protocol Specification (CPS) v1.0"
description: "Summary of the Capsule Protocol Specification: record structure, canonical serialization, sealing algorithm, hash chain rules, and golden test vectors."
date_modified: "2026-03-07"
ai_context: |
  Summary of CPS v1.0 for SDK authors and regulators. Covers the 6-section
  Capsule structure, canonical JSON rules (key ordering, whitespace, float
  formatting, datetime, UUID, escaping, null/boolean/empty), sealing algorithm
  (SHA3-256 + Ed25519 + optional ML-DSA-65), hash chain rules, golden test
  vectors (15 fixtures covering all CapsuleTypes, Unicode, chain states, float
  formatting, empty vs null, deep nesting, and failure paths), and implementation
  checklist. Full spec at specs/cps/README.md.
---

# Capsule Protocol Specification (CPS) v1.0

> **The protocol is the contract. Pass the golden fixtures, and you're compatible with every other implementation.**

*Version 1.0 — Active*

---

## What is CPS

The Capsule Protocol Specification defines the **exact byte-level serialization** of a Capsule for cryptographic operations. Any implementation in any language that follows this specification produces identical hashes for identical Capsules, enabling cross-language sealing and verification.

CPS is a protocol, not an implementation. The Python `qp-capsule` package is the reference implementation. Cross-language SDKs (TypeScript, Go, Rust) are planned.

```
  Language A (seal)  ──→  Canonical JSON + SHA3-256 + Ed25519  ──→  Language B (verify) ✓
```

---

## 1. Record Structure

A Capsule is a JSON object with 12 top-level keys (all required):

| Key | Type | Description |
|---|---|---|
| `id` | string | UUID v4, lowercase with hyphens |
| `type` | string | One of: `agent`, `tool`, `system`, `kill`, `workflow`, `chat`, `vault`, `auth` |
| `domain` | string | Functional area (default: `"agents"`) |
| `parent_id` | string or null | Parent Capsule UUID, or null |
| `sequence` | integer | Position in hash chain (0-indexed) |
| `previous_hash` | string or null | SHA3-256 hex digest of previous Capsule, or null for genesis |
| `trigger` | object | What initiated the action (type, source, timestamp, request, correlation_id, user_id) |
| `context` | object | System state (agent_id, session_id, environment) |
| `reasoning` | object | Why this decision was made (analysis, options, selected_option, reasoning, confidence, model, prompt_hash) |
| `authority` | object | Who approved (type, approver, policy_reference, chain, escalation_reason) |
| `execution` | object | What happened (tool_calls, duration_ms, resources_used) |
| `outcome` | object | The result (status, result, summary, error, side_effects, metrics) |

Seal fields (`hash`, `signature`, `signature_pq`, `signed_at`, `signed_by`) are metadata **outside** the canonical content. They are not included in `to_dict()` and are not part of the hash computation.

For complete field-level detail on each section, see the [full specification](https://github.com/quantumpipes/capsule/blob/main/specs/cps/README.md).

---

## 2. Canonical JSON Rules

The canonical form transforms a Capsule into a deterministic byte string. All implementations MUST produce byte-identical output for the same logical Capsule.

### Key Ordering

All object keys sorted **lexicographically by Unicode code point**, applied **recursively** to all nested objects. Array element order is preserved.

### Whitespace

Zero whitespace. No spaces after `:` or `,`. No newlines. Equivalent to Python's `json.dumps(separators=(",", ":"))`.

### Float-Typed Fields

`reasoning.confidence` and `reasoning.options[].feasibility` are float-typed and MUST always serialize with at least one decimal place:

| Value | Correct | Incorrect |
|---|---|---|
| Zero | `0.0` | `0` |
| One | `1.0` | `1` |
| Fractional | `0.95` | (correct as-is) |

All other numeric values (integers in `duration_ms`, `sequence`, etc.) use standard JSON integer formatting.

### DateTime Format

`trigger.timestamp` uses ISO 8601 with explicit UTC offset:

```
2026-01-15T14:30:00+00:00
```

Do NOT use `Z` suffix. Do NOT add fractional seconds unless present in the source value.

### UUID Format

Lowercase hexadecimal with hyphens: `12345678-1234-1234-1234-123456789012`.

### String Escaping

RFC 8259 (JSON) rules. Escape `"`, `\`, and control characters (U+0000 through U+001F). Do NOT escape `/` (solidus). Non-ASCII Unicode serializes as literal UTF-8.

### Null, Boolean, Empty Collections

`null`, `true`, `false`, `[]`, `{}` as specified in JSON.

---

## 3. Sealing Algorithm

### Hash Computation

```
Capsule → to_dict() → Canonical JSON → UTF-8 bytes → SHA3-256 → 64-char hex string
```

### Ed25519 Signature (Required)

```
SHA3-256 hex string (64 ASCII chars) → UTF-8 encode → Ed25519 sign → 128-char hex string
```

> **Critical detail:** The signature is computed over the **hex-encoded hash string** (64 ASCII characters encoded as UTF-8), not the raw 32-byte hash value.

### ML-DSA-65 Signature (Optional)

Same input as Ed25519: the hex-encoded hash string, UTF-8 encoded, signed with ML-DSA-65 (FIPS 204).

### Verification

1. Recompute canonical JSON from content (seal fields excluded)
2. Compute SHA3-256 of canonical JSON
3. Compare computed hash to stored `hash` (exact match)
4. Verify Ed25519 signature over the stored hash string using the public key
5. Optionally verify ML-DSA-65 signature

---

## 4. Hash Chain Rules

1. Genesis Capsule: `sequence: 0`, `previous_hash: null`
2. Each subsequent Capsule: `sequence: N+1`, `previous_hash: hash` of Capsule at sequence N
3. Sequence numbers MUST be consecutive with no gaps
4. Chain verification checks: consecutive sequences, hash linkage, genesis has null `previous_hash`

---

## 5. Golden Test Vectors

15 test vectors define conformance. Each contains:

- `capsule_dict` — The Capsule as a JSON object (output of `to_dict()`)
- `canonical_json` — The exact canonical JSON string
- `sha3_256_hash` — The expected SHA3-256 hex digest

| Fixture | Description |
|---|---|
| **minimal** | Minimal Capsule with defaults, float 0.0, nulls |
| **full** | Fully populated with options, tool calls, metrics |
| **kill_switch** | Kill switch activation (type `kill`, status `blocked`) |
| **tool_invocation** | Tool-type Capsule with tool call and error field |
| **chat_interaction** | Chat-type with session tracking |
| **workflow_hierarchy** | Workflow with parent_id hierarchy linking |
| **unicode_strings** | Non-ASCII in trigger, context, reasoning (UTF-8 conformance) |
| **fractional_timestamp** | Microsecond-precision datetime |
| **empty_vs_null** | Empty strings vs null distinction (critical for Go, Rust, JS) |
| **confidence_one** | Confidence 1.0 (float serialized as `1.0`, not `1`) |
| **deep_nesting** | Deeply nested objects testing recursive key sorting |
| **chain_genesis** | First Capsule in chain (sequence 0, previous_hash null) |
| **chain_linked** | Second Capsule with previous_hash set |
| **failure_with_error** | Failed tool call with error details |
| **auth_escalated** | Auth-type with MFA escalation chain |

An implementation is conformant if, for every fixture, it produces byte-identical `canonical_json` and matching `sha3_256_hash` from the `capsule_dict` input.

The fixture file is available at [`specs/cps/fixtures.json`](https://github.com/quantumpipes/capsule/blob/main/specs/cps/fixtures.json).

---

## 6. Implementation Checklist

For a conformant implementation in any language:

- [ ] Capsule data model with all 6 sections and all fields
- [ ] `to_dict()` — convert Capsule to a plain dictionary/map
- [ ] `canonicalize()` — serialize dict to canonical JSON (Section 2 rules)
- [ ] `compute_hash()` — SHA3-256 of canonical JSON
- [ ] `seal()` — compute hash + Ed25519 signature
- [ ] `verify()` — recompute hash and verify signature
- [ ] `from_dict()` — deserialize Capsule from dictionary/map
- [ ] Pass all 15 golden test vectors from `fixtures.json`
- [ ] Chain verification (sequence + hash linkage)

---

## Full Specification

This document is a summary. For the complete, authoritative specification including all field definitions, all serialization rules, and the full golden test vector format, see:

**[CPS v1.0 Full Specification](https://github.com/quantumpipes/capsule/blob/main/specs/cps/README.md)**

---

## Related Documentation

- [Architecture](./architecture.md) — How the Python reference implementation works
- [API Reference](./api.md) — Python API for the reference implementation
- [Compliance Mapping](./compliance.md) — FIPS algorithm compliance and regulatory mapping

---

*The specification is the contract. Pass the golden fixtures, and you're compatible with every other implementation.*
