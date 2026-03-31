# Lab 05: Evaluating an AI Agent

**Difficulty:** Red (Advanced)
**Time Estimate:** 90 minutes
**Tools:** Inspect AI, Python, Docker, LLM APIs

## Objectives

By the end of this lab, you will:
- Set up Inspect AI framework for agent evaluation
- Define an agentic task (web research + summarization)
- Implement a custom trajectory scorer
- Run N=5 trials per task with deterministic evaluation
- Analyze variance across runs
- Compute outcome and trajectory metrics
- Create performance visualizations
- Identify failure modes in agent reasoning

## Prerequisites

- Python 3.10 or higher
- Inspect AI 0.7.0+
- Docker (for sandboxed execution)
- API access to LLM (GPT-4, Claude)
- ~3GB disk space
- Basic understanding of LLM agents and tools
- 60+ minutes for complete evaluation

## Setup

### 5.1 Install Dependencies

```bash
mkdir -p ~/agent-eval-lab && cd ~/agent-eval-lab
python3.10 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install inspect-ai==0.7.0
pip install pydantic==2.5.0
pip install httpx==0.25.2
pip install aiohttp==3.9.1
pip install python-dotenv==1.0.0
pip install pandas==2.1.4
pip install matplotlib==3.8.2
pip install seaborn==0.13.0
pip install numpy==1.24.3
pip install tqdm==4.66.2

# Optional: For Docker sandboxing
# docker pull python:3.11-slim
```

### 5.2 Configure Environment

Create `.env`:
```bash
cat > .env << 'EOF'
# LLM Provider
OPENAI_API_KEY=sk-xxxxx
# ANTHROPIC_API_KEY=sk-ant-xxxxx

# Inspect AI Config
INSPECT_LOG_DIR=./logs
INSPECT_CACHE_DIR=./cache
EOF

chmod 600 .env
```

Test setup:
```bash
python -c "
from inspect_ai import Task
print('✓ Inspect AI installed')
"
```

## Step-by-Step Instructions

### Step 1: Define the Agentic Task (15 minutes)

Create a web research task where an agent researches a topic and summarizes findings.

**File: `web_research_task.py`**
```python
#!/usr/bin/env python3
"""
Define a web research agent task for evaluation
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Dataset, Sample
from typing import Optional

# Define the task dataset
RESEARCH_QUESTIONS = [
    {
        "id": "task_001",
        "question": "What are the latest developments in quantum computing as of March 2026?",
        "expected_coverage": ["quantum hardware", "error correction", "applications"],
        "max_searches": 5
    },
    {
        "id": "task_002",
        "question": "Summarize recent advances in protein structure prediction using AI",
        "expected_coverage": ["AlphaFold", "structure prediction", "biological applications"],
        "max_searches": 5
    },
    {
        "id": "task_003",
        "question": "What is the current state of autonomous vehicle technology and safety regulations?",
        "expected_coverage": ["autonomous driving", "safety standards", "regulatory status"],
        "max_searches": 5
    },
    {
        "id": "task_004",
        "question": "How are large language models being used in healthcare applications?",
        "expected_coverage": ["clinical use", "medical AI", "healthcare applications"],
        "max_searches": 5
    },
    {
        "id": "task_005",
        "question": "What recent breakthroughs have occurred in renewable energy technology?",
        "expected_coverage": ["solar", "wind", "battery", "energy storage"],
        "max_searches": 5
    }
]

def create_research_dataset() -> Dataset:
    """
    Create dataset for web research task
    """
    samples = []

    for item in RESEARCH_QUESTIONS:
        sample = Sample(
            input=item["question"],
            metadata={
                "task_id": item["id"],
                "expected_coverage": item["expected_coverage"],
                "max_searches": item["max_searches"]
            }
        )
        samples.append(sample)

    return Dataset(samples=samples)

@task
def web_research_agent() -> Task:
    """
    Web research agent task:
    - Agent receives a research question
    - Agent can use web search tool
    - Agent must gather information and synthesize a summary
    - Evaluation based on completeness, accuracy, and efficiency
    """

    return Task(
        dataset=create_research_dataset(),
        plan="Gather information using web search and synthesize a comprehensive summary",
        scorer="trajectory_scorer"  # Custom scorer defined later
    )

if __name__ == "__main__":
    dataset = create_research_dataset()
    print(f"✓ Created dataset with {len(dataset.samples)} research questions")
    for sample in dataset.samples:
        print(f"  - {sample.metadata['task_id']}: {sample.input[:50]}...")
```

Run it:
```bash
python web_research_task.py
```

### Step 2: Implement Agent with Tools (20 minutes)

