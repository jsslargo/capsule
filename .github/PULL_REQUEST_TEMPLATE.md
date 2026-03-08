## Summary

What does this PR do? Link to any related issues.

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that changes existing behavior)
- [ ] Protocol change (modifies the CPS specification)
- [ ] Documentation update
- [ ] Test improvement

## Checklist

### Python reference (`reference/python/`)
- [ ] Tests pass: `cd reference/python && pytest tests/`
- [ ] Linter passes: `cd reference/python && ruff check src/ tests/`
- [ ] Type checker passes: `cd reference/python && mypy src/qp_capsule/`
- [ ] Golden fixtures pass: `cd reference/python && pytest tests/test_golden_fixtures.py`

### TypeScript reference (`reference/typescript/`)
- [ ] Tests pass: `cd reference/typescript && npm test`
- [ ] Type check passes: `cd reference/typescript && npx tsc --noEmit`
- [ ] Conformance passes: `cd reference/typescript && npm run conformance`

### General
- [ ] Documentation updated (if applicable)
- [ ] CHANGELOG.md updated (if user-facing change)

## Protocol Impact

Does this PR change the Capsule Protocol Specification?

- [ ] No protocol impact (implementation only)
- [ ] Protocol change (requires CPS version bump and golden fixture update)
