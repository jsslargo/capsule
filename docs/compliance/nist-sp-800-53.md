# NIST SP 800-53 Rev. 5

Security and privacy controls for information systems. Capsule addresses controls in the Audit (AU), System and Communications Protection (SC), and System and Information Integrity (SI) families.

---

## Audit and Accountability (AU)

| Control | Title | How Capsule Addresses It |
|---|---|---|
| **AU-2** | Event Logging | Every AI action produces a Capsule. The `CapsuleType` enum defines 8 event categories: agent, tool, system, kill, workflow, chat, vault, auth. |
| **AU-3** | Content of Audit Records | Each Capsule contains 6 sections: Trigger (who/what/when), Context (system state), Reasoning (why), Authority (approval), Execution (how), Outcome (result). |
| **AU-3(1)** | Additional Audit Information | `correlation_id` links related Capsules across distributed operations. `parent_id` creates hierarchical relationships. `session_id` groups conversation turns. |
| **AU-8** | Time Stamps | `trigger.timestamp` records UTC time of action initiation. `signed_at` records UTC time of cryptographic sealing. Both are timezone-aware. |
| **AU-9** | Protection of Audit Information | SHA3-256 hash + Ed25519 signature prevents undetected modification. Hash chain prevents undetected deletion or insertion. |
| **AU-10** | Non-repudiation | Ed25519 digital signatures provide non-repudiation via `signed_by` (key fingerprint). `verify_with_key()` enables third-party verification. |
| **AU-11** | Audit Record Retention | Capsules are persisted in SQLite or PostgreSQL. Retention policies are configurable at the storage layer. |
| **AU-12** | Audit Record Generation | Capsule creation is application-initiated at the moment of action. The `seal_and_store()` convenience method ensures atomic chain + seal + store. |

## System and Communications Protection (SC)

| Control | Title | How Capsule Addresses It |
|---|---|---|
| **SC-13** | Cryptographic Protection | SHA3-256 (FIPS 202) for integrity, Ed25519 (FIPS 186-5) for signatures, ML-DSA-65 (FIPS 204) for quantum resistance. |
| **SC-28** | Protection of Information at Rest | Sealed Capsules are integrity-protected via cryptographic signatures. Storage-level encryption is configurable at the database layer. |

## System and Information Integrity (SI)

| Control | Title | How Capsule Addresses It |
|---|---|---|
| **SI-7** | Software, Firmware, and Information Integrity | `chain.verify()` detects any modification, deletion, or insertion in the audit trail. |
| **SI-7(1)** | Integrity Checks | Verification can run anytime: `seal.verify(capsule)` for individual records, `chain.verify()` for the entire chain. |

---

[Back to Compliance Overview](./README.md)