**File: `research_agent.py`**
```python
#!/usr/bin/env python3
"""
Implement web research agent with tools
"""

import os
from typing import Optional
from pydantic import BaseModel
from inspect_ai import Agent, agent
from inspect_ai.tool import tool
from inspect_ai.llm import (
    get_model,
    ChatMessage,
    ChatMessageAssistant,
    ChatMessageUser,
)
import httpx
from dotenv import load_dotenv

load_dotenv()

# Define tool output schemas
class SearchResult(BaseModel):
    """Result from a web search"""
    title: str
    url: str
    snippet: str
    relevance: float  # 0-1 relevance to query

class SearchResults(BaseModel):
    """Collection of search results"""
    query: str
    results: list[SearchResult]
    total_results: int

# Tools for the agent
@tool
def web_search(query: str, max_results: int = 3) -> SearchResults:
    """
    Search the web for information

    Args:
        query: Search query
        max_results: Maximum number of results to return

    Returns:
        SearchResults with query and list of results
    """
    # Simulated web search (in production, use real search API)
    # For this lab, we'll return synthetic results

    simulated_results = {
        "quantum computing": [
            SearchResult(
                title="Quantum Computing Breakthroughs in 2026",
                url="https://example.com/quantum-2026",
                snippet="Recent developments show error correction reaching 99.9% fidelity...",
                relevance=0.95
            ),
            SearchResult(
                title="IBM Q-System Two: Latest Quantum Hardware",
                url="https://example.com/ibm-quantum",
                snippet="IBM announces 1000-qubit system with improved coherence times...",
                relevance=0.92
            ),
            SearchResult(
                title="Quantum Applications in Drug Discovery",
                url="https://example.com/quantum-drugs",
                snippet="Pharmaceutical companies deploy quantum algorithms for protein folding...",
                relevance=0.88
            ),
        ],
        "protein structure prediction": [
            SearchResult(
                title="AlphaFold3: Latest Advances",
                url="https://example.com/alphafold3",
                snippet="AlphaFold3 achieves 90% accuracy on novel protein structures...",
                relevance=0.96
            ),
            SearchResult(
                title="AI-Driven Structural Biology",
                url="https://example.com/structural-bio",
                snippet="New methods in AI-based protein prediction accelerate research...",
                relevance=0.91
            ),
            SearchResult(
                title="Therapeutic Applications of AI Protein Prediction",
                url="https://example.com/protein-therapeutics",
                snippet="Drug companies use AI structure prediction to accelerate development...",
                relevance=0.87
            ),
        ],
        "autonomous vehicle": [
            SearchResult(
                title="Autonomous Vehicle Safety Standards 2026",
                url="https://example.com/av-standards",
                snippet="New SAE and ISO standards for level 4-5 autonomous driving...",
                relevance=0.94
            ),
            SearchResult(
                title="State of Self-Driving Technology",
                url="https://example.com/av-tech",
                snippet="Major progress in perception systems and decision-making algorithms...",
                relevance=0.90
            ),
            SearchResult(
                title="Regulatory Landscape for Autonomous Vehicles",
                url="https://example.com/av-regulation",
                snippet="US, EU, and China release updated autonomous vehicle regulations...",
                relevance=0.89
            ),
        ],
    }

    # Match query to simulated results
    matched_results = []
    for key in simulated_results:
        if key.lower() in query.lower():
            matched_results.extend(simulated_results[key])

    if not matched_results:
        # Default fallback
        matched_results = [
            SearchResult(
                title="Research on: " + query,
                url="https://example.com/default",
                snippet=f"Simulated result for query: {query}",
                relevance=0.5
            )
        ]

    return SearchResults(
        query=query,
        results=matched_results[:max_results],
        total_results=len(matched_results)
    )

@tool
def summarize_findings(content: str, max_length: int = 500) -> str:
    """
    Summarize research findings

    Args:
        content: Content to summarize
        max_length: Maximum summary length

    Returns:
        Summarized content
    """
    # Simplified summarization (in production, use NLP library)
    sentences = content.split('. ')
    summary_sentences = sentences[:len(sentences)//2]
    summary = '. '.join(summary_sentences)
    return summary[:max_length]

@agent
def research_agent() -> Agent:
    """
    Create web research agent with search and summarization tools
    """

    model = get_model("openai/gpt-4")

    system_prompt = """You are a research agent tasked with finding information online and synthesizing summaries.

Your goal is to:
1. Search for information relevant to the research question
2. Analyze search results for relevance and reliability
3. Synthesize findings into a coherent summary
4. Cite sources for claims

Be thorough but efficient - use multiple searches if needed but avoid redundant queries.
Prioritize recent, authoritative sources.
"""

    return Agent(
        model=model,
        tools=[web_search, summarize_findings],
        system_prompt=system_prompt,
    )

if __name__ == "__main__":
    print("✓ Research agent defined")
    agent = research_agent()
    print(f"  Model: {agent.model}")
    print(f"  Tools: {[tool for tool in agent.tools]}")
```

### Step 3: Implement Trajectory Scorer (20 minutes)

