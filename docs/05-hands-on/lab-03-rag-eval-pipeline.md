# Lab 03: End-to-End RAG Evaluation Pipeline

**Difficulty:** Yellow (Intermediate)
**Time Estimate:** 75 minutes
**Tools:** Ragas v1.2, LangChain, OpenAI/Anthropic, Python

## Objectives

By the end of this lab, you will:
- Build a working Retrieval-Augmented Generation (RAG) pipeline
- Create a comprehensive evaluation dataset
- Run Ragas metrics (faithfulness, context relevancy, answer relevancy)
- Analyze component-wise results to identify failure modes
- Create visualizations showing metric distributions
- Identify optimization opportunities for each pipeline component

## Prerequisites

- Python 3.11 or higher
- API access to an LLM (OpenAI GPT-4, Claude, etc.)
- API access to embeddings (OpenAI, Cohere, HuggingFace)
- ~2GB RAM and internet connectivity
- Basic understanding of RAG systems
- 30 minutes to run evaluations

## Setup

### 3.1 Install Dependencies

```bash
mkdir -p ~/rag-eval-lab && cd ~/rag-eval-lab
python3.11 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install ragas==0.1.2
pip install langchain==0.1.7
pip install langchain-openai==0.1.0
pip install langchain-anthropic==0.1.0
pip install langchain-community==0.1.0
pip install python-dotenv==1.0.0
pip install pandas==2.1.4
pip install numpy==1.24.3
pip install matplotlib==3.8.2
pip install seaborn==0.13.0
pip install tqdm==4.66.2
```

### 3.2 Configure API Keys

Create `.env`:
```bash
cat > .env << 'EOF'
# LLM Provider (choose one)
OPENAI_API_KEY=sk-xxxxx
# ANTHROPIC_API_KEY=sk-ant-xxxxx

# Embeddings Provider
OPENAI_API_KEY=sk-xxxxx

# Optional: HuggingFace (for free embeddings)
HUGGINGFACE_API_KEY=hf_xxxxx
EOF

chmod 600 .env
```

Test setup:
```bash
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('✓ Setup complete')
"
```

## Step-by-Step Instructions

### Step 1: Create Sample Knowledge Base (10 minutes)

Build a document corpus for RAG to retrieve from.

