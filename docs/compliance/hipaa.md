# HIPAA Security Rule

The HIPAA Security Rule (45 CFR Part 164, Subparts A and C) establishes standards for protecting electronic Protected Health Information (ePHI). Capsule provides protocol-level capabilities that support technical safeguards for integrity, audit controls, and authentication.

HIPAA has no formal certification. Compliance is demonstrated through risk analysis, attestation, and audit readiness.

---

## Technical Safeguards (§164.312)

| Standard | Specification | How Capsule Addresses It |
|---|---|---|
| **§164.312(b)** | Audit controls | Every AI action produces a sealed Capsule with 6 auditable sections. `chain.verify()` confirms the complete audit trail is intact. Hash chain provides tamper-evident temporal ordering. |
| **§164.312(c)(1)** | Integrity | SHA3-256 hash + Ed25519 signature on every Capsule. Any modification to content changes the hash and invalidates the signature. `seal.verify(capsule)` detects tampering. |
| **§164.312(c)(2)** | Mechanism to authenticate ePHI | Ed25519 digital signatures authenticate each record. `signed_by` identifies the signing key. `verify_with_key()` enables third-party verification of record authenticity. |
| **§164.312(e)(2)** | Integrity controls (transmission) | Capsule hashes are self-verifying: recompute SHA3-256 from content and compare to stored hash. Verification is independent of transport layer. |

## Administrative Safeguards (§164.308)

| Standard | Specification | How Capsule Addresses It |
|---|---|---|
| **§164.308(a)(1)(ii)(D)** | Information system activity review | Capsules are queryable by type, time range, tenant, and session. Chain provides complete operational history for review. |
| **§164.308(a)(5)(ii)(C)** | Log-in monitoring | `CapsuleType.AUTH` records authentication events with authority chain (e.g., MFA escalation). |
| **§164.308(a)(6)(ii)** | Response and reporting | Capsules contain full context (Trigger, Context, Reasoning, Authority, Execution, Outcome) for incident investigation. Kill switch Capsules record intervention events. |

## Complementary Controls

The following HIPAA requirements are outside the protocol's scope and must be addressed by the deployment environment:

- **§164.312(a)(1)** Access control -- application-level authentication and authorization
- **§164.312(d)** Person or entity authentication -- user identity management
- **§164.312(e)(1)** Transmission security (encryption) -- TLS at the transport layer
- **§164.308(a)(3)** Workforce security -- organizational HR and access policies

---

[Back to Compliance Overview](./README.md)
