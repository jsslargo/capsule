# Copyright 2026 Quantum Pipes Technologies, LLC
# SPDX-License-Identifier: Apache-2.0
#
# Patent Pending — See PATENTS.md for details.
# Licensed under the Apache License, Version 2.0 with patent grant (Section 3).

"""
Protocol: The storage contract.

Defines the interface that all Capsule storage backends must satisfy.
CapsuleChain depends on this contract — if a backend doesn't implement it,
chain verification will fail silently. The Protocol makes that impossible.

Both CapsuleStorage (SQLite) and PostgresCapsuleStorage satisfy this protocol.
Third-party backends can implement it to plug into the chain.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol, runtime_checkable
from uuid import UUID

if TYPE_CHECKING:
    from qp_capsule.capsule import Capsule, CapsuleType


@runtime_checkable
class CapsuleStorageProtocol(Protocol):
    """
    Formal contract for Capsule storage backends.

    Any storage backend used with CapsuleChain must implement this interface.
    Both CapsuleStorage (SQLite) and PostgresCapsuleStorage satisfy this protocol.

    Methods required by CapsuleChain:
        - store: Persist a sealed Capsule
        - get_latest: Retrieve the chain head
        - get_all_ordered: Retrieve all Capsules in sequence order
        - list: Paginated retrieval with optional filtering

    Additional methods for general storage consumers:
        - get: Retrieve a single Capsule by ID
        - count: Count Capsules with optional filtering
        - close: Release backend resources
    """

    async def store(
        self, capsule: Capsule, tenant_id: str | None = None
    ) -> Capsule:
        """Store a sealed Capsule."""
        ...

    async def get(
        self, capsule_id: str | UUID, tenant_id: str | None = None
    ) -> Capsule | None:
        """Retrieve a Capsule by ID."""
        ...

    async def get_latest(
        self, tenant_id: str | None = None
    ) -> Capsule | None:
        """Get the most recent Capsule (chain head)."""
        ...

    async def get_all_ordered(
        self, tenant_id: str | None = None
    ) -> Sequence[Capsule]:
        """Get all Capsules in sequence order (for chain verification)."""
        ...

    async def list(
        self,
        limit: int = 100,
        offset: int = 0,
        type_filter: CapsuleType | None = None,
        tenant_id: str | None = None,
    ) -> Sequence[Capsule]:
        """List Capsules with pagination and optional filtering."""
        ...

    async def count(
        self,
        type_filter: CapsuleType | None = None,
        tenant_id: str | None = None,
    ) -> int:
        """Count Capsules with optional filtering."""
        ...

    async def close(self) -> None:
        """Release backend resources."""
        ...
