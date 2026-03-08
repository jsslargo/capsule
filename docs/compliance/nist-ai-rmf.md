# NIST AI Risk Management Framework (AI RMF 1.0)

The AI RMF organizes AI risk management into four functions: GOVERN, MAP, MEASURE, MANAGE.

---

## GOVERN

*Cultivate and implement a culture of AI risk management.*

| Practice | How Capsule Supports It |
|---|---|
| Establish accountability structures | Authority section records who approved each action (`autonomous`, `human_approved`, `policy`, `escalated`) |
| Document AI decision-making processes | Reasoning section captures analysis, options considered, selected option, and confidence before execution |
| Maintain audit trails | Hash-chained Capsules provide an immutable, tamper-evident record of every AI action |

## MAP

*Contextualize AI risks.*

| Practice | How Capsule Supports It |
|---|---|
| Identify AI system components | Capsule Types map to system components: AGENT, TOOL, WORKFLOW, CHAT, VAULT |
| Document operating context | Context section records agent_id, session_id, and environment state at time of action |
| Track data lineage | Execution section records tool calls with arguments, results, and errors |

## MEASURE

*Analyze, assess, and track AI risks.*

| Practice | How Capsule Supports It |
|---|---|
| Quantify model confidence | `reasoning.confidence` (0.0 to 1.0) records model-reported confidence per action |
| Track performance metrics | `outcome.metrics` captures duration, token usage, cost, and custom metrics |
| Monitor for anomalies | `outcome.status` values (`success`, `failure`, `partial`, `blocked`) enable monitoring |

## MANAGE

*Prioritize and act on AI risks.*

| Practice | How Capsule Supports It |
|---|---|
| Implement kill switches | `CapsuleType.KILL` records kill switch activations with authority chain |
| Enable human oversight | Authority section's `escalation_reason` and `approver` fields document human-in-the-loop decisions |
| Verify system integrity | `chain.verify()` provides one-call integrity verification of the entire audit trail |

---

[Back to Compliance Overview](./README.md)
