# Building a Custom LLM Evaluation Harness from Scratch

**Version:** 1.0
**Last Updated:** March 2026

This guide covers building your own LLM evaluation framework in Python when existing tools don't meet your needs. Includes complete architecture, working code examples, and when to build custom vs use existing tools.

## Architecture Overview

A minimal evaluation harness needs these components:

```
┌─────────────────────────────────────────────────────────────┐
│                  Custom Evaluation Harness                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌─────────────┐  ┌────────────────┐     │
│  │ Config Loader│  │Model Factory│  │Metric Compute  │     │
│  │(YAML/JSON)  │  │(OpenAI, etc)│  │(Custom logic)  │     │
│  └──────────────┘  └─────────────┘  └────────────────┘     │
│         ↓                 ↓                  ↓               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           Evaluation Pipeline Orchestrator            │  │
│  │  - Load config  - Run models  - Compute metrics       │  │
│  │  - Parallel execution  - Handle failures              │  │
│  └──────────────────────────────────────────────────────┘  │
│         ↓                 ↓                  ↓               │
│  ┌──────────────┐  ┌─────────────┐  ┌────────────────┐     │
│  │  Data Store  │  │   Logger    │  │ Results Exporter
│  │(JSON/CSV)   │  │(Structured) │  │ (CSV/JSON/MD)  │     │
│  └──────────────┘  └─────────────┘  └────────────────┘     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Complete Working Implementation

### Project Structure

```
custom-eval-harness/
├── config.yaml                 # Configuration
├── requirements.txt            # Dependencies
├── harness.py                  # Main evaluation engine
├── metrics.py                  # Metric definitions
├── models.py                   # Model interfaces
├── data/
│   ├── test_cases.json        # Evaluation data
│   └── ground_truth.json      # Expected outputs
├── results/
│   ├── eval_results.json      # Raw results
│   ├── eval_report.csv        # Summary report
│   └── eval_report.md         # Markdown report
└── tests/
    └── test_harness.py        # Unit tests
```

### Configuration File (config.yaml)

```yaml
# config.yaml
evaluation:
  name: "My LLM Evaluation"
  version: "1.0"
  timestamp: "2026-03-31"

models:
  gpt4:
    provider: "openai"
    model: "gpt-4"
    temperature: 0.7
    max_tokens: 500

  gpt35:
    provider: "openai"
    model: "gpt-3.5-turbo"
    temperature: 0.7
    max_tokens: 500

  claude:
    provider: "anthropic"
    model: "claude-opus"
    temperature: 0.7
    max_tokens: 500

metrics:
  - name: "exact_match"
    type: "reference_based"
    threshold: 1.0

  - name: "contains"
    type: "reference_based"
    pattern: "machine learning"
    threshold: 0.0

  - name: "length"
    type: "custom"
    min_length: 50
    max_length: 500

  - name: "similarity"
    type: "semantic"
    model: "sentence-transformers/all-MiniLM-L6-v2"
    threshold: 0.7

data:
  test_cases_file: "data/test_cases.json"
  batch_size: 32
  max_samples: 1000

execution:
  parallel_workers: 10
  timeout_seconds: 60
  retry_attempts: 3
  retry_delay: 1.0

output:
  results_file: "results/eval_results.json"
  report_file: "results/eval_report.md"
  csv_file: "results/eval_report.csv"
```

### Main Evaluation Engine (harness.py)

```python
# harness.py
import asyncio
import json
import logging
from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import yaml
from concurrent.futures import ThreadPoolExecutor
import csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    """Single evaluation test case"""
    id: str
    input: str
    expected_output: str = None
    metadata: Dict = None

    def to_dict(self):
        return {
            "id": self.id,
            "input": self.input,
            "expected_output": self.expected_output,
            "metadata": self.metadata or {}
        }


@dataclass
class EvaluationResult:
    """Result of evaluating one test case"""
    test_case_id: str
    model: str
    output: str
    metrics: Dict[str, float]
    latency_ms: float
    cost: float
    timestamp: str
    error: str = None

    def to_dict(self):
        return {
            "test_case_id": self.test_case_id,
            "model": self.model,
            "output": self.output,
            "metrics": self.metrics,
            "latency_ms": self.latency_ms,
            "cost": self.cost,
            "timestamp": self.timestamp,
            "error": self.error
        }


