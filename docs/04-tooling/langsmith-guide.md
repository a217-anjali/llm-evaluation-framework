# LangSmith: Production Agent Evaluation Guide

**Version:** LangSmith (current)
**Type:** Commercial SaaS
**Pricing:** Usage-based, volume discounts
**Latest Update:** March 2026

LangSmith is the official evaluation and monitoring platform for LangChain. It specializes in agent trajectory analysis, production monitoring, human-in-the-loop evaluation, and dataset management. It's the primary tool for evaluating complex agentic systems in production.

## Setup & Authentication

### Installation

```bash
pip install langsmith

# Verify installation
python -c "import langsmith; print(langsmith.__version__)"
```

### Authentication

Get API key from https://smith.langchain.com:

```bash
export LANGCHAIN_API_KEY="lsv2_..."
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"

# Optional: project name
export LANGCHAIN_PROJECT="my-eval-project"
```

### Python Configuration

```python
from langsmith import Client

# Initialize client
client = Client(
    api_key="lsv2_...",
    api_url="https://api.smith.langchain.com"
)

# Verify connection
print(client.list_datasets())
```

## Tracing & Monitoring

### Automatic LangChain Tracing

```python
from langsmith import Client
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Set project
import os
os.environ["LANGCHAIN_PROJECT"] = "my-chain-eval"

# Build chain - traces automatically
prompt = ChatPromptTemplate.from_template("Explain {topic}")
llm = ChatOpenAI(model="gpt-4")
chain = prompt | llm

# Run - automatically traced in LangSmith
response = chain.invoke({"topic": "quantum computing"})

# View traces in LangSmith dashboard
# https://smith.langchain.com/projects/my-chain-eval
```

### Manual Span Creation

```python
from langsmith import trace

@trace
def evaluate_response(query: str, response: str) -> dict:
    """Manual tracing for custom functions"""
    # This function's execution is traced
    score = len(response) / len(query)
    return {"query": query, "score": score}

result = evaluate_response("What is AI?", "AI is artificial intelligence...")

# Appears in LangSmith dashboard
```

## Agent Trajectory Analysis

### Evaluating Agent Action Sequences

```python
from langsmith import Client, Run
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool

# Setup agent
@tool
def search_internet(query: str) -> str:
    """Search the internet"""
    return f"Search results for {query}"

@tool
def read_document(path: str) -> str:
    """Read a document"""
    return f"Document content from {path}"

tools = [search_internet, read_document]
llm = ChatOpenAI(model="gpt-4")

# Create agent
from langchain.agents import AgentType
from langchain.agents import initialize_agent

agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
)

# Run - traces action sequence
import os
os.environ["LANGCHAIN_PROJECT"] = "agent-eval"

response = agent.run("Research AI safety and write a summary")

# LangSmith shows:
# - Tool calls sequence
# - Tool inputs/outputs
# - Reasoning steps
# - Final response
# - Execution time per step
```

### Agent Evaluation Metrics

```python
from langsmith import Client, EvaluationResult, evaluate

def trajectory_scorer(run: Run, example) -> EvaluationResult:
    """Score agent trajectory"""
    steps = run.trace
    metrics = {
        "step_count": len(steps),
        "tool_calls": sum(1 for s in steps if s.type == "tool"),
        "successful": all(s.status == "success" for s in steps),
        "total_tokens": sum(s.token_count for s in steps),
    }

    # Gate based on metrics
    success = (
        metrics["step_count"] <= 10 and  # Not too many steps
        metrics["successful"] and
        metrics["total_tokens"] < 5000
    )

    return EvaluationResult(
        key="trajectory_quality",
        score=1 if success else 0,
        metadata=metrics
    )

# Evaluate dataset
client = Client()
results = evaluate(
    agent.run,  # Agent function
    data=evaluation_dataset,
    evaluators=[trajectory_scorer],
    experiment_prefix="agent-eval-v1"
)
```

## Dataset Management

### Creating Evaluation Datasets

```python
from langsmith import Client

client = Client()

# Create dataset
dataset = client.create_dataset(
    dataset_name="rag-qa-eval",
    description="RAG system evaluation dataset"
)

# Add examples
examples = [
    {
        "question": "What is machine learning?",
        "expected_output": "ML is a subset of AI..."
    },
    {
        "question": "How do transformers work?",
        "expected_output": "Transformers use attention mechanisms..."
    },
]

for example in examples:
    client.create_example(
        dataset_id=dataset.id,
        inputs={"question": example["question"]},
        outputs={"answer": example["expected_output"]}
    )

# Reference dataset in evals
dataset = client.read_dataset(dataset_name="rag-qa-eval")
for example in dataset.examples:
    print(f"Q: {example.inputs['question']}")
    print(f"A: {example.outputs['answer']}")
```

### Importing from JSON

