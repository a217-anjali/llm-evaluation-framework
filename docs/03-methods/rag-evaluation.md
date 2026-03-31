# RAG Evaluation Methods

## Overview

Retrieval-Augmented Generation (RAG) systems combine information retrieval with language generation, requiring evaluation at multiple levels: retrieval quality, generation quality, and end-to-end system performance. Unlike standard LLM evaluation, RAG evaluation must assess both components independently and their interaction.

## Component-Wise Evaluation

### Retrieval Metrics

Retrieval evaluation measures whether the system successfully finds relevant documents/passages for a given query.

#### Precision@K

Fraction of top-K retrieved documents that are relevant.

```python
def precision_at_k(relevant_docs, retrieved_docs, k):
    """
    Calculate precision@k
    relevant_docs: set of document IDs that are relevant
    retrieved_docs: list of document IDs returned by retriever (ordered)
    k: consider only top-k results
    """
    retrieved_at_k = set(retrieved_docs[:k])
    n_relevant = len(relevant_docs & retrieved_at_k)
    return n_relevant / k if k > 0 else 0.0

# Example:
# Query: "What is photosynthesis?"
# Relevant docs: {1, 5, 12}
# Retrieved: [5, 2, 1, 9, 3, 12, 8, 4, 7, 6]
# Precision@3 = 2/3 (docs 5, 1 are relevant; doc 2 is not)
# Precision@5 = 3/5 (docs 5, 1, 12 are relevant; docs 2, 9 are not)
```

**Interpretation:**
- High precision@5: Early results are good (good ranking)
- Precision@5 much higher than Precision@10: Strong ranking

#### Recall@K

Fraction of all relevant documents that appear in top-K results.

```python
def recall_at_k(relevant_docs, retrieved_docs, k):
    """
    Calculate recall@k
    """
    retrieved_at_k = set(retrieved_docs[:k])
    n_relevant = len(relevant_docs & retrieved_at_k)
    return n_relevant / len(relevant_docs) if relevant_docs else 0.0

# Same example:
# Recall@3 = 2/3 (2 of 3 relevant docs found)
# Recall@10 = 3/3 (all 3 relevant docs found by rank 10)
```

**Interpretation:**
- High recall@10, low recall@5: System finds docs but ranking is poor
- High recall@5: System ranks relevant docs highly

#### Mean Reciprocal Rank (MRR)

Average of the reciprocal ranks of the first relevant document.

```python
def mean_reciprocal_rank(relevant_docs_per_query, retrieved_docs_per_query):
    """
    Calculate MRR across queries
    """
    reciprocal_ranks = []

    for relevant_set, retrieved_list in zip(relevant_docs_per_query,
                                           retrieved_docs_per_query):
        # Find rank of first relevant document
        first_relevant_rank = None
        for rank, doc_id in enumerate(retrieved_list, 1):
            if doc_id in relevant_set:
                first_relevant_rank = rank
                break

        if first_relevant_rank is not None:
            reciprocal_ranks.append(1.0 / first_relevant_rank)
        else:
            reciprocal_ranks.append(0.0)

    return np.mean(reciprocal_ranks)

# Example:
# Query 1: First relevant doc at rank 1 → reciprocal = 1.0
# Query 2: First relevant doc at rank 5 → reciprocal = 0.2
# Query 3: No relevant doc found → reciprocal = 0.0
# MRR = (1.0 + 0.2 + 0.0) / 3 = 0.4
```

**Interpretation:**
- MRR = 1.0: Perfect (all first relevant docs at rank 1)
- MRR = 0.5: Typical first relevant doc at rank 2
- MRR < 0.3: Poor ranking

#### Normalized Discounted Cumulative Gain (NDCG)

Accounts for ranking quality and relevance scores (not just binary relevant/irrelevant).

```python
def ndcg_at_k(relevance_scores, retrieved_scores, k):
    """
    Calculate NDCG@k
    relevance_scores: true relevance scores (0-5) for each document
    retrieved_scores: list of (doc_id, relevance_score) retrieved, ordered
    k: consider top-k results
    """
    # Actual DCG@k
    dcg = 0.0
    for rank, (doc_id, score) in enumerate(retrieved_scores[:k], 1):
        dcg += score / np.log2(rank + 1)

    # Ideal DCG@k (perfect ranking)
    ideal_scores = sorted(relevance_scores, reverse=True)[:k]
    idcg = 0.0
    for rank, score in enumerate(ideal_scores, 1):
        idcg += score / np.log2(rank + 1)

    ndcg = dcg / idcg if idcg > 0 else 0.0
    return ndcg

# Example:
# Retrieved: [(doc1, 5), (doc2, 2), (doc3, 4), (doc4, 0)]
# Relevant set relevances: [5, 4, 2, 0]
#
# DCG@4 = 5/log2(2) + 2/log2(3) + 4/log2(4) + 0/log2(5)
#       = 5/1 + 2/1.58 + 4/2 + 0 = 5 + 1.26 + 2 = 8.26
#
# Ideal: [5, 4, 2, 0] → IDCG = 5 + 2.52 + 1 = 8.52
#
# NDCG = 8.26 / 8.52 = 0.97
```

