/**
 * Seal and verify tests.
 *
 * Tests the cryptographic sealing pipeline: SHA3-256 hashing + Ed25519 signing,
 * verification, tamper detection, and key management.
 */

import { describe, expect, it } from "vitest";
import {
  createCapsule,
  isSealed,
  toDict,
} from "../src/capsule.js";
import { computeHash } from "../src/seal.js";
import { seal, verify, generateKeyPair, getFingerprint } from "../src/seal.js";

describe("Seal", () => {
  it("seals a capsule with hash and signature", async () => {
    const capsule = createCapsule({ type: "agent" });
    const { privateKey, publicKey } = generateKeyPair();
    const pub = await publicKey;

    await seal(capsule, privateKey);

    expect(capsule.hash).toHaveLength(64);
    expect(capsule.signature).toHaveLength(128);
    expect(capsule.signed_at).toBeTruthy();
    expect(capsule.signed_by).toBeTruthy();
    expect(isSealed(capsule)).toBe(true);
  });

  it("verification passes for an untampered capsule", async () => {
    const capsule = createCapsule({ type: "tool" });
    const { privateKey, publicKey } = generateKeyPair();
    const pub = await publicKey;

    await seal(capsule, privateKey);

    expect(await verify(capsule, pub)).toBe(true);
  });

  it("verification fails after content tampering", async () => {
    const capsule = createCapsule({
      type: "agent",
      trigger: {
        type: "user_request",
        source: "test",
        timestamp: "2026-01-01T00:00:00+00:00",
        request: "original request",
        correlation_id: null,
        user_id: null,
      },
    });
    const { privateKey, publicKey } = generateKeyPair();
    const pub = await publicKey;

    await seal(capsule, privateKey);
    expect(await verify(capsule, pub)).toBe(true);

    capsule.trigger.request = "tampered request";
    expect(await verify(capsule, pub)).toBe(false);
  });

  it("verification fails with wrong public key", async () => {
    const capsule = createCapsule({ type: "agent" });
    const keys1 = generateKeyPair();
    const keys2 = generateKeyPair();

    await seal(capsule, keys1.privateKey);

    const wrongPub = await keys2.publicKey;
    expect(await verify(capsule, wrongPub)).toBe(false);
  });

  it("verification fails on unsealed capsule", async () => {
    const capsule = createCapsule({ type: "agent" });
    const { publicKey } = generateKeyPair();
    const pub = await publicKey;

    expect(await verify(capsule, pub)).toBe(false);
  });

  it("verification returns false on corrupted signature bytes", async () => {
    const capsule = createCapsule({ type: "agent" });
    const { privateKey, publicKey } = generateKeyPair();
    const pub = await publicKey;

    await seal(capsule, privateKey);
    capsule.signature = "zz";
    expect(await verify(capsule, pub)).toBe(false);
  });

  it("hash is deterministic for same content", () => {
    const dict = toDict(
      createCapsule({
        type: "agent",
        trigger: {
          type: "user_request",
          source: "determinism-test",
          timestamp: "2026-01-01T00:00:00+00:00",
          request: "same content",
          correlation_id: null,
          user_id: null,
        },
      }),
    );
    const hash1 = computeHash(dict);
    const hash2 = computeHash(dict);
    expect(hash1).toBe(hash2);
    expect(hash1).toHaveLength(64);
  });

  it("hash changes when content changes", () => {
    const c1 = createCapsule({ type: "agent" });
    const c2 = createCapsule({ type: "tool" });
    const h1 = computeHash(toDict(c1));
    const h2 = computeHash(toDict(c2));
    expect(h1).not.toBe(h2);
  });
});

describe("Key Management", () => {
  it("generates valid key pairs", async () => {
    const { privateKey, publicKey } = generateKeyPair();
    expect(privateKey).toHaveLength(32);
    const pub = await publicKey;
    expect(pub).toHaveLength(32);
  });

  it("fingerprint is 16 hex characters", async () => {
    const { privateKey } = generateKeyPair();
    const fp = await getFingerprint(privateKey);
    expect(fp).toHaveLength(16);
    expect(fp).toMatch(/^[0-9a-f]{16}$/);
  });

  it("different keys produce different fingerprints", async () => {
    const k1 = generateKeyPair();
    const k2 = generateKeyPair();
    const fp1 = await getFingerprint(k1.privateKey);
    const fp2 = await getFingerprint(k2.privateKey);
    expect(fp1).not.toBe(fp2);
  });
});