**File: `knowledge_base.py`**
```python
#!/usr/bin/env python3
"""
Create a sample knowledge base (document corpus)
"""

import json
from typing import List, Dict

# Sample documents about various topics
DOCUMENTS = [
    {
        "id": "doc_001",
        "title": "Introduction to Machine Learning",
        "content": """Machine learning is a branch of artificial intelligence that enables
        computers to learn from data without being explicitly programmed. There are three main
        types of machine learning: supervised learning, unsupervised learning, and reinforcement
        learning. In supervised learning, the algorithm learns from labeled data, learning to
        map inputs to outputs. Examples include classification (predicting categories) and
        regression (predicting continuous values). Unsupervised learning finds patterns in
        unlabeled data, such as clustering similar data points together. Reinforcement learning
        trains agents to maximize rewards through interaction with an environment. Modern machine
        learning relies heavily on deep learning, using neural networks with multiple layers to
        learn complex patterns in data. The field has applications in computer vision, natural
        language processing, autonomous vehicles, and medical diagnosis."""
    },
    {
        "id": "doc_002",
        "title": "Neural Networks and Deep Learning",
        "content": """A neural network is a computational model inspired by the structure of
        biological brains. It consists of interconnected nodes (neurons) organized in layers:
        input layer, hidden layers, and output layer. Each connection has a weight that is
        adjusted during training. Deep learning refers to neural networks with many hidden layers,
        allowing them to learn hierarchical representations. Convolutional Neural Networks (CNNs)
        excel at image recognition by using convolutional layers to detect features. Recurrent
        Neural Networks (RNNs) are designed for sequential data like time series or text,
        maintaining hidden states that capture temporal dependencies. Transformers, introduced
        in 2017, revolutionized NLP by using attention mechanisms to process sequences in
        parallel. The training process involves forward passes to compute predictions, backward
        passes to compute gradients, and parameter updates using optimization algorithms like
        stochastic gradient descent."""
    },
    {
        "id": "doc_003",
        "title": "Natural Language Processing",
        "content": """Natural Language Processing (NLP) is the field of AI focused on understanding
        and generating human language. Key NLP tasks include text classification, sentiment analysis,
        named entity recognition, and machine translation. Tokenization breaks text into words or
        subword units. Embedding methods like Word2Vec and GloVe convert words into numerical vectors.
        Language models predict the next token given previous context, learning statistical patterns
        in language. Large Language Models (LLMs) like GPT-4 and Claude are transformer-based models
        trained on billions of tokens, demonstrating emergent abilities in reasoning, coding, and
        creative tasks. Fine-tuning adapts pre-trained models to specific tasks with labeled data.
        Prompt engineering shapes model behavior through carefully crafted instructions. Challenges
        include handling ambiguity, coreference resolution, and dealing with out-of-distribution text."""
    },
    {
        "id": "doc_004",
        "title": "Retrieval-Augmented Generation (RAG)",
        "content": """Retrieval-Augmented Generation combines information retrieval with text
        generation. Instead of relying solely on a language model's parametric knowledge, RAG
        retrieves relevant documents from a corpus and uses them as context for generation. The
        process has three steps: retrieval, where a query is used to find relevant documents;
        reading, where relevant passages are extracted from retrieved documents; and generation,
        where the language model generates an answer using the retrieved context. Advantages of
        RAG include reducing hallucinations by grounding responses in retrieved facts, enabling
        knowledge updates without retraining, and improving transparency by showing source documents.
        Common retrieval methods include dense retrieval using embedding similarity and sparse
        retrieval using term overlap. RAG enables open-domain question answering, knowledge-intensive
        tasks, and fact-checking applications."""
    },
    {
        "id": "doc_005",
        "title": "Evaluation Metrics for NLP",
        "content": """Evaluation is crucial for assessing NLP system quality. For text generation,
        BLEU measures n-gram overlap between generated and reference texts. ROUGE evaluates
        summarization by comparing overlapping content units. METEOR incorporates stemming and
        synonymy for more meaningful comparisons. For NLG, human evaluation remains gold standard,
        assessing fluency, relevance, and factuality. Automatic metrics have limitations: they
        don't capture semantic similarity well and struggle with paraphrases. Reference-free
        metrics evaluate generation without requiring gold references. For information retrieval,
        precision and recall measure how many correct items are retrieved, while Mean Reciprocal
        Rank (MRR) emphasizes ranking position. For question answering, Exact Match (EM) requires
        perfect string match, while F1 score allows partial credit. Modern approaches use
        embedding-based metrics that compare semantic similarity rather than surface-level overlap."""
    },
    {
        "id": "doc_006",
        "title": "Knowledge Graphs and Semantic Networks",
        "content": """Knowledge graphs are structured representations of knowledge where entities are
        nodes and relationships are edges. They enable reasoning over interconnected facts. Knowledge
        graphs power search engines, recommendation systems, and question answering. Construction
        methods include manual curation, information extraction from text, and crowdsourcing. Link
        prediction infers missing relationships in incomplete graphs. Entity linking connects text
        mentions to knowledge base entries. Knowledge graph embedding methods like TransE represent
        entities and relations in vector space. Semantic networks, a related concept, explicitly
        represent semantic relationships between concepts. Integration of knowledge graphs with
        neural models enables neurosymbolic AI, combining learning and reasoning. Applications
        include improving search relevance and enabling multi-hop reasoning for complex questions."""
    },
    {
        "id": "doc_007",
        "title": "Transfer Learning and Fine-tuning",
        "content": """Transfer learning leverages knowledge from one task to improve performance on
        another. Pre-trained models learn general representations from large-scale data that transfer
        well to downstream tasks. Fine-tuning adapts pre-trained models using task-specific labeled
        data, typically updating some or all model parameters. Parameter-efficient fine-tuning methods
        like LoRA (Low-Rank Adaptation) add trainable low-rank modules to frozen base models,
        reducing memory and computation. Domain adaptation addresses distribution shift between source
        and target domains. Few-shot learning achieves good performance with minimal labeled examples.
        Meta-learning learns to learn, enabling rapid adaptation to new tasks. Multi-task learning
        shares representations across related tasks. Prompt-based learning treats fine-tuning as a
        prompting problem, finding good prompts rather than updating parameters. These techniques
        have made it practical to apply large models to diverse applications with limited resources."""
    },
    {
        "id": "doc_008",
        "title": "Model Evaluation and Benchmarking",
        "content": """Benchmarks provide standardized datasets and metrics for comparing model
        performance. GLUE benchmark evaluates general language understanding across 9 tasks. SQuAD
        measures reading comprehension on question answering. MMLU tests knowledge across 57 domains.
        Benchmark design requires carefully chosen evaluation sets that avoid contamination from
        training data. Adversarial evaluation tests robustness to edge cases and perturbations. Out-of-
        distribution evaluation assesses generalization beyond the training distribution. Statistical
        significance testing determines if performance differences are meaningful. Leaderboards enable
        comparative assessment and drive research progress. Limitations include potential overfitting
        to benchmarks and incomplete coverage of real-world requirements. Multi-dimensional evaluation
        across different aspects provides fuller picture than single metrics."""
    }
]

class KnowledgeBase:
    """Manager for document corpus"""

    def __init__(self, documents: List[Dict] = None):
        self.documents = documents or DOCUMENTS
        self.index = {doc['id']: doc for doc in self.documents}

    def get_all_documents(self) -> List[Dict]:
        """Get all documents"""
        return self.documents

    def get_document(self, doc_id: str) -> Dict:
        """Get a specific document"""
        return self.index.get(doc_id)

    def search_by_title(self, keyword: str) -> List[Dict]:
        """Search documents by title"""
        return [doc for doc in self.documents if keyword.lower() in doc['title'].lower()]

    def search_by_content(self, keyword: str) -> List[Dict]:
        """Search documents by content"""
        return [doc for doc in self.documents if keyword.lower() in doc['content'].lower()]

    def get_document_content(self, doc_id: str) -> str:
        """Get document content for RAG"""
        doc = self.get_document(doc_id)
        return doc['content'] if doc else ""

    def save_to_json(self, filepath: str = "knowledge_base.json"):
        """Save to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.documents, f, indent=2)
        print(f"✓ Knowledge base saved to {filepath}")

if __name__ == "__main__":
    kb = KnowledgeBase()
    print(f"Created knowledge base with {len(kb.documents)} documents:")
    for doc in kb.documents:
        print(f"  - {doc['id']}: {doc['title']} ({len(doc['content'])} chars)")
    kb.save_to_json()
```

