# LLM Evaluation Framework - Jupyter Notebooks

## Overview

Complete set of 9 Jupyter notebooks for comprehensive LLM evaluation, from basic benchmarking through statistical analysis and cost-quality-latency trade-off analysis.

## Notebooks

### Lab 01: Basic Benchmark (lab_01_basic_benchmark.ipynb)
- **Size**: 12 KB, 310 lines
- **Focus**: Foundation of LLM evaluation
- **Covers**:
  - Metric definitions (accuracy, BLEU, ROUGE, F1)
  - Test data creation (100 test cases)
  - Model evaluation on 3 models
  - Results aggregation and visualization
  - Basic statistical analysis
- **Key Output**: Benchmark scores, comparison tables, bar charts

### Lab 02: LLM-as-Judge (lab_02_llm_as_judge.ipynb)
- **Size**: 6.1 KB, 168 lines
- **Focus**: Using LLM as evaluator
- **Covers**:
  - Judge prompting and chain-of-thought
  - Rubric-based evaluation
  - Scoring calibration
  - Multi-dimension assessment
- **Key Output**: Quality judgments, rubric scores, judge consistency metrics

### Lab 03: RAG Evaluation Pipeline (lab_03_rag_eval_pipeline.ipynb)
- **Size**: 21 KB, 368 lines
- **Focus**: Specialized evaluation for retrieval-augmented generation
- **Covers**:
  - Retrieval evaluation (precision, recall, MRR)
  - Generation quality metrics
  - End-to-end RAG pipeline testing
  - Context relevance and answer correctness
- **Key Output**: RAG-specific metrics, retrieval effectiveness, generation quality

### Lab 04: Safety & Red Teaming (lab_04_safety_red_team.ipynb)
- **Size**: 19 KB, 497 lines
- **Focus**: Safety and adversarial evaluation
- **Covers**:
  - Red team prompt generation
  - Safety metric definitions
  - Jailbreak attempt detection
  - Harm categorization (bias, toxicity, illegal content)
  - Red team results analysis
- **Key Output**: Safety scores, red team effectiveness, adversarial analysis

### Lab 05: Agentic Evaluation (lab_05_agentic_eval.ipynb)
- **Size**: 24 KB, 532 lines
- **Focus**: Evaluating autonomous agent behavior
- **Covers**:
  - Tool use accuracy and appropriateness
  - Multi-step reasoning evaluation
  - Failure mode analysis
  - Agent trajectory assessment
  - Success rate by task complexity
- **Key Output**: Agent performance metrics, failure analysis, trajectory insights

### Lab 06: Custom Domain Evaluation - Legal Contracts (lab_06_custom_domain_eval.ipynb)
- **Size**: 24 KB, 498 lines
- **Focus**: Domain-specific evaluation (legal contract review)
- **Covers**:
  - Custom rubric definition (4 dimensions)
  - 10 contract types as test cases
  - LLM-as-judge scorer implementation
  - 3 model comparison (GPT-4o, Claude Sonnet, Llama Scout)
  - Statistical significance testing
  - Radar charts, heatmaps, CI visualizations
- **Key Output**: Domain-specific scores, model rankings, statistical comparisons

### Lab 07: Statistical Analysis (lab_07_statistical_analysis.ipynb)
- **Size**: 12 KB, 99 lines
- **Focus**: Advanced statistical methods
- **Covers**:
  - Bootstrap confidence intervals (10K resamples)
  - Paired permutation tests
  - Cohen's d and Cliff's delta effect sizes
  - Holm-Bonferroni multiple comparison correction
  - Publication-quality visualizations
- **Key Output**: CIs with error bars, p-value distributions, effect size comparisons

### Lab 08: CI/CD Integration (lab_08_eval_ci_cd.ipynb)
- **Size**: 44 KB, 924 lines
- **Focus**: Production integration and automation
- **Covers**:
  - Pytest-compatible test framework
  - Quality metric classes (accuracy, length, coherence)
  - GitHub Actions workflow configuration
  - Quality gates with thresholds
  - Cost budget tracking system
  - Slack notification setup
  - Local test execution demo
- **Key Output**: Test results, cost tracking, quality gate reports, CI/CD workflow

### Lab 09: Model Selection & Pareto Analysis (lab_09_model_selection_pareto.ipynb)
- **Size**: 8 KB, 87 lines
- **Focus**: Cost-quality-latency trade-off analysis
- **Covers**:
  - 7 model candidates with pricing
  - Quality evaluation (realistic benchmarks)
  - Cost analysis (monthly estimates)
  - Latency measurement
  - Pareto frontier computation
  - Use-case based recommendations (cost-sensitive, quality-first, balanced, latency-critical, mission-critical)
  - Multi-model strategies
- **Key Output**: Pareto frontier visualization, use-case recommendations, cost analysis

## Technical Details

### Format
- **Type**: Valid Jupyter Notebook JSON (.ipynb)
- **nbformat**: 4
- **Total Size**: 176 KB
- **Total Cells**: ~90 code cells, ~60 markdown cells

### Libraries Used
- **Data**: NumPy, Pandas
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Statistics**: SciPy (stats module)
- **Other**: json, dataclasses, typing, itertools

### Execution Requirements
- **Python Version**: 3.9+
- **Memory**: ~1-2 GB per notebook
- **Runtime**: 2-10 minutes per notebook (depends on bootstrap iterations)

## Key Features

### Comprehensive Coverage
- Basic to advanced evaluation techniques
- Domain-specific and general-purpose evaluation
- Safety and adversarial testing
- Production-ready CI/CD integration

### Statistical Rigor
- Bootstrap confidence intervals (non-parametric)
- Permutation tests (no distributional assumptions)
- Effect size calculations (Cohen's d, Cliff's delta)
- Multiple comparison corrections (Holm-Bonferroni)

### Publication Quality
- Professional visualizations (radar charts, heatmaps, forest plots)
- Detailed interpretation guides
- Full methodology documentation
- Reproducible results (seeded randomness)

### Production Ready
- GitHub Actions workflow templates
- Cost tracking and budgeting
- Slack notification integration
- Quality gate definitions
- Pytest-compatible test framework

## Usage Recommendations

### Learning Path
1. Start with Lab 01 (Basic Benchmark) to understand evaluation fundamentals
2. Progress through Labs 02-05 for specialized techniques
3. Lab 06 shows how to build custom domain evaluations
4. Labs 07-09 provide advanced statistical and operational insights

### For Research
- Labs 01, 06-07: Comprehensive evaluation methodology with statistical rigor
- Lab 03: RAG evaluation (specialized for retrieval systems)
- Lab 04: Safety evaluation (adversarial robustness)

### For Production
- Lab 08: Direct integration with CI/CD pipelines
- Lab 09: Model selection framework for deployment decisions
- All labs: Reproducible evaluation processes

## Customization

Each notebook can be customized for specific needs:
- **Custom metrics**: Modify metric definitions in Labs 01, 06
- **Domain evaluation**: Use Lab 06 template for new domains
- **Statistical tests**: Extend Lab 07 with additional tests
- **Models**: Update model lists and pricing in Lab 09
- **CI/CD**: Adapt Lab 08 workflow to your platform

## Notes

- All notebooks use seed 42 for reproducibility
- Synthetic data is used in most labs for demonstration
- Can be adapted to use real API calls (OpenAI, Anthropic, etc.)
- Performance metrics include accuracy, quality, cost, and latency dimensions