**Interpretation:**
- NDCG = 1.0: Perfect ranking
- NDCG > 0.90: Excellent ranking
- NDCG > 0.70: Good ranking
- NDCG < 0.50: Poor ranking

### Generation Metrics

Once documents are retrieved, evaluate whether the generation is faithful to and uses retrieved content properly.

#### Faithfulness

Whether the generated response is grounded in the retrieved documents (no hallucinations).

```python
def evaluate_faithfulness(query, retrieved_docs, generated_response):
    """
    Check if all claims in response are supported by retrieved docs
    Returns: (is_faithful: bool, unsupported_claims: list[str])
    """
    # Method 1: LLM-based evaluation
    prompt = f"""
    Query: {query}

    Retrieved documents:
    {chr(10).join(retrieved_docs)}

    Generated response:
    {generated_response}

    Are all factual claims in the response supported by the retrieved documents?
    List any unsupported claims.

    Response: [Yes/No], Unsupported claims: [list or "None"]
    """

    # Call LLM judge...
    result = call_llm(prompt)

    return result

# Alternative: Entailment-based
from transformers import pipeline

def faithfulness_via_entailment(retrieved_docs, generated_response):
    """
    Use NLI model to check if response entails from documents
    """
    entailment_model = pipeline("zero-shot-classification",
                               model="facebook/bart-large-mnli")

    premise = " ".join(retrieved_docs)
    hypothesis = generated_response

    result = entailment_model(hypothesis, [premise], multi_class=True)
    # result['scores'][0] is entailment probability

    return result['scores'][0]
```

**Evaluation Criteria:**
- 1 = Multiple unsupported claims
- 2 = Some unsupported claims
- 3 = Mostly faithful with minor unsupported details
- 4 = Faithful; all major claims supported
- 5 = Completely faithful; well-grounded in sources

#### Relevance

Whether the generated response actually answers the query.

```python
def evaluate_relevance(query, generated_response):
    """
    Semantic similarity between query intent and response content
    """
    from sentence_transformers import SentenceTransformer, util

    model = SentenceTransformer('all-MiniLM-L6-v2')

    query_embedding = model.encode(query, convert_to_tensor=True)
    response_embedding = model.encode(generated_response, convert_to_tensor=True)

    similarity = util.pytorch_cos_sim(query_embedding, response_embedding)

    return float(similarity)

# Alternatively: LLM-based
def relevance_via_llm(query, response):
    """
    Direct relevance assessment from LLM judge
    """
    prompt = f"""
    Query: {query}
    Response: {response}

    Does this response directly answer the query?
    Score 1-5 where 5=perfectly answers, 1=completely irrelevant
    """
    score = call_llm_scoring(prompt)
    return score
```

**Interpretation:**
- Similarity > 0.85: Highly relevant
- Similarity 0.70-0.85: Relevant
- Similarity < 0.50: Off-topic

#### Completeness

Whether the response covers all aspects of the query.

```python
def evaluate_completeness(query, response, retrieved_docs):
    """
    Check if response covers all information needs
    """
    prompt = f"""
    Query: {query}
    Response: {response}
    Available information: {chr(10).join(retrieved_docs)}

    Does the response comprehensively cover the query?
    What important aspects are missing, if any?

    Score: [1-5]
    Missing aspects: [list]
    """
    result = call_llm(prompt)
    return result
```

#### Citation Quality

How well the response attributes claims to sources.

```python
def evaluate_citations(query, response, retrieved_docs):
    """
    Check if response properly attributes claims to sources
    Metrics:
    - Coverage: % of response supporting facts with citations
    - Precision: % of citations that are accurate
    - Consistency: Do citations point to relevant docs?
    """
    citations = extract_citations(response)  # [("claim", doc_id), ...]

    # Precision: citations actually support the claim
    correct_citations = 0
    for claim, doc_id in citations:
        if doc_contains_support(retrieved_docs[doc_id], claim):
            correct_citations += 1

    citation_precision = correct_citations / len(citations) if citations else 1.0

    # Coverage: what % of claims are cited?
    claims = extract_claims(response)
    cited_claims = len(citations)
    citation_coverage = cited_claims / len(claims) if claims else 0.0

    return {
        'citation_precision': citation_precision,
        'citation_coverage': citation_coverage,
        'total_citations': len(citations),
        'total_claims': len(claims)
    }
```

