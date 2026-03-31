<div align="center">

# LLM Evaluation Framework

### The Definitive Open-Source Guide to Evaluating Large Language Models

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Last Updated](https://img.shields.io/badge/Last_Updated-March_2026-orange.svg)]()
[![Benchmarks Covered](https://img.shields.io/badge/Benchmarks_Covered-50+-purple.svg)]()
[![Tools Compared](https://img.shields.io/badge/Tools_Compared-25+-teal.svg)]()
[![Hands--On Labs](https://img.shields.io/badge/Labs-9-red.svg)]()

**Theory. Benchmarks. Tooling. Code. Labs. Production.**
*Everything you need to evaluate LLMs rigorously, from first principles to CI/CD integration.*

[Explore the Full Documentation](https://a217-anjali.github.io/llm-evaluation-framework/) |
[View the Portal](https://a217-anjali.github.io/llm-eval-hub/)

</div>

---

## Why This Exists

The LLM evaluation landscape in 2026 is simultaneously the most critical and most confusing part of the AI stack. With 300+ models ranked on Chatbot Arena, 50+ benchmarks of varying quality, and dozens of eval tools competing for attention, teams face real problems: Which benchmarks actually matter for my use case? How do I avoid contaminated results? Should I use LLM-as-judge or human evaluation? How do I set up continuous evaluation in production?

This framework answers all of those questions with depth, rigor, and working code.

## What's Inside

| Section | What You Get |
|---------|-------------|
| **Foundations** | Why evals matter, taxonomy of evaluation types, every major metric with formulas, statistical rigor guide |
| **Benchmarks** | Complete map of 50+ benchmarks across 12 categories with current (March 2026) model results |
| **Methods** | LLM-as-judge architecture, human evaluation protocols, RAG evaluation, pairwise/Elo systems, agentic eval, contamination detection |
| **Tooling** | Feature comparison of 25+ tools (DeepEval, lm-evaluation-harness, Inspect AI, Ragas, Promptfoo, LangSmith, Braintrust, and more) |
| **Hands-On Labs** | 9 complete labs with notebooks covering benchmarking, LLM-as-judge, RAG eval, safety red-teaming, agentic eval, custom domain eval, statistical analysis, CI/CD integration, and Pareto model selection |
| **Production** | Model selection frameworks, continuous evaluation, EvalOps architecture, reporting and governance |
| **References** | 60+ annotated papers, glossary, quarterly changelog of the eval landscape |
| **Reusable Library** | Python package with judges, metrics, harness, contamination detection, and model selection utilities |

## Quick Start

### Install the Framework Library

```bash
pip install -e ".[dev]"
```

### Run Your First Evaluation

```python
from llm_eval_framework.judges import RubricJudge
from llm_eval_framework.harness import EvalRunner, EvalConfig

# Define a rubric-based judge
judge = RubricJudge(
    model="gpt-4o",
    rubric={
        "accuracy": "Is the response factually correct? (1-5)",
        "completeness": "Does the response fully address the question? (1-5)",
        "clarity": "Is the response clear and well-structured? (1-5)",
    }
)

# Configure and run
config = EvalConfig.from_yaml("configs/benchmark_suite_basic.yaml")
runner = EvalRunner(config=config, judges=[judge])
results = await runner.run()
results.to_report("my_eval_report.html")
```

### Run the Labs

```bash
# Start Jupyter and open any lab notebook
jupyter lab notebooks/
```

### Build the Documentation Site

```bash
mkdocs serve  # Local preview at http://localhost:8000
```

## Project Structure

```
llm-evaluation-framework/
|-- README.md                          # You are here
|-- docs/                              # MkDocs Material documentation
|   |-- 01-foundations/                # Theory, metrics, statistics
|   |-- 02-benchmarks/                # Complete benchmark landscape
|   |-- 03-methods/                   # Evaluation methodologies
|   |-- 04-tooling/                   # Tool guides and comparisons
|   |-- 05-hands-on/                  # 9 lab guides
|   |-- 06-production/                # Production evaluation patterns
|   +-- 07-references/                # Papers, glossary, changelog
|-- notebooks/                         # Jupyter notebooks for all labs
|-- src/llm_eval_framework/           # Reusable Python library
|   |-- judges/                       # LLM-as-judge implementations
|   |-- metrics/                      # Custom evaluation metrics
|   |-- harness/                      # Evaluation runner and config
|   |-- contamination/                # Contamination detection tools
|   |-- selection/                    # Model selection (Pareto)
|   +-- utils/                        # Statistics, cost tracking, viz
|-- tests/                             # pytest test suite
|-- configs/                           # YAML configurations
+-- .github/workflows/                # CI/CD pipelines
```

## Current Landscape Snapshot (March 2026)

This framework is built on live research, not stale training data. Here's a snapshot of the current state:

**Frontier Models**: GPT-5.4, Claude Opus 4.6 (1M context), Gemini 3.1 Pro (leads 13/16 benchmarks), Grok 4.20 (2M context), Amazon Nova 2 Omni

**Top Open-Weight Models**: GLM-5 (745B MoE, MIT licensed, trained on Huawei Ascend), DeepSeek-V3.2 (671B MoE), Qwen 3.5/3.6, Llama 4 Scout/Maverick/Behemoth, Mistral Large 3

**Key Leaderboard Results**:
- Chatbot Arena: 333 models ranked, 5.6M+ votes, Claude Opus 4.6 leads coding (1561 Elo)
- SWE-bench Verified: Claude Opus 4.5 (80.9%), Gemini 3.1 Pro (80.6%)
- MMLU-Pro: Gemini 3 Pro Preview (89.8%)
- ARC-AGI-3: All frontier models <1% (genuine reasoning gap exposed)

**Critical Insight**: ARC-AGI-3 (March 2026) revealed that prior benchmark scores largely reflected format optimization, not genuine adaptive reasoning. Every frontier model dropped from 70-85% on ARC-AGI-2 to below 1% on ARC-AGI-3.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. We welcome contributions to benchmark coverage, tool guides, lab exercises, and the Python library.

## License

Apache 2.0. See [LICENSE](LICENSE) for details.

## Acknowledgments

Built with insights from the broader AI evaluation community, including researchers at Anthropic, Google DeepMind, EleutherAI, UK AISI, Hugging Face, LMSYS, Epoch AI, MLCommons, and the many open-source contributors who make rigorous evaluation possible.

---

<div align="center">

**If this framework helps your work, consider giving it a star.**

*Last updated: March 31, 2026*

</div>
