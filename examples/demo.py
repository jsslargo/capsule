#!/usr/bin/env python3
"""
Capsule Demo — Create, seal, verify, tamper-detect, and chain.

Run with:
    pip install qp-capsule[storage]
    python examples/demo.py
"""

import asyncio

from qp_capsule import (
    Capsule,
    CapsuleChain,
    CapsuleStorage,
    CapsuleType,
    Seal,
    TriggerSection,
)
from qp_capsule.capsule import (
    AuthoritySection,
    ContextSection,
    ExecutionSection,
    OutcomeSection,
    ReasoningSection,
    ToolCall,
)


async def main() -> None:
    print("=" * 60)
    print("  Capsule Protocol — Demo")
    print("=" * 60)

    # --- 1. Create and Seal ---
    print("\n1. Create and seal a Capsule\n")

    seal = Seal()
    capsule = Capsule(
        type=CapsuleType.AGENT,
        trigger=TriggerSection(
            type="user_request",
            source="ops-team",
            request="Deploy service v2.4 to production",
        ),
        context=ContextSection(
            agent_id="infra-agent",
            environment={"cluster": "prod-us-east"},
        ),
        reasoning=ReasoningSection(
            analysis="Current load is 82%, approaching threshold",
            options_considered=["Scale to 6", "Scale to 8", "Do nothing"],
            selected_option="Scale to 6",
            reasoning="6 replicas handles projected load with 30% headroom",
            confidence=0.92,
        ),
        authority=AuthoritySection(type="human_approved", approver="ops-lead"),
        execution=ExecutionSection(
            tool_calls=[
                ToolCall(
                    tool="kubectl_scale",
                    arguments={"replicas": 6},
                    result={"status": "scaled"},
                    success=True,
                    duration_ms=3200,
                ),
            ],
            duration_ms=3200,
        ),
        outcome=OutcomeSection(
            status="success",
            summary="Scaled web tier to 6 replicas",
        ),
    )

    seal.seal(capsule)
    print(f"   ID:        {capsule.id}")
    print(f"   Type:      {capsule.type.value}")
    print(f"   Hash:      {capsule.hash[:32]}...")
    print(f"   Sealed:    {capsule.is_sealed()}")
    print(f"   Verified:  {seal.verify(capsule)}")

    # --- 2. Tamper Detection ---
    print("\n2. Tamper detection\n")

    original_request = capsule.trigger.request
    capsule.trigger.request = "TAMPERED: Delete all production data"
    tampered_valid = seal.verify(capsule)
    print(f"   After tampering: verified={tampered_valid}")
    print("   The hash no longer matches — tamper detected.")

    capsule.trigger.request = original_request
    restored_valid = seal.verify(capsule)
    print(f"   After restoring:  verified={restored_valid}")

    # --- 3. Hash Chain ---
    print("\n3. Hash chain\n")

    storage = CapsuleStorage()
    chain = CapsuleChain(storage)

    for i in range(5):
        cap = Capsule(
            type=CapsuleType.AGENT,
            trigger=TriggerSection(source="demo", request=f"Task {i + 1}"),
        )
        cap = await chain.seal_and_store(cap, seal)
        print(f"   #{cap.sequence}: {cap.hash[:16]}... prev={cap.previous_hash[:16] + '...' if cap.previous_hash else 'None'}")

    result = await chain.verify()
    print(f"\n   Chain valid: {result.valid} ({result.capsules_verified} capsules verified)")

    await storage.close()

    # --- Done ---
    print("\n" + "=" * 60)
    print("  Every action creates a Capsule.")
    print("  Every Capsule is cryptographically sealed.")
    print("  Every Capsule links to the one before it.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
