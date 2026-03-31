# Contributing to the LLM Evaluation Framework

Thank you for your interest in contributing. This project aims to be the most comprehensive, current, and rigorous open-source resource for LLM evaluation. Contributions that improve depth, accuracy, or practical utility are welcome.

## Ways to Contribute

**Documentation improvements**: Fix errors, add clarity, update benchmark results with newer data, expand tool guides, or improve explanations.

**Benchmark coverage**: Add new benchmarks that have emerged, update results tables with current leaderboard data, or document benchmarks we've missed.

**Tool guides**: Write or improve hands-on guides for evaluation tools, especially newer entrants to the ecosystem.

**Lab exercises**: Propose new labs, improve existing ones, fix code issues, or add extension challenges.

**Python library**: Improve the `llm_eval_framework` package with new judges, metrics, or harness features.

**Bug fixes**: Report or fix issues in code, documentation, or notebooks.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/a217-anjali/llm-evaluation-framework.git
cd llm-evaluation-framework

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install all dependencies
pip install -e ".[all]"

# Install pre-commit hooks
pre-commit install
```

## Code Standards

All Python code should follow these standards:

- **Type hints**: Use Python 3.11+ type hint syntax throughout
- **Docstrings**: Google-style docstrings for all public functions and classes
- **Testing**: Add pytest tests for new functionality; aim for >80% coverage on new code
- **Linting**: Code must pass `ruff check` and `mypy` (strict mode)
- **Formatting**: Use `ruff format` for consistent style

Run checks locally before submitting:

```bash
make lint
make test
```

## Documentation Standards

When updating documentation:

- **Currentness**: If referencing model scores, tool versions, or benchmark results, verify they reflect the latest available data. Mark any unverified data with `[VERIFY]`.
- **Depth**: Provide intuitive explanations first, then formal/mathematical treatment where applicable.
- **Practicality**: Every concept should connect to a "so what" — why does this matter for someone building with LLMs?
- **References**: Cite papers, tools, and benchmarks with links. Use footnotes for academic citations.

## Submitting Changes

1. Fork the repository and create a feature branch from `main`
2. Make your changes with clear, atomic commits
3. Ensure all tests pass and linting is clean
4. Submit a pull request with a clear description of what changed and why
5. Reference any related issues

## Reporting Issues

Use GitHub Issues for bug reports, feature requests, or questions. When reporting benchmark data that has become stale, please include a link to the current source.

## Code of Conduct

Be respectful, constructive, and collaborative. We're building a shared resource for the AI community. Disagreements about technical approaches are welcome; personal attacks are not.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