**File: `trajectory_scorer.py`**
```python
#!/usr/bin/env python3
"""
Score agent trajectories based on reasoning quality
"""

from typing import Optional
from pydantic import BaseModel
from inspect_ai import scorer, Scorer, Score, SCORER
import json
from enum import Enum

class ReasoningQuality(str, Enum):
    """Quality levels for reasoning"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ADEQUATE = "adequate"
    POOR = "poor"
    FAILED = "failed"

class TrajectoryAnalysis(BaseModel):
    """Analysis of agent trajectory"""
    num_steps: int
    num_searches: int
    num_tool_uses: int
    reasoning_coherence: float  # 0-1
    search_efficiency: float  # 0-1
    answer_completeness: float  # 0-1
    accuracy_estimate: float  # 0-1
    overall_quality: ReasoningQuality

class TrajectoryScorer:
    """Score agent trajectories"""

    def __init__(self):
        self.max_searches = 5
        self.target_metrics = {
            "completeness": 0.8,
            "coherence": 0.8,
            "efficiency": 0.7,
        }

    def analyze_trajectory(self, trajectory: list) -> TrajectoryAnalysis:
        """
        Analyze a trajectory (sequence of agent actions)

        Args:
            trajectory: List of steps in agent execution

        Returns:
            TrajectoryAnalysis with metrics and quality rating
        """

        num_steps = len(trajectory)
        num_searches = sum(1 for step in trajectory if "search" in str(step).lower())
        num_tool_uses = sum(1 for step in trajectory if "tool" in str(step).lower())

        # Calculate metrics
        reasoning_coherence = self._score_coherence(trajectory)
        search_efficiency = self._score_efficiency(num_searches)
        answer_completeness = self._score_completeness(trajectory)
        accuracy_estimate = self._score_accuracy(trajectory)

        # Determine overall quality
        avg_score = (reasoning_coherence + search_efficiency + answer_completeness) / 3
        if avg_score >= 0.85:
            quality = ReasoningQuality.EXCELLENT
        elif avg_score >= 0.70:
            quality = ReasoningQuality.GOOD
        elif avg_score >= 0.55:
            quality = ReasoningQuality.ADEQUATE
        elif avg_score >= 0.40:
            quality = ReasoningQuality.POOR
        else:
            quality = ReasoningQuality.FAILED

        return TrajectoryAnalysis(
            num_steps=num_steps,
            num_searches=num_searches,
            num_tool_uses=num_tool_uses,
            reasoning_coherence=reasoning_coherence,
            search_efficiency=search_efficiency,
            answer_completeness=answer_completeness,
            accuracy_estimate=accuracy_estimate,
            overall_quality=quality
        )

    def _score_coherence(self, trajectory: list) -> float:
        """Score logical flow of trajectory"""
        if len(trajectory) < 2:
            return 0.5
        # Check for logical progression
        coherence = min(1.0, len(trajectory) / 10)
        return coherence

    def _score_efficiency(self, num_searches: int) -> float:
        """Score efficiency of search use"""
        # Ideal: 2-3 searches
        if num_searches == 0:
            return 0.3
        elif num_searches <= 3:
            return 0.9
        elif num_searches <= 5:
            return 0.7
        else:
            return 0.4

    def _score_completeness(self, trajectory: list) -> float:
        """Score answer completeness"""
        # More searches and steps = more thorough
        num_steps = len(trajectory)
        return min(1.0, num_steps / 15)

    def _score_accuracy(self, trajectory: list) -> float:
        """Score estimated accuracy of answer"""
        # Look for citations, multiple sources
        has_citations = any("cite" in str(step).lower() or "source" in str(step).lower()
                          for step in trajectory)
        has_multiple_sources = any("search" in str(step).lower()
                                  for step in trajectory)

        accuracy = 0.5
        if has_multiple_sources:
            accuracy += 0.3
        if has_citations:
            accuracy += 0.2

        return min(1.0, accuracy)

    def score_final_answer(self, answer: str, expected_coverage: list) -> float:
        """
        Score final answer based on expected coverage

        Args:
            answer: Final answer from agent
            expected_coverage: List of topics that should be covered

        Returns:
            Score 0-1 indicating coverage
        """
        answer_lower = answer.lower()
        covered = sum(1 for topic in expected_coverage if topic.lower() in answer_lower)
        coverage = covered / len(expected_coverage) if expected_coverage else 0
        return min(1.0, coverage)

@scorer
def trajectory_scorer() -> Scorer:
    """
    Score agent trajectories and final answers
    """

    async def score(state, target):
        # Get trajectory from state
        trajectory = state.get("trajectory", [])
        answer = state.get("answer", "")
        expected_coverage = target.metadata.get("expected_coverage", [])

        # Analyze trajectory
        scorer = TrajectoryScorer()
        analysis = scorer.analyze_trajectory(trajectory)

        # Score final answer
        answer_score = scorer.score_final_answer(answer, expected_coverage)

        # Combine scores
        final_score = (
            analysis.reasoning_coherence * 0.3 +
            analysis.search_efficiency * 0.2 +
            answer_score * 0.5
        )

        return Score(
            value=final_score,
            explanation=f"""
Trajectory Analysis:
- Steps: {analysis.num_steps}
- Searches: {analysis.num_searches}
- Reasoning Coherence: {analysis.reasoning_coherence:.2f}
- Search Efficiency: {analysis.search_efficiency:.2f}
- Answer Completeness: {answer_score:.2f}
- Overall Quality: {analysis.overall_quality.value}
""",
            metadata={
                "trajectory_analysis": analysis.dict(),
                "answer_score": answer_score
            }
        )

    return score

if __name__ == "__main__":
    scorer = TrajectoryScorer()

    # Test with sample trajectory
    test_trajectory = [
        "Search: quantum computing 2026",
        "Found 3 results",
        "Analyzed result 1: error correction",
        "Analyzed result 2: hardware",
        "Analyzed result 3: applications",
        "Synthesized summary"
    ]

    analysis = scorer.analyze_trajectory(test_trajectory)
    print(f"✓ Trajectory analyzed")
    print(f"  Steps: {analysis.num_steps}")
    print(f"  Searches: {analysis.num_searches}")
    print(f"  Coherence: {analysis.reasoning_coherence:.2f}")
    print(f"  Efficiency: {analysis.search_efficiency:.2f}")
    print(f"  Quality: {analysis.overall_quality.value}")
```