## End-to-End Evaluation Metrics

### Context Precision and Recall

Jointly assess whether retrieved context is both relevant and sufficient.

```python
def context_precision_recall(query, relevant_docs, retrieved_docs,
                            generated_response):
    """
    Holistic assessment of retrieved docs' usefulness for generating good response
    """
    # Context Precision: fraction of retrieved docs that are useful for good response
    useful_docs = identify_used_docs(generated_response, retrieved_docs)
    context_precision = len(useful_docs) / len(retrieved_docs)

    # Context Recall: fraction of relevant docs actually retrieved
    context_recall = len(set(useful_docs) & set(relevant_docs)) / len(relevant_docs)

    return {
        'context_precision': context_precision,
        'context_recall': context_recall,
        'useful_docs': useful_docs,
        'relevant_docs': relevant_docs
    }
```

### Answer Relevance

Does the final answer adequately address the original question?

```python
def answer_relevance_score(query, generated_response):
    """
    Measures if generated response is relevant to query
    Uses semantic similarity and LLM-based scoring
    """
    # Semantic similarity
    sem_sim = evaluate_relevance(query, generated_response)

    # LLM-based judgment
    llm_score = evaluate_relevance_llm(query, generated_response)

    # Composite
    answer_relevance = 0.4 * sem_sim + 0.6 * (llm_score / 5.0)

    return answer_relevance
```

## Ragas Framework

### Overview

RAGAS (Retrieval-Augmented Generation Assessment) is a framework specifically designed for RAG evaluation, providing pre-built metrics and evaluation pipelines.

### Core Metrics

**1. Context Relevance**

Measures whether each retrieved context is relevant to the query.

```python
from ragas.metrics import ContextRelevancy
from ragas.llm import LangchainLLMWrapper
from langchain.chat_models import ChatOpenAI

# Setup
llm = ChatOpenAI(model="gpt-4")
llm_wrapper = LangchainLLMWrapper(llm)

context_relevancy = ContextRelevancy(llm=llm_wrapper)

# Example evaluation
sample = {
    "question": "What is photosynthesis?",
    "contexts": [
        "Photosynthesis is the process by which plants convert sunlight...",
        "The capital of France is Paris...",  # Irrelevant
        "Chlorophyll absorbs light energy in photosynthesis..."
    ]
}

score = context_relevancy.score(sample)
# score.value: typically 0-1, higher is better
# Expected: ~0.67 (2 of 3 contexts are relevant)
```

**2. Faithfulness**

Measures whether generated response is factually consistent with contexts.

```python
from ragas.metrics import Faithfulness

faithfulness = Faithfulness(llm=llm_wrapper)

sample = {
    "question": "What causes photosynthesis?",
    "contexts": [
        "Photosynthesis is driven by sunlight energy..."
    ],
    "answer": "Photosynthesis is powered by solar energy."
}

score = faithfulness.score(sample)
# Expected: high (answer is faithful to context)
```

**3. Answer Relevance**

Measures whether answer addresses the question.

```python
from ragas.metrics import AnswerRelevancy

answer_relevancy = AnswerRelevancy(llm=llm_wrapper)

sample = {
    "question": "What is photosynthesis?",
    "answer": "Photosynthesis is the process by which plants use sunlight..."
}

score = answer_relevancy.score(sample)
# Expected: high (answer directly addresses question)
```

### Running Full RAG Evaluation

```python
from ragas import evaluate
from ragas.metrics import (
    context_relevancy,
    faithfulness,
    answer_relevancy,
    context_recall,  # Compares against golden context
    context_precision
)

# Your RAG system's outputs
rag_results = [
    {
        "question": "What is photosynthesis?",
        "contexts": [retrieved_doc1, retrieved_doc2, ...],
        "answer": generated_answer,
        # Optional: ground truth for comparison
        "ground_truth": reference_answer
    },
    ...  # more examples
]

# Evaluate
results = evaluate(
    rag_results,
    metrics=[
        context_relevancy,
        faithfulness,
        answer_relevancy,
        context_recall,
        context_precision
    ]
)

# Results summary
print(results)
# Output:
# context_relevancy: 0.82 ± 0.15
# faithfulness: 0.76 ± 0.18
# answer_relevancy: 0.88 ± 0.10
# context_recall: 0.71 ± 0.22
# context_precision: 0.65 ± 0.20
```

