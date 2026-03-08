# Regulatory Compliance Mapping

> **How the Capsule protocol maps to the frameworks your auditors care about.**

---

## Scope

This directory maps **protocol-level** capabilities to regulatory controls. Every mapping describes what the Capsule Protocol Specification (CPS) itself provides: structured records, cryptographic sealing, hash chain integrity, and cross-language verification.

Application-level controls (access management, network security, operational procedures) are the responsibility of the deployment environment, not the protocol.

---

## FIPS Algorithm Compliance

| Algorithm | FIPS Standard | Status | Capsule Usage |
|---|---|---|---|
| SHA3-256 | FIPS 202 (SHA-3) | Published August 2015 | Content hashing for every Capsule |
| Ed25519 | FIPS 186-5 (Digital Signatures) | Published February 2023 | Required signature on every Capsule |
| ML-DSA-65 | FIPS 204 (ML-DSA) | Published August 2024 | Optional post-quantum dual signature |

All three algorithms are NIST-standardized. No deprecated or non-standard cryptography is used.

---

## Framework Mappings

| Framework | Controls Mapped | Document |
|---|---|---|
| [NIST SP 800-53 Rev. 5](./nist-sp-800-53.md) | AU-2 through AU-12, SC-13, SC-28, SI-7 | Audit, integrity, crypto |
| [NIST AI RMF 1.0](./nist-ai-rmf.md) | GOVERN, MAP, MEASURE, MANAGE | AI risk management |
| [EU AI Act](./eu-ai-act.md) | Articles 12, 13, 14 | Record-keeping, transparency, oversight |
| [SOC 2 Type II](./soc2.md) | CC6.1, CC7.2, CC7.3, CC7.4, CC8.1 | Trust Services Criteria |
| [ISO 27001:2022](./iso27001.md) | A.8.15, A.8.16, A.8.17, A.8.24, A.8.25 | Annex A controls |
| [HIPAA](./hipaa.md) | §164.308, §164.312 | Security Rule safeguards |
| [GDPR](./gdpr.md) | Articles 5, 25, 30, 32, 35 | Data protection principles |
| [PCI DSS v4.0](./pci-dss.md) | Req 10, Req 11.5, Req 11.6 | Logging, monitoring, change detection |
| [FedRAMP](./fedramp.md) | AU-9(3), AU-10, SI-7(1-7), SC-8(1), SC-28(1), CM-3 | Federal cloud authorization |
| [FINRA](./finra.md) | SEC 17a-4, REC-2, Rule 3110 | Financial recordkeeping, supervision |
| [CMMC 2.0](./cmmc.md) | AU.L2-3.3.x, SC.L2-3.13.x, AC.L2-3.1.12 | DoD contractor CUI protection |

---

## Cross-Language Conformance

Capsule sealed in any language can be verified in any other. The Capsule Protocol Specification (CPS) defines:

- Byte-level canonical JSON serialization rules
- 16 golden test vectors covering all CapsuleTypes, Unicode, fractional timestamps, chain sequences, empty vs null, deep nesting, and failure paths
- SHA3-256 hash determinism across implementations

Python and TypeScript reference implementations are available now. All conformant implementations produce byte-identical canonical JSON and matching SHA3-256 hashes for the golden test vectors.

See [CPS Specification](../../spec/) for protocol details.

---

## Related Documentation

- [Security Evaluation](../security.md) -- Cryptographic architecture, key management, attack surface
- [Architecture](../architecture.md) -- 6-section model, sealing process, hash chain
- [CPS Specification](../../spec/) -- Protocol rules and golden test vectors
