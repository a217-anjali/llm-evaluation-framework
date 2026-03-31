# Lab 09: Cost-Quality-Latency Pareto Analysis

**Difficulty:** Yellow (Intermediate)
**Duration:** 75 minutes
**Tools:** Python, Plotly, pandas, numpy, scipy
**Prerequisites:** Lab 01-03, understanding of trade-offs and optimization

## Overview

This lab teaches cost-benefit analysis for model selection through Pareto frontier analysis. You will evaluate 5+ frontier and open-weight models on the same evaluation suite, measure quality (accuracy), cost (per token pricing), and latency (TTFT + total), compute the Pareto-optimal set of models, and create interactive visualizations to support decision-making.

## Learning Objectives

By the end of this lab, you will:

1. **Evaluate multiple models** on consistent benchmarks
2. **Measure quality, cost, and latency** for each model
3. **Compute Pareto-optimal frontier** for trade-off analysis
4. **Create interactive visualizations** of trade-offs
5. **Select optimal models** for different use cases
6. **Analyze cost-benefit** scenarios

## Part 1: Setup and Model Registry

Create the evaluation framework:

```python
# model_evaluation_setup.py
"""
Setup for multi-model cost-quality-latency evaluation.
Defines 5+ models and their pricing/performance profiles.
"""

import pandas as pd
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum
import numpy as np

class ModelType(Enum):
    FRONTIER = "frontier"  # Proprietary, latest models
    OPEN_WEIGHT = "open_weight"  # OSS models
    SMALLER = "smaller"  # Lightweight models

@dataclass
class ModelProfile:
    """Complete model profile with pricing and performance baseline."""

    name: str
    provider: str
    type: ModelType
    input_cost_per_1k: float  # USD per 1K input tokens
    output_cost_per_1k: float  # USD per 1K output tokens
    context_window: int  # Max tokens
    expected_accuracy: float  # 0.0-1.0 from benchmarks
    expected_ttft_ms: float  # Time to first token (ms)
    expected_total_latency_ms: float  # Total response time (ms)
    throughput_tokens_per_second: float
    availability: float  # Uptime SLA (0.0-1.0)

def create_model_registry() -> Dict[str, ModelProfile]:
    """Create registry of 5+ models for evaluation."""

    models = {
        "GPT-4o": ModelProfile(
            name="GPT-4o",
            provider="OpenAI",
            type=ModelType.FRONTIER,
            input_cost_per_1k=0.005,
            output_cost_per_1k=0.015,
            context_window=128000,
            expected_accuracy=0.89,
            expected_ttft_ms=350,
            expected_total_latency_ms=2500,
            throughput_tokens_per_second=15,
            availability=0.999
        ),
        "Claude-Sonnet-4.6": ModelProfile(
            name="Claude-Sonnet-4.6",
            provider="Anthropic",
            type=ModelType.FRONTIER,
            input_cost_per_1k=0.003,
            output_cost_per_1k=0.012,
            context_window=200000,
            expected_accuracy=0.91,
            expected_ttft_ms=400,
            expected_total_latency_ms=3000,
            throughput_tokens_per_second=12,
            availability=0.999
        ),
        "Gemini-3-Flash": ModelProfile(
            name="Gemini-3-Flash",
            provider="Google",
            type=ModelType.FRONTIER,
            input_cost_per_1k=0.0375,
            output_cost_per_1k=0.15,
            context_window=1000000,
            expected_accuracy=0.85,
            expected_ttft_ms=250,
            expected_total_latency_ms=1800,
            throughput_tokens_per_second=25,
            availability=0.999
        ),
        "Qwen-3.5-9B": ModelProfile(
            name="Qwen-3.5-9B",
            provider="Alibaba",
            type=ModelType.OPEN_WEIGHT,
            input_cost_per_1k=0.0002,  # Self-hosted estimate
            output_cost_per_1k=0.0003,
            context_window=32000,
            expected_accuracy=0.75,
            expected_ttft_ms=120,
            expected_total_latency_ms=1200,
            throughput_tokens_per_second=45,
            availability=0.95
        ),
        "Llama-4-Scout": ModelProfile(
            name="Llama-4-Scout",
            provider="Meta",
            type=ModelType.SMALLER,
            input_cost_per_1k=0.0001,  # Self-hosted estimate
            output_cost_per_1k=0.00015,
            context_window=8000,
            expected_accuracy=0.68,
            expected_ttft_ms=80,
            expected_total_latency_ms=800,
            throughput_tokens_per_second=60,
            availability=0.95
        )
    }

    return models

def create_evaluation_scenarios() -> Dict[str, Dict]:
    """Define typical usage scenarios for cost calculation."""

    return {
        "customer_support": {
            "name": "Customer Support Chat",
            "avg_input_tokens": 150,
            "avg_output_tokens": 200,
            "monthly_queries": 100000,
            "quality_criticality": "high",
            "latency_requirement_ms": 5000
        },
        "batch_processing": {
            "name": "Batch Document Analysis",
            "avg_input_tokens": 2000,
            "avg_output_tokens": 500,
            "monthly_queries": 10000,
            "quality_criticality": "high",
            "latency_requirement_ms": 60000
        },
        "real_time_classification": {
            "name": "Real-time Content Classification",
            "avg_input_tokens": 100,
            "avg_output_tokens": 50,
            "monthly_queries": 1000000,
            "quality_criticality": "medium",
            "latency_requirement_ms": 500
        },
        "summarization": {
            "name": "Long Document Summarization",
            "avg_input_tokens": 4000,
            "avg_output_tokens": 300,
            "monthly_queries": 5000,
            "quality_criticality": "high",
            "latency_requirement_ms": 30000
        }
    }

if __name__ == "__main__":
    models = create_model_registry()
    scenarios = create_evaluation_scenarios()

    print("MODEL REGISTRY")
    print("=" * 100)
    for name, profile in models.items():
        print(f"\n{name} ({profile.provider})")
        print(f"  Type: {profile.type.value}")
        print(f"  Cost: ${profile.input_cost_per_1k}/1K in, ${profile.output_cost_per_1k}/1K out")
        print(f"  Accuracy (benchmark): {profile.expected_accuracy:.1%}")
        print(f"  Latency: {profile.expected_ttft_ms}ms TTFT, {profile.expected_total_latency_ms}ms total")
        print(f"  Throughput: {profile.throughput_tokens_per_second} tokens/sec")

    print("\n\nEVALUATION SCENARIOS")
    print("=" * 100)
    for scenario_key, scenario in scenarios.items():
        print(f"\n{scenario['name']}")
        print(f"  Input: {scenario['avg_input_tokens']} tokens")
        print(f"  Output: {scenario['avg_output_tokens']} tokens")
        print(f"  Monthly Volume: {scenario['monthly_queries']:,}")
```

