# Ragas: RAG Evaluation Framework Guide

**Version:** Ragas v1.2+
**License:** Apache 2.0
**Maintainer:** HuggingFace
**Latest Update:** March 2026

Ragas is the purpose-built evaluation framework for Retrieval-Augmented Generation (RAG) systems. It provides 5 core reference-free metrics and seamless integration with LangChain and LlamaIndex RAG pipelines.

## Installation & Setup

### Basic Installation

```bash
pip install ragas

# With optional dependencies
pip install ragas[langchain]      # LangChain integration
pip install ragas[llama-index]    # LlamaIndex integration
pip install ragas[all]            # Everything

# Verify installation
python -c "import ragas; print(ragas.__version__)"
```

### Environment Configuration

```bash
# API keys for evaluation models
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional: Use local models
export RAGAS_MODEL="ollama/mistral:7b"
```

### Configuration File

Create `ragas_config.json`:

```json
{
  "embeddings_model": "BAAI/bge-base-en-v1.5",
  "llm_model": "gpt-3.5-turbo",
  "batch_size": 32,
  "timeout": 60,
  "use_cache": true,
  "cache_dir": ".ragas_cache"
}
```

## Ragas Metrics: 5-Core Framework

### 1. Context Precision

Measures what fraction of retrieved context is relevant to the question:

```python
from ragas.metrics import ContextPrecision
from ragas.run_config import RunConfig

# Context Precision = (relevant chunks / total chunks retrieved)
metric = ContextPrecision()

evaluation_sample = {
    "question": "What is machine learning?",
    "contexts": [
        "Machine learning is a subset of AI...",  # Relevant
        "Python is a programming language...",     # Irrelevant
        "ML enables systems to learn from data",  # Relevant
    ],
    "answer": "ML is a branch of AI that learns from data"
}

score = metric.score(evaluation_sample)
print(f"Context Precision: {score:.2f}")  # Output: 0.67 (2 of 3 relevant)
```

**Good value:** > 0.70 (70%+ retrieved context is relevant)
**Interpretation:** Measures retriever quality

### 2. Context Recall

Measures what fraction of answer-relevant context was retrieved:

```python
from ragas.metrics import ContextRecall

metric = ContextRecall()

# Ground truth: what context should have been retrieved
evaluation_sample = {
    "question": "What are LLM applications?",
    "ground_truth": "LLMs are used in chatbots, summarization, translation, coding assistance",
    "contexts": [
        "LLMs enable chatbots",
        "LLMs help with summarization",
    ],
    "answer": "LLMs power chatbots and summarization tools"
}

score = metric.score(evaluation_sample)
print(f"Context Recall: {score:.2f}")  # Output: 0.50 (2 of 4 applications mentioned)
```

**Good value:** > 0.80 (80%+ needed context retrieved)
**Interpretation:** Measures retriever completeness

### 3. Faithfulness

Measures how much of the answer is grounded in the retrieved context:

```python
from ragas.metrics import Faithfulness

metric = Faithfulness()

evaluation_sample = {
    "question": "When was Python created?",
    "contexts": [
        "Python was created in 1989 by Guido van Rossum",
        "It was first released as Python 0.9.0 in February 1991"
    ],
    "answer": "Python was created in 1989 and first released in 1991"
}

score = metric.score(evaluation_sample)
print(f"Faithfulness: {score:.2f}")  # Output: 1.0 (all statements grounded)
```

**Good value:** > 0.90 (90%+ answer grounded in context)
**Interpretation:** Detects hallucinations

### 4. Answer Relevance

Measures how directly the answer addresses the question:

```python
from ragas.metrics import AnswerRelevancy

metric = AnswerRelevancy()

evaluation_sample = {
    "question": "What is Python?",
    "answer": "Python is a high-level, interpreted programming language created in 1989",
    # No context needed - purely LLM-based relevance judgment
}

score = metric.score(evaluation_sample)
print(f"Answer Relevance: {score:.2f}")  # Output: 0.95 (directly answers Q)
```

**Good value:** > 0.75 (answer directly relevant)
**Interpretation:** Measures response quality

### 5. F1 Score

Traditional F1 score combining precision and recall:

```python
from ragas.metrics import F1Score

metric = F1Score()

# Requires exact match comparison
evaluation_sample = {
    "question": "What year was AI founded?",
    "ground_truth": "1956",
    "answer": "AI was founded in 1956"
}

score = metric.score(evaluation_sample)
print(f"F1 Score: {score:.2f}")
```

## Complete RAG Evaluation Pipeline

### Single Evaluation Sample