Run it:
```bash
python knowledge_base.py
```

### Step 2: Build RAG Pipeline (15 minutes)

**File: `rag_pipeline.py`**
```python
#!/usr/bin/env python3
"""
Build a RAG pipeline for evaluation
"""

import os
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from knowledge_base import KnowledgeBase

load_dotenv()

class RAGPipeline:
    """End-to-end RAG system"""

    def __init__(self, model_name: str = "gpt-4", chunk_size: int = 500, top_k: int = 3):
        """
        Initialize RAG pipeline

        Args:
            model_name: LLM to use for generation
            chunk_size: Size of text chunks for retrieval
            top_k: Number of documents to retrieve
        """
        self.model_name = model_name
        self.chunk_size = chunk_size
        self.top_k = top_k

        # Initialize components
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None

    def build_from_documents(self, documents: List[Dict]):
        """Build RAG from documents"""
        print(f"Building RAG pipeline with {len(documents)} documents...")

        # Convert to LangChain Document objects
        docs = [
            Document(page_content=doc['content'], metadata={
                'id': doc['id'],
                'title': doc['title']
            })
            for doc in documents
        ]

        # Split documents into chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = splitter.split_documents(docs)
        print(f"  - Created {len(chunks)} chunks")

        # Create vector store
        print("  - Creating vector embeddings...")
        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        print("  - Vector store created")

        # Create retriever
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": self.top_k}
        )

        # Create QA chain with custom prompt
        prompt_template = """Use the following pieces of retrieved context to answer the question.
If the context doesn't contain relevant information, say so.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )

        print("✓ RAG pipeline ready")

    def query(self, question: str) -> Dict:
        """
        Query the RAG system

        Returns:
            Dict with 'answer', 'source_documents', and metadata
        """
        if not self.qa_chain:
            raise ValueError("Pipeline not built. Call build_from_documents() first.")

        result = self.qa_chain({"query": question})

        return {
            "question": question,
            "answer": result['result'],
            "source_documents": [
                {
                    "id": doc.metadata['id'],
                    "title": doc.metadata['title'],
                    "content": doc.page_content
                }
                for doc in result['source_documents']
            ]
        }

    def retrieve_context(self, question: str) -> Tuple[List[str], List[str]]:
        """
        Retrieve context without generation (for evaluation)

        Returns:
            (retrieved_texts, document_ids)
        """
        if not self.retriever:
            raise ValueError("Pipeline not built.")

        docs = self.retriever.get_relevant_documents(question)

        texts = [doc.page_content for doc in docs]
        ids = [doc.metadata.get('id', 'unknown') for doc in docs]

        return texts, ids

if __name__ == "__main__":
    from knowledge_base import KnowledgeBase

    # Load knowledge base
    kb = KnowledgeBase()

    # Build pipeline
    pipeline = RAGPipeline(model_name="gpt-4", chunk_size=500, top_k=3)
    pipeline.build_from_documents(kb.get_all_documents())

    # Test queries
    test_questions = [
        "What is machine learning?",
        "Explain RAG systems",
        "How does transfer learning work?"
    ]

    print("\n" + "="*70)
    print("Testing RAG Pipeline")
    print("="*70)

    for question in test_questions:
        print(f"\nQuestion: {question}")
        result = pipeline.query(question)
        print(f"Answer: {result['answer'][:200]}...")
        print(f"Sources: {[doc['id'] for doc in result['source_documents']]}")
```

