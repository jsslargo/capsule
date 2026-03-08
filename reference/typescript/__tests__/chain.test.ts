/**
 * Chain verification tests.
 *
 * Tests the hash chain integrity: sequence ordering, hash linkage,
 * genesis validation, and tamper detection.
 */

import { describe, expect, it } from "vitest";
import { createCapsule } from "../src/capsule.js";
import { seal, generateKeyPair } from "../src/seal.js";
import { verifyChain } from "../src/chain.js";
import type { Capsule } from "../src/capsule.js";

async function buildChain(length: number): Promise<Capsule[]> {
  const { privateKey } = generateKeyPair();
  const chain: Capsule[] = [];

  for (let i = 0; i < length; i++) {
    const capsule = createCapsule({
      type: "agent",
      sequence: i,
      previous_hash: i === 0 ? null : chain[i - 1].hash,
    });
    await seal(capsule, privateKey);
    chain.push(capsule);
  }

  return chain;
}

describe("Chain Verification", () => {
  it("empty chain is valid", () => {
    const result = verifyChain([]);
    expect(result.valid).toBe(true);
    expect(result.capsules_verified).toBe(0);
  });

  it("single capsule (genesis) is valid", async () => {
    const chain = await buildChain(1);
    const result = verifyChain(chain);
    expect(result.valid).toBe(true);
    expect(result.capsules_verified).toBe(1);
  });

  it("multi-capsule chain is valid", async () => {
    const chain = await buildChain(5);
    const result = verifyChain(chain);
    expect(result.valid).toBe(true);
    expect(result.capsules_verified).toBe(5);
  });

  it("detects genesis with non-null previous_hash", async () => {
    const chain = await buildChain(1);
    chain[0].previous_hash = "deadbeef".repeat(8);

    const result = verifyChain(chain);
    expect(result.valid).toBe(false);
    expect(result.error).toContain("Genesis");
  });

  it("detects sequence gap", async () => {
    const chain = await buildChain(3);
    chain[1].sequence = 5;

    const result = verifyChain(chain);
    expect(result.valid).toBe(false);
    expect(result.error).toContain("Sequence gap");
    expect(result.capsules_verified).toBe(1);
  });

  it("detects hash linkage break", async () => {
    const chain = await buildChain(3);
    chain[2].previous_hash = "0".repeat(64);

    const result = verifyChain(chain);
    expect(result.valid).toBe(false);
    expect(result.error).toContain("previous_hash mismatch");
    expect(result.broken_at).toBe(chain[2].id);
    expect(result.capsules_verified).toBe(2);
  });
});