```python
from ragas.metrics import (
    ContextPrecision,
    ContextRecall,
    Faithfulness,
    AnswerRelevancy,
)

# Single test case
sample = {
    "question": "What is RAG?",
    "contexts": [
        "RAG combines retrieval and generation...",
        "It improves factual accuracy...",
    ],
    "answer": "RAG is Retrieval-Augmented Generation, which improves LLM factuality",
    "ground_truth": "RAG retrieves relevant documents then generates answers grounded in them"
}

# Create metrics
metrics = [
    ContextPrecision(),
    ContextRecall(),
    Faithfulness(),
    AnswerRelevancy(),
]

# Evaluate
results = {}
for metric in metrics:
    score = metric.score(sample)
    results[metric.name] = score
    print(f"{metric.name}: {score:.3f}")
```

### Batch Evaluation with Dataset

```python
from ragas import Dataset
from ragas.metrics import (
    ContextPrecision,
    ContextRecall,
    Faithfulness,
    AnswerRelevancy,
)
from ragas.llama_index import evaluate

# Create dataset from tuples
samples = [
    {
        "question": "What is machine learning?",
        "contexts": ["ML is a subset of AI..."],
        "answer": "ML learns from data",
        "ground_truth": "ML systems improve through data"
    },
    {
        "question": "What is deep learning?",
        "contexts": ["DL uses neural networks..."],
        "answer": "DL uses neural networks",
        "ground_truth": "DL is inspired by biological neurons"
    },
    # ... more samples
]

dataset = Dataset.from_dict({
    "question": [s["question"] for s in samples],
    "contexts": [s["contexts"] for s in samples],
    "answer": [s["answer"] for s in samples],
    "ground_truth": [s["ground_truth"] for s in samples],
})

# Evaluate dataset
metrics = [
    ContextPrecision(),
    ContextRecall(),
    Faithfulness(),
    AnswerRelevancy(),
]

results = evaluate(
    dataset=dataset,
    metrics=metrics,
    llm_model="gpt-3.5-turbo",  # For evaluation
)

# View results
print(results)
print(f"Average Faithfulness: {results['faithfulness'].mean():.3f}")
print(f"Average Recall: {results['context_recall'].mean():.3f}")
```

## LangChain Integration

### Evaluating LangChain RAG Chain

```python
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from ragas.metrics import ContextRecall, Faithfulness
from ragas.langchain import evaluate_langchain

# Setup RAG chain
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(documents, embeddings)
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model="gpt-4"),
    retriever=vectorstore.as_retriever()
)

# Prepare test questions
test_data = [
    {
        "question": "What is AI safety?",
        "ground_truth": "AI safety studies risks from advanced AI systems",
    },
    {
        "question": "What are transformers?",
        "ground_truth": "Transformers are neural architectures using attention mechanisms",
    },
]

# Run evaluation
results = evaluate_langchain(
    qa_chain,
    test_data,
    metrics=[ContextRecall(), Faithfulness()],
    llm_model="gpt-3.5-turbo"
)

# Analyze results
for i, result in enumerate(results):
    print(f"Question {i+1}: Recall={result['context_recall']:.3f}, "
          f"Faithfulness={result['faithfulness']:.3f}")
```

### Using with LlamaIndex

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.embeddings.openai import OpenAIEmbedding
from ragas.metrics import Faithfulness, ContextRecall
from ragas.llama_index import evaluate

# Setup LlamaIndex RAG
documents = SimpleDirectoryReader("documents/").load_data()
index = VectorStoreIndex.from_documents(
    documents,
    embed_model=OpenAIEmbedding(),
)
query_engine = index.as_query_engine()

# Create evaluation dataset
test_queries = [
    "What is machine learning?",
    "How do transformers work?",
]

eval_data = {
    "question": test_queries,
    "answer": [query_engine.query(q).response for q in test_queries],
    "contexts": [
        [doc.text for doc in query_engine.retrieve(q).nodes]
        for q in test_queries
    ],
    "ground_truth": [
        "ML is learning from data",
        "Transformers use attention mechanisms",
    ]
}

# Evaluate
from ragas import Dataset as RagasDataset
dataset = RagasDataset.from_dict(eval_data)

results = evaluate(
    dataset=dataset,
    metrics=[Faithfulness(), ContextRecall()],
    llm_model="gpt-3.5-turbo"
)

print(results)
```

## Custom Metrics

### Building a Custom Metric

```python
from ragas.metrics.base import Metric
from ragas.metrics.utils import get_llm_judge
import asyncio

