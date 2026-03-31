# Braintrust: Enterprise Evaluation & Scoring Guide

**Version:** Braintrust (current)
**Type:** Commercial SaaS
**Pricing:** Custom, starting $1000+/month
**Users:** Notion, Stripe, Vercel
**Latest Update:** March 2026

Braintrust is an enterprise-grade evaluation platform with 25+ built-in scorers, online evaluation capabilities, and AI-powered Loop assistant. It specializes in production-scale evaluation with advanced features for large organizations.

## Setup & Authentication

### Installation

```bash
pip install braintrust

# Verify installation
python -c "import braintrust; print(braintrust.__version__)"
```

### API Key Setup

Get API key from https://braintrust.dev:

```bash
export BRAINTRUST_API_KEY="sk_..."

# Or set in Python
import os
os.environ["BRAINTRUST_API_KEY"] = "sk_..."
```

### Initialize Client

```python
import braintrust

# Initialize client (auto-authenticated via environment)
client = braintrust.default_client()

# Or explicit initialization
client = braintrust.Braintrust(
    api_key="sk_...",
    org_name="my-company"
)
```

## 25+ Built-in Scorers

### Classification Scorers

```python
from braintrust import Scorer, default_client

client = default_client()

# Exact match scoring
score = Scorer.ExactMatch(
    expected="positive",
    actual="positive"
)  # Returns 1.0

# Normalized scoring
score = Scorer.ExactMatch(
    expected="positive",
    actual="positive",
    normalize=True
)  # Normalizes to 0-1 scale

# Multiple choice scoring
score = Scorer.MultipleChoice(
    expected="A",
    actual="A"
)  # Perfect score: 1.0
```

### Semantic Similarity Scorers

```python
from braintrust.scorer import Scorer

# Cosine similarity
score = Scorer.Cosine(
    expected="The capital of France",
    actual="Paris is the capital of France",
    model="sentence-transformers/all-MiniLM-L6-v2"
)  # Returns similarity 0-1

# LevenshteinDistance
score = Scorer.LevenshteinDistance(
    expected="machine learning",
    actual="machine learnings"
)  # Character edit distance

# F1 Score
score = Scorer.F1(
    expected=["cat", "dog", "bird"],
    actual=["cat", "dog", "fish"]
)  # Set overlap metric
```

### Language Model Scorers

```python
from braintrust.scorer import Scorer

# LLM as judge
score = Scorer.LLMClassifier(
    expected="positive",
    actual="I love this product!",
    prompt_template="""
    Is this review positive or negative?
    Review: {{actual}}
    Expected: {{expected}}
    """
)

# BLEU Score (machine translation)
score = Scorer.BLEU(
    expected="The quick brown fox",
    actual="A quick brown fox"
)  # Returns BLEU score 0-1

# ROUGE Score (summarization)
score = Scorer.ROUGE(
    expected="Climate change affects ecosystems",
    actual="Climate change impacts environmental systems"
)  # Returns ROUGE-L F1
```

### Task-Specific Scorers

```python
from braintrust.scorer import Scorer

# JSON structure matching
score = Scorer.JSONSchema(
    expected={"type": "object", "properties": {"name": {"type": "string"}}},
    actual='{"name": "John", "age": 30}'
)

# Regular expression matching
score = Scorer.Regex(
    pattern=r"^\d{3}-\d{2}-\d{4}$",  # SSN pattern
    actual="123-45-6789"
)

# URL validation
score = Scorer.URLValid(
    actual="https://example.com"
)

# Email validation
score = Scorer.EmailValid(
    actual="test@example.com"
)
```

## Online Evaluation

Online evaluation runs in real-time during inference:

### Setup Online Eval

```python
from braintrust import online_eval_client, Evaluator

# Initialize online evaluation
client = online_eval_client(api_key="sk_...")

# Define evaluator
def real_time_evaluator(actual: str) -> dict:
    """Score during inference"""
    return {
        "score": 1.0 if len(actual) > 10 else 0.0,
        "comment": "Response length check"
    }

# Run inference with automatic evaluation
response = client.predict(
    prompt="What is AI?",
    evaluators=[real_time_evaluator]
)

# Results include score
print(f"Response: {response.output}")
print(f"Score: {response.metrics}")
```

