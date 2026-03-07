"""
Tests for session-based conversation tracking.

PRIORITY: Session tracking is critical for conversation integrity.
          If sessions leak, user conversations could mix — a privacy disaster.

STRESSOR: Tests apply stress via multiple concurrent sessions, random IDs,
          and edge cases to ensure isolation holds under pressure.

SIGNAL: Each test name describes exactly what behavior is verified.
        Failures are self-diagnosing with full context.
"""

import uuid
from datetime import UTC, datetime

import pytest

from qp_capsule.capsule import (
    Capsule,
    CapsuleType,
    ContextSection,
    OutcomeSection,
    ReasoningSection,
    TriggerSection,
)

# =============================================================================
# FIXTURES
# =============================================================================


def create_chat_capsule(
    session_id: str,
    request: str = "test question",
    turn: int = 1,
) -> Capsule:
    """
    Helper to create a CHAT capsule with session tracking.

    This mirrors how the CLI creates conversation capsules.
    """
    return Capsule(
        type=CapsuleType.CHAT,
        trigger=TriggerSection(
            type="user_request",
            source="cli",
            timestamp=datetime.now(UTC),
            request=request,
        ),
        context=ContextSection(
            agent_id="quantumpipes-cli",
            session_id=session_id,
            environment={
                "model": "test-model",
                "turn": turn,
                "history_length": turn * 2,
            },
        ),
        reasoning=ReasoningSection(
            options_considered=["respond"],
            selected_option="respond",
            reasoning="User asked a question",
            confidence=0.9,
        ),
        outcome=OutcomeSection(
            status="success",
            result=f"Response to: {request}",
        ),
    )


# =============================================================================
# IMPORTANT PROBLEM: Session Query Functionality
# "If this fails, we can't retrieve conversation history at all"
# =============================================================================


class TestListBySessionBasicFunctionality:
    """
    Basic functionality tests for list_by_session.

    These tests verify the fundamental contract:
    - Returns capsules matching the session
    - Returns them in chronological order
    - Returns empty list for unknown sessions
    """

    @pytest.mark.asyncio
    async def test_list_by_session_returns_matching_capsules(self, temp_storage, temp_seal):
        """
        list_by_session returns all capsules with the given session_id.

        SIGNAL: If this fails, session tracking is fundamentally broken.
        """
        session_id = str(uuid.uuid4())

        # Create 3 capsules in the same session
        for turn in range(1, 4):
            capsule = create_chat_capsule(session_id, f"Question {turn}", turn)
            temp_seal.seal(capsule)
            await temp_storage.store(capsule)

        # Query by session
        results = await temp_storage.list_by_session(session_id)

        assert len(results) == 3, (
            f"Expected 3 capsules for session {session_id[:8]}, "
            f"got {len(results)}. "
            f"Session tracking may not be storing session_id correctly."
        )

    @pytest.mark.asyncio
    async def test_list_by_session_returns_chronological_order(self, temp_storage, temp_seal):
        """
        list_by_session returns capsules in chronological order (oldest first).

        SIGNAL: Conversation history must be in order for context to make sense.
        """
        session_id = str(uuid.uuid4())

        # Create capsules with distinct questions
        questions = ["First question", "Second question", "Third question"]
        for turn, question in enumerate(questions, 1):
            capsule = create_chat_capsule(session_id, question, turn)
            temp_seal.seal(capsule)
            await temp_storage.store(capsule)

        results = await temp_storage.list_by_session(session_id)

        # Verify order by checking questions
        actual_questions = [cap.trigger.request for cap in results]
        assert actual_questions == questions, (
            f"Expected chronological order: {questions}, "
            f"got: {actual_questions}. "
            f"Conversation history would be out of order!"
        )

    @pytest.mark.asyncio
    async def test_list_by_session_returns_empty_for_unknown_session(self, temp_storage):
        """
        list_by_session returns empty list for non-existent session.

        SIGNAL: Unknown sessions should return empty, not error.
        """
        unknown_session = str(uuid.uuid4())

        results = await temp_storage.list_by_session(unknown_session)

        assert results == [] or len(results) == 0, (
            f"Expected empty list for unknown session {unknown_session[:8]}, "
            f"got {len(results)} results. "
            f"This could leak other users' data!"
        )