class ConfigLoader:
    """Load evaluation configuration from YAML"""

    @staticmethod
    def load(config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)


class DataLoader:
    """Load test cases from JSON"""

    @staticmethod
    def load_test_cases(filepath: str, max_samples: int = None) -> List[TestCase]:
        with open(filepath, 'r') as f:
            data = json.load(f)

        test_cases = []
        for item in data[:max_samples] if max_samples else data:
            test_cases.append(TestCase(
                id=item.get("id", str(len(test_cases))),
                input=item["input"],
                expected_output=item.get("expected_output"),
                metadata=item.get("metadata", {})
            ))

        logger.info(f"Loaded {len(test_cases)} test cases")
        return test_cases


class ModelInterface:
    """Abstract interface for LLM models"""

    async def generate(self, prompt: str) -> tuple[str, float, float]:
        """
        Generate response from model
        Returns: (output, latency_ms, cost)
        """
        raise NotImplementedError

    def __init__(self, config: Dict[str, Any]):
        self.config = config


class OpenAIModel(ModelInterface):
    """OpenAI API implementation"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI()
        self.model = config.get("model", "gpt-4")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 500)

    async def generate(self, prompt: str) -> tuple[str, float, float]:
        import time
        start_time = time.time()

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            output = response.choices[0].message.content
            latency_ms = (time.time() - start_time) * 1000

            # Pricing (March 2026 rates)
            pricing = {
                "gpt-4": {"input": 0.003, "output": 0.006},
                "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
            }
            model_price = pricing.get(self.model, {"input": 0.001, "output": 0.002})
            cost = (
                response.usage.prompt_tokens * model_price["input"] / 1000 +
                response.usage.completion_tokens * model_price["output"] / 1000
            )

            return output, latency_ms, cost

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise


class AnthropicModel(ModelInterface):
    """Anthropic Claude implementation"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        from anthropic import AsyncAnthropic
        self.client = AsyncAnthropic()
        self.model = config.get("model", "claude-opus")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 500)

    async def generate(self, prompt: str) -> tuple[str, float, float]:
        import time
        start_time = time.time()

        try:
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{"role": "user", "content": prompt}]
            )

            output = message.content[0].text
            latency_ms = (time.time() - start_time) * 1000

            # Pricing for Anthropic
            pricing = {
                "claude-opus": {"input": 0.015, "output": 0.075},
                "claude-sonnet": {"input": 0.003, "output": 0.015},
            }
            model_price = pricing.get(self.model, {"input": 0.008, "output": 0.024})
            cost = (
                message.usage.input_tokens * model_price["input"] / 1000 +
                message.usage.output_tokens * model_price["output"] / 1000
            )

            return output, latency_ms, cost

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise


class ModelFactory:
    """Factory for creating model instances"""

    @staticmethod
    def create(config: Dict[str, Any]) -> ModelInterface:
        provider = config.get("provider", "openai")

        if provider == "openai":
            return OpenAIModel(config)
        elif provider == "anthropic":
            return AnthropicModel(config)
        else:
            raise ValueError(f"Unknown provider: {provider}")


