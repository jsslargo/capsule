"""Tests for Capsule.create() factory method."""

from uuid import uuid4

from qp_capsule.capsule import (
    AuthoritySection,
    Capsule,
    CapsuleType,
    ContextSection,
    ExecutionSection,
    OutcomeSection,
    ReasoningSection,
    TriggerSection,
)
from qp_capsule.seal import Seal


class TestCapsuleCreate:
    """Tests for Capsule.create() dict-based factory."""

    def test_create_minimal(self):
        """Capsule.create() with defaults produces valid capsule with default sections."""
        capsule = Capsule.create(capsule_type=CapsuleType.AGENT)

        assert capsule.type == CapsuleType.AGENT
        assert capsule.domain == "agents"
        assert isinstance(capsule.trigger, TriggerSection)
        assert isinstance(capsule.context, ContextSection)
        assert isinstance(capsule.reasoning, ReasoningSection)
        assert isinstance(capsule.authority, AuthoritySection)
        assert isinstance(capsule.execution, ExecutionSection)
        assert isinstance(capsule.outcome, OutcomeSection)

    def test_create_with_all_sections(self):
        """All 6 dicts populated, verify each section has correct values."""
        capsule = Capsule.create(
            capsule_type=CapsuleType.TOOL,
            trigger={"source": "conductor", "type": "system", "request": "deploy"},
            context={"agent_id": "agent-1", "session_id": "sess-1"},
            reasoning={"confidence": 0.95, "reasoning": "best approach"},
            authority={"type": "human_approved", "approver": "admin"},
            execution={"duration_ms": 500},
            outcome={"status": "success", "summary": "deployed"},
        )

        assert capsule.type == CapsuleType.TOOL
        assert capsule.trigger.source == "conductor"
        assert capsule.trigger.type == "system"
        assert capsule.trigger.request == "deploy"
        assert capsule.context.agent_id == "agent-1"
        assert capsule.context.session_id == "sess-1"
        assert capsule.reasoning.confidence == 0.95
        assert capsule.reasoning.reasoning == "best approach"
        assert capsule.authority.type == "human_approved"
        assert capsule.authority.approver == "admin"
        assert capsule.execution.duration_ms == 500
        assert capsule.outcome.status == "success"
        assert capsule.outcome.summary == "deployed"

    def test_create_partial(self):
        """Some sections provided, others default."""
        capsule = Capsule.create(
            trigger={"source": "test"},
            outcome={"status": "failure", "error": "boom"},
        )

        assert capsule.trigger.source == "test"
        assert capsule.outcome.status == "failure"
        assert capsule.outcome.error == "boom"
        assert capsule.context.agent_id == ""
        assert capsule.reasoning.confidence == 0.0

    def test_create_roundtrip(self):
        """create -> seal -> to_dict -> from_dict -> verify equal."""
        capsule = Capsule.create(
            capsule_type=CapsuleType.AGENT,
            trigger={"source": "roundtrip-test", "request": "verify"},
            context={"agent_id": "test-agent"},
        )

        seal = Seal()
        sealed = seal.seal(capsule)
        data = sealed.to_dict()
        restored = Capsule.from_dict(data)

        assert restored.id == capsule.id
        assert restored.trigger.source == "roundtrip-test"
        assert restored.trigger.request == "verify"
        assert restored.context.agent_id == "test-agent"

    def test_create_unknown_keys_ignored(self):
        """Dict with extra keys doesn't raise."""
        capsule = Capsule.create(
            trigger={
                "source": "test",
                "unknown_key": "should be ignored",
                "another_fake": 42,
            },
        )

        assert capsule.trigger.source == "test"
        assert not hasattr(capsule.trigger, "unknown_key")

    def test_create_with_domain(self):
        """domain='vault' sets capsule.domain correctly."""
        capsule = Capsule.create(domain="vault")
        assert capsule.domain == "vault"

    def test_create_with_parent_id(self):
        """parent_id links to parent capsule."""
        parent_id = uuid4()
        capsule = Capsule.create(parent_id=parent_id)
        assert capsule.parent_id == parent_id


class TestCapsuleCreateEdgeCases:
    """Edge cases and error paths for Capsule.create()."""

    def test_create_not_sealed(self):
        """Factory produces unsealed capsule — must seal before storing."""
        capsule = Capsule.create(capsule_type=CapsuleType.AGENT)
        assert not capsule.is_sealed()
        assert capsule.hash == ""
        assert capsule.signature == ""

    def test_create_empty_dicts_same_as_none(self):
        """Empty dict {} produces same defaults as None."""
        from_none = Capsule.create()
        from_empty = Capsule.create(
            trigger={}, context={}, reasoning={}, authority={}, execution={}, outcome={}
        )

        assert from_none.trigger.type == from_empty.trigger.type
        assert from_none.context.agent_id == from_empty.context.agent_id
        assert from_none.reasoning.confidence == from_empty.reasoning.confidence
        assert from_none.outcome.status == from_empty.outcome.status

    def test_create_all_capsule_types(self):
        """Every CapsuleType value works with create()."""
        for ct in CapsuleType:
            capsule = Capsule.create(capsule_type=ct)
            assert capsule.type == ct

    def test_create_preserves_uuid_uniqueness(self):
        """Each create() produces a unique capsule ID."""
        ids = {Capsule.create().id for _ in range(50)}
        assert len(ids) == 50

    def test_create_default_type_is_agent(self):
        """No type argument defaults to AGENT."""
        capsule = Capsule.create()
        assert capsule.type == CapsuleType.AGENT

    def test_create_unknown_keys_in_every_section(self):
        """Unknown keys silently dropped across all 6 sections."""
        capsule = Capsule.create(
            trigger={"source": "a", "fake": 1},
            context={"agent_id": "b", "nope": 2},
            reasoning={"confidence": 0.5, "bad": 3},
            authority={"type": "autonomous", "x": 4},
            execution={"duration_ms": 0, "y": 5},
            outcome={"status": "success", "z": 6},
        )
        assert capsule.trigger.source == "a"
        assert capsule.context.agent_id == "b"
        assert capsule.reasoning.confidence == 0.5
        assert capsule.authority.type == "autonomous"
        assert capsule.execution.duration_ms == 0
        assert capsule.outcome.status == "success"
