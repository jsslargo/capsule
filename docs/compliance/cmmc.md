# CMMC 2.0

The Cybersecurity Maturity Model Certification (CMMC) 2.0 is required for Department of Defense contractors handling Controlled Unclassified Information (CUI). CMMC Level 2 aligns with NIST SP 800-171 Rev. 2 (110 controls). Capsule provides protocol-level capabilities that address audit, integrity, and cryptographic protection requirements.

---

## Audit and Accountability (AU)

| Control | Requirement | How Capsule Addresses It |
|---|---|---|
| **AU.L2-3.3.1** | Create audit records for defined events | Every AI action produces a Capsule. `CapsuleType` defines 8 event categories. 6 sections capture the complete lifecycle. |
| **AU.L2-3.3.2** | Unique user accountability | `trigger.user_id` and `trigger.source` attribute actions to specific users or agents. `signed_by` identifies the signing key. |
| **AU.L2-3.3.4** | Alert on audit logging process failure | `outcome.status = "failure"` records action failures. Kill switch Capsules record system-level interventions. Applications can alert on chain verification failures. |
| **AU.L2-3.3.5** | Correlate audit review, analysis, and reporting | `correlation_id` links related Capsules. `parent_id` creates hierarchical relationships. `session_id` groups conversation turns. |
| **AU.L2-3.3.8** | Protect audit information from unauthorized access, modification, and deletion | SHA3-256 hash + Ed25519 signature prevents undetected modification. Hash chain prevents undetected deletion or insertion. Key files restricted to owner (`0600` permissions). |
| **AU.L2-3.3.9** | Manage and retain audit logs | Capsules are persisted in SQLite or PostgreSQL. `storage.list()` with pagination. Retention policies configurable at the storage layer. |

## System and Communications Protection (SC)

| Control | Requirement | How Capsule Addresses It |
|---|---|---|
| **SC.L2-3.13.8** | Implement cryptographic mechanisms to prevent unauthorized disclosure during transmission | Capsule hashes are self-verifying independent of transport. Recompute SHA3-256 and compare to stored hash on receipt. |
| **SC.L2-3.13.10** | Establish and manage cryptographic keys | Ed25519 keys auto-generated with `0600` permissions and `umask(0o077)`. ML-DSA-65 keys for post-quantum protection. `verify_with_key()` supports key rotation verification. |
| **SC.L2-3.13.11** | Employ FIPS-validated cryptography | SHA3-256 (FIPS 202), Ed25519 (FIPS 186-5), ML-DSA-65 (FIPS 204). All algorithms are NIST-standardized. |

## Access Control (AC)

| Control | Requirement | How Capsule Addresses It |
|---|---|---|
| **AC.L2-3.1.12** | Monitor and control remote access sessions | `CapsuleType.AUTH` records authentication events. Authority section records approval chains. Session tracking via `session_id`. |

## Complementary Controls

The following CMMC requirements are outside the protocol's scope:

- **AC.L2-3.1.1 through 3.1.11** Access control policies and enforcement -- application-level
- **IA** Identification and authentication -- application-level
- **IR** Incident response -- organizational (though Capsules provide evidence for investigation)
- **MP** Media protection -- physical security
- **PE** Physical protection -- facility security
- **PS** Personnel security -- organizational

---

[Back to Compliance Overview](./README.md)