### Custom Metrics in Ragas

```python
from ragas.metrics import MetricWithLLM
from ragas.metrics.utils import get_llm

class CustomRAGMetric(MetricWithLLM):
    name: str = "custom_rag_metric"
    description: str = "Custom evaluation metric"

    def _score(self, row):
        """
        row contains: question, contexts, answer, [ground_truth]
        """
        # Your custom scoring logic
        score_value = self.compute_score(
            question=row.question,
            contexts=row.contexts,
            answer=row.answer
        )
        return score_value

    def compute_score(self, question, contexts, answer):
        # Implement your metric
        return 0.85  # Example score

# Use in evaluation
custom_metric = CustomRAGMetric(llm=llm_wrapper)
results = evaluate(rag_results, metrics=[custom_metric])
```

## ARES Framework

### Overview

ARES (Automated Retrieval Evaluation with Self-training) provides self-training for evaluators without hand-labeled data.

**Key Innovation:**
- Automatically generates pseudo-labels from retriever predictions
- Uses them to train evaluator model
- Evaluates RAG system without manual annotations

### ARES Pipeline

```python
from ares import ARESEvaluator

# Initialize evaluator
evaluator = ARESEvaluator(
    retriever_model="bge-large-en-v1.5",
    generator_model="gpt-4",
    device="cuda"
)

# Pseudo-label generation (no manual labels needed)
queries = ["What is photosynthesis?", ...]
documents = [doc1, doc2, ...]  # Knowledge base

pseudo_labels = evaluator.generate_pseudo_labels(
    queries=queries,
    documents=documents,
    sample_size=100  # Evaluate on sample
)

# Train evaluator on pseudo-labels
evaluator.train(pseudo_labels)

# Evaluate your RAG system
rag_outputs = {
    "questions": [...],
    "contexts": [...],
    "answers": [...]
}

scores = evaluator.evaluate(rag_outputs)
# Outputs relevance, faithfulness, answerability scores
```

## Hallucination Detection

### LLM-Based Detection

```python
def detect_hallucinations(query, retrieved_docs, response):
    """
    Identify false/unsupported claims in response
    """
    prompt = f"""
    Context documents:
    {chr(10).join(retrieved_docs)}

    Generated response:
    {response}

    Identify any statements in the response that:
    1. Are not supported by the context
    2. Contradict the context
    3. Make up specific facts not in context

    For each hallucination, explain why it's unsupported.
    """

    result = call_llm(prompt)
    return parse_hallucinations(result)

# Example response:
# Hallucination 1: "Photosynthesis produces oxygen" - NOT FOUND in provided context
# This is a true claim but needs evidence from docs
```

### Token-Level Attribution

```python
def token_level_attribution(response, retrieved_docs):
    """
    For each token in response, find supporting source
    """
    from nltk.tokenize import sent_tokenize

    sentences = sent_tokenize(response)
    attribution_map = {}

    for sent_idx, sentence in enumerate(sentences):
        # Find supporting document for this sentence
        supporting_doc = find_supporting_doc(sentence, retrieved_docs)

        if supporting_doc:
            attribution_map[sent_idx] = {
                'sentence': sentence,
                'supported': True,
                'source': supporting_doc
            }
        else:
            attribution_map[sent_idx] = {
                'sentence': sentence,
                'supported': False,
                'source': None,
                'flag': 'HALLUCINATION'
            }

    return attribution_map
```

## Building a RAG Evaluation Pipeline

### End-to-End Example

