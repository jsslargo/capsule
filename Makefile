.PHONY: install lint typecheck test test-golden test-all format clean

install:
	pip install -e ".[storage,dev]"

lint:
	ruff check src/ tests/ specs/

format:
	ruff check --fix src/ tests/ specs/

typecheck:
	mypy src/qp_capsule/

test:
	pytest tests/ -v --tb=short --cov=qp_capsule --cov-fail-under=100

test-golden:
	pytest tests/test_golden_fixtures.py -v

test-all: lint typecheck test test-golden

golden-regenerate:
	python specs/cps/generate_fixtures.py

clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
