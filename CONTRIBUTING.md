# Contributing to Capsule

Thank you for your interest in contributing to the Capsule Protocol Specification (CPS) reference implementation.

## Getting Started

```bash
git clone https://github.com/quantumpipes/capsule.git
cd capsule
pip install -e ".[dev,storage]"
```

Or use the Makefile:

```bash
make install
```

## Development

### Running Tests

```bash
make test
```

This runs all 350 tests with 100% coverage enforcement. If coverage drops below 100%, the test run fails.

### Individual Commands

```bash
make lint         # ruff check src/ tests/ specs/
make typecheck    # mypy src/qp_capsule/
make test-golden  # Run only golden fixture conformance tests
make test-all     # lint + typecheck + test + golden
```

### Code Standards

- Python 3.11+ with type hints on all public functions
- Ruff for linting (E, F, I, W rules)
- mypy strict mode
- Docstrings on all public classes and methods
- `filterwarnings = ["error"]` — any new warning is a test failure
- 100% test coverage required (`fail_under = 100`)

## What to Contribute

- **Bug fixes** with regression tests
- **Storage backends** implementing `CapsuleStorageProtocol`
- **Golden test vectors** covering new edge cases
- **Documentation** improvements and corrections

## Types of Changes

### Implementation changes

Modify code in `src/qp_capsule/`. These must not change the canonical JSON output or sealing algorithm. Tests and golden fixtures must continue to pass.

### Protocol changes

Changes to the Capsule Protocol Specification itself. These are rare, require careful review, and must go through the [CPS change proposal](https://github.com/quantumpipes/capsule/issues/new?template=cps_change.md) process. Protocol changes require updating golden fixtures and may affect all SDK implementations.

## Submitting Changes

1. Fork the repository
2. Create a feature branch from `main`
3. Write tests for your changes (100% coverage required)
4. Run `make test-all` and ensure everything passes
5. Submit a pull request using the [PR template](./.github/PULL_REQUEST_TEMPLATE.md)

## Contributor License Agreement

By submitting contributions to this project, you agree that your contributions
are licensed under the Apache License 2.0, including the patent grant in
Section 3. See [PATENTS.md](./PATENTS.md) for details.

## Security

Report security vulnerabilities via [SECURITY.md](./SECURITY.md). Do not open
public issues for security bugs.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md).
