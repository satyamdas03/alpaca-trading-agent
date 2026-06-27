.PHONY: sync test lint format clean

sync:
	uv sync --extra dev

test:
	uv run pytest -v

lint:
	uv run ruff check src tests

format:
	uv run ruff format src tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	rm -rf .venv
