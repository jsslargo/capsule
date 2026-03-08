/**
 * Seal: Cryptographic proof for Capsules.
 *
 * SHA3-256 (FIPS 202) for content integrity + Ed25519 (FIPS 186-5) for authenticity.
 *
 * @license Apache-2.0
 */

import { sha3_256 } from "@noble/hashes/sha3.js";
import { bytesToHex } from "@noble/hashes/utils.js";
import * as ed25519 from "@noble/ed25519";
import { canonicalize } from "./canonical.js";
import type { Capsule, CapsuleDict } from "./capsule.js";
import { toDict } from "./capsule.js";

// ---------------------------------------------------------------------------
// Hash
// ---------------------------------------------------------------------------

/**
 * Compute the SHA3-256 hash of a Capsule's content.
 * Returns a 64-character lowercase hex string.
 */
export function computeHash(capsuleDict: CapsuleDict): string {
  const canonical = canonicalize(capsuleDict);
  const bytes = new TextEncoder().encode(canonical);
  return bytesToHex(sha3_256(bytes));
}

/**
 * Compute the SHA3-256 hash of an arbitrary object.
 * Uses canonical JSON serialization (sorted keys, no whitespace).
 */
export function computeHashFromDict(data: Record<string, unknown>): string {
  const canonical = canonicalize(data);
  const bytes = new TextEncoder().encode(canonical);
  return bytesToHex(sha3_256(bytes));
}

// ---------------------------------------------------------------------------
// Sign
// ---------------------------------------------------------------------------

/**
 * Seal a Capsule — compute hash and Ed25519 signature.
 *
 * Critical: Signs the hex-encoded hash STRING (64 ASCII chars as UTF-8 bytes),
 * not the raw 32-byte hash value. This matches the Python reference implementation.
 */
export async function seal(
  capsule: Capsule,
  privateKey: Uint8Array,
): Promise<Capsule> {
  const dict = toDict(capsule);
  const hashHex = computeHash(dict);

  const hashBytes = new TextEncoder().encode(hashHex);
  const signature = await ed25519.signAsync(hashBytes, privateKey);

  const publicKey = await ed25519.getPublicKeyAsync(privateKey);

  capsule.hash = hashHex;
  capsule.signature = bytesToHex(signature);
  capsule.signature_pq = "";
  capsule.signed_at = new Date().toISOString().replace("Z", "+00:00");
  capsule.signed_by = bytesToHex(publicKey).slice(0, 16);

  return capsule;
}

// ---------------------------------------------------------------------------
// Verify
// ---------------------------------------------------------------------------

/**
 * Verify a sealed Capsule's integrity and authenticity.
 *
 * 1. Recompute SHA3-256 from content and compare to stored hash
 * 2. Verify Ed25519 signature over the hash string
 */
export async function verify(
  capsule: Capsule,
  publicKey: Uint8Array,
): Promise<boolean> {
  if (!capsule.hash || !capsule.signature) {
    return false;
  }

  try {
    const dict = toDict(capsule);
    const computedHash = computeHash(dict);

    if (computedHash !== capsule.hash) {
      return false;
    }

    const hashBytes = new TextEncoder().encode(capsule.hash);
    const signatureBytes = hexToBytes(capsule.signature);

    return await ed25519.verifyAsync(signatureBytes, hashBytes, publicKey);
  } catch {
    return false;
  }
}

// ---------------------------------------------------------------------------
// Key utilities
// ---------------------------------------------------------------------------

/** Generate a new Ed25519 key pair. */
export function generateKeyPair(): {
  privateKey: Uint8Array;
  publicKey: Promise<Uint8Array>;
} {
  const privateKey = ed25519.utils.randomSecretKey();
  return {
    privateKey,
    publicKey: ed25519.getPublicKeyAsync(privateKey),
  };
}

/** Get the public key fingerprint (first 16 hex chars). */
export async function getFingerprint(privateKey: Uint8Array): Promise<string> {
  const pub = await ed25519.getPublicKeyAsync(privateKey);
  return bytesToHex(pub).slice(0, 16);
}

// ---------------------------------------------------------------------------
// Internal
// ---------------------------------------------------------------------------

function hexToBytes(hex: string): Uint8Array {
  const bytes = new Uint8Array(hex.length / 2);
  for (let i = 0; i < hex.length; i += 2) {
    bytes[i / 2] = parseInt(hex.substring(i, i + 2), 16);
  }
  return bytes;
}
