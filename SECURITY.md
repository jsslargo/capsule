# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |

## Reporting Vulnerabilities

For security concerns or vulnerability reports:

- **Email**: security@quantumpipes.com
- **GitHub Security Advisories**: [quantumpipes/capsule/security](https://github.com/quantumpipes/capsule/security)

We follow coordinated disclosure and will acknowledge reports within 48 hours.

## Cryptographic Algorithms

| Purpose | Algorithm | Standard |
|---------|-----------|----------|
| Content integrity | SHA3-256 | FIPS 202 |
| Classical signature | Ed25519 | RFC 8032 / FIPS 186-5 |
| Post-quantum signature | ML-DSA-65 | FIPS 204 |
| Temporal integrity | Hash chain | Capsule Protocol Specification (CPS) |

## Key Storage

- Ed25519 keys: `~/.quantumpipes/key` (permissions 0600)
- ML-DSA-65 keys: `~/.quantumpipes/key.ml` + `key.ml.pub` (permissions 0600/0644)
- Keys generated on first use with secure random