## Part 2: Run Multi-Model Evaluation

```python
# multi_model_evaluation.py
"""
Evaluate all models on same evaluation suite.
Measure quality, cost, and latency.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from model_evaluation_setup import ModelProfile, create_model_registry

class MultiModelEvaluator:
    """Evaluate multiple models on consistent metrics."""

    def __init__(self, models: Dict[str, ModelProfile]):
        self.models = models
        self.results = {}

    def evaluate_model_quality(self, model: ModelProfile, num_test_cases: int = 50) -> Dict:
        """
        Evaluate model quality on benchmark suite.

        Simulates evaluation results (in production, run actual evaluations).
        """

        # Simulate quality evaluation with some variance
        np.random.seed(hash(model.name) % 2**32)
        scores = np.random.normal(
            model.expected_accuracy * 100,
            5.0,  # Standard deviation
            num_test_cases
        )
        scores = np.clip(scores, 0, 100)

        return {
            'model': model.name,
            'accuracy_mean': np.mean(scores),
            'accuracy_std': np.std(scores),
            'accuracy_min': np.min(scores),
            'accuracy_max': np.max(scores),
            'accuracy_scores': scores
        }

    def measure_latency(self, model: ModelProfile, num_requests: int = 100) -> Dict:
        """
        Measure model latency (TTFT + total).

        Simulates latency measurements.
        """

        np.random.seed(hash(model.name + "latency") % 2**32)

        # Simulate TTFT (Time To First Token)
        ttft = np.random.normal(model.expected_ttft_ms, 50, num_requests)
        ttft = np.clip(ttft, model.expected_ttft_ms * 0.5, model.expected_ttft_ms * 1.5)

        # Simulate total latency
        total_latency = np.random.normal(model.expected_total_latency_ms, 300, num_requests)
        total_latency = np.clip(total_latency, model.expected_total_latency_ms * 0.7,
                               model.expected_total_latency_ms * 1.3)

        return {
            'model': model.name,
            'ttft_mean_ms': np.mean(ttft),
            'ttft_std_ms': np.std(ttft),
            'total_latency_mean_ms': np.mean(total_latency),
            'total_latency_std_ms': np.std(total_latency),
            'p95_latency_ms': np.percentile(total_latency, 95),
            'p99_latency_ms': np.percentile(total_latency, 99)
        }

    def calculate_cost(self, model: ModelProfile, scenario: Dict) -> Dict:
        """Calculate cost for a specific scenario."""

        input_cost = (scenario['avg_input_tokens'] / 1000 *
                     model.input_cost_per_1k)
        output_cost = (scenario['avg_output_tokens'] / 1000 *
                      model.output_cost_per_1k)

        cost_per_query = input_cost + output_cost
        monthly_cost = cost_per_query * scenario['monthly_queries']

        return {
            'model': model.name,
            'scenario': scenario['name'],
            'cost_per_query': cost_per_query,
            'monthly_cost': monthly_cost,
            'annual_cost': monthly_cost * 12
        }

    def evaluate_all_models(self, scenarios: Dict) -> pd.DataFrame:
        """Evaluate all models and return results dataframe."""

        all_results = []

        for model_name, model in self.models.items():
            print(f"Evaluating {model_name}...")

            # Quality evaluation
            quality = self.evaluate_model_quality(model)

            # Latency measurement
            latency = self.measure_latency(model)

            # Cost for each scenario
            for scenario_key, scenario in scenarios.items():
                cost = self.calculate_cost(model, scenario)

                all_results.append({
                    'model': model_name,
                    'provider': model.provider,
                    'type': model.type.value,
                    'accuracy': quality['accuracy_mean'],
                    'accuracy_std': quality['accuracy_std'],
                    'ttft_ms': latency['ttft_mean_ms'],
                    'latency_ms': latency['total_latency_mean_ms'],
                    'p95_latency_ms': latency['p95_latency_ms'],
                    'cost_per_query': cost['cost_per_query'],
                    'monthly_cost': cost['monthly_cost'],
                    'annual_cost': cost['annual_cost'],
                    'scenario': scenario['name']
                })

        df = pd.DataFrame(all_results)
        return df

if __name__ == "__main__":
    from model_evaluation_setup import create_model_registry, create_evaluation_scenarios

    models = create_model_registry()
    scenarios = create_evaluation_scenarios()

    evaluator = MultiModelEvaluator(models)
    results = evaluator.evaluate_all_models(scenarios)

    print("\nEVALUATION RESULTS")
    print("=" * 150)
    print(results.to_string(index=False))

    # Save results
    results.to_csv("model_evaluation_results.csv", index=False)
```

