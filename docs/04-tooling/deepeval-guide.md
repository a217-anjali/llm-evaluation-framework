# DeepEval: Complete Implementation Guide

**Version:** DeepEval v3.2.6+
**License:** Apache 2.0
**Latest Update:** March 2026

DeepEval is the most popular open-source LLM evaluation framework with 13k+ GitHub stars and 3M monthly PyPI downloads. It provides 50+ pre-built metrics, pytest integration, and agentic evaluation capabilities.

## Installation & Setup

### Basic Installation

```bash
pip install deepeval
```

### With Optional Dependencies

```bash
# For advanced features
pip install deepeval[langchain]     # LangChain integration
pip install deepeval[ollama]        # Local LLM support
pip install deepeval[all]           # Everything

# Verify installation
python -c "import deepeval; print(deepeval.__version__)"
```

### API Key Configuration

```bash
# OpenAI (for evaluation LLM judge)
export OPENAI_API_KEY="sk-..."

# Optional: Azure OpenAI
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://..."

# Optional: Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional: HuggingFace
export HUGGINGFACE_API_KEY="hf_..."
```

### Minimal Configuration File

Create `deepeval.ini`:

```ini
[deepeval]
api_key = your_openai_key_here
model = gpt-4  # or gpt-3.5-turbo for cost savings
timeout = 60
use_cache = true
```

## Your First Evaluation

### Simple Metric Evaluation

```python
from deepeval.metrics import Faithfulness, AnswerRelevancy
from deepeval.test_cases import LLMTestCase

# Define test case
test_case = LLMTestCase(
    input="What is the capital of France?",
    actual_output="Paris is the capital of France.",
    expected_output="Paris"
)

# Create metrics
faithfulness = Faithfulness()
relevancy = AnswerRelevancy()

# Run evaluation
print(faithfulness.measure(test_case))  # Score: 0-1
print(relevancy.measure(test_case))      # Score: 0-1
```

### Batch Evaluation

```python
from deepeval import evaluate
from deepeval.metrics import Hallucination
from deepeval.test_cases import LLMTestCase

# Create multiple test cases
test_cases = [
    LLMTestCase(
        input="Who won the 2024 World Cup?",
        actual_output="Argentina won the 2024 World Cup.",
        context=["Argentina defeated France in the 2022 World Cup final."]
    ),
    LLMTestCase(
        input="What is Python?",
        actual_output="Python is a programming language.",
        context=["Python is a high-level programming language."]
    ),
]

# Evaluate all at once
results = evaluate(test_cases, [Hallucination()])

# Print summary
print(f"Pass Rate: {results.pass_rate}%")
print(f"Average Score: {results.average_score}")
```

## Pre-built Metrics (50+)

### Reference-Free Metrics

```python
from deepeval.metrics import (
    Faithfulness,        # Answer grounded in context
    Hallucination,       # No hallucinated content
    AnswerRelevancy,     # Answer directly answers question
    ContextualRelevancy, # Context is relevant to input
    Summarization,       # Summary quality
    Coherence,          # Logical flow and clarity
)

# Usage pattern
metric = Hallucination()
metric.measure(test_case)
```

### Reference-Based Metrics

```python
from deepeval.metrics import (
    BLEU,               # Exact match similarity
    ROUGE,              # Overlap-based similarity
    Cosine,             # Semantic similarity
    Ragas,              # RAG-specific metrics
    ToxicityMetric,     # Content safety
)

# Reference-based requires expected_output
test_case = LLMTestCase(
    input="Summarize quantum computing",
    actual_output="Quantum computing uses qubits...",
    expected_output="Quantum computing harnesses quantum mechanics..."
)

metric = BLEU()
metric.measure(test_case)  # Compares actual vs expected
```

### Bias & Fairness Metrics

```python
from deepeval.metrics import BiasMetric

bias_metric = BiasMetric()
bias_metric.measure(test_case)

# Detects: gender bias, racial bias, religious bias
# Threshold typically: score < 0.5 indicates bias present
```