```python
import json
from langsmith import Client

# Load examples from file
with open("eval_dataset.json") as f:
    examples = json.load(f)

# Create dataset
client = Client()
dataset = client.create_dataset(
    dataset_name="imported-eval",
    description="Imported evaluation set"
)

# Batch create examples
for example in examples:
    client.create_example(
        dataset_id=dataset.id,
        inputs=example.get("inputs", {}),
        outputs=example.get("outputs", {})
    )
```

## Human-in-the-Loop Evaluation

### Creating Feedback Queues

```python
from langsmith import Client

client = Client()

# Get runs that need feedback
runs = client.list_runs(
    project_name="my-project",
    filter='feedback.score is null',  # No feedback yet
    limit=100
)

# Queue for human annotation
for run in runs:
    client.create_feedback(
        run_id=run.id,
        key="human_judgment",
        score=None,  # Awaiting human input
        comment="Please review and rate this response",
        tags=["needs_review"]
    )
```

### Collecting Feedback

```python
from langsmith import Client

client = Client()

# Simulate human feedback collection
run_id = "..."  # From LangSmith dashboard

# Submit feedback
client.create_feedback(
    run_id=run_id,
    key="quality",
    score=4.0,  # 1-5 scale
    comment="Good response, could be more concise",
    tags=["human_review"]
)

# Retrieve feedback
run = client.read_run(run_id)
print(f"Feedback: {run.feedback}")
```

### Feedback-Driven Improvement

```python
from langsmith import Client

client = Client()

# Get feedback distribution
project = client.read_project(project_name="my-project")
runs = client.list_runs(project_name="my-project", limit=1000)

feedback_scores = []
for run in runs:
    if run.feedback:
        for feedback in run.feedback:
            if feedback.key == "quality":
                feedback_scores.append(feedback.score)

# Analyze trends
import statistics
avg_score = statistics.mean(feedback_scores)
median_score = statistics.median(feedback_scores)

print(f"Average score: {avg_score:.2f}/5.0")
print(f"Median score: {median_score:.2f}/5.0")

# Trigger retraining if scores below threshold
if avg_score < 3.5:
    print("WARNING: Quality degraded, retrain model")
```

## Production Monitoring

### Setting Up Alerts

```python
from langsmith import Client
import time

client = Client()

def monitor_production_chain(
    chain_func,
    alert_threshold: dict = None
):
    """Monitor chain performance with alerts"""

    if alert_threshold is None:
        alert_threshold = {
            "latency_ms": 5000,      # Alert if >5s
            "error_rate": 0.05,      # Alert if >5% errors
            "token_cost": 0.50,      # Alert if >$0.50 per call
        }

    # Monitor for 24 hours
    errors = []
    latencies = []
    costs = []

    start_time = time.time()
    while time.time() - start_time < 86400:
        runs = client.list_runs(
            project_name="production",
            filter='created_at > "now - 1m"',
            limit=100
        )

        for run in runs:
            # Check metrics
            if run.error:
                errors.append(run.id)

            if hasattr(run, 'latency_ms'):
                latencies.append(run.latency_ms)
                if run.latency_ms > alert_threshold["latency_ms"]:
                    print(f"ALERT: High latency {run.latency_ms}ms")

            if hasattr(run, 'total_cost'):
                costs.append(run.total_cost)
                if run.total_cost > alert_threshold["token_cost"]:
                    print(f"ALERT: High cost ${run.total_cost}")

        # Sleep before next check
        time.sleep(60)

    # Summary
    error_rate = len(errors) / len(runs) if runs else 0
    if error_rate > alert_threshold["error_rate"]:
        print(f"ALERT: High error rate {error_rate:.1%}")

monitor_production_chain(chain_func)
```

### Cost Tracking

```python
from langsmith import Client

client = Client()

# Get cost by model
runs = client.list_runs(
    project_name="production",
    filter='created_at > "now - 7d"',
    limit=10000
)

costs_by_model = {}
for run in runs:
    model = run.extra.get("model", "unknown")
    cost = getattr(run, 'total_cost', 0)
    costs_by_model[model] = costs_by_model.get(model, 0) + cost

# Print cost breakdown
total_cost = sum(costs_by_model.values())
print(f"Total 7-day cost: ${total_cost:.2f}")
for model, cost in sorted(costs_by_model.items(), key=lambda x: x[1], reverse=True):
    percentage = cost / total_cost * 100
    print(f"  {model}: ${cost:.2f} ({percentage:.1f}%)")
```

## Advanced Evaluation

### Custom Evaluators