## Part 3: Compute Pareto Frontier

```python
# pareto_analysis.py
"""
Compute Pareto-optimal frontier for model selection.
Identifies non-dominated models for different objectives.
"""

import numpy as np
import pandas as pd
from typing import List, Tuple
from scipy.spatial.distance import cdist

class ParetoOptimizer:
    """Compute Pareto frontier and identify optimal solutions."""

    @staticmethod
    def is_dominated(point: np.ndarray, pareto_set: np.ndarray,
                    minimize: List[bool]) -> bool:
        """
        Check if a point is dominated by any point in pareto set.

        minimize: List of bool indicating which objectives to minimize.
                 True = minimize, False = maximize
        """

        for p in pareto_set:
            dominated = True
            for i, min_flag in enumerate(minimize):
                if min_flag:
                    # Minimize: p[i] should be <= point[i]
                    if p[i] > point[i]:
                        dominated = False
                        break
                else:
                    # Maximize: p[i] should be >= point[i]
                    if p[i] < point[i]:
                        dominated = False
                        break

            if dominated:
                return True

        return False

    @staticmethod
    def compute_pareto_frontier(points: np.ndarray, minimize: List[bool]) -> np.ndarray:
        """
        Compute Pareto frontier (non-dominated solutions).

        Args:
            points: (n_points, n_objectives) array
            minimize: List indicating minimize (True) or maximize (False) for each objective

        Returns:
            Boolean array indicating which points are on Pareto frontier
        """

        n_points = len(points)
        frontier_mask = np.ones(n_points, dtype=bool)

        for i in range(n_points):
            if not frontier_mask[i]:
                continue

            for j in range(n_points):
                if i == j or not frontier_mask[j]:
                    continue

                # Check if j dominates i
                dominated = True
                for k, min_flag in enumerate(minimize):
                    if min_flag:
                        if points[j, k] > points[i, k]:
                            dominated = False
                            break
                    else:
                        if points[j, k] < points[i, k]:
                            dominated = False
                            break

                if dominated:
                    frontier_mask[i] = False
                    break

        return frontier_mask

    @staticmethod
    def analyze_trade_offs(df: pd.DataFrame) -> Dict:
        """Analyze quality vs cost vs latency trade-offs."""

        # Filter to unique model evaluations (one per model per scenario)
        unique_models = df.groupby('model').first().reset_index()

        # Normalize scores to 0-1 range
        accuracy_norm = (unique_models['accuracy'] - unique_models['accuracy'].min()) / \
                       (unique_models['accuracy'].max() - unique_models['accuracy'].min())

        # Cost: lower is better (minimize)
        cost_norm = (unique_models['cost_per_query'] - unique_models['cost_per_query'].min()) / \
                   (unique_models['cost_per_query'].max() - unique_models['cost_per_query'].min())

        # Latency: lower is better (minimize)
        latency_norm = (unique_models['latency_ms'] - unique_models['latency_ms'].min()) / \
                      (unique_models['latency_ms'].max() - unique_models['latency_ms'].min())

        # Compute Pareto frontier
        objectives = np.column_stack([
            accuracy_norm,  # Maximize (negate for minimize)
            cost_norm,      # Minimize
            latency_norm    # Minimize
        ])

        # For Pareto: maximize accuracy, minimize cost, minimize latency
        minimize_flags = [False, True, True]

        pareto_mask = ParetoOptimizer.compute_pareto_frontier(objectives, minimize_flags)

        # Add results back to dataframe
        unique_models['on_frontier'] = pareto_mask
        unique_models['accuracy_norm'] = accuracy_norm.values
        unique_models['cost_norm'] = cost_norm.values
        unique_models['latency_norm'] = latency_norm.values

        return {
            'models': unique_models,
            'pareto_frontier': unique_models[pareto_mask],
            'dominated': unique_models[~pareto_mask]
        }

    @staticmethod
    def rank_by_efficiency(df: pd.DataFrame) -> pd.DataFrame:
        """
        Rank models by efficiency scores.

        Combined metric: accuracy / (cost + latency_weight)
        """

        # Normalize metrics
        accuracy_norm = df['accuracy'] / df['accuracy'].max()
        cost_norm = df['cost_per_query'] / df['cost_per_query'].max()
        latency_norm = df['latency_ms'] / df['latency_ms'].max()

        # Efficiency: high accuracy, low cost, low latency
        # Weighted: 60% accuracy, 30% cost, 10% latency
        efficiency = (0.6 * accuracy_norm) / (0.3 * cost_norm + 0.1 * latency_norm + 1e-6)

        df_ranked = df.copy()
        df_ranked['efficiency_score'] = efficiency
        df_ranked = df_ranked.sort_values('efficiency_score', ascending=False)
        df_ranked['rank'] = range(1, len(df_ranked) + 1)

        return df_ranked

if __name__ == "__main__":
    # Load evaluation results
    df = pd.read_csv("model_evaluation_results.csv")

    # Analyze trade-offs
    analysis = ParetoOptimizer.analyze_trade_offs(df)

    print("PARETO FRONTIER ANALYSIS")
    print("=" * 100)
    print("\nModels on Pareto Frontier:")
    print(analysis['pareto_frontier'][['model', 'accuracy', 'cost_per_query', 'latency_ms']].to_string(index=False))

    print("\n\nDominated Models:")
    print(analysis['dominated'][['model', 'accuracy', 'cost_per_query', 'latency_ms']].to_string(index=False))

    # Rank by efficiency
    ranked = ParetoOptimizer.rank_by_efficiency(df)
    print("\n\nRanked by Efficiency (Quality/Cost/Latency):")
    print(ranked[['rank', 'model', 'accuracy', 'cost_per_query', 'latency_ms', 'efficiency_score']].to_string(index=False))
```