Run it:
```bash
python rag_pipeline.py
```

### Step 3: Create Evaluation Dataset (10 minutes)

**File: `eval_dataset.py`**
```python
#!/usr/bin/env python3
"""
Create evaluation dataset for RAG assessment
"""

import json
from typing import List, Dict

# Questions with ground truth answers
EVALUATION_DATASET = [
    {
        "id": "q_001",
        "question": "What are the three main types of machine learning?",
        "ground_truth": "The three main types of machine learning are supervised learning, unsupervised learning, and reinforcement learning.",
        "expected_sources": ["doc_001"]
    },
    {
        "id": "q_002",
        "question": "What is the difference between supervised and unsupervised learning?",
        "ground_truth": "Supervised learning uses labeled data to learn to map inputs to outputs, while unsupervised learning finds patterns in unlabeled data without predefined outputs.",
        "expected_sources": ["doc_001"]
    },
    {
        "id": "q_003",
        "question": "Name some types of neural networks and their applications.",
        "ground_truth": "CNNs excel at image recognition using convolutional layers. RNNs are designed for sequential data like time series or text. Transformers revolutionized NLP using attention mechanisms.",
        "expected_sources": ["doc_002"]
    },
    {
        "id": "q_004",
        "question": "What is the main advantage of RAG over using language models alone?",
        "ground_truth": "RAG reduces hallucinations by grounding responses in retrieved facts, enables knowledge updates without retraining, and improves transparency by showing source documents.",
        "expected_sources": ["doc_004"]
    },
    {
        "id": "q_005",
        "question": "Describe the three steps of the RAG process.",
        "ground_truth": "The three steps are: retrieval (finding relevant documents), reading (extracting relevant passages), and generation (the language model generating an answer using retrieved context).",
        "expected_sources": ["doc_004"]
    },
    {
        "id": "q_006",
        "question": "What are key NLP tasks?",
        "ground_truth": "Key NLP tasks include text classification, sentiment analysis, named entity recognition, and machine translation.",
        "expected_sources": ["doc_003"]
    },
    {
        "id": "q_007",
        "question": "What makes LLMs different from traditional language models?",
        "ground_truth": "LLMs like GPT-4 and Claude are transformer-based models trained on billions of tokens, demonstrating emergent abilities in reasoning, coding, and creative tasks.",
        "expected_sources": ["doc_003"]
    },
    {
        "id": "q_008",
        "question": "What does fine-tuning accomplish?",
        "ground_truth": "Fine-tuning adapts pre-trained models to specific tasks with labeled data by updating some or all model parameters, enabling knowledge transfer from general to task-specific domains.",
        "expected_sources": ["doc_007"]
    },
    {
        "id": "q_009",
        "question": "What are some major NLP benchmarks?",
        "ground_truth": "GLUE evaluates general language understanding, SQuAD measures reading comprehension on question answering, and MMLU tests knowledge across 57 domains.",
        "expected_sources": ["doc_008"]
    },
    {
        "id": "q_010",
        "question": "What is a knowledge graph and what are its applications?",
        "ground_truth": "A knowledge graph is a structured representation where entities are nodes and relationships are edges. Applications include search engines, recommendation systems, and question answering.",
        "expected_sources": ["doc_006"]
    }
]

def save_dataset(filepath: str = "evaluation_dataset.json"):
    """Save evaluation dataset"""
    with open(filepath, 'w') as f:
        json.dump(EVALUATION_DATASET, f, indent=2)
    print(f"✓ Evaluation dataset saved to {filepath} ({len(EVALUATION_DATASET)} QA pairs)")

def load_dataset(filepath: str = "evaluation_dataset.json") -> List[Dict]:
    """Load evaluation dataset"""
    with open(filepath) as f:
        return json.load(f)

if __name__ == "__main__":
    save_dataset()
```

