# Langfuse: Self-Hosted Tracing & Evaluation Guide

**Version:** Langfuse v2.1.0+
**License:** MIT
**Type:** Open Source + Self-Hosted SaaS
**Latest Update:** March 2026

Langfuse is an open-source LLM observability platform. It provides tracing, evaluation, human annotation, and cost tracking with the flexibility of self-hosting or cloud SaaS. It's the most cost-effective alternative to LangSmith for production monitoring.

## Installation & Setup

### Docker Self-Hosting (Recommended)

```bash
# Clone repository
git clone https://github.com/langfuse/langfuse
cd langfuse

# Create .env file
cat > .env << EOF
DATABASE_URL="postgresql://langfuse:password@postgres:5432/langfuse"
NEXTAUTH_SECRET="your-secret-here"
NEXTAUTH_URL="http://localhost:3000"
EOF

# Run with Docker Compose
docker-compose up -d

# Access dashboard at http://localhost:3000
```

### Python SDK Installation

```bash
pip install langfuse

# Verify installation
python -c "import langfuse; print(langfuse.__version__)"
```

### Cloud SaaS Setup

```bash
# Sign up at https://cloud.langfuse.com
# Get API credentials from dashboard

export LANGFUSE_PUBLIC_KEY="pk_..."
export LANGFUSE_SECRET_KEY="sk_..."
export LANGFUSE_HOST="https://cloud.langfuse.com"  # Or your self-hosted URL
```

## Tracing Setup

### Basic Tracing with LangChain

```python
from langfuse.callback_handler import CallbackHandler
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Initialize Langfuse handler
langfuse_handler = CallbackHandler(
    public_key="pk_...",
    secret_key="sk_...",
    host="https://cloud.langfuse.com"  # Or self-hosted URL
)

# Build chain
prompt = ChatPromptTemplate.from_template("Explain {topic}")
llm = ChatOpenAI(model="gpt-4")
chain = prompt | llm

# Run with tracing
response = chain.invoke(
    {"topic": "quantum computing"},
    config={"callbacks": [langfuse_handler]}
)

# Automatically traced in Langfuse dashboard
# Shows: prompts, LLM calls, latency, cost
```

### Manual Trace Creation

```python
from langfuse import Langfuse

# Initialize client
langfuse = Langfuse(
    public_key="pk_...",
    secret_key="sk_...",
)

# Create trace
trace = langfuse.trace(
    name="user-query",
    user_id="user-123",
    metadata={"environment": "production"}
)

# Log generation
generation = trace.generation(
    name="qa-response",
    model="gpt-4",
    prompt="What is AI?",
    completion="AI is artificial intelligence...",
    usage={"input_tokens": 10, "output_tokens": 100}
)

# Log span (nested operation)
span = trace.span(
    name="retrieve-context",
    start_time=datetime.now(),
    end_time=datetime.now()
)

# Flush to Langfuse
langfuse.flush()
```

## LLM-as-Judge Evaluation

### Built-in Model-Graded Evaluation

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk_...",
    secret_key="sk_..."
)

# Get trace
trace = langfuse.get_trace(trace_id="...")

# Score with LLM judge
score = langfuse.score_trace(
    trace_id=trace.id,
    name="answer_quality",
    value=0.8,  # 0-1 score
    comment="Good answer, could be more concise",
    evaluator="gpt-4"  # LLM judge
)

# Or batch score traces
traces = langfuse.get_traces(limit=100)
for trace in traces:
    # Automatic LLM-based scoring
    langfuse.score_trace(
        trace_id=trace.id,
        name="relevance",
        value=langfuse.evaluate_with_llm(
            prompt=f"Is this response relevant?\n{trace.output}"
        )
    )
```

### Custom Evaluation Prompts

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk_...",
    secret_key="sk_..."
)

# Define evaluation template
evaluation_prompt = """
Question: {{question}}
Answer: {{answer}}

Rate the answer quality on a scale of 0-10.
Consider: factuality, clarity, completeness.

Score: """

# Score with custom prompt
score = langfuse.score_trace(
    trace_id="...",
    name="custom_eval",
    value=8.5,
    comment="Evaluated with custom rubric",
    metadata={"prompt_template": "factuality+clarity"}
)
```

