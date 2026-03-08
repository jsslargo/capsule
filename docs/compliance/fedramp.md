# FedRAMP (NIST SP 800-53 Rev. 5)

The Federal Risk and Authorization Management Program (FedRAMP) standardizes security assessment for cloud services used by federal agencies. FedRAMP controls are drawn from NIST SP 800-53 Rev. 5. Capsule provides protocol-level capabilities that address controls in the Audit (AU), System and Communications Protection (SC), System and Information Integrity (SI), and Configuration Management (CM) families.

For the core AU, SC, and SI mappings shared with NIST SP 800-53, see [nist-sp-800-53.md](./nist-sp-800-53.md). This document covers additional FedRAMP-specific requirements and higher-baseline enhancements.

---

## FedRAMP-Specific Enhancements

### Audit and Accountability (AU)

| Control | Title | Baseline | How Capsule Addresses It |
|---|---|---|---|
| **AU-9(3)** | Cryptographic Protection of Audit Information | High | SHA3-256 (FIPS 202) integrity hashing + Ed25519 (FIPS 186-5) signatures on every Capsule. Optional ML-DSA-65 (FIPS 204) post-quantum dual signatures. |
| **AU-10** | Non-repudiation | High | Ed25519 digital signatures with `signed_by` key fingerprint. `verify_with_key()` enables independent third-party verification. |

### System and Information Integrity (SI)

| Control | Title | Baseline | How Capsule Addresses It |
|---|---|---|---|
| **SI-7(1)** | Integrity Checks | Moderate | `seal.verify(capsule)` for individual records, `chain.verify()` for the full chain. Both can run at startup, on schedule, or on demand. |
| **SI-7(2)** | Automated Notifications of Integrity Violations | High | `chain.verify()` returns `broken_at` with the Capsule ID where integrity failed. Applications can alert on this. |
| **SI-7(5)** | Automated Response to Integrity Violations | High | Kill switch Capsules (`CapsuleType.KILL`) record automated termination events when integrity violations are detected. |
| **SI-7(7)** | Integration of Detection and Response | Moderate | Chain verification results include Capsule context (6 sections) for direct incident response integration. |

### System and Communications Protection (SC)

| Control | Title | Baseline | How Capsule Addresses It |
|---|---|---|---|
| **SC-8(1)** | Cryptographic Protection (Transmission) | Moderate | Capsule hashes are self-verifying: recompute SHA3-256 from content and compare to stored hash. Verification is independent of transport layer. |
| **SC-28(1)** | Cryptographic Protection (At Rest) | Moderate | Sealed Capsules are integrity-protected via cryptographic signatures. Storage-level encryption is configurable at the database layer. |

### Configuration Management (CM)

| Control | Title | Baseline | How Capsule Addresses It |
|---|---|---|---|
| **CM-3** | Configuration Change Control | Moderate | Each Capsule records what changed (`outcome.side_effects`), who approved it (`authority`), and why (`reasoning`). Hash chain provides tamper-evident change history. |

## Air-Gapped Operation

Capsule is designed for air-gapped federal environments:

- Zero runtime network dependencies
- No telemetry, analytics, or license server
- All cryptographic operations use local key material
- SQLite storage requires no network access
- FIPS-approved algorithms throughout (SHA3-256, Ed25519, ML-DSA-65)

## Complementary Controls

The following FedRAMP control families are outside the protocol's scope:

- **AC** Access control -- application-level authentication and authorization
- **AT** Awareness and training -- organizational
- **CA** Assessment, authorization, and monitoring -- organizational
- **CP** Contingency planning -- infrastructure-level
- **IA** Identification and authentication -- application-level
- **IR** Incident response procedures -- organizational (though Capsules provide the evidence for incident investigation)

---

[Back to Compliance Overview](./README.md)
