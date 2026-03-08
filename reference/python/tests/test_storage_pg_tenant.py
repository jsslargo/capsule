"""Tests for tenant-scoped PostgresCapsuleStorage."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from qp_capsule.capsule import Capsule, CapsuleType
from qp_capsule.exceptions import StorageError
from qp_capsule.seal import Seal
from qp_capsule.storage_pg import PostgresCapsuleStorage


@pytest.fixture
async def storage(tmp_path):
    """PostgresCapsuleStorage backed by SQLite for testing."""
    db_url = f"sqlite+aiosqlite:///{tmp_path / 'test.db'}"
    s = PostgresCapsuleStorage.__new__(PostgresCapsuleStorage)
    s.database_url = db_url
    s._engine = create_async_engine(db_url, echo=False)
    s._session_factory = async_sessionmaker(s._engine, class_=AsyncSession, expire_on_commit=False)
    s._initialized = False
    yield s
    await s.close()


@pytest.fixture
def seal(tmp_path):
    """Seal with temporary key directory."""
    return Seal(key_path=tmp_path / "keys" / "key")


def _make_sealed(seal_instance: Seal, seq: int = 0, **create_kwargs) -> Capsule:
    """Create, assign sequence, and seal a capsule."""
    capsule = Capsule.create(**create_kwargs)
    capsule.sequence = seq
    return seal_instance.seal(capsule)


class TestStoragePGTenant:
    """Tests for tenant-scoped capsule storage."""

    @pytest.mark.asyncio
    async def test_store_with_tenant_id(self, storage, seal):
        """Store capsule with tenant, verify tenant_id persists."""
        capsule = _make_sealed(seal, capsule_type=CapsuleType.AGENT)
        stored = await storage.store(capsule, tenant_id="tenant-1")
        assert stored.id == capsule.id

    @pytest.mark.asyncio
    async def test_store_without_tenant_id(self, storage, seal):
        """Store capsule without tenant (backwards compat)."""
        capsule = _make_sealed(seal, capsule_type=CapsuleType.AGENT)
        stored = await storage.store(capsule)
        assert stored.id == capsule.id

    @pytest.mark.asyncio
    async def test_list_filters_by_tenant(self, storage, seal):
        """Store 3 capsules across 2 tenants, list(tenant_id=A) returns only A's."""
        await storage.store(_make_sealed(seal, seq=0), tenant_id="tenant-a")
        await storage.store(_make_sealed(seal, seq=1), tenant_id="tenant-b")
        await storage.store(_make_sealed(seal, seq=2), tenant_id="tenant-a")

        a_capsules = await storage.list(tenant_id="tenant-a")
        assert len(a_capsules) == 2

        b_capsules = await storage.list(tenant_id="tenant-b")
        assert len(b_capsules) == 1

    @pytest.mark.asyncio
    async def test_list_without_tenant_returns_all(self, storage, seal):
        """list() with no tenant returns everything."""
        await storage.store(_make_sealed(seal, seq=0), tenant_id="t1")
        await storage.store(_make_sealed(seal, seq=1), tenant_id="t2")

        all_capsules = await storage.list()
        assert len(all_capsules) == 2

    @pytest.mark.asyncio
    async def test_get_latest_scoped(self, storage, seal):
        """2 tenants with interleaved capsules, get_latest per tenant correct."""
        for i, (src, tid) in enumerate(
            [
                ("a-first", "tenant-a"),
                ("b-first", "tenant-b"),
                ("a-second", "tenant-a"),
            ]
        ):
            c = _make_sealed(seal, seq=i, trigger={"source": src})
            await storage.store(c, tenant_id=tid)

        latest_a = await storage.get_latest(tenant_id="tenant-a")
        assert latest_a is not None
        assert latest_a.trigger.source == "a-second"

        latest_b = await storage.get_latest(tenant_id="tenant-b")
        assert latest_b is not None
        assert latest_b.trigger.source == "b-first"

    @pytest.mark.asyncio
    async def test_get_latest_global(self, storage, seal):
        """get_latest() without tenant returns global latest."""
        for i in range(3):
            c = _make_sealed(seal, seq=i, trigger={"source": f"cap-{i}"})
            await storage.store(c, tenant_id=f"t{i}")

        latest = await storage.get_latest()
        assert latest is not None
        assert latest.trigger.source == "cap-2"

    @pytest.mark.asyncio
    async def test_count_scoped(self, storage, seal):
        """count per tenant matches expected."""
        for i in range(3):
            await storage.store(_make_sealed(seal, seq=i), tenant_id="tenant-a")

        for i in range(3, 5):
            await storage.store(_make_sealed(seal, seq=i), tenant_id="tenant-b")

        assert await storage.count(tenant_id="tenant-a") == 3
        assert await storage.count(tenant_id="tenant-b") == 2
        assert await storage.count() == 5

    @pytest.mark.asyncio
    async def test_tenant_isolation(self, storage, seal):
        """Store for tenant A, query for tenant B, get empty result."""
        await storage.store(_make_sealed(seal), tenant_id="tenant-a")

        b_capsules = await storage.list(tenant_id="tenant-b")
        assert len(b_capsules) == 0

        b_latest = await storage.get_latest(tenant_id="tenant-b")
        assert b_latest is None

    @pytest.mark.asyncio
    async def test_get_without_tenant_returns_any(self, storage, seal):
        """get(id) without tenant_id returns the capsule regardless of tenant."""
        capsule = _make_sealed(seal)
        await storage.store(capsule, tenant_id="tenant-a")

        retrieved = await storage.get(str(capsule.id))
        assert retrieved is not None
        assert retrieved.id == capsule.id

    @pytest.mark.asyncio
    async def test_get_with_correct_tenant_returns_capsule(self, storage, seal):
        """get(id, tenant_id) returns the capsule if it belongs to that tenant."""
        capsule = _make_sealed(seal)
        await storage.store(capsule, tenant_id="tenant-a")

        retrieved = await storage.get(str(capsule.id), tenant_id="tenant-a")
        assert retrieved is not None
        assert retrieved.id == capsule.id

    @pytest.mark.asyncio
    async def test_get_with_wrong_tenant_returns_none(self, storage, seal):
        """get(id, tenant_id) returns None if capsule belongs to different tenant."""
        capsule = _make_sealed(seal)
        await storage.store(capsule, tenant_id="tenant-a")

        retrieved = await storage.get(str(capsule.id), tenant_id="tenant-b")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_mixed_tenants_interleaved(self, storage, seal):
        """Interleave stores across 3 tenants, verify each tenant's list."""
        tenants = {"t1": 0, "t2": 0, "t3": 0}
        seq = 0
        for _ in range(2):
            for tid in tenants:
                await storage.store(
                    _make_sealed(seal, seq=seq, trigger={"source": tid}),
                    tenant_id=tid,
                )
                tenants[tid] += 1
                seq += 1

        for tid, expected_count in tenants.items():
            capsules = await storage.list(tenant_id=tid)
            assert len(capsules) == expected_count
            for c in capsules:
                assert c.trigger.source == tid


