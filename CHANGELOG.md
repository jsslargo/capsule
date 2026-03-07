# Changelog

All notable changes to Capsule are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-03-07

Initial public release of the Capsule Protocol Specification (CPS) v1.0 reference implementation.

### Added

- **Capsule model** with 6 mandatory sections: Trigger, Context, Reasoning, Authority, Execution, Outcome
- **8 Capsule types**: agent, tool, system, kill, workflow, chat, vault, auth
- **Cryptographic sealing**: SHA3-256 (FIPS 202) + Ed25519 (FIPS 186-5)
- **Post-quantum dual signatures**: optional ML-DSA-65 (FIPS 204) via `pip install qp-capsule[pq]`
- **Hash chain**: tamper-evident linking with sequence numbers and `previous_hash`
- **CapsuleStorageProtocol**: runtime-checkable `typing.Protocol` for custom storage backends
- **SQLite storage**: zero-config persistence via `pip install qp-capsule[storage]`
- **PostgreSQL storage**: multi-tenant isolation via `pip install qp-capsule[postgres]`
- **Pre-execution reasoning capture**: Section 3 (Reasoning) written before Section 5 (Execution)
- **ReasoningOption.rejection_reason**: mandatory explanation for non-selected options
- **Key management**: auto-generated keys with `0600` permissions, umask-based creation
- **Cross-language interoperability**: canonical JSON serialization rules and 15 golden test vectors covering Unicode, fractional timestamps, all CapsuleTypes, chain sequences, deep nesting, failure paths
- **Documentation**: getting-started, architecture, API reference, security evaluation, compliance mapping, CPS specification summary
- **350 automated tests** across 14 test files with **100% code coverage** enforced in CI
- **CPS v1.0 specification** shipped with the repo at `specs/cps/`
- **Apache 2.0 license** with additional patent grant

### Security

- Ed25519 signatures required on every Capsule
- SHA3-256 chosen over SHA-256 for length-extension resistance
- Key files created with restrictive umask (no TOCTOU race)
- ML-DSA-65 uses FIPS 204 standardized name
- Zero runtime network dependencies (air-gapped operation)
- `filterwarnings = ["error"]` with zero exemptions — any warning is a test failure
- 100% test coverage enforced (`fail_under = 100`)

---

[1.0.0]: https://github.com/quantumpipes/capsule/releases/tag/v1.0.0
