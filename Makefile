.PHONY: help install install-dev install-all docs docs-serve test lint format clean

PYTHON := python3
PIP := pip

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install the package
	$(PIP) install -e .

install-dev: ## Install with development dependencies
	$(PIP) install -e ".[dev]"

install-all: ## Install with all dependencies (dev + docs + notebooks)
	$(PIP) install -e ".[all]"

docs: ## Build documentation
	mkdocs build

docs-serve: ## Serve documentation locally with hot-reload
	mkdocs serve

docs-deploy: ## Deploy documentation to GitHub Pages
	mkdocs gh-deploy --force

test: ## Run tests
	pytest tests/ -v --cov=src/llm_eval_framework --cov-report=term-missing

test-fast: ## Run tests excluding slow and integration tests
	pytest tests/ -v -m "not slow and not integration"

lint: ## Run linting checks
	ruff check src/ tests/
	mypy src/

format: ## Auto-format code
	ruff format src/ tests/
	ruff check --fix src/ tests/

clean: ## Clean build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache
	rm -rf site/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

lab: ## Start Jupyter Lab for hands-on notebooks
	jupyter lab notebooks/

eval-basic: ## Run basic benchmark suite
	$(PYTHON) -m llm_eval_framework.harness.runner --config configs/benchmark_suite_basic.yaml

eval-full: ## Run full benchmark suite
	$(PYTHON) -m llm_eval_framework.harness.runner --config configs/benchmark_suite_full.yaml

eval-safety: ## Run safety evaluation suite
	$(PYTHON) -m llm_eval_framework.harness.runner --config configs/safety_eval_config.yaml