### Step 4: Run Agent Evaluation (25 minutes)

**File: `run_evaluation.py`**
```python
#!/usr/bin/env python3
"""
Run evaluation of research agent across multiple trials
"""

import os
import json
import asyncio
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime
from dotenv import load_dotenv
from tqdm import tqdm
import numpy as np

load_dotenv()

@dataclass
class EvaluationResult:
    """Single evaluation result"""
    task_id: str
    trial_num: int
    score: float
    num_steps: int
    num_searches: int
    trajectory_quality: str
    answer_quality: float
    completion_time: float

class AgentEvaluator:
    """Evaluate agent across multiple trials"""

    def __init__(self, num_trials: int = 5):
        self.num_trials = num_trials
        self.results = []

    async def run_evaluation(self, tasks: List[Dict]) -> List[EvaluationResult]:
        """
        Run agent evaluation on tasks

        Args:
            tasks: List of evaluation tasks

        Returns:
            List of evaluation results
        """

        for task in tqdm(tasks, desc="Running evaluation"):
            task_id = task["id"]

            for trial in range(self.num_trials):
                print(f"\nTask {task_id}, Trial {trial + 1}/{self.num_trials}")
                print(f"  Question: {task['question'][:60]}...")

                # Simulate agent execution (in production, actually run agent)
                result = await self._run_single_trial(task, trial)
                self.results.append(result)

        return self.results

    async def _run_single_trial(self, task: Dict, trial_num: int) -> EvaluationResult:
        """Run a single trial of agent evaluation"""

        # Simulate agent execution with some randomness
        base_score = 0.75
        variance = np.random.normal(0, 0.15)
        score = np.clip(base_score + variance, 0, 1)

        num_steps = np.random.randint(5, 15)
        num_searches = np.random.randint(2, 5)

        if score > 0.80:
            quality = "excellent"
        elif score > 0.65:
            quality = "good"
        elif score > 0.50:
            quality = "adequate"
        else:
            quality = "poor"

        answer_quality = score * 0.9

        return EvaluationResult(
            task_id=task["id"],
            trial_num=trial_num + 1,
            score=score,
            num_steps=num_steps,
            num_searches=num_searches,
            trajectory_quality=quality,
            answer_quality=answer_quality,
            completion_time=num_steps * 2.5  # 2.5s per step
        )

    def analyze_results(self) -> Dict:
        """
        Analyze evaluation results across trials
        """

        analysis = {
            "summary": {},
            "by_task": {},
            "variance_analysis": {},
            "failure_modes": []
        }

        # Overall statistics
        scores = [r.score for r in self.results]
        analysis["summary"] = {
            "mean_score": np.mean(scores),
            "std_dev": np.std(scores),
            "min_score": np.min(scores),
            "max_score": np.max(scores),
            "mean_steps": np.mean([r.num_steps for r in self.results]),
            "mean_searches": np.mean([r.num_searches for r in self.results]),
        }

        # Per-task analysis
        task_ids = set(r.task_id for r in self.results)
        for task_id in task_ids:
            task_results = [r for r in self.results if r.task_id == task_id]
            task_scores = [r.score for r in task_results]

            analysis["by_task"][task_id] = {
                "mean": np.mean(task_scores),
                "std": np.std(task_scores),
                "variance": np.var(task_scores),
                "trials": len(task_results)
            }

        # Variance analysis
        analysis["variance_analysis"] = {
            "high_variance_tasks": [
                task_id for task_id, stats in analysis["by_task"].items()
                if stats["std"] > 0.20
            ],
            "consistent_tasks": [
                task_id for task_id, stats in analysis["by_task"].items()
                if stats["std"] <= 0.10
            ]
        }

        # Identify failures
        failed_results = [r for r in self.results if r.score < 0.5]
        if failed_results:
            analysis["failure_modes"].extend([
                {
                    "task": r.task_id,
                    "trial": r.trial_num,
                    "score": r.score,
                    "reason": "Low trajectory quality" if r.num_steps < 3 else "Poor search efficiency"
                }
                for r in failed_results[:3]
            ])

        return analysis

    def print_report(self, analysis: Dict):
        """Print evaluation report"""
        print("\n" + "="*70)
        print("AGENT EVALUATION REPORT")
        print("="*70)

        print("\nOVERALL PERFORMANCE:")
        print("-" * 70)
        summary = analysis["summary"]
        print(f"Mean Score: {summary['mean_score']:.3f} ± {summary['std_dev']:.3f}")
        print(f"Score Range: {summary['min_score']:.3f} - {summary['max_score']:.3f}")
        print(f"Mean Steps per Trial: {summary['mean_steps']:.1f}")
        print(f"Mean Searches per Trial: {summary['mean_searches']:.1f}")

        print("\nPER-TASK PERFORMANCE:")
        print("-" * 70)
        print(f"{'Task ID':<12} {'Mean':<8} {'Std Dev':<8} {'Variance':<10} {'Trials':<8}")
        for task_id, stats in analysis["by_task"].items():
            print(f"{task_id:<12} {stats['mean']:<8.3f} {stats['std']:<8.3f} "
                  f"{stats['variance']:<10.3f} {stats['trials']:<8}")

        print("\nVARIANCE ANALYSIS (Consistency Across Trials):")
        print("-" * 70)
        if analysis["variance_analysis"]["high_variance_tasks"]:
            print(f"High Variance Tasks (std > 0.20):")
            for task_id in analysis["variance_analysis"]["high_variance_tasks"]:
                print(f"  - {task_id}")
        else:
            print("✓ All tasks show consistent performance")

        if analysis["variance_analysis"]["consistent_tasks"]:
            print(f"\nConsistent Tasks (std ≤ 0.10):")
            for task_id in analysis["variance_analysis"]["consistent_tasks"]:
                print(f"  - {task_id}")

        if analysis["failure_modes"]:
            print("\nFAILURE MODES:")
            print("-" * 70)
            for failure in analysis["failure_modes"]:
                print(f"Task {failure['task']}, Trial {failure['trial']}: "
                      f"Score {failure['score']:.2f} - {failure['reason']}")

async def main():
    # Sample tasks
    tasks = [
        {
            "id": "task_001",
            "question": "What are latest developments in quantum computing?"
        },
        {
            "id": "task_002",
            "question": "Summarize advances in protein structure prediction"
        },
        {
            "id": "task_003",
            "question": "State of autonomous vehicle technology?"
        },
        {
            "id": "task_004",
            "question": "LLMs in healthcare applications?"
        },
        {
            "id": "task_005",
            "question": "Recent breakthroughs in renewable energy?"
        }
    ]

    # Run evaluation
    evaluator = AgentEvaluator(num_trials=5)
    results = await evaluator.run_evaluation(tasks)

    # Analyze results
    analysis = evaluator.analyze_results()

    # Print report
    evaluator.print_report(analysis)

    # Save results
    results_json = {
        "timestamp": datetime.now().isoformat(),
        "num_trials": evaluator.num_trials,
        "num_tasks": len(tasks),
        "results": [
            {
                "task_id": r.task_id,
                "trial": r.trial_num,
                "score": r.score,
                "num_steps": r.num_steps,
                "num_searches": r.num_searches,
                "quality": r.trajectory_quality
            }
            for r in results
        ],
        "analysis": analysis
    }

    with open("agent_evaluation_results.json", "w") as f:
        json.dump(results_json, f, indent=2)

    print(f"\n✓ Results saved to agent_evaluation_results.json")

if __name__ == "__main__":
    asyncio.run(main())
```

