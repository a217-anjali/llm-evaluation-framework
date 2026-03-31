"""Pareto-optimal model selection based on quality/cost/latency tradeoffs."""

from typing import Optional

import numpy as np


class ParetoSelector:
    """Selects Pareto-optimal models given multiple objectives."""

    def __init__(self, maximize_metrics: list[str], minimize_metrics: list[str]):
        """Initialize the Pareto selector.

        Args:
            maximize_metrics: Metrics to maximize (e.g., ['accuracy', 'f1'])
            minimize_metrics: Metrics to minimize (e.g., ['cost', 'latency'])

        Example:
            selector = ParetoSelector(
                maximize_metrics=['quality_score'],
                minimize_metrics=['cost_per_call', 'latency_ms']
            )
        """
        self.maximize_metrics = maximize_metrics
        self.minimize_metrics = minimize_metrics

    def find_pareto_frontier(self, models: list[dict]) -> list[dict]:
        """Find Pareto-optimal models.

        Args:
            models: List of model dicts with metrics

        Returns:
            List of non-dominated models
        """
        if not models:
            return []

        dominated = set()

        for i, model_a in enumerate(models):
            for j, model_b in enumerate(models):
                if i == j:
                    continue

                # Check if model_a dominates model_b
                if self._dominates(model_a, model_b):
                    dominated.add(j)
                # Check if model_b dominates model_a
                elif self._dominates(model_b, model_a):
                    dominated.add(i)

        pareto_frontier = [
            models[i] for i in range(len(models)) if i not in dominated
        ]

        return sorted(
            pareto_frontier,
            key=lambda m: self._compute_score(m),
            reverse=True,
        )

    def _dominates(self, model_a: dict, model_b: dict) -> bool:
        """Check if model_a dominates model_b.

        A model dominates another if it's better on all objectives.

        Args:
            model_a: First model
            model_b: Second model

        Returns:
            True if model_a dominates model_b
        """
        better_on_some = False
        worse_on_none = True

        for metric in self.maximize_metrics:
            val_a = model_a.get(metric, 0)
            val_b = model_b.get(metric, 0)

            if val_a > val_b:
                better_on_some = True
            elif val_a < val_b:
                worse_on_none = False

        for metric in self.minimize_metrics:
            val_a = model_a.get(metric, float('inf'))
            val_b = model_b.get(metric, float('inf'))

            if val_a < val_b:
                better_on_some = True
            elif val_a > val_b:
                worse_on_none = False

        return better_on_some and worse_on_none

    def _compute_score(self, model: dict) -> float:
        """Compute a scalar score for ranking within Pareto frontier.

        Args:
            model: Model with metrics

        Returns:
            Scalar score
        """
        score = 0.0

        for metric in self.maximize_metrics:
            val = model.get(metric, 0)
            score += val

        for metric in self.minimize_metrics:
            val = model.get(metric, 1.0)
            score -= val

        return score

    def rank_by_metric(
        self,
        models: list[dict],
        metric: str,
        ascending: bool = False,
    ) -> list[dict]:
        """Rank models by a specific metric.

        Args:
            models: List of models
            metric: Metric to rank by
            ascending: If True, sort ascending (for metrics to minimize)

        Returns:
            Sorted list of models
        """
        return sorted(
            models,
            key=lambda m: m.get(metric, 0),
            reverse=not ascending,
        )

    def dominated_count(self, models: list[dict]) -> dict:
        """Count how many models dominate each model.

        Args:
            models: List of models

        Returns:
            Dict mapping model index to domination count
        """
        counts = {i: 0 for i in range(len(models))}

        for i, model_a in enumerate(models):
            for j, model_b in enumerate(models):
                if i != j and self._dominates(model_a, model_b):
                    counts[j] += 1

        return counts

    def get_frontier_stats(self, models: list[dict]) -> dict:
        """Get statistics about the Pareto frontier.

        Args:
            models: List of models

        Returns:
            Dict with frontier statistics
        """
        frontier = self.find_pareto_frontier(models)

        stats = {
            "total_models": len(models),
            "frontier_size": len(frontier),
            "frontier_percentage": (len(frontier) / len(models) * 100) if models else 0,
            "frontier": frontier,
        }

        for metric in self.maximize_metrics + self.minimize_metrics:
            values = [m.get(metric, 0) for m in frontier]
            if values:
                stats[f"{metric}_range"] = (min(values), max(values))
                stats[f"{metric}_mean"] = sum(values) / len(values)

        return stats

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ParetoSelector("
            f"maximize={self.maximize_metrics}, "
            f"minimize={self.minimize_metrics})"
        )