### Streaming Evaluation

```python
from braintrust import online_eval_client

client = online_eval_client(api_key="sk_...")

# Evaluate streaming responses
for chunk in client.predict_stream(
    prompt="Explain quantum computing",
    evaluators=[length_evaluator, quality_evaluator]
):
    print(f"Chunk: {chunk.text}")
    print(f"Streaming metrics: {chunk.metrics}")
```

## Loop AI Assistant

Braintrust's Loop AI assistant helps with evaluation design:

```python
from braintrust import loop_client

# Initialize Loop
loop = loop_client(api_key="sk_...")

# Ask Loop for metric suggestions
metrics = loop.suggest_metrics(
    task_description="Evaluate RAG system responses",
    output_type="string",
    context="We need to measure factuality and relevance"
)

# Loop suggests appropriate metrics
# > Context Precision
# > Faithfulness
# > Answer Relevancy

# Ask Loop for scorer recommendations
scorers = loop.recommend_scorers(
    evaluation_type="RAG",
    desired_metrics=["factuality", "relevance"]
)

# Loop recommends:
# > LLMClassifier for factuality
# > Cosine for semantic relevance
```

## Programmatic Evaluation API

### Run Evaluations

```python
from braintrust import default_client
from braintrust.scorer import Scorer

client = default_client()

# Prepare evaluation data
eval_samples = [
    {
        "prompt": "Classify: I love this!",
        "expected": "positive",
        "output": "positive"
    },
    {
        "prompt": "Classify: This is awful",
        "expected": "negative",
        "output": "negative"
    },
]

# Create experiment
experiment = client.log_experiment(
    project_name="classification-eval",
    experiment_name="baseline-v1"
)

# Score each sample
for sample in eval_samples:
    score = Scorer.ExactMatch(
        expected=sample["expected"],
        actual=sample["output"]
    )

    experiment.log(
        input=sample["prompt"],
        output=sample["output"],
        expected=sample["expected"],
        scores={"exact_match": score}
    )

experiment.close()

# View results
results = experiment.summarize()
print(f"Accuracy: {results['exact_match']:.2%}")
```

### Batch Evaluation with Multiple Scorers

```python
from braintrust import default_client
from braintrust.scorer import Scorer
import json

client = default_client()

# Load test data
with open("test_data.json") as f:
    test_samples = json.load(f)

# Create experiment with multiple scorers
experiment = client.log_experiment(
    project_name="multi-scorer-eval",
    experiment_name="comprehensive-eval"
)

for sample in test_samples:
    # Apply multiple scorers
    scores = {
        "exact_match": Scorer.ExactMatch(
            expected=sample["expected"],
            actual=sample["actual"]
        ),
        "semantic_similarity": Scorer.Cosine(
            expected=sample["expected"],
            actual=sample["actual"]
        ),
        "length_check": 1.0 if len(sample["actual"]) > 50 else 0.5,
    }

    experiment.log(
        input=sample["input"],
        output=sample["actual"],
        expected=sample["expected"],
        scores=scores
    )

experiment.close()

# Analyze composite scores
results = experiment.summarize()
for scorer_name, score in results.items():
    print(f"{scorer_name}: {score:.3f}")
```

## A/B Testing & Comparison

### Run A/B Tests