class TestStoragePGTenantErrorPaths:
    """Error paths and validation for tenant-scoped storage."""

    @pytest.mark.asyncio
    async def test_store_unsealed_with_tenant_raises(self, storage):
        """Unsealed capsule raises StorageError even with tenant_id."""
        capsule = Capsule.create()
        with pytest.raises(StorageError, match="unsealed"):
            await storage.store(capsule, tenant_id="tenant-a")

    @pytest.mark.asyncio
    async def test_count_empty_storage(self, storage):
        """count() on empty storage returns 0."""
        assert await storage.count() == 0
        assert await storage.count(tenant_id="nonexistent") == 0

    @pytest.mark.asyncio
    async def test_get_latest_empty_storage(self, storage):
        """get_latest() on empty storage returns None."""
        assert await storage.get_latest() is None
        assert await storage.get_latest(tenant_id="nonexistent") is None

    @pytest.mark.asyncio
    async def test_get_nonexistent_id(self, storage):
        """get() with unknown ID returns None."""
        assert await storage.get("00000000-0000-0000-0000-000000000000") is None


class TestStoragePGTenantCombinedFilters:
    """Combined filter queries with tenant scoping."""

    @pytest.mark.asyncio
    async def test_count_type_plus_tenant(self, storage, seal):
        """count() with both type and tenant_id filters."""
        c1 = _make_sealed(seal, seq=0, capsule_type=CapsuleType.AGENT)
        c2 = _make_sealed(seal, seq=1, capsule_type=CapsuleType.TOOL)
        c3 = _make_sealed(seal, seq=2, capsule_type=CapsuleType.AGENT)
        await storage.store(c1, tenant_id="t1")
        await storage.store(c2, tenant_id="t1")
        await storage.store(c3, tenant_id="t2")

        assert await storage.count(type_filter=CapsuleType.AGENT, tenant_id="t1") == 1
        assert await storage.count(type_filter=CapsuleType.TOOL, tenant_id="t1") == 1
        assert await storage.count(type_filter=CapsuleType.AGENT, tenant_id="t2") == 1
        assert await storage.count(type_filter=CapsuleType.TOOL, tenant_id="t2") == 0

    @pytest.mark.asyncio
    async def test_list_domain_plus_tenant(self, storage, seal):
        """list() with both domain and tenant_id filters."""
        await storage.store(_make_sealed(seal, seq=0, domain="vault"), tenant_id="t1")
        await storage.store(_make_sealed(seal, seq=1, domain="agents"), tenant_id="t1")
        await storage.store(_make_sealed(seal, seq=2, domain="vault"), tenant_id="t2")

        result = await storage.list(domain="vault", tenant_id="t1")
        assert len(result) == 1

        result = await storage.list(domain="vault", tenant_id="t2")
        assert len(result) == 1

        result = await storage.list(domain="agents", tenant_id="t2")
        assert len(result) == 0


class TestStoragePGSealRoundtrip:
    """Verify _to_capsule restores seal info from model columns."""

    @pytest.mark.asyncio
    async def test_get_restores_hash_and_signature(self, storage, seal):
        """get() returns capsule with hash and signature intact."""
        capsule = _make_sealed(seal, trigger={"source": "seal-test"})
        original_hash = capsule.hash
        original_sig = capsule.signature
        await storage.store(capsule, tenant_id="t1")

        retrieved = await storage.get(str(capsule.id))
        assert retrieved is not None
        assert retrieved.hash == original_hash
        assert retrieved.signature == original_sig
        assert retrieved.is_sealed()

    @pytest.mark.asyncio
    async def test_list_restores_hash(self, storage, seal):
        """list() returns capsules with hash for chain verification."""
        capsule = _make_sealed(seal)
        await storage.store(capsule, tenant_id="t1")

        results = await storage.list(tenant_id="t1")
        assert len(results) == 1
        assert results[0].hash == capsule.hash
        assert results[0].is_sealed()

    @pytest.mark.asyncio
    async def test_get_all_ordered_returns_sequence_order(self, storage, seal):
        """get_all_ordered() returns capsules sorted by sequence ascending."""
        for i in [2, 0, 1]:
            await storage.store(_make_sealed(seal, seq=i), tenant_id="t1")

        ordered = await storage.get_all_ordered()
        assert len(ordered) == 3
        assert [c.sequence for c in ordered] == [0, 1, 2]