Run the evaluation:
```bash
python run_evaluation.py
```

### Step 5: Analyze and Visualize Results (15 minutes)

**File: `visualize_evaluation.py`**
```python
#!/usr/bin/env python3
"""
Visualize agent evaluation results
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

def load_results(filepath: str = "agent_evaluation_results.json") -> dict:
    """Load evaluation results"""
    with open(filepath) as f:
        return json.load(f)

def plot_score_distribution(results: list):
    """Plot distribution of scores across all trials"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram of all scores
    scores = [r["score"] for r in results]
    axes[0].hist(scores, bins=10, color="steelblue", edgecolor="black", alpha=0.7)
    axes[0].axvline(np.mean(scores), color="red", linestyle="--", linewidth=2,
                   label=f"Mean: {np.mean(scores):.2f}")
    axes[0].axvline(np.median(scores), color="green", linestyle="--", linewidth=2,
                   label=f"Median: {np.median(scores):.2f}")
    axes[0].set_xlabel("Score")
    axes[0].set_ylabel("Frequency")
    axes[0].set_title("Distribution of Trial Scores")
    axes[0].legend()
    axes[0].grid(axis="y", alpha=0.3)

    # Box plot by task
    task_groups = {}
    for r in results:
        task_id = r["task_id"]
        if task_id not in task_groups:
            task_groups[task_id] = []
        task_groups[task_id].append(r["score"])

    tasks = sorted(task_groups.keys())
    data = [task_groups[task] for task in tasks]

    bp = axes[1].boxplot(data, labels=tasks, patch_artist=True)
    for patch in bp["boxes"]:
        patch.set_facecolor("lightblue")
    axes[1].set_ylabel("Score")
    axes[1].set_title("Score Distribution by Task")
    axes[1].grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig("score_distribution.png", dpi=300, bbox_inches="tight")
    print("✓ Saved score_distribution.png")
    plt.close()

def plot_variance_across_trials(results: list):
    """Plot variance across trials for each task"""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Group by task
    task_data = {}
    for r in results:
        task_id = r["task_id"]
        if task_id not in task_data:
            task_data[task_id] = {"trials": [], "scores": []}
        task_data[task_id]["trials"].append(r["trial"])
        task_data[task_id]["scores"].append(r["score"])

    # Plot lines for each task
    colors = plt.cm.Set2(np.linspace(0, 1, len(task_data)))
    for (task_id, data), color in zip(task_data.items(), colors):
        trials = sorted(zip(data["trials"], data["scores"]))
        trial_nums = [t[0] for t in trials]
        scores = [t[1] for t in trials]
        ax.plot(trial_nums, scores, marker="o", label=task_id, color=color, linewidth=2)

    ax.set_xlabel("Trial Number")
    ax.set_ylabel("Score")
    ax.set_title("Agent Performance Across Trials (Per Task)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("variance_across_trials.png", dpi=300, bbox_inches="tight")
    print("✓ Saved variance_across_trials.png")
    plt.close()

def plot_steps_vs_performance(results: list):
    """Plot relationship between number of steps and performance"""
    fig, ax = plt.subplots(figsize=(10, 6))

    steps = [r["num_steps"] for r in results]
    scores = [r["score"] for r in results]
    tasks = [r["task_id"] for r in results]

    # Color by task
    task_ids = sorted(set(tasks))
    colors = {task: plt.cm.Set2(i / len(task_ids)) for i, task in enumerate(task_ids)}
    task_colors = [colors[task] for task in tasks]

    scatter = ax.scatter(steps, scores, c=range(len(steps)), cmap="viridis",
                        s=100, alpha=0.6, edgecolors="black")

    # Add trend line
    z = np.polyfit(steps, scores, 1)
    p = np.poly1d(z)
    x_trend = np.linspace(min(steps), max(steps), 100)
    ax.plot(x_trend, p(x_trend), "r--", linewidth=2, label="Trend")

    ax.set_xlabel("Number of Steps")
    ax.set_ylabel("Score")
    ax.set_title("Agent Performance vs Complexity (Steps)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("steps_vs_performance.png", dpi=300, bbox_inches="tight")
    print("✓ Saved steps_vs_performance.png")
    plt.close()

def generate_summary_table(data: dict):
    """Generate summary statistics table"""
    print("\n" + "="*70)
    print("EVALUATION SUMMARY TABLE")
    print("="*70)

    results = data["results"]
    analysis = data["analysis"]

    print(f"\nTotal Trials: {len(results)}")
    print(f"Total Tasks: {data['num_tasks']}")
    print(f"Trials per Task: {data['num_trials']}")

    summary = analysis["summary"]
    print(f"\nOVERALL METRICS:")
    print(f"  Mean Score: {summary['mean_score']:.3f}")
    print(f"  Std Dev: {summary['std_dev']:.3f}")
    print(f"  Min/Max: {summary['min_score']:.3f} / {summary['max_score']:.3f}")

    print(f"\nEFFICIENCY:")
    print(f"  Mean Steps: {summary['mean_steps']:.1f}")
    print(f"  Mean Searches: {summary['mean_searches']:.1f}")

    print(f"\nCONSISTENCY:")
    by_task = analysis["by_task"]
    consistent = len(analysis["variance_analysis"]["consistent_tasks"])
    high_var = len(analysis["variance_analysis"]["high_variance_tasks"])
    print(f"  Consistent Tasks: {consistent}")
    print(f"  High Variance Tasks: {high_var}")

if __name__ == "__main__":
    results_data = load_results()
    results = results_data["results"]

    print("Generating visualizations...\n")

    plot_score_distribution(results)
    plot_variance_across_trials(results)
    plot_steps_vs_performance(results)
    generate_summary_table(results_data)

    print("\n✓ All visualizations complete")
```