```python
from braintrust import default_client

client = default_client()

# Create variant A (baseline)
exp_a = client.log_experiment(
    project_name="prompt-test",
    experiment_name="prompt-v1-baseline"
)

for sample in test_samples:
    output_a = run_model_with_prompt_v1(sample["input"])
    score_a = evaluate_output(output_a, sample["expected"])

    exp_a.log(
        input=sample["input"],
        output=output_a,
        expected=sample["expected"],
        scores={"quality": score_a}
    )

exp_a.close()

# Create variant B (new prompt)
exp_b = client.log_experiment(
    project_name="prompt-test",
    experiment_name="prompt-v2-improved"
)

for sample in test_samples:
    output_b = run_model_with_prompt_v2(sample["input"])
    score_b = evaluate_output(output_b, sample["expected"])

    exp_b.log(
        input=sample["input"],
        output=output_b,
        expected=sample["expected"],
        scores={"quality": score_b}
    )

exp_b.close()

# Compare results (via web dashboard)
print("Results available at https://braintrust.dev/your-project")
# Dashboard shows:
# - Side-by-side outputs
# - Score differences
# - Statistical significance
# - Decision: Keep/switch variant
```

## Dataset Management

### Create Evaluation Datasets

```python
from braintrust import default_client

client = default_client()

# Create dataset
dataset = client.create_dataset(
    project_name="qa-eval",
    dataset_name="benchmark-v1"
)

# Add examples
examples = [
    {"question": "What is AI?", "expected_answer": "Artificial Intelligence"},
    {"question": "What is ML?", "expected_answer": "Machine Learning"},
]

for example in examples:
    dataset.add_example(
        input=example["question"],
        expected=example["expected_answer"]
    )

dataset.close()

# Reference in evaluations
loaded_dataset = client.read_dataset(
    project_name="qa-eval",
    dataset_name="benchmark-v1"
)

for example in loaded_dataset.examples:
    print(f"Q: {example.input}")
    print(f"Expected: {example.expected}")
```

## Enterprise Features

### Team Management

```python
from braintrust import default_client

client = default_client(org_name="my-company")

# Create team project
project = client.create_project(
    name="production-evals",
    description="Production evaluation suite"
)

# Share with team (via web dashboard)
# - Invite team members
# - Set permissions (view/edit/admin)
# - Configure approval workflows
```

### Audit & Compliance

```python
from braintrust import default_client

client = default_client()

# Get audit logs
logs = client.get_audit_logs(
    project_name="production-evals",
    limit=1000
)

for log in logs:
    print(f"Action: {log.action}")
    print(f"User: {log.user}")
    print(f"Timestamp: {log.timestamp}")
    print(f"Details: {log.details}")
```

### Custom Scorers

```python
from braintrust import Scorer

class CustomDomainScorer(Scorer):
    """Custom scorer for domain-specific evaluation"""

    def __init__(self, domain_rules: dict):
        self.domain_rules = domain_rules

    def score(self, actual: str, expected: str) -> float:
        """Score based on domain rules"""
        score = 0.0

        # Check domain-specific criteria
        for rule, weight in self.domain_rules.items():
            if rule in actual.lower():
                score += weight

        return min(score / sum(self.domain_rules.values()), 1.0)

# Use custom scorer
custom_scorer = CustomDomainScorer({
    "safety": 0.4,
    "accuracy": 0.3,
    "clarity": 0.3
})

score = custom_scorer.score(
    actual="AI systems must prioritize safety and accuracy",
    expected="AI evaluation metrics"
)
```

## Integration with Production Systems

### Production Monitoring

```python
from braintrust import online_eval_client
from braintrust.scorer import Scorer
import time

client = online_eval_client(api_key="sk_...")

def monitor_production():
    """Continuous production monitoring"""

    while True:
        # Get recent predictions
        recent = client.get_recent_predictions(limit=100)

        scores = []
        for pred in recent:
            score = Scorer.ExactMatch(
                expected=pred.expected,
                actual=pred.output
            )
            scores.append(score)

        # Check quality
        avg_score = sum(scores) / len(scores)
        if avg_score < 0.85:
            print(f"ALERT: Quality degraded ({avg_score:.2%})")
            # Trigger alerting system
        else:
            print(f"OK: Quality nominal ({avg_score:.2%})")

        time.sleep(3600)  # Check hourly

monitor_production()
```

## Troubleshooting

### Common Issues

