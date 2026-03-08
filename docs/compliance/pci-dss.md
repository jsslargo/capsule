# PCI DSS v4.0

The Payment Card Industry Data Security Standard (PCI DSS) v4.0.1 establishes security requirements for organizations that store, process, or transmit cardholder data. Capsule provides protocol-level capabilities that support audit logging, integrity verification, and change detection requirements.

---

## Requirement 10: Log and Monitor All Access

| Sub-Requirement | Title | How Capsule Addresses It |
|---|---|---|
| **10.2** | Audit logs record actions | Each Capsule records: who triggered the action (`trigger.user_id`, `trigger.source`), event type (`CapsuleType`), timestamp (`trigger.timestamp`, `signed_at`), success/failure (`outcome.status`), and affected data (`execution.tool_calls`, `outcome.side_effects`). |
| **10.3** | Access to audit logs restricted and protected from alteration | SHA3-256 hash + Ed25519 signature on every Capsule. Hash chain detects any modification, deletion, or insertion. `chain.verify()` confirms the complete trail is intact. |
| **10.4.1.1** | Automated audit log reviews | Capsules are machine-readable and queryable by type, time range, status, and tenant. Structured 6-section format enables automated analysis. |
| **10.7.2** | Detection of failures of critical security control systems | `outcome.status = "failure"` and `outcome.status = "blocked"` record control failures. Kill switch Capsules (`CapsuleType.KILL`) record system-level interventions. |
| **10.7.3** | Response to failures of critical security control systems | Capsules provide full context (Trigger, Context, Reasoning, Authority, Execution, Outcome) for incident investigation and response. |

## Requirement 11: Test Security Regularly

| Sub-Requirement | Title | How Capsule Addresses It |
|---|---|---|
| **11.5** | Change-detection mechanisms | `chain.verify()` detects unauthorized changes to any record. SHA3-256 hash comparison identifies which record was modified. |
| **11.6** | Detect and prevent tampering | Hash chain is tamper-evident by construction: modifying any Capsule changes its hash, which invalidates every subsequent Capsule's `previous_hash` link. |

## Complementary Controls

The following PCI DSS requirements are outside the protocol's scope:

- **Req 1-2** Network security and secure configurations -- infrastructure-level
- **Req 3-4** Cardholder data encryption at rest and in transit -- application/transport layer
- **Req 5** Malware protection -- endpoint security
- **Req 6** Secure development -- organizational SDLC (though Capsule itself is developed with 100% test coverage and strict linting)
- **Req 7-9** Access control, physical security, personnel -- organizational controls

---

[Back to Compliance Overview](./README.md)
