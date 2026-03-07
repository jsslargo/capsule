# Copyright 2026 Quantum Pipes Technologies, LLC
# SPDX-License-Identifier: Apache-2.0

"""
Shared test fixtures for the Capsule test suite.

Provides temporary storage and seal instances that are isolated per test.
"""

from pathlib import Path

import pytest

from qp_capsule.chain import CapsuleChain
from qp_capsule.seal import Seal
from qp_capsule.storage import CapsuleStorage


@pytest.fixture
async def temp_storage(tmp_path: Path):
    """Create temporary SQLite storage for testing. Closes on teardown."""
    db_path = tmp_path / "test_capsules.db"
    storage = CapsuleStorage(db_path=db_path)
    yield storage
    await storage.close()


@pytest.fixture
def temp_seal(tmp_path: Path) -> Seal:
    """Create temporary seal with isolated test key."""
    key_path = tmp_path / "test_key"
    return Seal(key_path=key_path)


@pytest.fixture
async def temp_chain(temp_storage: CapsuleStorage):
    """Create a chain with temporary storage."""
    yield CapsuleChain(storage=temp_storage)