Run it:
```bash
python eval_dataset.py
```

### Step 4: Run Ragas Evaluation (30 minutes)

**File: `ragas_evaluation.py`**
```python
#!/usr/bin/env python3
"""
Run Ragas evaluation on RAG outputs
"""

import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    context_relevancy,
    answer_relevancy,
    context_precision,
    context_recall
)
from datasets import Dataset
from rag_pipeline import RAGPipeline
from knowledge_base import KnowledgeBase
from eval_dataset import load_dataset

load_dotenv()

class RAGEvaluator:
    """Evaluate RAG system using Ragas"""

    def __init__(self, rag_pipeline: RAGPipeline):
        self.pipeline = rag_pipeline

    def generate_rag_outputs(self, questions: List[Dict]) -> List[Dict]:
        """
        Generate RAG outputs for evaluation

        Args:
            questions: List of question dicts with 'question' key

        Returns:
            List of outputs with question, answer, retrieved context
        """
        outputs = []

        for i, q in enumerate(questions):
            print(f"Generating output {i+1}/{len(questions)}...")

            # Get RAG response
            rag_result = self.pipeline.query(q['question'])

            # Extract context
            contexts = [doc['content'] for doc in rag_result['source_documents']]

            outputs.append({
                "question": q['question'],
                "answer": rag_result['answer'],
                "contexts": contexts,
                "ground_truth": q.get('ground_truth', '')
            })

        return outputs

    def evaluate_outputs(self, outputs: List[Dict]) -> Dict:
        """
        Run Ragas metrics on outputs

        Args:
            outputs: RAG outputs

        Returns:
            Dictionary with metric scores
        """
        print("\nRunning Ragas evaluation...")

        # Convert to Hugging Face Dataset format
        dataset_dict = {
            "question": [o['question'] for o in outputs],
            "answer": [o['answer'] for o in outputs],
            "contexts": [o['contexts'] for o in outputs],
            "ground_truth": [o.get('ground_truth', '') for o in outputs]
        }

        dataset = Dataset.from_dict(dataset_dict)

        # Run evaluation with selected metrics
        print("Computing metrics...")
        results = evaluate(
            dataset,
            metrics=[
                faithfulness,
                context_relevancy,
                answer_relevancy,
                context_precision,
                context_recall
            ]
        )

        return results

    def analyze_results(self, results: Dict, outputs: List[Dict]) -> Dict:
        """
        Analyze evaluation results in detail
        """
        analysis = {
            "overall_metrics": {},
            "per_question_analysis": [],
            "failure_modes": []
        }

        # Overall metrics
        for metric_name in results.features:
            if metric_name not in ['question', 'answer']:
                scores = results[metric_name]
                analysis["overall_metrics"][metric_name] = {
                    "mean": sum(scores) / len(scores),
                    "min": min(scores),
                    "max": max(scores),
                    "std": (sum((x - sum(scores)/len(scores))**2 for x in scores) / len(scores)) ** 0.5
                }

        # Per-question analysis
        for i, output in enumerate(outputs):
            question_analysis = {
                "question_id": i,
                "question": output['question'],
                "answer_length": len(output['answer']),
                "num_contexts": len(output['contexts']),
                "metrics": {}
            }

            # Get metrics for this question
            for metric_name in results.features:
                if metric_name not in ['question', 'answer']:
                    question_analysis["metrics"][metric_name] = results[metric_name][i]

            analysis["per_question_analysis"].append(question_analysis)

            # Identify potential failures
            if results['faithfulness'][i] < 0.5:
                analysis["failure_modes"].append({
                    "type": "low_faithfulness",
                    "question": output['question'],
                    "score": results['faithfulness'][i]
                })

            if results['context_relevancy'][i] < 0.5:
                analysis["failure_modes"].append({
                    "type": "poor_retrieval",
                    "question": output['question'],
                    "score": results['context_relevancy'][i]
                })

        return analysis

def print_evaluation_report(analysis: Dict):
    """Pretty-print evaluation results"""
    print("\n" + "="*70)
    print("RAG EVALUATION REPORT")
    print("="*70)

    print("\nOVERALL METRICS:")
    print("-" * 70)
    for metric_name, stats in analysis["overall_metrics"].items():
        print(f"\n{metric_name.upper()}")
        print(f"  Mean: {stats['mean']:.3f}")
        print(f"  Min:  {stats['min']:.3f}")
        print(f"  Max:  {stats['max']:.3f}")
        print(f"  Std:  {stats['std']:.3f}")

    print("\n\nPER-QUESTION BREAKDOWN:")
    print("-" * 70)
    for qa in analysis["per_question_analysis"]:
        print(f"\nQ{qa['question_id']+1}: {qa['question'][:60]}...")
        print(f"  Answer length: {qa['answer_length']} chars")
        print(f"  Retrieved contexts: {qa['num_contexts']}")
        for metric, score in qa['metrics'].items():
            status = "✓" if score > 0.7 else "~" if score > 0.5 else "✗"
            print(f"  {status} {metric}: {score:.3f}")

    print("\n\nFAILURE ANALYSIS:")
    print("-" * 70)
    if analysis["failure_modes"]:
        for failure in analysis["failure_modes"][:5]:
            print(f"\n{failure['type'].upper()}")
            print(f"  Question: {failure['question'][:60]}...")
            print(f"  Score: {failure['score']:.3f}")
    else:
        print("No significant failures detected ✓")

if __name__ == "__main__":
    from rag_pipeline import RAGPipeline
    from knowledge_base import KnowledgeBase

    # Load knowledge base and build RAG
    print("Loading knowledge base...")
    kb = KnowledgeBase()

    print("Building RAG pipeline...")
    pipeline = RAGPipeline(model_name="gpt-4")
    pipeline.build_from_documents(kb.get_all_documents())

    # Load evaluation dataset
    questions = load_dataset()

    # Generate outputs
    evaluator = RAGEvaluator(pipeline)
    outputs = evaluator.generate_rag_outputs(questions)

    # Evaluate
    results = evaluator.evaluate_outputs(outputs)

    # Analyze
    analysis = evaluator.analyze_results(results, outputs)

    # Print report
    print_evaluation_report(analysis)

    # Save results
    with open("ragas_results.json", "w") as f:
        json.dump({
            "metrics": analysis,
            "outputs": outputs
        }, f, indent=2)
    print("\n✓ Results saved to ragas_results.json")
```