# =============================================================================
# CRITICAL: Session Isolation
# "If sessions leak, users see each other's conversations — privacy disaster"
# =============================================================================


class TestSessionIsolation:
    """
    Tests that sessions are strictly isolated from each other.

    This is the most critical property of session tracking.
    A leak here is a privacy violation.
    """

    @pytest.mark.asyncio
    async def test_sessions_are_completely_isolated(self, temp_storage, temp_seal):
        """
        Capsules from different sessions never mix.

        SIGNAL: If this fails, users could see each other's conversations.
        """
        session_a = str(uuid.uuid4())
        session_b = str(uuid.uuid4())

        # Create capsules in session A
        for turn in range(1, 4):
            capsule = create_chat_capsule(session_a, f"Session A Turn {turn}", turn)
            temp_seal.seal(capsule)
            await temp_storage.store(capsule)

        # Create capsules in session B
        for turn in range(1, 6):  # Different count to make detection easier
            capsule = create_chat_capsule(session_b, f"Session B Turn {turn}", turn)
            temp_seal.seal(capsule)
            await temp_storage.store(capsule)

        # Query each session
        results_a = await temp_storage.list_by_session(session_a)
        results_b = await temp_storage.list_by_session(session_b)

        # Verify isolation
        assert len(results_a) == 3, (
            f"Session A should have 3 capsules, got {len(results_a)}. Sessions may be leaking!"
        )
        assert len(results_b) == 5, (
            f"Session B should have 5 capsules, got {len(results_b)}. Sessions may be leaking!"
        )

        # Verify no cross-contamination
        for capsule in results_a:
            assert capsule.context.session_id == session_a, (
                f"Session A query returned capsule with session_id "
                f"{capsule.context.session_id[:8]}, expected {session_a[:8]}. "
                f"PRIVACY VIOLATION: Sessions are leaking!"
            )

        for capsule in results_b:
            assert capsule.context.session_id == session_b, (
                f"Session B query returned capsule with session_id "
                f"{capsule.context.session_id[:8]}, expected {session_b[:8]}. "
                f"PRIVACY VIOLATION: Sessions are leaking!"
            )

    @pytest.mark.asyncio
    async def test_many_concurrent_sessions_stay_isolated(self, temp_storage, temp_seal):
        """
        Stress test: many sessions created concurrently remain isolated.

        ANTIFRAGILE: Random session creation order shouldn't matter.
        """
        num_sessions = 10
        capsules_per_session = 5

        sessions = [str(uuid.uuid4()) for _ in range(num_sessions)]

        # Create capsules for all sessions (interleaved, not sequential)
        for turn in range(1, capsules_per_session + 1):
            for session_id in sessions:
                capsule = create_chat_capsule(
                    session_id,
                    f"Turn {turn} in session {session_id[:8]}",
                    turn,
                )
                temp_seal.seal(capsule)
                await temp_storage.store(capsule)

        # Verify each session has exactly its capsules
        for session_id in sessions:
            results = await temp_storage.list_by_session(session_id)

            assert len(results) == capsules_per_session, (
                f"Session {session_id[:8]} should have {capsules_per_session} "
                f"capsules, got {len(results)}. "
                f"Sessions leaked under interleaved creation stress."
            )

            # Verify all belong to this session
            for capsule in results:
                assert capsule.context.session_id == session_id, (
                    f"Session {session_id[:8]} query returned wrong capsule. "
                    f"Got session {capsule.context.session_id[:8]}."
                )


# =============================================================================
# EDGE CASES: What happens at the boundaries?
# =============================================================================