class MetricComputer:
    """Compute evaluation metrics"""

    def __init__(self, metrics_config: List[Dict[str, Any]]):
        self.metrics_config = metrics_config

    def compute_all(
        self,
        test_case: TestCase,
        output: str
    ) -> Dict[str, float]:
        """Compute all metrics for test case"""
        metrics = {}

        for metric_config in self.metrics_config:
            metric_name = metric_config["name"]
            metric_type = metric_config.get("type", "custom")

            try:
                if metric_type == "exact_match":
                    metrics[metric_name] = self._exact_match(
                        test_case.expected_output,
                        output
                    )
                elif metric_type == "reference_based":
                    metrics[metric_name] = self._contains(
                        metric_config,
                        output
                    )
                elif metric_type == "semantic":
                    metrics[metric_name] = self._semantic_similarity(
                        metric_config,
                        test_case.expected_output,
                        output
                    )
                elif metric_type == "custom":
                    metrics[metric_name] = self._custom_metric(
                        metric_config,
                        output
                    )
            except Exception as e:
                logger.warning(f"Error computing {metric_name}: {e}")
                metrics[metric_name] = 0.0

        return metrics

    def _exact_match(self, expected: str, actual: str) -> float:
        """Exact string match"""
        if not expected:
            return 0.0
        return 1.0 if expected.strip() == actual.strip() else 0.0

    def _contains(self, config: Dict, output: str) -> float:
        """Check if output contains pattern"""
        pattern = config.get("pattern", "")
        return 1.0 if pattern.lower() in output.lower() else 0.0

    def _semantic_similarity(
        self,
        config: Dict,
        expected: str,
        actual: str
    ) -> float:
        """Compute semantic similarity using embeddings"""
        try:
            from sentence_transformers import SentenceTransformer
            model_name = config.get("model", "sentence-transformers/all-MiniLM-L6-v2")
            model = SentenceTransformer(model_name)

            # Compute embeddings
            expected_embed = model.encode(expected or "", convert_to_tensor=True)
            actual_embed = model.encode(actual or "", convert_to_tensor=True)

            # Cosine similarity
            from sentence_transformers import util
            similarity = util.pytorch_cos_sim(expected_embed, actual_embed).item()

            return float(similarity)
        except Exception as e:
            logger.warning(f"Semantic similarity error: {e}")
            return 0.0

    def _custom_metric(self, config: Dict, output: str) -> float:
        """Custom business logic metric"""
        if config["name"] == "length":
            output_len = len(output)
            min_len = config.get("min_length", 0)
            max_len = config.get("max_length", float('inf'))

            if min_len <= output_len <= max_len:
                return 1.0
            else:
                return 0.0

        return 0.0


class EvaluationOrchestrator:
    """Orchestrate the evaluation pipeline"""

    def __init__(
        self,
        config: Dict[str, Any],
        test_cases: List[TestCase],
        models: Dict[str, ModelInterface],
        metric_computer: MetricComputer
    ):
        self.config = config
        self.test_cases = test_cases
        self.models = models
        self.metric_computer = metric_computer
        self.results: List[EvaluationResult] = []

    async def run_async(self) -> List[EvaluationResult]:
        """Run evaluation with async concurrency"""
        execution_config = self.config.get("execution", {})
        max_workers = execution_config.get("parallel_workers", 10)

        tasks = []
        for test_case in self.test_cases:
            for model_name, model in self.models.items():
                task = self._evaluate_single_async(test_case, model_name, model)
                tasks.append(task)

        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Task failed: {result}")
            else:
                self.results.append(result)

        return self.results

    async def _evaluate_single_async(
        self,
        test_case: TestCase,
        model_name: str,
        model: ModelInterface
    ) -> EvaluationResult:
        """Evaluate single test case with single model"""
        import time

        try:
            # Generate response
            output, latency_ms, cost = await model.generate(test_case.input)

            # Compute metrics
            metrics = self.metric_computer.compute_all(test_case, output)

            # Create result
            result = EvaluationResult(
                test_case_id=test_case.id,
                model=model_name,
                output=output,
                metrics=metrics,
                latency_ms=latency_ms,
                cost=cost,
                timestamp=datetime.now().isoformat()
            )

            logger.info(
                f"✓ {test_case.id} / {model_name} - "
                f"Latency: {latency_ms:.0f}ms, Cost: ${cost:.4f}"
            )

            return result

        except Exception as e:
            logger.error(f"✗ {test_case.id} / {model_name} - {e}")
            return EvaluationResult(
                test_case_id=test_case.id,
                model=model_name,
                output="",
                metrics={},
                latency_ms=0,
                cost=0,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )

    def run(self) -> List[EvaluationResult]:
        """Run evaluation (blocking)"""
        return asyncio.run(self.run_async())


