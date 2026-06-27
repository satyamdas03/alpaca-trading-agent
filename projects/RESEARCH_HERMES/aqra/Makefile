.PHONY: sync test lint format clean ingest certify deploy-dry monitor

# Install all dependencies including pytest and dev tools.
sync:
	uv sync --extra dev

# Run the full test suite (must use uv's Python to avoid wrong interpreter).
test:
	uv run python -m pytest tests/ -v

# Lint and auto-format with ruff.
lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

# AQRA pipeline commands (Phase 1 uses free-tier data and paper trading only).
ingest:
	uv run aqra ingest --start 2020-01-01 --end 2024-12-31

certify:
	uv run aqra certify

deploy-dry:
	uv run aqra deploy --dry-run

monitor:
	uv run aqra monitor

# Remove caches and the virtual environment.
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	rm -rf .venv