class TestSessionEdgeCases:
    """
    Edge case tests for session tracking.

    These test the boundaries where bugs often hide.
    """

    @pytest.mark.asyncio
    async def test_single_capsule_session(self, temp_storage, temp_seal):
        """
        Session with only one capsule is retrievable.

        SIGNAL: New conversations (single turn) should work.
        """
        session_id = str(uuid.uuid4())

        capsule = create_chat_capsule(session_id, "Only question", 1)
        temp_seal.seal(capsule)
        await temp_storage.store(capsule)

        results = await temp_storage.list_by_session(session_id)

        assert len(results) == 1, (
            f"Single-capsule session should return 1 capsule, got {len(results)}"
        )
        assert results[0].trigger.request == "Only question"

    @pytest.mark.asyncio
    async def test_empty_session_id_handled_gracefully(self, temp_storage):
        """
        Empty session ID returns empty list, not error.

        SIGNAL: Edge case — shouldn't crash, should return nothing.
        """
        results = await temp_storage.list_by_session("")

        assert results == [] or len(results) == 0, (
            f"Empty session ID should return empty list, got {len(results)} results"
        )

    @pytest.mark.asyncio
    async def test_capsules_without_session_id_excluded(self, temp_storage, temp_seal):
        """
        Capsules with None session_id are not returned by session queries.

        SIGNAL: Non-conversation capsules shouldn't pollute session results.
        """
        session_id = str(uuid.uuid4())

        # Create capsule WITH session_id
        capsule_with_session = create_chat_capsule(session_id, "Has session", 1)
        temp_seal.seal(capsule_with_session)
        await temp_storage.store(capsule_with_session)

        # Create capsule WITHOUT session_id (e.g., one-shot ask)
        capsule_no_session = Capsule(
            type=CapsuleType.AGENT,
            trigger=TriggerSection(request="No session"),
            context=ContextSection(
                agent_id="test",
                session_id=None,  # Explicitly no session
            ),
            reasoning=ReasoningSection(
                options_considered=["respond"],
                selected_option="respond",
            ),
            outcome=OutcomeSection(status="success", result="done"),
        )
        temp_seal.seal(capsule_no_session)
        await temp_storage.store(capsule_no_session)

        results = await temp_storage.list_by_session(session_id)

        assert len(results) == 1, (
            f"Session query should return only session capsules. "
            f"Expected 1, got {len(results)}. "
            f"Non-session capsule may have leaked in."
        )
        assert results[0].context.session_id == session_id

    @pytest.mark.asyncio
    async def test_session_id_is_case_sensitive(self, temp_storage, temp_seal):
        """
        Session IDs are case-sensitive (UUIDs should match exactly).

        SIGNAL: "ABC123" and "abc123" are different sessions.
        """
        session_lower = "test-session-abc123"
        session_upper = "TEST-SESSION-ABC123"

        # Create capsule with lowercase session
        capsule = create_chat_capsule(session_lower, "Lowercase session", 1)
        temp_seal.seal(capsule)
        await temp_storage.store(capsule)

        # Query with uppercase should return nothing
        results = await temp_storage.list_by_session(session_upper)

        assert len(results) == 0, (
            f"Query with different case returned {len(results)} results. "
            f"Session IDs must be case-sensitive!"
        )


# =============================================================================
# ANTIFRAGILE: Property-Based / Stress Tests
# =============================================================================


class TestSessionStress:
    """
    Stress tests that make the system stronger.

    These tests apply random stress to find edge cases.
    """

    @pytest.mark.asyncio
    async def test_long_conversation_retrieval(self, temp_storage, temp_seal):
        """
        Long conversation (100 turns) retrieves correctly in order.

        ANTIFRAGILE: System should handle lengthy conversations.
        """
        session_id = str(uuid.uuid4())
        num_turns = 100

        # Create a long conversation
        for turn in range(1, num_turns + 1):
            capsule = create_chat_capsule(session_id, f"Turn {turn}", turn)
            temp_seal.seal(capsule)
            await temp_storage.store(capsule)

        results = await temp_storage.list_by_session(session_id)

        assert len(results) == num_turns, (
            f"Expected {num_turns} capsules for long conversation, got {len(results)}"
        )

        # Verify order is preserved
        for i, capsule in enumerate(results, 1):
            expected_turn = capsule.context.environment.get("turn")
            assert expected_turn == i, (
                f"Turn {i} has wrong turn number in environment: {expected_turn}. "
                f"Order may be corrupted in long conversations."
            )

    @pytest.mark.asyncio
    async def test_uuid_session_ids_dont_collide(self, temp_storage, temp_seal):
        """
        Property: UUIDs should never collide in practice.

        Creates many sessions to verify no accidental collisions.
        """
        num_sessions = 50

        sessions = [str(uuid.uuid4()) for _ in range(num_sessions)]

        # Verify all unique
        assert len(set(sessions)) == num_sessions, "UUID collision detected!"

        # Create one capsule per session
        for session_id in sessions:
            capsule = create_chat_capsule(session_id, "Single turn", 1)
            temp_seal.seal(capsule)
            await temp_storage.store(capsule)

        # Verify each session has exactly one capsule
        for session_id in sessions:
            results = await temp_storage.list_by_session(session_id)
            assert len(results) == 1, (
                f"Session {session_id[:8]} has {len(results)} capsules. "
                f"Possible UUID collision or session leak."
            )