**Issue: "Authentication failed"**
```bash
export BRAINTRUST_API_KEY="sk_..."

# Verify key
python -c "from braintrust import default_client; client = default_client(); print(client.get_org())"
```

**Issue: "Scorer not found"**
```python
from braintrust.scorer import Scorer

# List available scorers
print(dir(Scorer))

# Common scorers:
# - ExactMatch
# - Cosine
# - LevenshteinDistance
# - LLMClassifier
# - BLEU
# - ROUGE
```

**Issue: "Online eval not working"**
```python
from braintrust import online_eval_client

# Ensure correct client type
client = online_eval_client(api_key="sk_...")  # Not default_client()

# Verify evaluator signature
def evaluator(actual: str) -> dict:
    return {"score": 1.0}

# Must return dict with "score" key
```

## Pros & Cons

### Advantages
- **25+ scorers:** Most comprehensive built-in scorer library
- **Online evaluation:** Real-time scoring during inference
- **Enterprise-ready:** Used by Notion, Stripe, Vercel
- **Loop assistant:** AI-powered evaluation design
- **Team management:** Full multi-user support
- **Professional UX:** Polished web interface
- **Audit trails:** Compliance and traceability
- **A/B testing:** Statistical significance testing

### Disadvantages
- **Expensive:** Starting $1000+/month
- **Proprietary:** No open source version
- **Vendor lock-in:** Braintrust-specific APIs
- **Unclear pricing:** Custom quotes, hard to estimate
- **Limited documentation:** Fewer examples than open source
- **Learning curve:** Complex for beginners
- **Data residency:** SaaS only, data on Braintrust servers
- **Minimum commitment:** Enterprise plans typically 12 months

## Cost Structure (March 2026)

| Size | Users | Price | Includes |
|------|-------|-------|----------|
| Startup | 1-3 | $1000/mo | Basic team, 100k evals/mo |
| Growth | 4-10 | $3000/mo | Team features, 1M evals/mo |
| Enterprise | 10+ | Custom | Dedicated support, unlimited |

**Estimation:**
- 100k evaluations/month: ~$1000
- 1M evaluations/month: ~$3000
- Multi-team setup: +50% per team

## When to Use Braintrust

**Best For:**
- Enterprise deployments (Stripe, Notion scale)
- Teams with large budgets
- Complex A/B testing requirements
- Online evaluation at scale
- Multi-team organizations
- Compliance-critical applications
- Require professional SLA

**Not Best For:**
- Startups or bootstrapped projects (too expensive)
- Research and development (use DeepEval)
- Budget-conscious (use Langfuse)
- Benchmark evaluation (use lm-eval-harness)
- Simple use cases (overkill)
- Self-hosted requirements (SaaS only)
- Open source preference (proprietary)

## Comparison with Alternatives

| Feature | Braintrust | LangSmith | Langfuse |
|---------|-----------|-----------|---------|
| Scorers | 25+ | Limited | 5+ custom |
| Online eval | Yes | No | Limited |
| Cost | $$$ | $$ | $ |
| Enterprise | Excellent | Good | Fair |
| Self-hosted | No | No | Yes |
| Support | 24/7 | Business hours | Community |

## Notable Enterprise Users

- **Notion:** Uses Braintrust for content eval
- **Stripe:** Uses for financial ML models
- **Vercel:** Uses for deployment quality gates
- **OpenAI partners:** Used in various partnerships

(As of March 2026)

## Next Steps

1. **Contact sales:** Request demo at braintrust.dev
2. **Setup trial:** 30-day free trial
3. **Create project:** Import test data
4. **Design scorers:** Use Loop AI assistant
5. **Run baseline:** Evaluate current system
6. **Configure thresholds:** Set quality gates

## Resources

- **Website:** https://braintrust.dev
- **Docs:** https://docs.braintrust.dev
- **Support:** support@braintrust.dev
- **Demo:** Request at braintrust.dev/demo

---

**Document Version:** 1.0
**Last Verified:** March 31, 2026
