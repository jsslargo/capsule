# FINRA

FINRA (Financial Industry Regulatory Authority) cybersecurity rules govern broker-dealers and financial services firms. Key regulations include SEC Rule 17a-4 (electronic recordkeeping), Regulation S-P (privacy), Regulation S-ID (identity theft), and FINRA Rules 3110 (supervision) and 4370 (business continuity).

Capsule provides protocol-level capabilities that address recordkeeping integrity, record authenticity, and supervisory audit requirements.

---

## SEC Rule 17a-4: Electronic Recordkeeping

| Requirement | How Capsule Addresses It |
|---|---|
| Records must be preserved in non-rewriteable, non-erasable (WORM) format | Capsules are sealed with SHA3-256 + Ed25519 at the moment of action. Any modification changes the hash and invalidates the signature. Hash chain makes the record sequence tamper-evident. |
| 2 years of immediately accessible records; 3-6 years archive | Capsules are persisted in SQLite or PostgreSQL with configurable retention. `storage.list()` provides paginated retrieval. |
| Records must be indexed and searchable | Capsules are queryable by type (`CapsuleType`), time range, tenant, session, and chain position. |

## Record Authenticity (REC-2)

| Requirement | How Capsule Addresses It |
|---|---|
| Digital signatures to verify record origin | Ed25519 signature on every Capsule with `signed_by` key fingerprint. Optional ML-DSA-65 (FIPS 204) post-quantum dual signature. |
| Hash verification to detect unauthorized modification | SHA3-256 content hash. `seal.verify(capsule)` recomputes the hash from content and compares to the stored hash. |
| Audit trails to detect unauthorized modifications | Hash chain links each Capsule to the previous via `previous_hash`. `chain.verify()` detects any modification, deletion, or insertion in the sequence. |

## FINRA Rule 3110: Supervision

| Requirement | How Capsule Addresses It |
|---|---|
| Written supervisory procedures | Authority section records authorization type (`autonomous`, `human_approved`, `policy`, `escalated`), policy references, and approval chains. |
| Review of supervisory activities | Capsules are structured, machine-readable records. Reasoning section captures pre-execution deliberation for supervisory review. |
| Evidence of supervision | Each Capsule's Authority section documents who or what approved the action and why escalation occurred (if applicable). |

## Complementary Controls

The following FINRA requirements are outside the protocol's scope:

- **Reg S-P** Customer data privacy -- application-level data handling
- **Reg S-ID** Identity theft prevention -- application-level identity management
- **Rule 4370** Business continuity planning -- organizational
- **WORM storage enforcement** -- Capsule provides tamper-evidence at the protocol layer; WORM storage enforcement is a deployment-level concern (e.g., S3 Object Lock, immutable storage)

---

[Back to Compliance Overview](./README.md)
