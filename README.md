<div align="center">

# Capsule Protocol Specification (CPS)

**Know what your AI did, why it did it, and who approved it — with cryptographic proof.**

*Tamper-evident audit records for AI operations.*

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/)
[![CPS](https://img.shields.io/badge/CPS-v1.0-orange.svg)](./specs/cps/)
[![Coverage](https://img.shields.io/badge/Coverage-100%25-brightgreen.svg)](./pyproject.toml)
[![FIPS](https://img.shields.io/badge/Crypto-FIPS_202%20·%20186--5%20·%20204-purple.svg)](#the-cryptographic-seal)

</div>

---

## What is a Capsule?

A Capsule is a cryptographically sealed record of a single AI action. It has six sections that capture the complete audit trail for that action: what initiated it, what the system state was, why the AI made the decision it made, who or what authorized it, what tools were called, and what the outcome was.

Every Capsule is hashed with SHA3-256 and signed with Ed25519. Each Capsule records the hash of the previous one, forming a chain where tampering with any record invalidates every record that follows.

```
∀ action: ∃ capsule
"For every action, there exists a Capsule."
```

## Why Capsules?

AI systems make thousands of autonomous decisions. When something goes wrong — or when a regulator asks "why did the AI do that?" — you need evidence that existed *before* the question was asked.

Capsules solve three problems that logging does not:

1. **Pre-execution reasoning capture.** Section 3 (Reasoning) records the AI's analysis, the options it considered, the option it selected, and why it rejected the alternatives — all captured *before* Section 5 (Execution) runs. This is contemporaneous evidence of deliberation, not a post-hoc reconstruction.

2. **Cryptographic tamper evidence.** Every Capsule is hashed and signed at the moment of creation. If anyone modifies the content after the fact, the hash changes, the signature fails, and the chain breaks. This is not a property of the storage layer — it is a property of every individual record.

3. **Cross-language interoperability.** The Capsule Protocol Specification defines byte-level serialization rules. A Capsule sealed in Python can be verified in Go, Rust, or TypeScript. All implementations produce identical canonical JSON for the same input, validated by 15 golden test vectors.

## How It Works

### The 6 Sections

Every Capsule records a complete action through six mandatory sections:

```
┌─────────────────────────────────────────────────────────┐
│                       CAPSULE                           │
├─────────────┬───────────────────────────────────────────┤
│ 1. Trigger  │ What initiated this action?               │
│ 2. Context  │ What was the state of the system?         │
│ 3. Reasoning│ Why was this decision made?               │
│ 4. Authority│ Who or what approved it?                  │
│ 5. Execution│ What tools were called?                   │
│ 6. Outcome  │ Did it succeed? What changed?             │
├─────────────┴───────────────────────────────────────────┤
│ SHA3-256 hash │ Ed25519 signature │ ML-DSA-65 (opt.)    │
│ Previous hash │ Sequence number   │ Timestamp           │
└─────────────────────────────────────────────────────────┘
```

### The Hash Chain

Each Capsule records the SHA3-256 hash of the previous Capsule. This creates a chain where modifying, deleting, or inserting any record is immediately detectable.

```
Capsule #0          Capsule #1          Capsule #2
┌──────────┐        ┌──────────┐        ┌──────────┐
│ hash: A  │◀───────│ prev: A  │◀───────│ prev: B  │
│ prev: ∅  │        │ hash: B  │        │ hash: C  │
└──────────┘        └──────────┘        └──────────┘
```

No consensus mechanism. No distributed ledger. SHA3-256 hashes linking one record to the next.

### The Cryptographic Seal

Every Capsule is sealed with a two-tier cryptographic architecture:

| Layer | Algorithm | Standard | Purpose |
|---|---|---|---|
| Content integrity | SHA3-256 | FIPS 202 | Tamper-evident hashing |
| Classical signature | Ed25519 | RFC 8032 / FIPS 186-5 | Authenticity and non-repudiation |
| Post-quantum signature | ML-DSA-65 | FIPS 204 | Quantum-resistant protection (optional) |
| Temporal integrity | Hash chain | CPS v1.0 | Ordering and completeness |

Ed25519 is always required. ML-DSA-65 runs alongside Ed25519 as an optional dual signature (`pip install qp-capsule[pq]`). No deprecated cryptography. No runtime network dependencies. Air-gapped operation supported.

---

## Quick Start

```bash
pip install qp-capsule
```

```python
from qp_capsule import Capsule, Seal, CapsuleType, TriggerSection

# Create a Capsule
capsule = Capsule(
    type=CapsuleType.AGENT,
    trigger=TriggerSection(
        type="user_request",
        source="deploy-bot",
        request="Deploy service v2.4 to production",
    ),
)

# Seal it — SHA3-256 hash + Ed25519 signature
seal = Seal()
seal.seal(capsule)

# Verify it — anyone can, anytime
assert seal.verify(capsule)
```

### With Hash Chain

```bash
pip install qp-capsule[storage]
```

```python
from qp_capsule import Capsule, Seal, CapsuleChain, CapsuleStorage, CapsuleType, TriggerSection

storage = CapsuleStorage()
chain = CapsuleChain(storage)
seal = Seal()

capsule = Capsule(
    type=CapsuleType.AGENT,
    trigger=TriggerSection(source="deploy-bot", request="Deploy v2.4"),
)

# One call: chain + seal + store
capsule = await chain.seal_and_store(capsule, seal)

# Verify the entire chain
result = await chain.verify()
assert result.valid
```

### What a Sealed Capsule Looks Like

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "type": "agent",
  "trigger": {
    "source": "deploy-bot",
    "request": "Deploy service v2.4 to production"
  },
  "reasoning": {
    "options_considered": ["Deploy v2.4", "Rollback to v2.3", "Do nothing"],
    "selected_option": "Deploy v2.4",
    "confidence": 0.92
  },
  "authority": { "type": "human_approved", "approver": "ops-lead" },
  "execution": {
    "tool_calls": [{ "tool": "kubectl_apply", "success": true, "duration_ms": 3200 }]
  },
  "outcome": { "status": "success", "summary": "Deployed v2.4 to prod-us-east" },
  "hash": "4cb02d65...",
  "signature": "a3f8b2c1...",
  "previous_hash": "7d2e9f41...",
  "sequence": 42
}
```

Six sections. Hashed with SHA3-256. Signed with Ed25519. Chained to the previous record. Reasoning captured *before* execution.

### High-Level API

The fastest way to add audit trails to any Python application. One class, one decorator.

```bash
pip install qp-capsule[storage]
```

```python
from qp_capsule import Capsules

capsules = Capsules()  # SQLite, zero config

@capsules.audit(type="agent")
async def run_agent(task: str, *, site_id: str):
    cap = capsules.current()
    cap.reasoning.model = "gpt-4o"
    cap.reasoning.confidence = 0.92

    result = await llm.complete(task)
    cap.outcome.summary = f"Generated {len(result.text)} chars"
    return result

# Every call is now audited with a sealed Capsule.
# If capsule creation fails, your function still works normally.
await run_agent("Write a summary", site_id="tenant-123")
```

**PostgreSQL:**

```python
capsules = Capsules("postgresql://user:pass@localhost/mydb")
```

**FastAPI integration** — three read-only endpoints for inspecting the audit chain:

```python
from qp_capsule.integrations.fastapi import mount_capsules

app = FastAPI()
mount_capsules(app, capsules, prefix="/api/v1/capsules")
# GET /api/v1/capsules/         — List (paginated, filterable)
# GET /api/v1/capsules/{id}     — Get by ID
# GET /api/v1/capsules/verify   — Verify chain integrity
```

See [High-Level API docs](./docs/high-level-api.md) for the full guide.

---

## Install

```bash
pip install qp-capsule
```

Cross-language SDKs (TypeScript, Go, Rust) are planned. The [CPS specification](./specs/cps/) and 15 golden test vectors define the byte-level contract — any conforming implementation can seal and verify Capsules interchangeably.

### Python extras

| Command | What You Get | Dependencies |
|---|---|---|
| `pip install qp-capsule` | Create, seal, verify | **1** (pynacl) |
| `pip install qp-capsule[storage]` | + Hash chain + SQLite persistence | **2** (+ sqlalchemy) |
| `pip install qp-capsule[postgres]` | + Hash chain + PostgreSQL (multi-tenant) | **2** (+ sqlalchemy) |
| `pip install qp-capsule[pq]` | + Post-quantum ML-DSA-65 signatures | **2** (+ liboqs) |

---

## Capsule Protocol Specification (CPS)

All implementations follow the **Capsule Protocol Specification**, which defines:

- **Record structure** — the 6-section Capsule model with all field types and defaults
- **Canonical serialization** — byte-level JSON rules for deterministic hashing
- **Sealing algorithm** — SHA3-256 + Ed25519 + optional ML-DSA-65
- **Hash chain rules** — sequence numbering and hash linking
- **Golden test vectors** — 15 conformance fixtures for cross-language verification

```
  Language A (seal)  ──→  Canonical JSON + SHA3-256 + Ed25519  ──→  Language B (verify) ✓
```

The specification is language-agnostic. Any implementation that passes the 15 golden test vectors can seal and verify Capsules produced by any other.

Full specification: [`specs/cps/`](./specs/cps/)

---

## Examples

The [`examples/`](./examples/) directory contains realistic Capsule records showing the 6-section model in practice:

| Example | Type | Scenario |
|---|---|---|
| [deploy-to-production.json](./examples/deploy-to-production.json) | AGENT | Production deployment with structured reasoning, human approval, and tool calls |
| [file-read-tool.json](./examples/file-read-tool.json) | TOOL | Simple tool invocation by an agent |
| [kill-switch-activation.json](./examples/kill-switch-activation.json) | KILL | Emergency stop triggered by anomaly detection |
| [chat-with-rag.json](./examples/chat-with-rag.json) | CHAT | RAG query with source attribution and model metadata |
| [policy-denied-action.json](./examples/policy-denied-action.json) | TOOL | Destructive action blocked by safety policy |
| [multi-step-workflow.json](./examples/multi-step-workflow.json) | WORKFLOW | Three linked Capsules showing parent-child hierarchy |

---

## Custom Storage Backends

Capsule ships with SQLite and PostgreSQL storage. To build your own backend, implement `CapsuleStorageProtocol` — a runtime-checkable `typing.Protocol` with 7 async methods. Any conforming backend plugs directly into `CapsuleChain`. See [Architecture](./docs/architecture.md#storage-architecture) for details.

---

## Documentation

| Document | Audience |
|---|---|
| [High-Level API](./docs/high-level-api.md) | Developers |
| [Getting Started](./docs/getting-started.md) | Developers |
| [Architecture](./docs/architecture.md) | Developers, Auditors |
| [API Reference](./docs/api.md) | Developers |
| [Security Evaluation](./docs/security.md) | CISOs, Security Teams |
| [Compliance Mapping](./docs/compliance.md) | Regulators, GRC |
| [CPS Specification](./docs/specification.md) | SDK Authors |
| [Audit Report](./docs/audit-report.md) | CISOs, Auditors |

---

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). Protocol changes go through the [CPS change proposal](https://github.com/quantumpipes/capsule/issues/new?template=cps_change.md) process.

## License and Patents

[Apache License 2.0](./LICENSE) with [additional patent grant](./PATENTS.md). You can use all patented innovations freely for any purpose, including commercial use.

## Full Platform

This package provides the protocol primitives. For the full autonomous AI platform with Vault, Cognition, Intelligence, and Hub, see **[Quantum Pipes Core](https://github.com/quantumpipes/core)**.

---

<div align="center">

**∀ action: ∃ capsule**

Python reference implementation · Cross-language SDKs planned

[Website](https://quantumpipes.com) · [Full Platform](https://github.com/quantumpipes/core) · [CPS Specification](./specs/cps/) · [Security Policy](./SECURITY.md) · [Patent Grant](./PATENTS.md)

Copyright 2026 [Quantum Pipes Technologies, LLC](https://quantumpipes.com)

</div>