```python
from langsmith import evaluate, EvaluationResult, Run

def answer_length_evaluator(run: Run, example) -> EvaluationResult:
    """Evaluate if answer length is reasonable"""
    output = run.outputs.get("output", "")
    word_count = len(output.split())

    return EvaluationResult(
        key="answer_length",
        score=1.0 if 50 <= word_count <= 500 else 0.0,
        comment=f"Answer is {word_count} words",
    )

def relevance_evaluator(run: Run, example) -> EvaluationResult:
    """LLM-based relevance evaluation"""
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4")

    prompt = f"""
    Question: {example.inputs['question']}
    Answer: {run.outputs['output']}

    Rate how relevant the answer is to the question (0-1).
    Return only the number.
    """

    score = float(llm.predict(prompt).strip())

    return EvaluationResult(
        key="relevance",
        score=score,
    )

# Run evaluation
results = evaluate(
    chain_func,
    data=dataset,
    evaluators=[answer_length_evaluator, relevance_evaluator],
    experiment_prefix="eval-v2"
)

print(f"Pass rate: {results.pass_rate}")
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: LangSmith Evaluation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'

      - run: pip install langchain langsmith

      - name: Run evaluation
        run: python eval/run_evals.py
        env:
          LANGCHAIN_API_KEY: ${{ secrets.LANGCHAIN_API_KEY }}
          LANGCHAIN_PROJECT: ${{ github.head_ref || github.ref_name }}

      - name: Check results
        run: python eval/check_results.py
```

## Troubleshooting

### Common Issues

**Issue: "API key not authenticated"**
```bash
export LANGCHAIN_API_KEY="lsv2_..."
export LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"

# Test connection
python -c "from langsmith import Client; Client().list_datasets()"
```

**Issue: "Traces not appearing in LangSmith"**
```python
import os

# Ensure environment variables set
os.environ["LANGCHAIN_API_KEY"] = "lsv2_..."
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "my-project"

# Then run LangChain code
```

**Issue: "Dataset examples not loading"**
```python
from langsmith import Client

client = Client()

# Check dataset exists
datasets = client.list_datasets()
print([d.name for d in datasets])

# Verify examples
dataset = client.read_dataset(dataset_name="my-dataset")
print(f"Examples: {len(list(dataset.examples))}")
```

## Pros & Cons

### Advantages
- **Agent-focused:** Best trajectory analysis in industry
- **Production-ready:** Built for production monitoring
- **LangChain native:** Seamless integration
- **Human feedback:** Built-in human-in-the-loop
- **Dataset management:** Create/manage eval datasets
- **Cost tracking:** Automatic cost per run
- **Professional support:** Commercial backing
- **Scalable:** Designed for high volume

### Disadvantages
- **Expensive:** $500-5000+ monthly for production use
- **Proprietary:** No open source alternative available
- **Vendor lock-in:** Tight coupling with LangChain
- **Limited flexibility:** Less customization than open source
- **Pricing opacity:** Usage-based, hard to predict costs
- **No local option:** SaaS only, data goes to LangChain servers
- **Learning curve:** Complex setup for advanced features
- **High barrier:** Minimum spend required

## Cost Structure (March 2026)

| Usage Level | Cost | Notes |
|-------------|------|-------|
| Hobby (< 1k runs/mo) | Free | Free tier available |
| Startup (10k runs/mo) | $500-1000 | Typical startup spend |
| Growth (100k runs/mo) | $2000-5000 | Volume discounts |
| Enterprise | Custom | Dedicated support |

**Estimation:**
- Typical deployment: 100 runs/day = 3k/month
- Cost: ~$100-200/month (with volume discount)

## When to Use LangSmith

**Best For:**
- Production agent deployments
- Human-in-the-loop evaluation
- Cost tracking and optimization
- Teams using LangChain
- Complex agentic workflows
- Data-driven product iteration
- Enterprise with budgets

**Not Best For:**
- Budget-conscious teams (use Langfuse)
- Benchmark evaluation (use lm-eval-harness)
- RAG evaluation (use Ragas)
- Research projects (use DeepEval)
- Red teaming (use Promptfoo or Garak)
- Self-hosted requirements (use Langfuse)

## Comparison with Alternatives

| Feature | LangSmith | Langfuse | Braintrust |
|---------|-----------|----------|-----------|
| Agent eval | Excellent | Moderate | Good |
| Cost | $$$ | $$ | $$$ |
| LangChain | Native | Good | Good |
| Self-hosted | No | Yes | No |
| Human feedback | Built-in | Built-in | Built-in |
| Tracing | Full | Full | Full |

## Next Steps

1. **Create account:** https://smith.langchain.com
2. **Get API key:** Copy from dashboard
3. **Install SDK:** `pip install langsmith`
4. **Run traces:** Add LANGCHAIN_TRACING_V2=true
5. **Evaluate:** Use example evaluators
6. **Monitor:** Set up production alerts

## Resources

- **Dashboard:** https://smith.langchain.com
- **Docs:** https://docs.smith.langchain.com
- **GitHub:** https://github.com/langchain-ai/langsmith-sdk
- **Support:** support@langchain.com

---

**Document Version:** 1.0
**Last Verified:** March 31, 2026
