"""Multi-judge panel that aggregates evaluations from multiple judges."""

from enum import Enum
from typing import Literal

from llm_eval_framework.judges.base_judge import BaseJudge, JudgeInput, JudgeOutput, ScoreDimension


class VotingStrategy(str, Enum):
    """Voting strategies for aggregating judge opinions."""

    MAJORITY = "majority"
    WEIGHTED = "weighted"
    UNANIMOUS = "unanimous"


class MultiJudgePanel:
    """Runs multiple judges and aggregates their evaluations.

    This class enables consensus-based evaluation by running multiple judge
    instances and combining their scores using various strategies.
    """

    def __init__(
        self,
        judges: list[BaseJudge],
        voting_strategy: Literal["majority", "weighted", "unanimous"] = "majority",
        weights: list[float] | None = None,
    ):
        """Initialize the multi-judge panel.

        Args:
            judges: List of BaseJudge instances
            voting_strategy: Strategy for aggregating scores (majority, weighted, unanimous)
            weights: Optional weights for each judge (used with weighted strategy)

        Raises:
            ValueError: If weights length doesn't match judges length
        """
        self.judges = judges
        self.voting_strategy = VotingStrategy(voting_strategy)

        if weights is None:
            self.weights = [1.0 / len(judges)] * len(judges)
        else:
            if len(weights) != len(judges):
                raise ValueError(f"weights length ({len(weights)}) != judges length ({len(judges)})")
            total = sum(weights)
            self.weights = [w / total for w in weights]

    async def judge_single(self, judge_input: JudgeInput) -> dict:
        """Evaluate a response using all judges and aggregate results.

        Args:
            judge_input: The input to evaluate

        Returns:
            Dict with aggregated score, per-judge scores, and agreement stats
        """
        judge_outputs = await self._run_all_judges(judge_input)
        aggregated = self._aggregate_scores(judge_outputs)

        return aggregated

    async def judge_batch(
        self, judge_inputs: list[JudgeInput], parallel: bool = True
    ) -> list[dict]:
        """Evaluate multiple responses using all judges.

        Args:
            judge_inputs: List of inputs to evaluate
            parallel: Whether to evaluate in parallel

        Returns:
            List of aggregated evaluation results
        """
        if not parallel:
            results = []
            for judge_input in judge_inputs:
                result = await self.judge_single(judge_input)
                results.append(result)
            return results

        import asyncio
        tasks = [self.judge_single(judge_input) for judge_input in judge_inputs]
        return await asyncio.gather(*tasks)

    async def _run_all_judges(self, judge_input: JudgeInput) -> list[JudgeOutput]:
        """Run evaluation on all judges in parallel.

        Args:
            judge_input: The input to evaluate

        Returns:
            List of JudgeOutput from each judge
        """
        import asyncio
        tasks = [judge.judge_single(judge_input) for judge in self.judges]
        return await asyncio.gather(*tasks)

    def _aggregate_scores(self, judge_outputs: list[JudgeOutput]) -> dict:
        """Aggregate scores from multiple judges.

        Args:
            judge_outputs: List of outputs from each judge

        Returns:
            Aggregated result dict with scores and statistics
        """
        if not judge_outputs:
            raise ValueError("No judge outputs to aggregate")

        scores = [output.overall_score for output in judge_outputs]

        if self.voting_strategy == VotingStrategy.MAJORITY:
            aggregated_score = sum(scores) / len(scores)
        elif self.voting_strategy == VotingStrategy.WEIGHTED:
            aggregated_score = sum(s * w for s, w in zip(scores, self.weights))
        elif self.voting_strategy == VotingStrategy.UNANIMOUS:
            aggregated_score = min(scores)
        else:
            aggregated_score = sum(scores) / len(scores)

        # Compute agreement statistics
        score_std = self._compute_std(scores)
        score_mean = sum(scores) / len(scores)

        # Aggregate dimensions
        all_dimensions = {}
        for output in judge_outputs:
            for dim in output.dimensions:
                if dim.name not in all_dimensions:
                    all_dimensions[dim.name] = []
                all_dimensions[dim.name].append(dim.score)

        aggregated_dimensions = []
        for dim_name, dim_scores in all_dimensions.items():
            avg_score = sum(dim_scores) / len(dim_scores)
            aggregated_dimensions.append(
                ScoreDimension(
                    name=dim_name,
                    score=avg_score,
                    explanation=f"Average score across {len(dim_scores)} judges",
                )
            )

        # Explanation aggregation
        explanations = [output.explanation for output in judge_outputs]
        combined_explanation = " | ".join(explanations[:2])  # Use first 2 explanations

        return {
            "overall_score": aggregated_score,
            "dimensions": aggregated_dimensions,
            "explanation": combined_explanation,
            "per_judge_scores": scores,
            "score_mean": score_mean,
            "score_std": score_std,
            "judge_agreement": 1.0 - (score_std / (score_mean + 1e-6)) if score_mean > 0 else 1.0,
            "num_judges": len(self.judges),
            "strategy": self.voting_strategy.value,
        }

    @staticmethod
    def _compute_std(values: list[float]) -> float:
        """Compute sample standard deviation.

        Args:
            values: List of values

        Returns:
            Sample standard deviation
        """
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5

    def __repr__(self) -> str:
        """String representation of the panel."""
        judge_names = ", ".join(str(j) for j in self.judges)
        return f"MultiJudgePanel({self.voting_strategy.value}, judges=[{judge_names}])"
