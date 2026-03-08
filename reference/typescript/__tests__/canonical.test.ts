/**
 * Canonical JSON serialization tests.
 *
 * Verifies CPS Section 2 rules: key ordering, whitespace, float formatting,
 * null handling, string escaping, and edge cases.
 */

import { describe, expect, it } from "vitest";
import { canonicalize } from "../src/canonical.js";

describe("Canonical JSON — Key Ordering", () => {
  it("sorts object keys lexicographically", () => {
    expect(canonicalize({ z: 1, a: 2, m: 3 })).toBe('{"a":2,"m":3,"z":1}');
  });

  it("sorts nested object keys recursively", () => {
    const input = { b: { z: 1, a: 2 }, a: { y: 3, x: 4 } };
    expect(canonicalize(input)).toBe('{"a":{"x":4,"y":3},"b":{"a":2,"z":1}}');
  });

  it("preserves array element order", () => {
    expect(canonicalize([3, 1, 2])).toBe("[3,1,2]");
  });

  it("sorts keys within array objects", () => {
    const input = [{ b: 1, a: 2 }];
    expect(canonicalize(input)).toBe('[{"a":2,"b":1}]');
  });
});

describe("Canonical JSON — Whitespace", () => {
  it("uses zero whitespace", () => {
    const result = canonicalize({ key: "value" });
    expect(result).not.toContain(" ");
    expect(result).not.toContain("\n");
    expect(result).toBe('{"key":"value"}');
  });
});

describe("Canonical JSON — Float Formatting", () => {
  it("formats confidence 0 as 0.0", () => {
    const input = { reasoning: { confidence: 0 } };
    expect(canonicalize(input)).toContain('"confidence":0.0');
  });

  it("formats confidence 1 as 1.0", () => {
    const input = { reasoning: { confidence: 1 } };
    expect(canonicalize(input)).toContain('"confidence":1.0');
  });

  it("formats confidence 0.95 as 0.95", () => {
    const input = { reasoning: { confidence: 0.95 } };
    expect(canonicalize(input)).toContain('"confidence":0.95');
  });

  it("formats feasibility in options as float", () => {
    const input = { reasoning: { options: [{ feasibility: 1 }] } };
    expect(canonicalize(input)).toContain('"feasibility":1.0');
  });

  it("formats non-float integers normally", () => {
    const input = { execution: { duration_ms: 42 } };
    expect(canonicalize(input)).toContain('"duration_ms":42');
    expect(canonicalize(input)).not.toContain("42.0");
  });
});

describe("Canonical JSON — Null, Boolean, Empty Collections", () => {
  it("serializes null", () => {
    expect(canonicalize(null)).toBe("null");
  });

  it("serializes undefined as null", () => {
    expect(canonicalize(undefined)).toBe("null");
  });

  it("serializes true and false", () => {
    expect(canonicalize(true)).toBe("true");
    expect(canonicalize(false)).toBe("false");
  });

  it("serializes empty array", () => {
    expect(canonicalize([])).toBe("[]");
  });

  it("serializes empty object", () => {
    expect(canonicalize({})).toBe("{}");
  });
});

describe("Canonical JSON — Strings", () => {
  it("escapes double quotes", () => {
    expect(canonicalize('say "hello"')).toBe('"say \\"hello\\""');
  });

  it("escapes backslash", () => {
    expect(canonicalize("back\\slash")).toBe('"back\\\\slash"');
  });

  it("handles Unicode (non-ASCII as literal UTF-8)", () => {
    const result = canonicalize("café");
    expect(result).toBe('"café"');
    expect(result).not.toContain("\\u");
  });
});

describe("Canonical JSON — Error Cases", () => {
  it("rejects Infinity", () => {
    expect(() => canonicalize(Infinity)).toThrow("Infinity");
  });

  it("rejects NaN", () => {
    expect(() => canonicalize(NaN)).toThrow("NaN");
  });

  it("rejects -Infinity", () => {
    expect(() => canonicalize(-Infinity)).toThrow("Infinity");
  });

  it("rejects unsupported types (Symbol)", () => {
    expect(() => canonicalize(Symbol("test") as unknown)).toThrow(
      "Cannot serialize type",
    );
  });
});
