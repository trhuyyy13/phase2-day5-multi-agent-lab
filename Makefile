PYTHON ?= ./.venv/bin/python

.PHONY: install test lint format typecheck run-baseline run-multi clean

install:
	$(PYTHON) -m pip install ".[dev,llm]"

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check src tests

format:
	$(PYTHON) -m ruff format src tests

typecheck:
	$(PYTHON) -m mypy src

run-baseline:
	$(PYTHON) -m multi_agent_research_lab.cli baseline --query "Research GraphRAG state-of-the-art"

run-multi:
	$(PYTHON) -m multi_agent_research_lab.cli multi-agent --query "Research GraphRAG state-of-the-art"

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache dist build *.egg-info