### Custom Code Evaluation

```python
from deepeval.metrics import CustomMetric
from deepeval.test_cases import LLMTestCase

# Define custom scoring function
def custom_scorer(actual_output: str) -> float:
    """Returns score 0-1"""
    if "error" in actual_output.lower():
        return 0.0
    if len(actual_output) < 10:
        return 0.3
    return 0.9

metric = CustomMetric(
    name="Custom Output Validator",
    measurement=custom_scorer,
    threshold=0.5
)

metric.measure(test_case)
```

## Pytest Integration

### Setup for Pytest

```bash
pip install pytest
```

### Test File Structure

```python
# tests/test_llm_responses.py
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancy, Faithfulness
from deepeval.test_cases import LLMTestCase

def test_answer_relevancy():
    test_case = LLMTestCase(
        input="What is machine learning?",
        actual_output="Machine learning enables systems to learn from data.",
    )
    assert_test(test_case, [AnswerRelevancy()])

def test_hallucination_free():
    test_case = LLMTestCase(
        input="Current date?",
        actual_output="Today is March 31, 2026.",
        context=["Current date is March 31, 2026."]
    )
    assert_test(test_case, [Hallucination()])

def test_multiple_metrics():
    test_case = LLMTestCase(
        input="Explain AI safety",
        actual_output="AI safety addresses preventing harmful AI outcomes...",
        context=["AI safety is a research field..."]
    )
    metrics = [
        AnswerRelevancy(threshold=0.7),
        Hallucination(threshold=0.5),
    ]
    assert_test(test_case, metrics)
```

### Run Pytest

```bash
# Run all tests
pytest tests/test_llm_responses.py -v

# Run with coverage
pytest tests/test_llm_responses.py --cov

# Run specific test
pytest tests/test_llm_responses.py::test_hallucination_free -v

# Exit on first failure
pytest tests/test_llm_responses.py -x
```

### CI/CD Integration

```yaml
# .github/workflows/eval.yml
name: LLM Evaluation Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install deepeval pytest
      - run: export OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
      - run: pytest tests/test_llm_responses.py -v --tb=short
```

## Advanced Features

### Custom Metrics

```python
from deepeval.metrics.utils import (
    get_or_create_metric,
    get_metric_score_by_name
)
from deepeval.test_cases import LLMTestCase

# Template for custom metric
class CustomSimilarityMetric:
    def __init__(self, name: str = "Custom Similarity", threshold: float = 0.5):
        self.name = name
        self.threshold = threshold

    def measure(self, test_case: LLMTestCase) -> float:
        from sentence_transformers import SentenceTransformer

        # Load embedding model
        model = SentenceTransformer('all-MiniLM-L6-v2')

        # Embed outputs
        actual_embed = model.encode(test_case.actual_output)
        expected_embed = model.encode(test_case.expected_output or "")

        # Compute cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity([actual_embed], [expected_embed])[0][0]

        # Set score and threshold
        test_case.success = similarity >= self.threshold
        test_case.score = float(similarity)

        return float(similarity)
```

### Agentic Evaluation

DeepEval v3.0+ supports evaluating LLM agent trajectories:

```python
from deepeval.metrics import AgentGoalCompletion
from deepeval.test_cases import LLMTestCase

# Agent trajectory: sequence of actions + reasoning
test_case = LLMTestCase(
    input="Book a flight from NYC to LA on March 31",
    actual_output="Flight booked successfully",
    context=[
        "Agent Action 1: Query flight database",
        "Agent Observation: Found flights",
        "Agent Action 2: Check user preferences",
        "Agent Observation: User prefers morning flights",
        "Agent Action 3: Book flight at 8:00 AM",
        "Agent Observation: Booking confirmed"
    ]
)

# Evaluate if agent correctly completed goal
metric = AgentGoalCompletion()
metric.measure(test_case)
```