Run the full evaluation:
```bash
python ragas_evaluation.py
```

### Step 5: Visualization and Analysis (10 minutes)

**File: `visualize_results.py`**
```python
#!/usr/bin/env python3
"""
Visualize RAG evaluation results
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def load_results(filepath: str = "ragas_results.json") -> dict:
    """Load evaluation results"""
    with open(filepath) as f:
        return json.load(f)

def plot_metric_distributions(analysis: dict):
    """Plot distributions of metrics"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('RAG Evaluation Metrics Distribution', fontsize=16, fontweight='bold')

    metrics = list(analysis["overall_metrics"].keys())

    for idx, metric in enumerate(metrics):
        ax = axes[idx // 3, idx % 3]

        # Get per-question scores
        scores = [qa["metrics"][metric] for qa in analysis["per_question_analysis"]]

        # Plot
        ax.hist(scores, bins=5, color='steelblue', edgecolor='black', alpha=0.7)
        ax.axvline(np.mean(scores), color='red', linestyle='--', linewidth=2, label=f'Mean: {np.mean(scores):.2f}')
        ax.set_xlabel('Score')
        ax.set_ylabel('Frequency')
        ax.set_title(metric.replace('_', ' ').title())
        ax.set_ylim([0, max(scores.count(s) for s in set(scores)) + 1])
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

    # Remove empty subplot
    fig.delaxes(axes[1, 2])

    plt.tight_layout()
    plt.savefig('metric_distributions.png', dpi=300, bbox_inches='tight')
    print("✓ Saved visualization to metric_distributions.png")
    plt.close()

def plot_question_heatmap(analysis: dict):
    """Plot per-question metric scores as heatmap"""
    metrics_list = list(analysis["overall_metrics"].keys())
    num_questions = len(analysis["per_question_analysis"])

    # Build matrix
    scores_matrix = []
    for qa in analysis["per_question_analysis"]:
        scores_matrix.append([qa["metrics"][m] for m in metrics_list])

    scores_matrix = np.array(scores_matrix)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(scores_matrix, annot=True, fmt='.2f', cmap='RdYlGn', vmin=0, vmax=1,
                xticklabels=[m.replace('_', ' ').title() for m in metrics_list],
                yticklabels=[f"Q{i+1}" for i in range(num_questions)],
                ax=ax, cbar_kws={'label': 'Score'})

    ax.set_title('Per-Question Metric Scores Heatmap', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('question_heatmap.png', dpi=300, bbox_inches='tight')
    print("✓ Saved heatmap to question_heatmap.png")
    plt.close()

def create_summary_table(analysis: dict):
    """Create summary table"""
    print("\n" + "="*80)
    print("METRIC SUMMARY TABLE")
    print("="*80)

    print(f"\n{'Metric':<25} {'Mean':>10} {'Min':>10} {'Max':>10} {'Std':>10}")
    print("-" * 80)

    for metric, stats in analysis["overall_metrics"].items():
        print(f"{metric:<25} {stats['mean']:>10.3f} {stats['min']:>10.3f} {stats['max']:>10.3f} {stats['std']:>10.3f}")

if __name__ == "__main__":
    results = load_results()
    analysis = results["metrics"]

    plot_metric_distributions(analysis)
    plot_question_heatmap(analysis)
    create_summary_table(analysis)

    print("\n✓ Visualization complete")
```

