/**
 * Canonical JSON serialization for Capsules.
 *
 * Produces byte-identical output to Python's:
 *   json.dumps(capsule.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
 *
 * This is THE critical function for cross-language compatibility.
 * See spec/README.md Section 2 for the full specification.
 *
 * @license Apache-2.0
 */

const FLOAT_PATHS = new Set([
  "reasoning.confidence",
  "reasoning.options.*.feasibility",
]);

/**
 * Serialize a value to canonical JSON matching the Capsule Protocol Specification.
 *
 * Rules (CPS Section 2):
 * - Objects: keys sorted lexicographically by Unicode code point (recursive)
 * - No whitespace (no spaces after : or ,)
 * - Float-typed fields always include decimal point (0.0, not 0)
 * - Strings follow RFC 8259 escaping; non-ASCII as literal UTF-8
 */
export function canonicalize(value: unknown): string {
  return serializeValue(value, "");
}

function serializeValue(value: unknown, path: string): string {
  if (value === null || value === undefined) {
    return "null";
  }

  if (typeof value === "boolean") {
    return value ? "true" : "false";
  }

  if (typeof value === "number") {
    if (!Number.isFinite(value)) {
      throw new Error(`Cannot serialize ${value} — Infinity and NaN are prohibited`);
    }
    return formatNumber(value, path);
  }

  if (typeof value === "string") {
    return JSON.stringify(value);
  }

  if (Array.isArray(value)) {
    const itemPath = path ? `${path}.*` : "*";
    const items = value.map((item) => serializeValue(item, itemPath));
    return "[" + items.join(",") + "]";
  }

  if (typeof value === "object") {
    const obj = value as Record<string, unknown>;
    const keys = Object.keys(obj).sort();
    const pairs = keys.map((key) => {
      const childPath = path ? `${path}.${key}` : key;
      return JSON.stringify(key) + ":" + serializeValue(obj[key], childPath);
    });
    return "{" + pairs.join(",") + "}";
  }

  throw new Error(`Cannot serialize type: ${typeof value}`);
}

function isFloatPath(path: string): boolean {
  return FLOAT_PATHS.has(path);
}

function formatNumber(value: number, path: string): string {
  if (isFloatPath(path)) {
    return formatFloat(value);
  }
  return JSON.stringify(value);
}

/**
 * Format a number as a float, always including a decimal point.
 * Matches Python's json.dumps behavior for float values.
 *
 * 0.0  → "0.0"  (not "0")
 * 1.0  → "1.0"  (not "1")
 * 0.95 → "0.95"
 */
function formatFloat(value: number): string {
  const s = JSON.stringify(value);
  if (Number.isInteger(value) && !s.includes(".") && !s.includes("e")) {
    return s + ".0";
  }
  return s;
}
