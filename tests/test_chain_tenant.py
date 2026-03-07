"""Tests for per-tenant hash chains."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from qp_capsule.capsule import Capsule
from qp_capsule.chain import CapsuleChain
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
def seal_instance(tmp_path):
    """Seal with temporary key directory."""
    return Seal(key_path=tmp_path / "keys" / "key")


class TestChainTenant:
    """Tests for per-tenant hash chain operations."""

    @pytest.mark.asyncio
    async def test_add_with_tenant(self, storage, seal_instance):
        """Adds to tenant-scoped chain, sequence increments correctly."""
        chain = CapsuleChain(storage)

        c1 = Capsule.create(trigger={"source": "first"})
        c1 = await chain.add(c1, tenant_id="t1")
        assert c1.sequence == 0
        assert c1.previous_hash is None

        c1 = seal_instance.seal(c1)
        await storage.store(c1, tenant_id="t1")

        c2 = Capsule.create(trigger={"source": "second"})
        c2 = await chain.add(c2, tenant_id="t1")
        assert c2.sequence == 1
        assert c2.previous_hash == c1.hash

    @pytest.mark.asyncio
    async def test_add_without_tenant(self, storage, seal_instance):
        """Backwards compat, global chain works."""
        chain = CapsuleChain(storage)

        c1 = Capsule.create()
        c1 = await chain.add(c1)
        assert c1.sequence == 0
        assert c1.previous_hash is None

    @pytest.mark.asyncio
    async def test_independent_sequences(self, storage, seal_instance):
        """Tenant A gets 0,1,2; tenant B gets 0,1; sequences are independent."""
        chain = CapsuleChain(storage)

        for i in range(3):
            c = Capsule.create()
            c = await chain.add(c, tenant_id="tenant-a")
            assert c.sequence == i
            c = seal_instance.seal(c)
            await storage.store(c, tenant_id="tenant-a")

        for i in range(2):
            c = Capsule.create()
            c = await chain.add(c, tenant_id="tenant-b")
            assert c.sequence == i
            c = seal_instance.seal(c)
            await storage.store(c, tenant_id="tenant-b")

        assert await chain.get_chain_length(tenant_id="tenant-a") == 3
        assert await chain.get_chain_length(tenant_id="tenant-b") == 2

    @pytest.mark.asyncio
    async def test_verify_tenant_chain(self, storage, seal_instance):
        """3 capsules for tenant A, verify returns valid."""
        chain = CapsuleChain(storage)

        for _ in range(3):
            c = Capsule.create()
            c = await chain.add(c, tenant_id="tenant-a")
            c = seal_instance.seal(c)
            await storage.store(c, tenant_id="tenant-a")

        result = await chain.verify(tenant_id="tenant-a")
        assert result.valid is True
        assert result.capsules_verified == 3

    @pytest.mark.asyncio
    async def test_verify_global_unchanged(self, storage, seal_instance):
        """verify() without tenant works as before."""
        chain = CapsuleChain(storage)

        for _ in range(3):
            c = Capsule.create()
            c = await chain.add(c)
            c = seal_instance.seal(c)
            await storage.store(c)

        result = await chain.verify()
        assert result.valid is True
        assert result.capsules_verified == 3

    @pytest.mark.asyncio
    async def test_chain_integrity_violation(self, storage, seal_instance):
        """Tamper with tenant A's chain, detect break."""
        chain = CapsuleChain(storage)

        capsules = []
        for _ in range(3):
            c = Capsule.create()
            c = await chain.add(c, tenant_id="tenant-a")
            c = seal_instance.seal(c)
            await storage.store(c, tenant_id="tenant-a")
            capsules.append(c)

        # Tamper: store a capsule with wrong previous_hash
        bad = Capsule.create()
        bad.sequence = 3
        bad.previous_hash = "tampered_hash"
        bad = seal_instance.seal(bad)
        await storage.store(bad, tenant_id="tenant-a")

        result = await chain.verify(tenant_id="tenant-a")
        assert result.valid is False

    @pytest.mark.asyncio
    async def test_seal_and_store(self, storage, seal_instance):
        """Convenience method chains, seals, and stores in one call."""
        chain = CapsuleChain(storage)

        c = Capsule.create(trigger={"source": "convenience"})
        stored = await chain.seal_and_store(c, seal=seal_instance)

        assert stored.is_sealed()
        assert stored.sequence == 0

        retrieved = await storage.get(str(stored.id))
        assert retrieved is not None

    @pytest.mark.asyncio
    async def test_seal_and_store_with_tenant(self, storage, seal_instance):
        """seal_and_store with tenant scoping."""
        chain = CapsuleChain(storage)

        c1 = Capsule.create()
        await chain.seal_and_store(c1, seal=seal_instance, tenant_id="t1")

        c2 = Capsule.create()
        stored = await chain.seal_and_store(c2, seal=seal_instance, tenant_id="t1")

        assert stored.sequence == 1
        assert await chain.get_chain_length(tenant_id="t1") == 2
        assert await chain.get_chain_length(tenant_id="t2") == 0


class TestChainTenantEdgeCases:
    """Edge cases for per-tenant chain operations."""

    @pytest.mark.asyncio
    async def test_get_chain_head_with_tenant(self, storage, seal_instance):
        """get_chain_head(tenant_id) returns correct head per tenant."""
        chain = CapsuleChain(storage)

        c1 = Capsule.create(trigger={"source": "head-a"})
        await chain.seal_and_store(c1, seal=seal_instance, tenant_id="ta")

        c2 = Capsule.create(trigger={"source": "head-b"})
        await chain.seal_and_store(c2, seal=seal_instance, tenant_id="tb")

        head_a = await chain.get_chain_head(tenant_id="ta")
        assert head_a is not None
        assert head_a.trigger.source == "head-a"

        head_b = await chain.get_chain_head(tenant_id="tb")
        assert head_b is not None
        assert head_b.trigger.source == "head-b"

    @pytest.mark.asyncio
    async def test_get_chain_head_empty(self, storage, seal_instance):
        """get_chain_head for nonexistent tenant returns None."""
        chain = CapsuleChain(storage)
        assert await chain.get_chain_head(tenant_id="ghost") is None

    @pytest.mark.asyncio
    async def test_seal_and_store_builds_valid_chain(self, storage, seal_instance):
        """Multiple seal_and_store calls produce a verifiable chain."""
        chain = CapsuleChain(storage)

        for _ in range(5):
            await chain.seal_and_store(Capsule.create(), seal=seal_instance, tenant_id="chain-test")

        result = await chain.verify(tenant_id="chain-test")
        assert result.valid is True
        assert result.capsules_verified == 5

    @pytest.mark.asyncio
    async def test_interleaved_tenants_both_valid(self, storage, seal_instance):
        """Build two tenant chains in interleaved order, both verify valid."""
        chain = CapsuleChain(storage)

        for i in range(6):
            tid = "alpha" if i % 2 == 0 else "beta"
            await chain.seal_and_store(Capsule.create(), seal=seal_instance, tenant_id=tid)

        result_a = await chain.verify(tenant_id="alpha")
        assert result_a.valid is True
        assert result_a.capsules_verified == 3

        result_b = await chain.verify(tenant_id="beta")
        assert result_b.valid is True
        assert result_b.capsules_verified == 3

    @pytest.mark.asyncio
    async def test_verify_empty_tenant_is_valid(self, storage, seal_instance):
        """Verifying a tenant with no capsules returns valid with 0 verified."""
        chain = CapsuleChain(storage)
        result = await chain.verify(tenant_id="empty")
        assert result.valid is True
        assert result.capsules_verified == 0