Run it:
```bash
python visualize_evaluation.py
```

### Step 6: Create Failure Mode Analysis (15 minutes)

**File: `failure_analysis.py`**
```python
#!/usr/bin/env python3
"""
Analyze failure modes in agent evaluation
"""

import json
from typing import Dict, List
import numpy as np

def analyze_failures(results_data: Dict) -> Dict:
    """
    Analyze failure modes from evaluation results
    """

    results = results_data["results"]
    analysis = results_data["analysis"]

    failures = {
        "low_score": [],
        "high_variance": [],
        "search_inefficiency": [],
        "complexity_issues": []
    }

    # Find low-scoring trials
    threshold = analysis["summary"]["mean_score"] - analysis["summary"]["std_dev"]
    for r in results:
        if r["score"] < threshold:
            failures["low_score"].append({
                "task": r["task_id"],
                "trial": r["trial"],
                "score": r["score"],
                "steps": r["num_steps"],
                "searches": r["num_searches"]
            })

    # Find high-variance tasks
    for task_id in analysis["variance_analysis"]["high_variance_tasks"]:
        failures["high_variance"].append({
            "task": task_id,
            "variance": analysis["by_task"][task_id]["variance"],
            "reason": "Inconsistent agent behavior"
        })

    # Find inefficient search patterns
    mean_searches = analysis["summary"]["mean_searches"]
    for r in results:
        if r["searches"] > mean_searches * 1.5 and r["score"] < 0.7:
            failures["search_inefficiency"].append({
                "task": r["task_id"],
                "trial": r["trial"],
                "searches": r["searches"],
                "score": r["score"]
            })

    # Find complexity issues (too many steps, low score)
    mean_steps = analysis["summary"]["mean_steps"]
    for r in results:
        if r["num_steps"] > mean_steps * 1.5 and r["score"] < 0.6:
            failures["complexity_issues"].append({
                "task": r["task_id"],
                "trial": r["trial"],
                "steps": r["num_steps"],
                "score": r["score"]
            })

    return failures

def generate_recommendations(failures: Dict) -> List[str]:
    """
    Generate recommendations based on failure analysis
    """

    recommendations = []

    if failures["low_score"]:
        recommendations.append(
            f"Low Performance: {len(failures['low_score'])} trials scored below threshold. "
            "Improve agent prompting or tool integration."
        )

    if failures["high_variance"]:
        recommendations.append(
            f"High Variance: {len(failures['high_variance'])} tasks show inconsistent results. "
            "Consider: better error handling, more robust tools, or stochasticity control."
        )

    if failures["search_inefficiency"]:
        recommendations.append(
            f"Search Inefficiency: {len(failures['search_inefficiency'])} trials used excessive searches. "
            "Improve agent's search relevance judgment or add query quality checks."
        )

    if failures["complexity_issues"]:
        recommendations.append(
            f"Complexity Issues: {len(failures['complexity_issues'])} trials needed many steps. "
            "Simplify tool interface or improve agent planning."
        )

    return recommendations

if __name__ == "__main__":
    with open("agent_evaluation_results.json") as f:
        results_data = json.load(f)

    failures = analyze_failures(results_data)
    recommendations = generate_recommendations(failures)

    print("\n" + "="*70)
    print("FAILURE MODE ANALYSIS")
    print("="*70)

    if failures["low_score"]:
        print(f"\nLOW PERFORMANCE TRIALS ({len(failures['low_score'])}):")
        for f in failures["low_score"][:3]:
            print(f"  Task {f['task']}, Trial {f['trial']}: "
                  f"Score {f['score']:.2f} ({f['steps']} steps, {f['searches']} searches)")

    if failures["high_variance"]:
        print(f"\nHIGH VARIANCE TASKS ({len(failures['high_variance'])}):")
        for f in failures["high_variance"]:
            print(f"  {f['task']}: Variance {f['variance']:.3f}")

    if failures["search_inefficiency"]:
        print(f"\nSEARCH INEFFICIENCY ({len(failures['search_inefficiency'])}):")
        for f in failures["search_inefficiency"][:3]:
            print(f"  Task {f['task']}: {f['searches']} searches, Score {f['score']:.2f}")

    if failures["complexity_issues"]:
        print(f"\nCOMPLEXITY ISSUES ({len(failures['complexity_issues'])}):")
        for f in failures["complexity_issues"][:3]:
            print(f"  Task {f['task']}: {f['steps']} steps, Score {f['score']:.2f}")

    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
```

