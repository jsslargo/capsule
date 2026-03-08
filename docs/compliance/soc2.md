# SOC 2 Trust Services Criteria

SOC 2 Type II audit mappings for the Security and Availability trust service categories.

---

| Criterion | Title | How Capsule Addresses It |
|---|---|---|
| **CC6.1** | Logical access security | Ed25519 key-based signing; key files restricted to owner (0600 permissions) |
| **CC7.2** | System monitoring | Every AI action produces a Capsule; chain provides complete operational history |
| **CC7.3** | Detection of unauthorized changes | `chain.verify()` detects any modification, deletion, or insertion |
| **CC7.4** | Incident response data | Capsules contain full context (6 sections) for post-incident analysis |
| **CC8.1** | Change management | Each Capsule records what changed (`outcome.side_effects`), who approved it (`authority`), and why (`reasoning`) |

---

[Back to Compliance Overview](./README.md)
