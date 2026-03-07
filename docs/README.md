---
title: "Capsule Documentation"
description: "Documentation for the Capsule Protocol Specification (CPS) reference implementation."
date_modified: "2026-03-07"
---

# Capsule Documentation

Every AI action. Sealed with SHA3-256 + Ed25519. Chained into a tamper-evident audit trail. Reasoning captured before execution, not reconstructed afterward.

---

## Who Are You?

| I am a... | Start here |
|---|---|
| **Developer** building with Capsule | [Getting Started](./getting-started.md) — zero to sealed Capsule in 60 seconds |
| **CISO** evaluating Capsule for my organization | [Security Evaluation](./security.md) — crypto architecture, key management, checklist |
| **Compliance team** mapping to regulatory frameworks | [Compliance Mapping](./compliance.md) — NIST SP 800-53, EU AI Act, SOC 2, ISO 27001 |
| **Auditor** reviewing cryptographic guarantees | [Audit Report](./audit-report.md) — Bandit scan, OWASP assessment, 20-point checklist |
| **SDK author** implementing CPS in another language | [CPS Specification](./specification.md) — canonical JSON rules, sealing algorithm, 15 golden vectors |

---

## All Documents

| Document | What It Covers |
|---|---|
| [Getting Started](./getting-started.md) | Install, create, seal, verify, chain — working code in 60 seconds |
| [Architecture](./architecture.md) | The 6-section model, cryptographic sealing, hash chain, storage backends, CapsuleStorageProtocol |
| [API Reference](./api.md) | Every class, method, parameter, and type in the Python package |
| [Security Evaluation](./security.md) | FIPS algorithm selection, key management, tamper evidence, attack surface, deployment, evaluation checklist |
| [Compliance Mapping](./compliance.md) | NIST SP 800-53 (AU, SC, SI), NIST AI RMF, EU AI Act (Articles 12-14), SOC 2, ISO 27001 |
| [CPS Specification](./specification.md) | Record structure, canonical JSON rules, sealing algorithm, hash chain rules, 15 golden test vectors |
| [Audit Report](./audit-report.md) | Bandit scan results, dependency audit, OWASP Top 10 assessment, test metrics, 20-point evaluation checklist |

---

## Additional Resources

| Resource | Location |
|---|---|
| CPS v1.0 full specification | [`specs/cps/`](../specs/cps/) |
| Golden test vectors (15 fixtures) | [`specs/cps/fixtures.json`](../specs/cps/fixtures.json) |
| Changelog | [`CHANGELOG.md`](../CHANGELOG.md) |
| Security policy | [`SECURITY.md`](../SECURITY.md) |
| Contributing | [`CONTRIBUTING.md`](../CONTRIBUTING.md) |
| Patent grant | [`PATENTS.md`](../PATENTS.md) |
| Full platform (Quantum Pipes Core) | [github.com/quantumpipes/core](https://github.com/quantumpipes/core) |

---

*Capsule v1.0.0 — Capsule Protocol Specification (CPS) v1.0*