# =============================================================================
# INTEGRATION: End-to-End Conversation Flow
# =============================================================================


class TestConversationFlow:
    """
    Integration tests for the full conversation flow.

    These simulate how the CLI actually uses session tracking.
    """

    @pytest.mark.asyncio
    async def test_conversation_capsules_contain_full_context(self, temp_storage, temp_seal):
        """
        Each capsule in a conversation contains full audit context.

        SIGNAL: Verifies capsules have everything needed for replay.
        """
        session_id = str(uuid.uuid4())

        # Simulate a 3-turn conversation
        conversation = [
            ("What is Python?", "Python is a programming language."),
            ("How do I install it?", "Download from python.org."),
            ("What about on Mac?", "Mac has Python pre-installed."),
        ]

        for turn, (question, response) in enumerate(conversation, 1):
            capsule = Capsule(
                type=CapsuleType.CHAT,
                trigger=TriggerSection(
                    type="user_request",
                    source="cli",
                    timestamp=datetime.now(UTC),
                    request=question,
                ),
                context=ContextSection(
                    agent_id="quantumpipes-cli",
                    session_id=session_id,
                    environment={
                        "model": "llama3.2",
                        "turn": turn,
                        "history_length": turn * 2,
                    },
                ),
                reasoning=ReasoningSection(
                    options_considered=["respond to user"],
                    selected_option="respond to user",
                    reasoning="User asked a question in conversation",
                    confidence=0.95,
                ),
                outcome=OutcomeSection(
                    status="success",
                    result=response,
                ),
            )
            temp_seal.seal(capsule)
            await temp_storage.store(capsule)

        # Retrieve and verify full context
        results = await temp_storage.list_by_session(session_id)

        for i, capsule in enumerate(results):
            # Verify type
            assert capsule.type == CapsuleType.CHAT, f"Turn {i + 1} has wrong type: {capsule.type}"

            # Verify session linkage
            assert capsule.context.session_id == session_id, f"Turn {i + 1} has wrong session_id"

            # Verify turn tracking
            assert capsule.context.environment.get("turn") == i + 1, (
                f"Turn {i + 1} has wrong turn number in environment"
            )

            # Verify question preserved
            expected_question = conversation[i][0]
            assert capsule.trigger.request == expected_question, (
                f"Turn {i + 1} question mismatch. "
                f"Expected: {expected_question}, "
                f"Got: {capsule.trigger.request}"
            )

            # Verify response preserved
            expected_response = conversation[i][1]
            assert capsule.outcome.result == expected_response, (
                f"Turn {i + 1} response mismatch. "
                f"Expected: {expected_response}, "
                f"Got: {capsule.outcome.result}"
            )

            # Verify sealed (audit requirement)
            assert capsule.is_sealed(), (
                f"Turn {i + 1} capsule is not sealed! Conversation history must be tamper-evident."
            )

    @pytest.mark.asyncio
    async def test_new_session_starts_fresh(self, temp_storage, temp_seal):
        """
        Starting a new session (/new command) gives fresh empty history.

        SIGNAL: User can start over without old context.
        """
        old_session = str(uuid.uuid4())
        new_session = str(uuid.uuid4())

        # Create conversation in old session
        for turn in range(1, 6):
            capsule = create_chat_capsule(old_session, f"Old turn {turn}", turn)
            temp_seal.seal(capsule)
            await temp_storage.store(capsule)

        # New session should be empty
        new_results = await temp_storage.list_by_session(new_session)

        assert len(new_results) == 0, (
            f"New session should be empty, got {len(new_results)} capsules. "
            f"Old session may be leaking to new session."
        )

        # Old session still has its capsules
        old_results = await temp_storage.list_by_session(old_session)

        assert len(old_results) == 5, (
            f"Old session should still have 5 capsules, got {len(old_results)}"
        )
