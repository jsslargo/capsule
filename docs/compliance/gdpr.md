# GDPR

The General Data Protection Regulation (EU 2016/679) governs how organizations process personal data of EU residents. Capsule provides protocol-level capabilities that support integrity, accountability, records of processing, and data protection by design.

---

## Data Protection Principles (Article 5)

| Principle | Article | How Capsule Addresses It |
|---|---|---|
| **Integrity and confidentiality** | Art. 5(1)(f) | SHA3-256 hash + Ed25519 signature seals every Capsule. Hash chain detects modification, deletion, or insertion. |
| **Accountability** | Art. 5(2) | Every AI action produces a Capsule with 6 auditable sections. Authority section records who approved the action. Chain provides a verifiable audit trail. |

## Data Protection by Design (Article 25)

| Requirement | How Capsule Addresses It |
|---|---|
| Technical measures at design time | Cryptographic sealing is built into the protocol, not added as an afterthought. Every Capsule is sealed at the moment of action. |
| Audit without content exposure | `reasoning.prompt_hash` records the SHA3-256 hash of a prompt for audit purposes without storing the prompt content itself. |
| Structured minimization | The 6-section model separates concerns: auditors reviewing authority need not access execution details. `capsule://` URI fragments address individual sections. |

## Records of Processing Activities (Article 30)

| Requirement | How Capsule Addresses It |
|---|---|
| Maintain records of processing | Each Capsule is a structured record of a processing activity: what triggered it, what data context existed, why the AI decided to act, who authorized it, what tools were called, and what the outcome was. |
| Categories of processing | `CapsuleType` categorizes processing activities: agent, tool, system, kill, workflow, chat, vault, auth. |
| Description of technical measures | Capsule metadata records cryptographic algorithms (SHA3-256, Ed25519, ML-DSA-65), key fingerprints, and chain position. |

## Security of Processing (Article 32)

| Measure | How Capsule Addresses It |
|---|---|
| Integrity of processing | SHA3-256 content hash detects any modification. Ed25519 signature authenticates the record. Hash chain detects deletion or insertion. |
| Ability to restore availability | Capsules are self-verifying: given the content and the hash, any party can confirm integrity without trusting the storage layer. |
| Process for regular testing | `chain.verify()` provides one-call integrity verification. `seal.verify(capsule)` tests individual records. Both can run on any schedule. |

## Data Protection Impact Assessment (Article 35)

| Requirement | How Capsule Addresses It |
|---|---|
| Systematic description of processing | Reasoning section captures analysis, options considered, and rationale before execution. |
| Assessment of necessity | `reasoning.confidence` records the AI's assessed confidence (0.0 to 1.0). `ReasoningOption.rejection_reason` documents why alternatives were not chosen. |
| Assessment of risks | `ReasoningOption.risks` captures identified risks per option. `ReasoningOption.estimated_impact` records scope and severity. |

## Complementary Controls

The following GDPR requirements are outside the protocol's scope and must be addressed by the deployment environment:

- **Art. 5(1)(a)** Lawfulness, fairness, transparency -- legal basis for processing
- **Art. 5(1)(b)** Purpose limitation -- organizational data governance
- **Art. 5(1)(e)** Storage limitation -- retention policies at the application layer
- **Art. 15-22** Data subject rights (access, erasure, portability) -- application-level data management
- **Art. 32** Encryption at rest/in transit -- storage and transport layer encryption

---

[Back to Compliance Overview](./README.md)