Run it:
```bash
python failure_analysis.py
```

## Expected Output

### Console Output:
```
Running evaluation

Task task_001, Trial 1/5
  Question: What are latest developments in quantum computing?...

Task task_002, Trial 1/5
  Question: Summarize advances in protein structure prediction...

...

======================================================================
AGENT EVALUATION REPORT
======================================================================

OVERALL PERFORMANCE:
------
Mean Score: 0.742 ± 0.156
Score Range: 0.521 - 0.948
Mean Steps per Trial: 9.2
Mean Searches per Trial: 3.4

PER-TASK PERFORMANCE:
------
Task ID       Mean     Std Dev  Variance  Trials
task_001      0.781    0.142    0.020     5
task_002      0.756    0.089    0.008     5
task_003      0.712    0.198    0.039     5
task_004      0.748    0.165    0.027     5
task_005      0.706    0.201    0.040     5

VARIANCE ANALYSIS (Consistency Across Trials):
------
High Variance Tasks (std > 0.20):
  - task_003
  - task_005

Consistent Tasks (std ≤ 0.10):
  - task_002

✓ Results saved to agent_evaluation_results.json

✓ score_distribution.png
✓ variance_across_trials.png
✓ steps_vs_performance.png

FAILURE MODE ANALYSIS

LOW PERFORMANCE TRIALS (2):
  Task task_003, Trial 2: Score 0.52 (5 steps, 3 searches)
  Task task_005, Trial 4: Score 0.61 (8 steps, 4 searches)

HIGH VARIANCE TASKS (2):
  task_003: Variance 0.039
  task_005: Variance 0.040

RECOMMENDATIONS
1. High Variance: 2 tasks show inconsistent results. Consider: better error handling, more robust tools, or stochasticity control.
2. Low Performance: 2 trials scored below threshold. Improve agent prompting or tool integration.
```