```python
import pandas as pd
import numpy as np
from collections import defaultdict

class RAGEvaluationPipeline:
    def __init__(self, llm_judge_model="gpt-4"):
        self.llm = llm_judge_model
        self.results = defaultdict(list)

    def evaluate_retrieval(self, queries, relevant_docs, retrieved_docs):
        """
        Evaluate retrieval component
        """
        metrics = []

        for query, relevant, retrieved in zip(queries, relevant_docs,
                                             retrieved_docs):
            metric_dict = {
                'query': query,
                'precision@5': precision_at_k(relevant, retrieved, 5),
                'recall@5': recall_at_k(relevant, retrieved, 5),
                'ndcg@10': ndcg_at_k(relevant, retrieved, 10),
                'mrr': mean_reciprocal_rank([relevant], [retrieved])
            }
            metrics.append(metric_dict)

        retrieval_df = pd.DataFrame(metrics)
        print("\nRETRIEVAL METRICS:")
        print(retrieval_df.describe())

        self.results['retrieval'] = retrieval_df
        return retrieval_df

    def evaluate_generation(self, queries, retrieved_docs, responses):
        """
        Evaluate generation component
        """
        metrics = []

        for query, docs, response in zip(queries, retrieved_docs, responses):
            # Faithfulness
            faithfulness = evaluate_faithfulness(query, docs, response)

            # Relevance
            relevance = evaluate_relevance(query, response)

            # Citation quality
            citation_metrics = evaluate_citations(query, response, docs)

            metric_dict = {
                'query': query,
                'faithfulness': faithfulness,
                'relevance': relevance,
                'citation_precision': citation_metrics['citation_precision'],
                'citation_coverage': citation_metrics['citation_coverage']
            }
            metrics.append(metric_dict)

        generation_df = pd.DataFrame(metrics)
        print("\nGENERATION METRICS:")
        print(generation_df.describe())

        self.results['generation'] = generation_df
        return generation_df

    def evaluate_end_to_end(self, queries, relevant_docs, retrieved_docs,
                            responses):
        """
        Overall RAG system evaluation
        """
        # Component evals
        self.evaluate_retrieval(queries, relevant_docs, retrieved_docs)
        self.evaluate_generation(queries, retrieved_docs, responses)

        # End-to-end metrics
        e2e_metrics = []
        for query, rel_docs, ret_docs, response in zip(
            queries, relevant_docs, retrieved_docs, responses
        ):
            # Does retrieved context enable good answer?
            context_usefulness = evaluate_context_usefulness(
                query, ret_docs, response
            )

            # Final answer quality
            answer_quality = evaluate_answer_quality(query, response)

            e2e_metrics.append({
                'context_usefulness': context_usefulness,
                'answer_quality': answer_quality,
                'e2e_score': 0.6 * context_usefulness + 0.4 * answer_quality
            })

        e2e_df = pd.DataFrame(e2e_metrics)
        print("\nEND-TO-END METRICS:")
        print(e2e_df.describe())

        self.results['e2e'] = e2e_df
        return e2e_df

    def generate_report(self):
        """
        Summarize evaluation results
        """
        print("\n" + "="*50)
        print("RAG EVALUATION REPORT")
        print("="*50)

        for component, df in self.results.items():
            print(f"\n{component.upper()}:")
            print(df.describe())

            # Failure analysis
            if component == 'retrieval':
                low_recall = df[df['recall@5'] < 0.5]
                if len(low_recall) > 0:
                    print(f"  WARNING: {len(low_recall)} queries with poor recall")

            if component == 'generation':
                low_faith = df[df['faithfulness'] < 0.7]
                if len(low_faith) > 0:
                    print(f"  WARNING: {len(low_faith)} responses with hallucinations")

# Usage
pipeline = RAGEvaluationPipeline()
pipeline.evaluate_end_to_end(
    queries=test_queries,
    relevant_docs=ground_truth_docs,
    retrieved_docs=retriever_output,
    responses=generator_output
)
pipeline.generate_report()
```

### Interpretation Guide

**Metric Combinations and What They Mean:**

| Retrieval | Generation | Interpretation |
|---|---|---|
| High | High | Excellent RAG system |
| High | Low | Retriever works; generator struggles with context |
| Low | High | Retriever fails; generator can't compensate |
| Low | Low | Systematic failure; rethink approach |

**When Scores Are Low:**

- **Low Precision@5, High Recall@10**: Retriever ranks poorly; improve ranking
- **Low Recall**: Retriever misses relevant docs; improve retriever
- **Low Faithfulness**: Generator hallucinates; use more grounded generation
- **Low Citation Coverage**: Generator doesn't attribute claims; train on citations

## Implementation Checklist

- [ ] Define evaluation dataset with gold-standard relevance labels
- [ ] Implement retrieval metrics (precision@k, recall@k, NDCG, MRR)
- [ ] Implement generation metrics (faithfulness, relevance, citations)
- [ ] Setup Ragas framework for automated evaluation
- [ ] Baseline comparison: benchmark against existing systems
- [ ] Hallucination detection: implement token-level attribution
- [ ] Human validation: run 100-200 item human eval for correlation
- [ ] Build evaluation dashboard: track metrics over time
- [ ] Error analysis: categorize failures (retrieval vs. generation)
- [ ] Document evaluation procedures and results