## Human Annotation

### Create Annotation Tasks

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk_...",
    secret_key="sk_..."
)

# Get traces needing annotation
traces = langfuse.get_traces(
    filter='metadata.needs_review=true',
    limit=50
)

# Create annotation queue
for trace in traces:
    langfuse.create_annotation_task(
        trace_id=trace.id,
        prompt="Does this response answer the question correctly?",
        options=["Yes", "Partially", "No"],
        priority="high"
    )

# Later: retrieve annotations
annotations = langfuse.get_annotations(
    trace_id="...",
    limit=10
)

for annotation in annotations:
    print(f"Annotator: {annotation.user_id}")
    print(f"Response: {annotation.value}")
    print(f"Comment: {annotation.comment}")
```

### Bulk Annotation Import

```python
from langfuse import Langfuse
import json

langfuse = Langfuse(
    public_key="pk_...",
    secret_key="sk_..."
)

# Load annotations from file
with open("annotations.json") as f:
    annotations = json.load(f)

# Import annotations
for annotation in annotations:
    langfuse.create_annotation(
        trace_id=annotation["trace_id"],
        value=annotation["label"],
        comment=annotation["comment"],
        user_id=annotation["annotator"]
    )

langfuse.flush()
```

## Cost Tracking

### Automatic Cost Calculation

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk_...",
    secret_key="sk_..."
)

# Get cost by model
traces = langfuse.get_traces(limit=1000)

cost_by_model = {}
for trace in traces:
    for generation in trace.generations:
        model = generation.model
        cost = generation.cost  # Automatically calculated

        if model not in cost_by_model:
            cost_by_model[model] = 0
        cost_by_model[model] += cost

# Print cost breakdown
total_cost = sum(cost_by_model.values())
print(f"Total cost: ${total_cost:.2f}")

for model, cost in sorted(
    cost_by_model.items(),
    key=lambda x: x[1],
    reverse=True
):
    percentage = cost / total_cost * 100
    print(f"  {model}: ${cost:.2f} ({percentage:.1f}%)")
```

### Cost Monitoring & Alerts

```python
from langfuse import Langfuse
import time
from datetime import datetime, timedelta

langfuse = Langfuse(
    public_key="pk_...",
    secret_key="sk_..."
)

def monitor_costs(daily_budget: float = 100.0):
    """Monitor daily costs and alert on budget"""

    while True:
        # Get traces from last 24 hours
        start_time = datetime.now() - timedelta(hours=24)
        traces = langfuse.get_traces(
            filters=f'timestamp >= {start_time.isoformat()}',
            limit=10000
        )

        # Calculate total cost
        total_cost = sum(
            sum(g.cost for g in trace.generations)
            for trace in traces
        )

        print(f"24h cost: ${total_cost:.2f} (budget: ${daily_budget:.2f})")

        if total_cost > daily_budget:
            print(f"ALERT: Daily cost exceeded budget!")
            # Trigger alerting system (e.g., Slack, email)

        time.sleep(3600)  # Check every hour

monitor_costs(daily_budget=100.0)
```

## Evaluation Metrics

### Standard Metrics

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk_...",
    secret_key="sk_..."
)

# Score traces with various metrics
trace = langfuse.get_trace(trace_id="...")

# Accuracy metric
langfuse.score_trace(
    trace_id=trace.id,
    name="accuracy",
    value=1.0 if trace.output == expected else 0.0
)

# Latency metric (auto-calculated)
latency_ms = (trace.end_time - trace.start_time).total_seconds() * 1000

langfuse.score_trace(
    trace_id=trace.id,
    name="latency",
    value=latency_ms
)

# Cost metric (auto-calculated)
cost = trace.cost

langfuse.score_trace(
    trace_id=trace.id,
    name="cost",
    value=cost
)

# Composite score
quality_score = (
    accuracy * 0.5 +  # 50% weight
    (1.0 - latency_ms / 10000) * 0.3 +  # 30% weight (normalized)
    (1.0 - cost / 1.0) * 0.2  # 20% weight
)