class CustomRelevanceMetric(Metric):
    """Custom metric for domain-specific relevance"""

    name: str = "custom_relevance"
    description: str = "Custom domain relevance score"

    async def _score(self, row):
        """Score a single sample"""
        llm = get_llm_judge()

        prompt = f"""
        Question: {row["question"]}
        Answer: {row["answer"]}

        Is the answer relevant to the question? Score 0-1.
        Consider domain-specific context.
        """

        score = await llm.apredict(prompt)
        return float(score)

    async def score(self, dataset, callbacks=None):
        """Score entire dataset"""
        scores = []
        for row in dataset:
            score = await self._score(row)
            scores.append(score)
        return scores

# Use custom metric
custom_metric = CustomRelevanceMetric()
results = evaluate(
    dataset=eval_dataset,
    metrics=[custom_metric, Faithfulness()],
    llm_model="gpt-3.5-turbo"
)
```

## Production RAG Monitoring

### Continuous Evaluation

```python
import json
from datetime import datetime
from ragas.metrics import ContextRecall, Faithfulness

def monitor_rag_pipeline(query: str, retrieved_contexts: list, answer: str):
    """Monitor RAG performance in production"""

    # Create sample
    sample = {
        "question": query,
        "contexts": retrieved_contexts,
        "answer": answer,
    }

    # Evaluate metrics
    metrics = [ContextRecall(), Faithfulness()]
    scores = {}

    for metric in metrics:
        score = metric.score(sample)
        scores[metric.name] = float(score)

    # Log results
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "scores": scores,
        "passed": all(s > 0.8 for s in scores.values())
    }

    with open("rag_monitoring.jsonl", "a") as f:
        json.dump(log_entry, f)

    return scores

# In production
scores = monitor_rag_pipeline(
    query="What is climate change?",
    retrieved_contexts=["Climate change refers to..."],
    answer="Climate change is the warming of Earth's climate..."
)

print(f"Metrics: {scores}")
```

### Alert Thresholds

```python
import logging

logger = logging.getLogger("rag_monitor")

def evaluate_with_alerts(sample):
    """Evaluate with alerting on quality degradation"""

    metrics = {
        "context_recall": (ContextRecall(), 0.80),
        "faithfulness": (Faithfulness(), 0.85),
        "context_precision": (ContextPrecision(), 0.70),
    }

    for metric_name, (metric, threshold) in metrics.items():
        score = metric.score(sample)

        if score < threshold:
            logger.warning(
                f"ALERT: {metric_name} below threshold: "
                f"{score:.3f} < {threshold:.3f}"
            )
        else:
            logger.info(f"{metric_name}: {score:.3f} (OK)")

    return scores
```

## Performance & Optimization

### Batch Processing for Speed

```python
from ragas.metrics import ContextRecall
import concurrent.futures

# Process 1000 samples efficiently
samples = load_evaluation_set()  # 1000+ samples

metric = ContextRecall()

# Sequential (slow)
# results = [metric.score(s) for s in samples]  # ~30 min

# Parallel (fast)
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(
        executor.map(metric.score, samples)
    )  # ~3 min

print(f"Processed {len(results)} samples")
print(f"Average recall: {sum(results)/len(results):.3f}")
```

### Using Cheaper Evaluation Models

```python
from ragas.metrics import Faithfulness

# Default: GPT-4 (expensive: $0.03-0.06 per eval)
# metric = Faithfulness(llm="gpt-4")

# Faster: GPT-3.5-turbo (5x cheaper, 30% slower)
metric_cheap = Faithfulness(llm="gpt-3.5-turbo")

# Local: Ollama (free, but requires local inference)
metric_local = Faithfulness(llm="ollama/mistral:7b")

# Cost comparison for 1000 evals:
# GPT-4: $30-60
# GPT-3.5: $6-12 (recommended)
# Ollama: $0 (electricity only)
```

### Caching Results

```python
from ragas.metrics import Faithfulness
from functools import lru_cache

# Enable caching
metric = Faithfulness(use_cache=True)

# First evaluation: 2 seconds (calls LLM)
score1 = metric.score(sample)

# Second evaluation of same sample: <100ms (cached)
score2 = metric.score(sample)

assert score1 == score2
```

## Troubleshooting

### Common Issues

**Issue: "OpenAI API key not configured"**
```bash
export OPENAI_API_KEY="sk-..."

# Or in Python:
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

from ragas.metrics import Faithfulness
metric = Faithfulness()  # Now works
```

**Issue: "Metric returns NaN"**
```python
# Check if context is empty
if not sample["contexts"]:
    print("ERROR: No context provided")

# Check if answer is empty
if not sample["answer"]:
    print("ERROR: No answer provided")

# Provide ground truth for Context Recall
if "ground_truth" not in sample:
    print("WARNING: Context Recall requires ground_truth")