## Part 4: Create Interactive Visualizations

```python
# pareto_visualizations.py
"""
Create publication-quality Pareto frontier visualizations.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict

class ParetoVisualizations:
    """Create interactive Pareto frontier visualizations."""

    @staticmethod
    def plot_2d_pareto(df: pd.DataFrame, x_metric: str, y_metric: str,
                       color_metric: str = 'model',
                       title: str = "Model Comparison") -> None:
        """
        Create 2D scatter plot with Pareto frontier.

        Args:
            x_metric: Column name for X axis
            y_metric: Column name for Y axis
            color_metric: Column for coloring points
        """

        # Determine if metrics should be maximized or minimized
        minimize_x = x_metric in ['cost_per_query', 'latency_ms']
        minimize_y = y_metric in ['cost_per_query', 'latency_ms']

        # Compute Pareto frontier
        from pareto_analysis import ParetoOptimizer

        points = df[[x_metric, y_metric]].values
        minimize = [minimize_x, minimize_y]
        pareto_mask = ParetoOptimizer.compute_pareto_frontier(points, minimize)

        df_plot = df.copy()
        df_plot['is_frontier'] = pareto_mask

        fig = px.scatter(df_plot, x=x_metric, y=y_metric, hover_name='model',
                        size='accuracy', color='is_frontier',
                        color_discrete_map={True: 'red', False: 'blue'},
                        title=title, labels={
                            'cost_per_query': 'Cost per Query ($)',
                            'accuracy': 'Accuracy (%)',
                            'latency_ms': 'Latency (ms)'
                        })

        # Add frontier line
        frontier_points = df_plot[pareto_mask].sort_values(x_metric)

        fig.add_trace(go.Scatter(
            x=frontier_points[x_metric],
            y=frontier_points[y_metric],
            mode='lines',
            name='Pareto Frontier',
            line=dict(color='red', dash='dash', width=2),
            hoverinfo='skip'
        ))

        fig.update_layout(height=600, template='plotly_white')
        fig.show()

    @staticmethod
    def plot_3d_pareto(df: pd.DataFrame) -> None:
        """Create 3D scatter plot: accuracy vs cost vs latency."""

        fig = go.Figure()

        # Normalize for color scale
        accuracy_norm = (df['accuracy'] - df['accuracy'].min()) / \
                       (df['accuracy'].max() - df['accuracy'].min())

        fig.add_trace(go.Scatter3d(
            x=df['cost_per_query'],
            y=df['latency_ms'],
            z=df['accuracy'],
            mode='markers+text',
            marker=dict(
                size=8,
                color=accuracy_norm,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Accuracy"),
                line=dict(width=2, color='white')
            ),
            text=df['model'],
            textposition='top center',
            hovertemplate='<b>%{text}</b><br>Cost: $%{x:.4f}<br>Latency: %{y:.0f}ms<br>Accuracy: %{z:.1f}%<extra></extra>'
        ))

        fig.update_layout(
            scene=dict(
                xaxis_title='Cost per Query ($)',
                yaxis_title='Latency (ms)',
                zaxis_title='Accuracy (%)'
            ),
            title='3D Model Comparison: Quality vs Cost vs Latency',
            height=700,
            template='plotly_white'
        )

        fig.show()

    @staticmethod
    def plot_bubble_chart(df: pd.DataFrame) -> None:
        """
        Create bubble chart: X=cost, Y=latency, size=accuracy, color=type.
        """

        fig = px.scatter(df, x='cost_per_query', y='latency_ms',
                        size='accuracy', color='type',
                        hover_name='model',
                        size_max=60,
                        title='Model Comparison: Cost vs Latency (bubble size = accuracy)',
                        labels={
                            'cost_per_query': 'Cost per Query ($)',
                            'latency_ms': 'Total Latency (ms)',
                            'type': 'Model Type'
                        })

        fig.update_layout(height=600, template='plotly_white')
        fig.show()

    @staticmethod
    def plot_efficiency_ranking(ranked_df: pd.DataFrame) -> None:
        """Create bar chart of efficiency rankings."""

        fig = px.bar(ranked_df, x='efficiency_score', y='model',
                    color='accuracy',
                    orientation='h',
                    title='Model Efficiency Ranking',
                    labels={
                        'efficiency_score': 'Efficiency Score',
                        'accuracy': 'Accuracy (%)'
                    })

        fig.update_layout(height=600, template='plotly_white',
                         yaxis={'categoryorder': 'total ascending'})
        fig.show()

    @staticmethod
    def plot_cost_quality_trade_off(df: pd.DataFrame) -> None:
        """Analyze cost-quality trade-off curve."""

        # Sort by cost
        df_sorted = df.sort_values('cost_per_query')

        fig = go.Figure()

        # Quality vs Cost curve
        fig.add_trace(go.Scatter(
            x=df_sorted['cost_per_query'],
            y=df_sorted['accuracy'],
            mode='lines+markers',
            name='Cost-Quality Curve',
            marker=dict(size=10),
            line=dict(color='blue', width=2),
            fill='tozeroy'
        ))

        # Annotations for models
        for _, row in df.iterrows():
            fig.add_annotation(
                x=row['cost_per_query'],
                y=row['accuracy'],
                text=row['model'],
                showarrow=True,
                arrowhead=2
            )

        fig.update_layout(
            title='Cost-Quality Trade-off Analysis',
            xaxis_title='Cost per Query ($)',
            yaxis_title='Accuracy (%)',
            height=600,
            template='plotly_white'
        )

        fig.show()

    @staticmethod
    def plot_scenario_comparison(df: pd.DataFrame) -> None:
        """Compare annual costs across scenarios."""

        scenario_costs = df.groupby(['model', 'scenario'])['annual_cost'].first().reset_index()

        fig = px.bar(scenario_costs, x='model', y='annual_cost', color='scenario',
                    barmode='group',
                    title='Annual Costs by Model and Scenario',
                    labels={
                        'annual_cost': 'Annual Cost ($)',
                        'model': 'Model'
                    })

        fig.update_yaxes(type='log')  # Log scale for readability
        fig.update_layout(height=600, template='plotly_white')
        fig.show()

if __name__ == "__main__":
    df = pd.read_csv("model_evaluation_results.csv")

    # Get unique models (one per model across scenarios)
    df_unique = df.groupby('model').first().reset_index()

    viz = ParetoVisualizations()

    print("Creating Pareto visualizations...")
    viz.plot_2d_pareto(df_unique, 'cost_per_query', 'accuracy',
                      title='Pareto Frontier: Cost vs Accuracy')
    viz.plot_2d_pareto(df_unique, 'latency_ms', 'accuracy',
                      title='Pareto Frontier: Latency vs Accuracy')
    viz.plot_3d_pareto(df_unique)
    viz.plot_bubble_chart(df_unique)

    from pareto_analysis import ParetoOptimizer
    ranked = ParetoOptimizer.rank_by_efficiency(df_unique)
    viz.plot_efficiency_ranking(ranked)

    viz.plot_cost_quality_trade_off(df_unique)
    viz.plot_scenario_comparison(df)
```