Run it:
```bash
python visualize_results.py
```

### Step 6: Identify Optimization Opportunities (10 minutes)

**File: `optimization_recommendations.py`**
```python
#!/usr/bin/env python3
"""
Analyze evaluation results and recommend optimizations
"""

import json

def analyze_failure_modes(analysis: dict) -> dict:
    """Identify and categorize failure modes"""
    recommendations = {
        "retrieval_issues": [],
        "generation_issues": [],
        "ranking_issues": []
    }

    for qa in analysis["per_question_analysis"]:
        # Low context relevancy -> retrieval issue
        if qa["metrics"].get("context_relevancy", 1) < 0.6:
            recommendations["retrieval_issues"].append({
                "question": qa["question"],
                "score": qa["metrics"]["context_relevancy"],
                "fix": "Improve retrieval: better embeddings, expand knowledge base, tune retrieval parameters"
            })

        # Low faithfulness -> generation issue
        if qa["metrics"].get("faithfulness", 1) < 0.6:
            recommendations["generation_issues"].append({
                "question": qa["question"],
                "score": qa["metrics"]["faithfulness"],
                "fix": "Improve generation: better prompting, stronger model, add fact-checking step"
            })

    return recommendations

def generate_report(analysis: dict, recommendations: dict):
    """Generate optimization report"""
    print("\n" + "="*80)
    print("OPTIMIZATION RECOMMENDATIONS")
    print("="*80)

    overall = analysis["overall_metrics"]

    # Identify weak areas
    weak_metrics = {m: s for m, s in overall.items() if s["mean"] < 0.7}

    if weak_metrics:
        print("\nWEAK AREAS (need improvement):")
        for metric, stats in weak_metrics.items():
            print(f"\n  {metric.upper()}: {stats['mean']:.3f}")
            if "retrieval" in metric:
                print("    → Optimize document retrieval")
                print("    → Try different embedding models")
                print("    → Adjust chunk size and overlap")
                print("    → Expand or better structure knowledge base")
            elif "faithfulness" in metric:
                print("    → Improve answer generation")
                print("    → Use stronger model")
                print("    → Add explicit fact-checking")
                print("    → Better prompt engineering")
            elif "answer" in metric:
                print("    → Improve answer relevancy")
                print("    → Better context selection")
                print("    → Refine prompt to emphasize question relevance")

    # Specific failures
    if recommendations["retrieval_issues"]:
        print(f"\nRETRIEVAL FAILURES ({len(recommendations['retrieval_issues'])}):")
        for issue in recommendations["retrieval_issues"][:3]:
            print(f"  • Q: {issue['question'][:50]}...")
            print(f"    Fix: {issue['fix']}")

    if recommendations["generation_issues"]:
        print(f"\nGENERATION FAILURES ({len(recommendations['generation_issues'])}):")
        for issue in recommendations["generation_issues"][:3]:
            print(f"  • Q: {issue['question'][:50]}...")
            print(f"    Fix: {issue['fix']}")

    # Quick wins
    print("\nQUICK WINS:")
    print("  1. Experiment with top-k retrieval (current: 3)")
    print("  2. Try different chunk sizes (current: 500)")
    print("  3. Add query expansion to retrieval")
    print("  4. Use re-ranking to improve retrieved context quality")

if __name__ == "__main__":
    with open("ragas_results.json") as f:
        results = json.load(f)

    analysis = results["metrics"]
    recommendations = analyze_failure_modes(analysis)
    generate_report(analysis, recommendations)
```

Run it:
```bash
python optimization_recommendations.py
```

## Expected Output