langfuse.score_trace(
    trace_id=trace.id,
    name="quality",
    value=quality_score
)
```

### Custom Evaluation Functions

```python
from langfuse import Langfuse
from datetime import datetime

langfuse = Langfuse(
    public_key="pk_...",
    secret_key="sk_..."
)

def evaluate_trace(trace, expected_output=None):
    """Custom evaluation logic"""

    scores = {}

    # Length check
    output_length = len(trace.output or "")
    scores["length_ok"] = 1.0 if 50 < output_length < 500 else 0.0

    # Contains key terms
    key_terms = ["key", "important", "essential"]
    scores["has_key_terms"] = 1.0 if any(
        term in trace.output.lower() for term in key_terms
    ) else 0.0

    # Expected match (if provided)
    if expected_output:
        scores["exact_match"] = 1.0 if trace.output == expected_output else 0.0

    # Latency acceptable
    latency_ms = (trace.end_time - trace.start_time).total_seconds() * 1000
    scores["latency_ok"] = 1.0 if latency_ms < 5000 else 0.0

    return scores

# Apply evaluation to all traces
traces = langfuse.get_traces(limit=100)

for trace in traces:
    scores = evaluate_trace(trace)

    for metric_name, score in scores.items():
        langfuse.score_trace(
            trace_id=trace.id,
            name=metric_name,
            value=score
        )
```

## Production Integration

### Trace in Production

```python
from langfuse.callback_handler import CallbackHandler
from langchain.agents import AgentExecutor

# Setup tracing for production
langfuse_handler = CallbackHandler(
    public_key="pk_...",
    secret_key="sk_...",
    host="https://cloud.langfuse.com",
    enabled=True  # Can disable for A/B testing
)

# Use in agent
agent = AgentExecutor.from_agent_and_tools(...)

# Every call is traced
response = agent.run(
    query="What is AI?",
    callbacks=[langfuse_handler]
)

# Traces available at:
# https://cloud.langfuse.com/traces
```

### Sampling for Cost Control

```python
from langfuse.callback_handler import CallbackHandler
import random

# Only trace 10% of requests (reduce costs)
langfuse_handler = CallbackHandler(
    public_key="pk_...",
    secret_key="sk_...",
    enabled=random.random() < 0.1
)

# Run agent - most calls don't create traces
response = agent.run(
    query=user_query,
    callbacks=[langfuse_handler]
)

# Reduces tracing cost by 90%
# Still captures representative sample
```

## Dashboard & Analytics

### Metrics Dashboard

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk_...",
    secret_key="sk_..."
)

# Get performance metrics
metrics = langfuse.get_metrics(
    time_range="7d",  # Last 7 days
    group_by="model"
)

for model_metrics in metrics:
    print(f"Model: {model_metrics['model']}")
    print(f"  Avg latency: {model_metrics['avg_latency_ms']:.0f}ms")
    print(f"  Avg cost: ${model_metrics['avg_cost']:.4f}")
    print(f"  Error rate: {model_metrics['error_rate']:.1%}")
    print(f"  Call count: {model_metrics['count']}")
```

### Creating Alerts

Self-hosted dashboard allows setting thresholds:

```python
# Configure in Langfuse dashboard:
# - Alert if latency > 5000ms
# - Alert if cost > $1.00 per trace
# - Alert if error rate > 5%
# - Alert if token usage > 10k per day

# Alerts can integrate with:
# - Email
# - Slack (via webhook)
# - PagerDuty
# - Custom webhooks
```

## Troubleshooting

### Common Issues

**Issue: "Database connection failed (self-hosted)"**
```bash
# Check PostgreSQL is running
docker-compose ps

# Verify DATABASE_URL
echo $DATABASE_URL

# Fix connection
# DATABASE_URL="postgresql://user:password@host:5432/langfuse"
```

**Issue: "API key not working"**
```python
from langfuse import Langfuse

try:
    langfuse = Langfuse(
        public_key="pk_...",
        secret_key="sk_..."
    )
    print("Connection OK")
except Exception as e:
    print(f"Error: {e}")
```