## Part 5: Model Selection Decision Framework

```python
# model_selection.py
"""
Decision framework for model selection based on requirements.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple

class ModelSelectionFramework:
    """Systematic model selection based on requirements."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.df_unique = df.groupby('model').first().reset_index()

    def select_by_requirements(self,
                              quality_threshold: float = 0.80,
                              max_cost: float = 0.01,
                              max_latency: float = 5000) -> pd.DataFrame:
        """
        Select models meeting all requirements.

        Args:
            quality_threshold: Minimum accuracy (0-100)
            max_cost: Maximum cost per query ($)
            max_latency: Maximum latency (ms)

        Returns:
            DataFrame of eligible models
        """

        eligible = self.df_unique[
            (self.df_unique['accuracy'] >= quality_threshold) &
            (self.df_unique['cost_per_query'] <= max_cost) &
            (self.df_unique['latency_ms'] <= max_latency)
        ]

        return eligible.sort_values('accuracy', ascending=False)

    def select_best_for_use_case(self, use_case: str) -> Dict:
        """
        Recommend best model for specific use case.

        Use cases:
            - 'low_cost': Minimize cost, tolerate lower quality
            - 'high_quality': Maximize quality regardless of cost
            - 'real_time': Minimize latency
            - 'balanced': Balance all three metrics
        """

        recommendations = {}

        if use_case == 'low_cost':
            # Sort by cost, filter quality > 0.70
            candidates = self.df_unique[self.df_unique['accuracy'] >= 70]
            best = candidates.loc[candidates['cost_per_query'].idxmin()]
            recommendations['model'] = best['model']
            recommendations['reason'] = f"Lowest cost (${best['cost_per_query']:.4f}) among quality-acceptable models"

        elif use_case == 'high_quality':
            # Select best accuracy
            best = self.df_unique.loc[self.df_unique['accuracy'].idxmax()]
            recommendations['model'] = best['model']
            recommendations['reason'] = f"Highest accuracy ({best['accuracy']:.1f}%)"

        elif use_case == 'real_time':
            # Select lowest latency meeting quality > 0.75
            candidates = self.df_unique[self.df_unique['accuracy'] >= 75]
            best = candidates.loc[candidates['latency_ms'].idxmin()]
            recommendations['model'] = best['model']
            recommendations['reason'] = f"Lowest latency ({best['latency_ms']:.0f}ms) with good quality"

        elif use_case == 'balanced':
            # Balanced scoring: 40% quality, 30% cost, 30% latency
            scores = pd.DataFrame()
            scores['model'] = self.df_unique['model']

            quality_norm = self.df_unique['accuracy'] / self.df_unique['accuracy'].max()
            cost_norm = 1 - (self.df_unique['cost_per_query'] /
                           self.df_unique['cost_per_query'].max())
            latency_norm = 1 - (self.df_unique['latency_ms'] /
                              self.df_unique['latency_ms'].max())

            scores['balanced_score'] = (0.4 * quality_norm +
                                       0.3 * cost_norm +
                                       0.3 * latency_norm)

            best_idx = scores['balanced_score'].idxmax()
            best = self.df_unique.iloc[best_idx]
            recommendations['model'] = best['model']
            recommendations['reason'] = "Balanced across quality, cost, and latency"

        return recommendations

    def generate_selection_report(self) -> str:
        """Generate comprehensive model selection report."""

        report = []
        report.append("=" * 100)
        report.append("MODEL SELECTION RECOMMENDATION REPORT")
        report.append("=" * 100)

        report.append("\n1. PARETO FRONTIER ANALYSIS")
        report.append("-" * 100)

        from pareto_analysis import ParetoOptimizer
        analysis = ParetoOptimizer.analyze_trade_offs(self.df_unique)
        frontier_models = analysis['pareto_frontier']['model'].tolist()

        report.append(f"Models on Pareto frontier: {', '.join(frontier_models)}")
        report.append("\nFrontier models offer optimal trade-offs between quality, cost, and latency.")

        report.append("\n2. USE CASE SPECIFIC RECOMMENDATIONS")
        report.append("-" * 100)

        use_cases = ['low_cost', 'high_quality', 'real_time', 'balanced']
        for uc in use_cases:
            rec = self.select_by_requirements() if uc == 'balanced' else self.select_by_requirements()
            uc_name = uc.replace('_', ' ').title()
            report.append(f"\n{uc_name}:")
            rec = self.select_best_for_use_case(uc)
            report.append(f"  Model: {rec['model']}")
            report.append(f"  Reason: {rec['reason']}")

        report.append("\n3. DETAILED MODEL COMPARISON")
        report.append("-" * 100)
        report.append(self.df_unique[['model', 'accuracy', 'cost_per_query',
                                       'latency_ms', 'type']].to_string(index=False))

        report.append("\n4. DECISION CRITERIA")
        report.append("-" * 100)
        report.append("• Quality: Accuracy on evaluation suite (higher is better)")
        report.append("• Cost: Per-query cost in USD (lower is better)")
        report.append("• Latency: End-to-end response time in ms (lower is better)")
        report.append("• Availability: Expected uptime SLA")

        report.append("\n" + "=" * 100)

        return "\n".join(report)

if __name__ == "__main__":
    df = pd.read_csv("model_evaluation_results.csv")
    selector = ModelSelectionFramework(df)

    # Example: Select for real-time use case
    print("REAL-TIME USE CASE (max 500ms latency)")
    real_time = selector.select_by_requirements(
        quality_threshold=75,
        max_cost=0.005,
        max_latency=500
    )
    print(real_time[['model', 'accuracy', 'cost_per_query', 'latency_ms']])

    # Generate full report
    report = selector.generate_selection_report()
    print("\n" + report)

    with open("model_selection_report.txt", "w") as f:
        f.write(report)
```

## Summary

In this lab, you have:

1. **Evaluated 5+ models** on consistent quality, cost, and latency metrics
2. **Measured actual performance** across frontier and open-weight models
3. **Computed Pareto-optimal frontier** identifying non-dominated solutions
4. **Created 3D visualizations** showing all three dimensions
5. **Developed decision framework** for model selection by use case
6. **Generated selection reports** with specific recommendations

## Key Takeaways

- Pareto analysis reveals actual trade-offs rather than assuming single best model
- Frontier models are not always optimal for every use case
- Cost dramatically varies with usage patterns and deployment scenarios
- Latency requirements often exclude frontier models for real-time applications
- Open-weight models can be Pareto-optimal for cost-conscious deployments
- Different use cases require different optimization objectives

## Next Steps

- Use selected models in production pipelines (see Production Guides)
- Set up continuous cost tracking and re-evaluate quarterly
- Monitor for new models that may shift Pareto frontier
- Implement A/B tests comparing finalist models in production
- Use this framework for model rotation strategy
