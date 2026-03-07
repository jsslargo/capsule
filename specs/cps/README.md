# Capsule Protocol Specification (CPS)

**Version**: 1.0
**Status**: Active
**Last Updated**: 2026-03-04

---

## Purpose

This specification defines the **exact byte-level serialization** of a Capsule for cryptographic operations. Any implementation in any language that follows this specification will produce identical hashes for identical capsules, enabling cross-language sealing and verification.

The canonical form is the single point of truth for the entire cryptographic chain of trust: `Capsule → Canonical JSON → SHA3-256 → Ed25519`.

---

## 1. Capsule Structure

A Capsule is a JSON object with the following top-level keys (all required):

| Key | Type | Description |
|-----|------|-------------|
| `id` | string | UUID v4 |
| `type` | string | One of: `agent`, `tool`, `system`, `kill`, `workflow`, `chat`, `vault`, `auth` |
| `domain` | string | Functional area (default: `"agents"`) |
| `parent_id` | string \| null | Parent Capsule UUID or null |
| `sequence` | integer | Position in hash chain (0-indexed) |
| `previous_hash` | string \| null | SHA3-256 hex digest of previous Capsule, or null for genesis |
| `trigger` | object | [Trigger Section](#11-trigger-section) |
| `context` | object | [Context Section](#12-context-section) |
| `reasoning` | object | [Reasoning Section](#13-reasoning-section) |
| `authority` | object | [Authority Section](#14-authority-section) |
| `execution` | object | [Execution Section](#15-execution-section) |
| `outcome` | object | [Outcome Section](#16-outcome-section) |

### 1.1 Trigger Section

| Key | Type | Description |
|-----|------|-------------|
| `type` | string | `"user_request"`, `"scheduled"`, `"system"`, `"agent"` |
| `source` | string | Origin identifier |
| `timestamp` | string | ISO 8601 datetime (see [DateTime Format](#24-datetime-format)) |
| `request` | string | Task description |
| `correlation_id` | string \| null | Distributed tracing ID |
| `user_id` | string \| null | Authenticated user ID |

### 1.2 Context Section

| Key | Type | Description |
|-----|------|-------------|
| `agent_id` | string | Agent identifier |
| `session_id` | string \| null | Session identifier |
| `environment` | object | Arbitrary key-value pairs |

### 1.3 Reasoning Section

| Key | Type | Description |
|-----|------|-------------|
| `analysis` | string | Initial analysis |
| `options` | array | Array of [ReasoningOption](#reasoning-option) objects |
| `options_considered` | array | Array of strings (option descriptions) |
| `selected_option` | string | Chosen option |
| `reasoning` | string | Rationale |
| `confidence` | number | 0.0 to 1.0 (**float-typed**, see [Float Rules](#23-float-typed-fields)) |
| `model` | string \| null | AI model identifier |
| `prompt_hash` | string \| null | SHA3-256 of full prompt |

#### Reasoning Option

| Key | Type | Description |
|-----|------|-------------|
| `id` | string | Option identifier |
| `description` | string | Option description |
| `pros` | array | Array of strings |
| `cons` | array | Array of strings |
| `estimated_impact` | object | Arbitrary key-value pairs |
| `feasibility` | number | 0.0 to 1.0 (**float-typed**) |
| `risks` | array | Array of strings |
| `selected` | boolean | Whether this option was chosen |
| `rejection_reason` | string | Why not selected |

### 1.4 Authority Section

| Key | Type | Description |
|-----|------|-------------|
| `type` | string | `"autonomous"`, `"human_approved"`, `"policy"`, `"escalated"` |
| `approver` | string \| null | Approver identifier |
| `policy_reference` | string \| null | Policy ID |
| `chain` | array | Array of approval objects |
| `escalation_reason` | string \| null | Why escalation occurred |

### 1.5 Execution Section

| Key | Type | Description |
|-----|------|-------------|
| `tool_calls` | array | Array of [ToolCall](#tool-call) objects |
| `duration_ms` | integer | Total duration in milliseconds |
| `resources_used` | object | Arbitrary key-value pairs |

#### Tool Call

| Key | Type | Description |
|-----|------|-------------|
| `tool` | string | Tool name |
| `arguments` | object | Input arguments |
| `result` | any | Output (any JSON type) |
| `success` | boolean | Whether the call succeeded |
| `duration_ms` | integer | Call duration |
| `error` | string \| null | Error message |

### 1.6 Outcome Section

| Key | Type | Description |
|-----|------|-------------|
| `status` | string | `"pending"`, `"success"`, `"failure"`, `"partial"`, `"blocked"` |
| `result` | any | Detailed result (any JSON type) |
| `summary` | string | Human-readable summary |
| `error` | string \| null | Error message |
| `side_effects` | array | Array of strings |
| `metrics` | object | Arbitrary key-value pairs |

---

## 2. Canonical JSON Serialization Rules

The canonical form transforms a Capsule object into a deterministic byte string. All implementations MUST produce byte-identical output for the same logical Capsule.

### 2.1 Key Ordering

All object keys MUST be sorted **lexicographically by Unicode code point**, applied **recursively** to all nested objects.

This includes:
- Top-level Capsule keys
- Section keys (trigger, context, etc.)
- Keys within `environment`, `resources_used`, `metrics`, `result` (if object), `arguments`, `estimated_impact`
- Keys within objects inside `chain` array elements

Array elements are NOT sorted — their order is preserved.

### 2.2 Whitespace

Zero whitespace. No spaces after `:` or `,`. No newlines.

Equivalent to Python's `json.dumps(separators=(",", ":"))`.

### 2.3 Float-Typed Fields

The following fields are **float-typed** and MUST always be serialized with at least one decimal place, even when the value is mathematically an integer:

| Field Path | Example |
|------------|---------|
| `reasoning.confidence` | `0.0`, `0.95`, `1.0` |
| `reasoning.options[].feasibility` | `0.0`, `0.5`, `1.0` |

Rules for float-typed fields:
- `0.0` → `0.0` (NOT `0`)
- `1.0` → `1.0` (NOT `1`)
- `0.95` → `0.95`
- `Infinity` and `NaN` are PROHIBITED (raise an error)

All other numeric values (integers in `duration_ms`, `sequence`, values in arbitrary dicts) follow standard JSON number formatting:
- `0` → `0`
- `42` → `42`

**Rationale**: Python's `json.dumps` preserves the float/int distinction from the Python type system. The float-typed fields in the Capsule data model are defined as `float` in the Python reference implementation, so they always serialize with a decimal point. Other languages (JavaScript, Go) do not distinguish floats from integers; implementations in those languages must explicitly format these fields.

### 2.4 DateTime Format

The `trigger.timestamp` field uses Python's `datetime.isoformat()` output format for UTC datetimes:

```
YYYY-MM-DDTHH:MM:SS+00:00
```

Examples:
- `2026-01-01T00:00:00+00:00` (correct)
- `2026-01-01T00:00:00Z` (INCORRECT — do not use `Z` suffix)
- `2026-01-01T00:00:00.000+00:00` (INCORRECT — no fractional seconds unless present in source)

When fractional seconds are present:
- `2026-01-01T12:30:45.123456+00:00` (correct — preserve microseconds from source)

### 2.5 UUID Format

UUIDs MUST be serialized as lowercase hexadecimal with hyphens:

```
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Example: `12345678-1234-1234-1234-123456789012`

### 2.6 String Escaping

Strings follow RFC 8259 (JSON) escaping rules. Characters that MUST be escaped:
- `"` → `\"`
- `\` → `\\`
- Control characters (U+0000 through U+001F) → `\uXXXX`

Characters that MUST NOT be escaped:
- `/` (solidus) — serialize as literal `/`, not `\/`
- Printable ASCII (U+0020 through U+007E) — serialize as literal characters
- Non-ASCII Unicode (U+0080 and above) — serialize as literal UTF-8 characters

### 2.7 Null, Boolean, and Empty Collections

| Value | Serialized |
|-------|------------|
| null | `null` |
| true | `true` |
| false | `false` |
| empty array | `[]` |
| empty object | `{}` |

---

## 3. Sealing Algorithm

### 3.1 Hash Computation

```
INPUT:  Capsule object
OUTPUT: 64-character lowercase hex string

1. Convert Capsule to dict via to_dict()
2. Serialize to canonical JSON following all rules in Section 2
3. Encode canonical JSON as UTF-8 bytes
4. Compute SHA3-256 (FIPS 202) of the bytes
5. Return lowercase hexadecimal digest
```

### 3.2 Ed25519 Signature (Required)

```
INPUT:  SHA3-256 hex digest (64-character ASCII string)
OUTPUT: 128-character hex string

1. Encode the hex digest string as UTF-8 bytes (64 bytes of ASCII)
   NOTE: Sign the hex STRING, not the raw 32-byte hash
2. Sign with Ed25519 (RFC 8032) using the private key
3. Return lowercase hexadecimal signature
```

**Critical detail**: The Ed25519 signature is computed over the **hex-encoded hash string** (64 ASCII characters encoded as UTF-8), not the raw 32-byte hash value. This is intentional and must be replicated exactly.

### 3.3 ML-DSA-65 Signature (Optional)

```
INPUT:  SHA3-256 hex digest (64-character ASCII string)
OUTPUT: hex string

1. Encode the hex digest string as UTF-8 bytes
2. Sign with ML-DSA-65 (FIPS 204) / Dilithium3 using the private key
3. Return lowercase hexadecimal signature
```

### 3.4 Verification

```
INPUT:  Capsule with hash and signature fields populated
OUTPUT: boolean

1. Extract hash and signature from Capsule
2. Clear hash, signature, signature_pq, signed_at, signed_by fields
   (these are NOT part of the canonical content)
3. Recompute canonical JSON from the Capsule content
4. Compute SHA3-256 of canonical JSON
5. Compare computed hash with stored hash (must match exactly)
6. Verify Ed25519 signature over the stored hash string using public key
7. Return true only if both hash and signature verify
```

Note: The seal fields (`hash`, `signature`, `signature_pq`, `signed_at`, `signed_by`) are metadata OUTSIDE the canonical content. The `to_dict()` method does not include them. Verification recomputes canonical JSON from the content fields only.

---

## 4. Hash Chain Rules

1. The first Capsule (genesis) has `sequence: 0` and `previous_hash: null`
2. Each subsequent Capsule has `sequence: N+1` and `previous_hash` equal to the `hash` of the Capsule at sequence N
3. Sequence numbers MUST be consecutive with no gaps
4. Chain verification checks: consecutive sequences, hash linkage, and genesis has null previous_hash

---

## 5. Golden Test Vectors

See `fixtures.json` in this directory for test vectors that all implementations must pass. Each vector contains:

- `capsule_dict`: The Capsule as a JSON object (output of `to_dict()`)
- `canonical_json`: The exact canonical JSON string
- `sha3_256_hash`: The expected SHA3-256 hex digest

An implementation is conformant if, for every test vector, it produces byte-identical `canonical_json` and `sha3_256_hash` from the `capsule_dict` input.

---

## 6. Implementation Checklist

For a conformant implementation in any language:

- [ ] Capsule data model with all 6 sections and all fields
- [ ] `to_dict()` — convert Capsule to a plain dictionary/map
- [ ] `canonicalize()` — serialize dict to canonical JSON (Section 2)
- [ ] `compute_hash()` — SHA3-256 of canonical JSON
- [ ] `seal()` — compute hash + Ed25519 signature
- [ ] `verify()` — recompute hash and verify signature
- [ ] `from_dict()` — deserialize Capsule from dictionary/map
- [ ] Pass all golden test vectors from `fixtures.json`
- [ ] Chain verification (sequence + hash linkage)

---

*This specification is the contract. Pass the golden fixtures, and you're compatible with every other implementation.*