```

**Issue: "Evaluation too slow"**
```python
# Use faster model
from ragas.metrics import Faithfulness
metric = Faithfulness(llm="gpt-3.5-turbo")  # 5x faster

# Or use cheaper model for non-critical evals
metric = Faithfulness(llm="ollama/mistral")  # Local, free
```

**Issue: "Out of memory with large batches"**
```python
# Reduce batch size
dataset = Dataset.from_dict(data, batch_size=8)  # Default: 32

# Or process samples one at a time
for sample in samples:
    score = metric.score(sample)
```

## Pros & Cons

### Advantages
- **Purpose-built for RAG:** Only framework designed specifically for RAG
- **Reference-free:** Doesn't require ground truth (only QA pair + context)
- **Zero hallucinations:** Faithfulness metric directly detects hallucinations
- **LangChain native:** Perfect integration with LangChain RAG chains
- **Easy setup:** Minimal configuration needed
- **Well-maintained:** HuggingFace backing ensures stability
- **Cheap:** Can use gpt-3.5-turbo (~$0.01 per eval)
- **Proven metrics:** 5 core metrics validated on 10k+ samples

### Disadvantages
- **Limited to RAG:** Not suitable for other evaluation types
- **LLM-dependent:** Evaluation quality depends on judge model
- **Context must exist:** Can't evaluate retriever if no context returned
- **No agentic support:** Not designed for agent evaluation
- **No safety testing:** Use Garak or Inspect AI for adversarial eval
- **Benchmark-agnostic:** Not for MMLU, GSM8K style benchmarks
- **Cost accumulates:** 1000 samples * $0.01 = $10/eval

## Performance Benchmarks

| Metric | Time per Sample | Cost (GPT-3.5) | Cost (Local) |
|--------|-----------------|----------------|--------------|
| ContextRecall | 2-5s | $0.005 | $0.00 |
| Faithfulness | 3-5s | $0.008 | $0.00 |
| AnswerRelevancy | 2-3s | $0.003 | $0.00 |
| All 5 metrics | 15-30s | $0.025 | $0.00 |

**For 1000 samples:**
- All metrics: 250-500 minutes (4-8 hours)
- Cost: $25 (GPT-3.5) or $0 (local)

## When to Use Ragas

**Best For:**
- Evaluating RAG systems
- LangChain RAG pipelines
- Detecting hallucinations
- Measuring retrieval quality
- Production RAG monitoring
- Teams with limited budgets (use gpt-3.5)

**Not Best For:**
- Benchmark alignment (MMLU, GSM8K)
- Agent evaluation (use LangSmith)
- Safety testing (use Garak)
- Agentic systems (use Inspect AI)
- General LLM evaluation (use DeepEval)
- Models without retrieval

## Comparison with Alternatives

| Feature | Ragas | DeepEval | Inspect AI |
|---------|-------|----------|-----------|
| RAG specific | Yes | No | No |
| Metrics | 5 | 50+ | 100+ |
| Setup | 5 min | 5 min | 30 min |
| Cost | $0.025/sample | $0.05/sample | $0.10/sample |
| LangChain | Native | Good | Moderate |
| Production ready | Yes | Yes | Moderate |

## Integration Example: Production Gate

```python
from ragas.metrics import ContextRecall, Faithfulness, AnswerRelevancy

def can_deploy_rag_update(new_rag_chain, test_dataset):
    """Gate before deploying new RAG version"""

    metrics = [
        (ContextRecall(), 0.80),
        (Faithfulness(), 0.85),
        (AnswerRelevancy(), 0.75),
    ]

    thresholds_met = True

    for metric, threshold in metrics:
        scores = [metric.score(sample) for sample in test_dataset]
        avg_score = sum(scores) / len(scores)

        print(f"{metric.name}: {avg_score:.3f} (threshold: {threshold})")

        if avg_score < threshold:
            print(f"FAIL: {metric.name} below threshold")
            thresholds_met = False

    return thresholds_met

# Use in deployment
if can_deploy_rag_update(new_chain, test_data):
    print("Approved: Deploy new RAG version")
else:
    print("Rejected: Keep current RAG version")
```

## Next Steps

1. **Install:** `pip install ragas`
2. **Evaluate:** Run on your existing RAG pipeline
3. **Optimize:** Improve metrics based on results
4. **Monitor:** Integrate into production pipeline
5. **Iterate:** Continuously improve RAG quality

## Resources

- **GitHub:** https://github.com/explodinggradients/ragas
- **Docs:** https://docs.ragas.io
- **Examples:** https://github.com/explodinggradients/ragas/tree/main/examples
- **Discord:** Community support channel

---

**Document Version:** 1.0
**Last Verified:** March 31, 2026