### Console Output:
```
Loading knowledge base...
Created knowledge base with 8 documents

Building RAG pipeline...
Building RAG pipeline with 8 documents...
  - Created 32 chunks
  - Creating vector embeddings...
  - Vector store created
✓ RAG pipeline ready

Generating output 1/10...
Generating output 2/10...
...

Running Ragas evaluation...
Computing metrics...

======================================================================
RAG EVALUATION REPORT
======================================================================

OVERALL METRICS:
------

FAITHFULNESS
  Mean: 0.782
  Min:  0.450
  Max:  1.000
  Std:  0.178

CONTEXT_RELEVANCY
  Mean: 0.856
  Min:  0.600
  Max:  1.000
  Std:  0.142

ANSWER_RELEVANCY
  Mean: 0.841
  Min:  0.680
  Max:  0.980
  Std:  0.103

CONTEXT_PRECISION
  Mean: 0.743
  Min:  0.400
  Max:  1.000
  Std:  0.215

CONTEXT_RECALL
  Mean: 0.625
  Min:  0.200
  Max:  1.000
  Std:  0.283

...

✓ Results saved to ragas_results.json
```

## Troubleshooting

### Issue: "API rate limit exceeded"
**Solution:**
```python
# Add delays between queries
import time
time.sleep(2)  # 2-second delay between API calls
```

### Issue: "Low faithfulness scores (< 0.6)"
**Causes:**
- Generated answer doesn't match retrieved context
- Model hallucinating facts

**Solutions:**
1. Add explicit instruction to "only use context"
2. Use stronger model (GPT-4 vs GPT-3.5)
3. Implement fact-checking step
4. Improve prompt template

### Issue: "Low context relevancy scores"
**Causes:**
- Retrieved documents not relevant to question
- Embedding model not suitable

**Solutions:**
1. Try different embedding model
2. Adjust chunk size (larger or smaller)
3. Add query expansion
4. Use re-ranking

## Extension Challenges

### Challenge 1: Add Custom Faithfulness Metric
**Difficulty:** 15 minutes

```python
from ragas.metrics import Metric

class CustomFaithfulness(Metric):
    """Custom faithfulness using LLM evaluation"""

    def _score(self, row, **kwargs):
        # Implement custom scoring logic
        context = " ".join(row.contexts)
        answer = row.answer

        prompt = f"""Is the following answer faithful to the context?
Context: {context}
Answer: {answer}

Response: """

        # Call LLM and parse response
        score = llm(prompt)
        return score

    @property
    def name(self):
        return "custom_faithfulness"
```

### Challenge 2: Test Different Chunking Strategies
**Difficulty:** 20 minutes

```python
chunk_configs = [
    {"size": 250, "overlap": 50},
    {"size": 500, "overlap": 100},
    {"size": 1000, "overlap": 200},
]

results = {}
for config in chunk_configs:
    pipeline = RAGPipeline(chunk_size=config['size'])
    # ... build and evaluate ...
    results[str(config)] = metrics

# Compare results to find optimal configuration
```

### Challenge 3: Implement Re-ranking
**Difficulty:** 20 minutes

```python
from langchain_community.document_compressors import CohereRerank
from langchain.retrievers import ContextualCompressionRetriever

# Add re-ranking to retriever
compressor = CohereRerank(model="rerank-english-v2.0")
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=retriever
)

# Use in pipeline
pipeline.retriever = compression_retriever
```

## Lab Completion Checklist

- [ ] Created knowledge base with 8+ documents
- [ ] Built working RAG pipeline with LangChain
- [ ] Created evaluation dataset with 10+ Q&A pairs
- [ ] Generated RAG outputs for all questions
- [ ] Ran Ragas metrics (faithfulness, context relevancy, answer relevancy, etc.)
- [ ] Analyzed per-question results
- [ ] Created visualizations (distribution plots, heatmap)
- [ ] Identified failure modes and optimization opportunities
- [ ] Generated optimization recommendations
- [ ] Completed at least one extension challenge

## Summary

In this lab, you:
1. Built an end-to-end RAG system with LangChain
2. Created a comprehensive evaluation dataset
3. Ran Ragas metrics to assess RAG quality
4. Analyzed results by component (retrieval vs generation)
5. Identified specific failure modes
6. Generated actionable optimization recommendations

Key findings:
- Ragas metrics reveal component-wise issues (retrieval vs generation)
- Faithfulness measures answer grounding in context
- Context relevancy measures retrieval quality
- Answer relevancy measures response appropriateness
- Combining metrics enables targeted optimization

**Time Spent:** Approximately 75 minutes including all evaluation and analysis