class ResultsExporter:
    """Export evaluation results to various formats"""

    @staticmethod
    def export_json(results: List[EvaluationResult], filepath: str):
        """Export to JSON"""
        data = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_evaluations": len(results),
            },
            "results": [r.to_dict() for r in results]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported JSON results to {filepath}")

    @staticmethod
    def export_csv(results: List[EvaluationResult], filepath: str):
        """Export to CSV"""
        if not results:
            return

        # Flatten results
        rows = []
        for result in results:
            row = {
                "test_case_id": result.test_case_id,
                "model": result.model,
                "latency_ms": result.latency_ms,
                "cost": result.cost,
                "error": result.error or "",
            }
            # Add metrics
            row.update(result.metrics)
            rows.append(row)

        # Write CSV
        if rows:
            keys = rows[0].keys()
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(rows)

        logger.info(f"Exported CSV results to {filepath}")

    @staticmethod
    def export_markdown_report(
        results: List[EvaluationResult],
        filepath: str,
        config: Dict[str, Any]
    ):
        """Export to Markdown report"""
        from collections import defaultdict

        # Aggregate results by model
        model_results = defaultdict(list)
        for result in results:
            model_results[result.model].append(result)

        # Generate report
        lines = [
            "# LLM Evaluation Report\n",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            f"**Configuration:** {config.get('evaluation', {}).get('name', 'Unknown')}\n\n",
        ]

        lines.append("## Summary\n")
        lines.append(f"- Total evaluations: {len(results)}\n")
        lines.append(f"- Models tested: {len(model_results)}\n")
        lines.append(f"- Test cases: {len(set(r.test_case_id for r in results))}\n\n")

        # Per-model summary
        lines.append("## Model Performance\n\n")

        for model_name in sorted(model_results.keys()):
            model_evals = model_results[model_name]

            # Calculate aggregates
            avg_latency = sum(r.latency_ms for r in model_evals) / len(model_evals)
            total_cost = sum(r.cost for r in model_evals)
            error_count = sum(1 for r in model_evals if r.error)

            lines.append(f"### {model_name}\n")
            lines.append(f"- Evaluations: {len(model_evals)}\n")
            lines.append(f"- Avg latency: {avg_latency:.0f}ms\n")
            lines.append(f"- Total cost: ${total_cost:.2f}\n")
            lines.append(f"- Errors: {error_count}\n")

            # Metric averages
            if model_evals and model_evals[0].metrics:
                lines.append("- Metrics:\n")
                for metric_name in model_evals[0].metrics.keys():
                    values = [
                        r.metrics[metric_name] for r in model_evals
                        if metric_name in r.metrics
                    ]
                    if values:
                        avg = sum(values) / len(values)
                        lines.append(f"  - {metric_name}: {avg:.3f}\n")

            lines.append("\n")

        # Write report
        with open(filepath, 'w') as f:
            f.writelines(lines)

        logger.info(f"Exported Markdown report to {filepath}")


def main():
    """Main evaluation script"""
    import argparse

    parser = argparse.ArgumentParser(description="LLM Evaluation Harness")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    args = parser.parse_args()

    # Load configuration
    config = ConfigLoader.load(args.config)
    logger.info("Loaded configuration")

    # Load test cases
    data_config = config.get("data", {})
    test_cases = DataLoader.load_test_cases(
        data_config.get("test_cases_file"),
        max_samples=data_config.get("max_samples")
    )

    # Create model instances
    models = {}
    for model_name, model_config in config.get("models", {}).items():
        models[model_name] = ModelFactory.create(model_config)
        logger.info(f"Created model: {model_name}")

    # Create metric computer
    metric_computer = MetricComputer(config.get("metrics", []))

    # Run evaluation
    orchestrator = EvaluationOrchestrator(
        config,
        test_cases,
        models,
        metric_computer
    )

    logger.info("Starting evaluation...")
    results = orchestrator.run()
    logger.info(f"Completed {len(results)} evaluations")

    # Export results
    output_config = config.get("output", {})
    ResultsExporter.export_json(results, output_config.get("results_file", "results.json"))
    ResultsExporter.export_csv(results, output_config.get("csv_file", "results.csv"))
    ResultsExporter.export_markdown_report(
        results,
        output_config.get("report_file", "report.md"),
        config
    )

    logger.info("Evaluation complete!")


if __name__ == "__main__":
    main()