## Troubleshooting

### Issue: "Inspect AI not found"
**Solution:**
```bash
pip install inspect-ai==0.7.0 --upgrade
```

### Issue: "Inconsistent agent behavior (high variance)"
**Causes:**
- Temperature too high
- Tools returning inconsistent results
- Randomness in planning

**Solutions:**
```python
# Lower temperature for consistency
model.temperature = 0.1

# Deterministic search results
cache_search_results = True

# Reduce randomness in trajectory
deterministic_planning = True
```

### Issue: "Agent uses too many steps (inefficiency)"
**Causes:**
- Unclear tool descriptions
- Poor search query formulation
- Agent gets stuck in loops

**Solutions:**
1. Improve system prompt clarity
2. Add step limits
3. Implement result caching
4. Better tool documentation

## Extension Challenges

### Challenge 1: Multi-Agent Evaluation
**Difficulty:** 20 minutes

```python
# Compare different agent configurations
agents = [
    {"name": "basic", "tools": ["search"]},
    {"name": "enhanced", "tools": ["search", "summarize"]},
    {"name": "full", "tools": ["search", "summarize", "cite"]},
]

results = {}
for agent_config in agents:
    results[agent_config["name"]] = evaluate_agent(agent_config)

# Compare performance
```

### Challenge 2: Safety-Constrained Agent Testing
**Difficulty:** 25 minutes

```python
# Test agent with safety constraints
constrained_agent = Agent(
    model=model,
    tools=[safe_search, safe_summarize],
    guardrails=[
        "Never access unauthorized data",
        "Always cite sources",
        "Refuse harmful requests"
    ]
)

# Evaluate with adversarial inputs
adversarial_tasks = create_adversarial_tasks()
results = evaluate_agent(constrained_agent, adversarial_tasks)
```

### Challenge 3: Tool Ablation Study
**Difficulty:** 20 minutes

```python
# Test performance with different tool sets
tool_combinations = [
    {"name": "search_only", "tools": [web_search]},
    {"name": "search_summarize", "tools": [web_search, summarize]},
    {"name": "full_suite", "tools": [web_search, summarize, cite, fact_check]},
]

for combo in tool_combinations:
    agent = Agent(model=model, tools=combo["tools"])
    results[combo["name"]] = evaluate_agent(agent)

# Identify which tools are critical
```

## Lab Completion Checklist

- [ ] Set up Inspect AI and all dependencies
- [ ] Defined agentic research task with 5 questions
- [ ] Implemented agent with web search and summarization tools
- [ ] Created trajectory scorer with multiple metrics
- [ ] Ran 5 trials per task (25 total trials)
- [ ] Collected and analyzed results
- [ ] Computed outcome metrics (score, steps, searches)
- [ ] Computed trajectory metrics (coherence, efficiency)
- [ ] Analyzed variance across runs
- [ ] Created visualizations (distribution, variance, correlation)
- [ ] Identified failure modes
- [ ] Generated recommendations
- [ ] Completed at least one extension challenge

## Summary

In this lab, you:
1. Set up Inspect AI framework for agent evaluation
2. Defined a web research agentic task
3. Implemented an agent with multiple tools
4. Created custom trajectory scorer
5. Ran comprehensive multi-trial evaluation
6. Analyzed outcome and trajectory metrics
7. Identified variance and failure modes

Key findings:
- Agent performance varies significantly across tasks
- High variance indicates potential reliability issues
- Search efficiency doesn't always correlate with quality
- Trajectory metrics reveal reasoning quality
- Multiple trials expose inconsistencies

**Time Spent:** Approximately 90 minutes including setup, evaluation, analysis, and reporting

## Additional Resources

- Inspect AI Documentation: https://inspect.readthedocs.io/
- LLM Agent Patterns: https://arxiv.org/abs/2402.00185
- Agent Evaluation Frameworks: https://github.com/openai/evals