**Issue: "Tracing not appearing in dashboard"**
```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key="pk_...",
    secret_key="sk_...",
    debug=True  # Enable debug logging
)

# Ensure flush is called
langfuse.flush()  # Force sync to server
```

**Issue: "High costs with tracing"**
```python
# Solution 1: Sample traces
langfuse_handler = CallbackHandler(
    public_key="pk_...",
    secret_key="sk_...",
    enabled=random.random() < 0.1  # Only 10%
)

# Solution 2: Disable trace recording
langfuse_handler = CallbackHandler(enabled=False)

# Solution 3: Batch flush
langfuse = Langfuse(batch_size=100)  # Flush every 100 traces
```

## Pros & Cons

### Advantages
- **Open source:** MIT licensed, full transparency
- **Self-hosted:** Full control, data stays local
- **Cheap:** ~$0.10 per 1M tokens (self-hosted)
- **LLM-as-judge:** Built-in evaluation scoring
- **Human annotation:** Queue-based labeling interface
- **Cost tracking:** Automatic token/cost accounting
- **LangChain native:** Perfect integration
- **Production-ready:** Used in production deployments
- **Privacy:** No data sent to external APIs (if self-hosted)

### Disadvantages
- **Operational overhead:** Must manage own infrastructure
- **Limited features:** Fewer scorers than Braintrust
- **Smaller ecosystem:** Fewer integrations than LangSmith
- **Documentation:** Less comprehensive than commercial tools
- **No paid support:** Community-driven support only
- **Scaling complexity:** Must manage PostgreSQL scaling
- **Feature gaps:** Limited agent trajectory analysis
- **Learning curve:** Self-hosting requires DevOps knowledge

## Cost Comparison

| Tool | Monthly Cost (1k evals) | Cost per eval | Self-hosted |
|------|------------------------|---------------|----|
| Langfuse | $0 (self) / $100 (cloud) | $0 / $0.01 | Yes |
| LangSmith | $500+ | $0.50 | No |
| Braintrust | $1000+ | $1.00 | No |
| DeepEval | $0 (+ LLM judge) | $0.05 | Yes |

## When to Use Langfuse

**Best For:**
- Budget-conscious teams ($0-100/month)
- Organizations needing self-hosting
- Privacy-critical applications
- LangChain users
- Production monitoring with human review
- Scaling from startup to scale

**Not Best For:**
- Teams needing 24/7 support (no paid support)
- Enterprise requiring SLA (community-driven)
- Organizations without DevOps resources
- Very simple use cases (overkill to self-host)
- Organizations needing advanced scorers

## Comparison with Alternatives

| Feature | Langfuse | LangSmith | Braintrust | DeepEval |
|---------|----------|-----------|-----------|----------|
| Cost | $ | $$ | $$$ | $0 |
| Self-hosted | Yes | No | No | Yes |
| LLM-as-judge | Yes | Yes | Limited | Yes |
| Human annotation | Yes | Yes | Yes | No |
| Tracing | Excellent | Excellent | Good | No |
| Support | Community | Professional | 24/7 | Community |

## Self-Hosting Checklist

- [ ] Docker & Docker Compose installed
- [ ] PostgreSQL database running
- [ ] Sufficient disk space (100GB+ recommended)
- [ ] Firewall configured for access
- [ ] Backups scheduled
- [ ] Monitoring setup (disk, CPU, DB)
- [ ] SSL/TLS certificates configured
- [ ] Regular updates planned

## Next Steps

1. **Choose deployment:** Cloud vs self-hosted
2. **Setup:** Follow installation instructions
3. **Integrate:** Add LangChain callback
4. **Monitor:** View traces in dashboard
5. **Evaluate:** Set up LLM-as-judge scoring
6. **Annotate:** Create human review queue
7. **Alert:** Configure cost/latency monitoring

## Resources

- **GitHub:** https://github.com/langfuse/langfuse
- **Cloud:** https://cloud.langfuse.com
- **Docs:** https://docs.langfuse.com
- **Discord:** Community support channel

---

**Document Version:** 1.0
**Last Verified:** March 31, 2026