### Caching & Performance

```python
from deepeval import cache_metrics
from deepeval.metrics import Faithfulness

# Enable caching
cache_metrics(enable=True)  # Caches results by hash

# For expensive evaluations, avoid re-running
test_case = LLMTestCase(
    input="Define entropy",
    actual_output="Entropy measures disorder in a system..."
)

metric = Faithfulness()
# First run: ~2 seconds (calls LLM judge)
result1 = metric.measure(test_case)

# Second run: <100ms (cached)
result2 = metric.measure(test_case)

assert result1 == result2
```

### Parallel Evaluation

```python
from deepeval import evaluate
from deepeval.metrics import Hallucination, AnswerRelevancy
import concurrent.futures

test_cases = [...]  # 1000+ test cases

# Parallelize evaluation
results = evaluate(
    test_cases,
    [Hallucination(), AnswerRelevancy()],
    max_workers=10,  # Use 10 parallel workers
    run_async=True
)

print(f"Completed {len(results)} evaluations")
print(f"Pass Rate: {results.pass_rate}%")
```

## RAG & LangChain Integration

### With LangChain Chains

```python
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from deepeval.test_cases import LLMTestCase
from deepeval.metrics import Hallucination, Faithfulness

# Setup RAG chain
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4"),
    retriever=vectorstore.as_retriever()
)

# Evaluate chain output
question = "What is AI safety?"
response = qa_chain.invoke({"query": question})

test_case = LLMTestCase(
    input=question,
    actual_output=response["result"],
    context=response["source_documents"]  # Retrieved chunks
)

# Evaluate
faithfulness = Faithfulness()
hallucination = Hallucination()

print(f"Faithfulness: {faithfulness.measure(test_case)}")
print(f"Hallucination: {hallucination.measure(test_case)}")
```

### Custom Dataset Management

```python
from deepeval.dataset import EvaluationDataset
from deepeval.test_cases import LLMTestCase

# Create dataset
dataset = EvaluationDataset()
dataset.add_test_cases([
    LLMTestCase(
        input="What is Python?",
        expected_output="A programming language",
    ),
    LLMTestCase(
        input="What year was AI founded?",
        expected_output="1956 at Dartmouth"
    ),
])

# Save dataset
dataset.save_as_json("datasets/my_eval.json")

# Load dataset
dataset_loaded = EvaluationDataset()
dataset_loaded.load_json("datasets/my_eval.json")
```

## Monitoring & Logging

### Structured Logging

```python
import logging
from deepeval.logger import DeepEvalLogger

# Configure logging
logger = DeepEvalLogger()
logger.set_level(logging.DEBUG)
logger.to_file("deepeval.log")

# All evaluations logged automatically
# - Input/output pairs
# - Metric scores
# - Execution time
# - Model used
```

### Metric Statistics

```python
from deepeval import evaluate
from deepeval.metrics import Hallucination

# Run evaluation
results = evaluate(test_cases, [Hallucination()])

# Access detailed metrics
print(f"Total Tests: {results.total_count}")
print(f"Passed: {results.success_count}")
print(f"Failed: {results.failed_count}")
print(f"Pass Rate: {results.pass_rate}%")
print(f"Average Score: {results.average_score:.3f}")

# Per-metric breakdown
for metric_name, scores in results.scores_by_metric.items():
    print(f"{metric_name}: mean={sum(scores)/len(scores):.2f}")
```

## Troubleshooting

### Common Issues & Solutions

**Issue: "OpenAI API key not found"**
```python
import os
from deepeval.metrics import Hallucination

# Set key directly
os.environ["OPENAI_API_KEY"] = "sk-..."

metric = Hallucination()
# Now works
```

**Issue: "Model rate limit exceeded"**
```python
import time
from deepeval.metrics import Hallucination

# Add delay between evaluations
for test_case in test_cases:
    metric = Hallucination()
    metric.measure(test_case)
    time.sleep(1)  # 1 second delay
```

