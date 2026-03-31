"""Evaluation runner: Orchestrates evaluation execution."""

import json
import logging
from pathlib import Path
from typing import Any, Optional

from llm_eval_framework.harness.config import EvalConfig
from llm_eval_framework.judges import BaseJudge, RubricJudge, PairwiseJudge, ConstitutionalJudge
from llm_eval_framework.metrics import (
    FaithfulnessScorer,
    InstructionFollowingScorer,
    CodeExecutionScorer,
    SafetyScorer,
)

logger = logging.getLogger(__name__)


class EvalRunner:
    """Orchestrates LLM evaluation runs using configuration."""

    def __init__(self, config: EvalConfig):
        """Initialize the evaluation runner.

        Args:
            config: EvalConfig instance
        """
        self.config = config
        self.judges: dict[str, BaseJudge] = {}
        self.metrics: dict[str, Any] = {}
        self.results: list[dict] = []

        self._output_dir = Path(config.output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def _instantiate_judges(self) -> None:
        """Instantiate all configured judges."""
        judge_mapping = {
            "rubric": RubricJudge,
            "pairwise": PairwiseJudge,
            "constitutional": ConstitutionalJudge,
        }

        for judge_config in self.config.judges:
            judge_class = judge_mapping.get(judge_config.name)
            if not judge_class:
                logger.warning(f"Unknown judge type: {judge_config.name}")
                continue

            # Get model from first model config
            model = self.config.models[0].name if self.config.models else "gpt-4"

            params = judge_config.params.copy()
            params["model"] = model

            try:
                judge = judge_class(**params)
                self.judges[judge_config.name] = judge
                logger.info(f"Instantiated judge: {judge_config.name}")
            except Exception as e:
                logger.error(f"Failed to instantiate judge {judge_config.name}: {e}")

    def _instantiate_metrics(self) -> None:
        """Instantiate all configured metrics."""
        metric_mapping = {
            "faithfulness": FaithfulnessScorer,
            "instruction_following": InstructionFollowingScorer,
            "code_execution": CodeExecutionScorer,
            "safety": SafetyScorer,
        }

        for metric_config in self.config.metrics:
            metric_class = metric_mapping.get(metric_config.name)
            if not metric_class:
                logger.warning(f"Unknown metric type: {metric_config.name}")
                continue

            try:
                metric = metric_class(**metric_config.params)
                self.metrics[metric_config.name] = metric
                logger.info(f"Instantiated metric: {metric_config.name}")
            except Exception as e:
                logger.error(f"Failed to instantiate metric {metric_config.name}: {e}")

    async def _load_dataset(self) -> list[dict]:
        """Load evaluation dataset.

        Returns:
            List of data examples

        Raises:
            ValueError: If dataset format not supported
        """
        dataset_path = self.config.dataset.path

        if not Path(dataset_path).exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

        if self.config.dataset.format == "json":
            with open(dataset_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and self.config.dataset.split:
                    return data.get(self.config.dataset.split, [])
                else:
                    return [data]

        elif self.config.dataset.format == "csv":
            import csv
            data = []
            with open(dataset_path, 'r') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            return data

        else:
            raise ValueError(f"Unsupported dataset format: {self.config.dataset.format}")

    async def evaluate(self, example: dict) -> dict:
        """Evaluate a single example.

        Args:
            example: Dictionary with prompt, response, etc.

        Returns:
            Dict with all evaluation results
        """
        result = {
            "example_id": example.get("id", "unknown"),
            "prompt": example.get("prompt", ""),
            "response": example.get("response", ""),
            "judges": {},
            "metrics": {},
        }

        # Run judges
        for judge_name, judge in self.judges.items():
            try:
                from llm_eval_framework.judges import JudgeInput
                judge_input = JudgeInput(
                    prompt=example.get("prompt", ""),
                    response=example.get("response", ""),
                    context=example.get("context"),
                )
                judge_output = await judge.judge_single(judge_input)
                result["judges"][judge_name] = {
                    "score": judge_output.overall_score,
                    "explanation": judge_output.explanation,
                }
            except Exception as e:
                logger.error(f"Judge {judge_name} failed: {e}")
                result["judges"][judge_name] = {"error": str(e)}

        # Run metrics
        for metric_name, metric in self.metrics.items():
            try:
                metric_result = await metric.score(
                    response=example.get("response", ""),
                    context=example.get("context"),
                    **example.get(f"{metric_name}_params", {}),
                )
                result["metrics"][metric_name] = metric_result
            except Exception as e:
                logger.error(f"Metric {metric_name} failed: {e}")
                result["metrics"][metric_name] = {"error": str(e)}

        return result

    async def run(self) -> list[dict]:
        """Run the complete evaluation.

        Returns:
            List of evaluation results
        """
        logger.info(f"Starting evaluation: {self.config.name}")

        self._instantiate_judges()
        self._instantiate_metrics()

        dataset = await self._load_dataset()
        logger.info(f"Loaded {len(dataset)} examples")

        self.results = []

        for i, example in enumerate(dataset):
            if i > 0 and i % 10 == 0:
                logger.info(f"Progress: {i}/{len(dataset)}")

            result = await self.evaluate(example)
            self.results.append(result)

        logger.info(f"Evaluation complete. Results: {len(self.results)}")

        # Save results
        self._save_results()

        return self.results

    def _save_results(self) -> None:
        """Save evaluation results."""
        output_path = self._output_dir / f"results.{self.config.save_format}"

        if self.config.save_format == "json":
            with open(output_path, 'w') as f:
                json.dump(self.results, f, indent=2)
        elif self.config.save_format == "csv":
            import csv
            if not self.results:
                return
            keys = set()
            for result in self.results:
                keys.update(result.keys())
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=list(keys))
                writer.writeheader()
                writer.writerows(self.results)

        logger.info(f"Results saved to {output_path}")

    def __repr__(self) -> str:
        """String representation."""
        return f"EvalRunner(config={self.config.name}, judges={len(self.judges)}, metrics={len(self.metrics)})"