```

### Data File (data/test_cases.json)

```json
[
  {
    "id": "qa_001",
    "input": "What is machine learning?",
    "expected_output": "Machine learning is a subset of artificial intelligence that enables systems to learn from data without being explicitly programmed.",
    "metadata": {
      "category": "definitions",
      "difficulty": "easy"
    }
  },
  {
    "id": "qa_002",
    "input": "Explain the transformer architecture",
    "expected_output": "Transformers use attention mechanisms to process sequences in parallel, allowing for efficient training and superior performance on NLP tasks.",
    "metadata": {
      "category": "technical",
      "difficulty": "hard"
    }
  }
]
```

### Requirements File

```
requirements.txt
openai>=1.0.0
anthropic>=0.7.0
pyyaml>=6.0
sentence-transformers>=2.2.0
torch>=2.0.0
```

## When to Build Custom vs Use Existing Tools

### Build Custom When:

1. **Domain-specific metrics:** Your metrics don't exist in standard tools
2. **Complex integration:** Need tight integration with proprietary systems
3. **Cost optimization:** Custom harness can be 10x cheaper than SaaS
4. **Data privacy:** Cannot send data to external services
5. **Unique workflows:** Non-standard evaluation pipeline
6. **Learning:** Want to understand evaluation internals deeply

**Example custom metric:**
```python
def custom_risk_scoring(output: str, regulations: List[str]) -> float:
    """Company-specific risk evaluation"""
    risk_score = 0.0
    for regulation in regulations:
        if violates_regulation(output, regulation):
            risk_score += 0.1
    return max(0.0, 1.0 - risk_score)
```

### Use Existing Tools When:

1. **Standard metrics:** Exact match, BLEU, semantic similarity, etc.
2. **Time pressure:** Need results in days, not weeks
3. **Scale required:** Need distributed evaluation across 100+ GPUs
4. **Team size:** Team doesn't have ML/DevOps expertise
5. **Features needed:** Need human annotation, dashboards, alerts
6. **Benchmark alignment:** Need MMLU, GSM8K, etc.

## Performance Optimization Tips

### Parallel Execution

```python
# Current: Sequential (slow)
for test_case in test_cases:
    for model in models:
        result = evaluate(test_case, model)

# Optimized: Async parallel (10x faster)
results = await orchestrator.run_async()
```

### Batch Processing

```python
# Batch 32 prompts for a single model call
batch_size = 32
for i in range(0, len(test_cases), batch_size):
    batch = test_cases[i:i+batch_size]
    results = model.generate_batch(batch)  # Faster than sequential
```

### Caching

```python
import hashlib
import json

def cache_key(test_case: TestCase, model_name: str) -> str:
    data = f"{test_case.input}:{model_name}"
    return hashlib.md5(data.encode()).hexdigest()

# Check cache before calling model
if cache_key in results_cache:
    return results_cache[cache_key]

# Call model and cache
result = await model.generate(test_case.input)
results_cache[cache_key] = result
```

## Cost Estimation

For a custom harness evaluating 1000 test cases on 3 models:

| Component | Cost | Notes |
|-----------|------|-------|
| GPT-4 | $15 | 1000 x 3 calls |
| GPT-3.5 | $3 | Cheaper alternative |
| Embedding model | $0 | Local (free) |
| Hosting | $0 | Your infrastructure |
| **Total** | **$3-15** | vs $500+ for SaaS |

## Production Deployment

### Docker Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "harness.py"]
```

### Kubernetes Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: llm-evaluation
spec:
  template:
    spec:
      containers:
      - name: eval
        image: custom-eval-harness:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai
      restartPolicy: Never
```

## Comparison: Custom vs Tools

| Factor | Custom | DeepEval | LangSmith |
|--------|--------|----------|-----------|
| Setup time | 1-2 weeks | 5 min | 30 min |
| Cost/1000 evals | $3-15 | $50 | $500+ |
| Customization | 100% | 50% | 20% |
| Support | Self | Community | Commercial |
| Time to value | 2 weeks | 1 hour | 1 day |
| Team size needed | 1-2 ML eng | 1 engineer | 1 product manager |

## Next Steps

1. **Evaluate feasibility:** Do you need custom metrics or complex workflows?
2. **Start with open source:** Try DeepEval first
3. **Prototype custom:** Build minimal harness (300 lines)
4. **Iterate:** Add metrics based on needs
5. **Optimize:** Parallelize and cache
6. **Deploy:** Containerize and automate

## Resources for Building Custom Tools

- **AsyncIO tutorial:** https://docs.python.org/3/library/asyncio.html
- **OpenAI API docs:** https://platform.openai.com/docs
- **Anthropic API docs:** https://docs.anthropic.com
- **Sentence Transformers:** https://www.sbert.net

---

**Document Version:** 1.0
**Last Verified:** March 31, 2026