**Issue: "Evaluation too slow"**
```python
# Solution 1: Use faster model
from deepeval.metrics import Hallucination

metric = Hallucination(model="gpt-3.5-turbo")  # 5x faster, cheaper
metric.measure(test_case)

# Solution 2: Batch process
from deepeval import evaluate

results = evaluate(
    test_cases,
    [Hallucination()],
    run_async=True,
    max_workers=10
)
```

**Issue: "Metric score is always 1.0 (too lenient)"**
```python
# Increase metric strictness
from deepeval.metrics import Hallucination

metric = Hallucination(
    threshold=0.8,  # Higher threshold = stricter
    use_strict_mode=True  # Additional strictness
)
```

## Pros & Cons

### Advantages
- **Easiest to start:** `pip install` → 5 lines of code
- **Most metrics:** 50+ pre-built options
- **pytest native:** Integrates with standard testing workflows
- **No cost:** Fully open source, self-hostable
- **Well maintained:** Active development, 13k+ stars
- **LLM-agnostic:** Works with any API (OpenAI, Anthropic, Ollama)
- **Good documentation:** Clear examples, active community

### Disadvantages
- **LLM judge costs:** Every evaluation calls an LLM (adds $0.01-0.50 per test)
- **Limited production features:** No built-in monitoring dashboard
- **No multi-user:** Designed for single-user/team notebooks
- **Metric quality varies:** Some metrics less robust than others
- **No built-in sampling:** Must manage test set yourself
- **Slower than reference-based:** LLM-as-judge slower than string matching

## Performance Benchmarks (March 2026)

| Task | Time | Cost | Notes |
|------|------|------|-------|
| Single Hallucination check | 2-4s | $0.01-0.02 | GPT-4 |
| 100 test cases (serial) | 200-400s | $1-2 | 4-5 min |
| 100 test cases (parallel x10) | 20-40s | $1-2 | Recommended |
| 1000 test cases (parallel x10) | 200-400s | $10-20 | 3-6 min |

**Cost optimization:**
- Use gpt-3.5-turbo: 5x cheaper, 30% slower
- Use caching: Reduces cost by 50-80%
- Batch evaluations: More parallelization

## When to Use DeepEval

**Best For:**
- CI/CD integration with pytest
- Quick prototyping (5-minute setup)
- Teams already using Python/pytest
- Organizations with OpenAI/Anthropic budgets
- Starting with LLM evaluation (learning curve minimal)

**Not Best For:**
- Budget-constrained evaluation (high LLM judge costs)
- Large-scale production monitoring (100k+ evals/day)
- On-premises requirements (requires external API)
- Real-time inference evaluation (too slow)
- Complex multi-agent workflows (limited agent features)

## Comparison with Alternatives

| Feature | DeepEval | Inspect AI | Promptfoo |
|---------|----------|-----------|-----------|
| Setup time | 5 min | 15 min | 10 min |
| Metrics count | 50+ | 100+ | 30+ |
| Safety focus | Moderate | High | High |
| Agentic | Basic | Advanced | Moderate |
| Cost | $0 (+ LLM judge) | $0 | $0 |
| Maturity | Very high | High | Moderate |
| Docs quality | Excellent | Good | Good |

## Next Steps

1. **Install:** `pip install deepeval`
2. **Run example:** Follow "Your First Evaluation" section
3. **Integrate:** Add to your CI/CD pipeline
4. **Customize:** Build custom metrics for your domain
5. **Monitor:** Set up logging and dashboards

## Resources

- **Official Docs:** https://docs.confident-ai.com
- **GitHub:** https://github.com/confident-ai/deepeval
- **Examples:** https://github.com/confident-ai/deepeval/tree/main/examples
- **Community:** Slack #deepeval channel

---

**Document Version:** 1.0
**Last Verified:** March 31, 2026
