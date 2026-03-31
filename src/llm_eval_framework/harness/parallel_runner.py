"""Parallel evaluation runner with async support."""

import asyncio
import logging
from typing import Optional

from llm_eval_framework.harness.config import EvalConfig
from llm_eval_framework.harness.runner import EvalRunner

logger = logging.getLogger(__name__)


class ParallelEvalRunner(EvalRunner):
    """Runs evaluations in parallel with configurable concurrency limits."""

    def __init__(
        self,
        config: EvalConfig,
        max_concurrent: int = 10,
        rate_limit_per_second: Optional[float] = None,
    ):
        """Initialize the parallel runner.

        Args:
            config: EvalConfig instance
            max_concurrent: Maximum concurrent evaluations
            rate_limit_per_second: Optional rate limit (requests per second)
        """
        super().__init__(config)
        self.max_concurrent = max_concurrent
        self.rate_limit_per_second = rate_limit_per_second
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._rate_limiter: Optional[asyncio.Semaphore] = None

    async def _acquire_semaphore(self) -> None:
        """Acquire a permit from the concurrency semaphore."""
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(self.max_concurrent)
        await self._semaphore.acquire()

    def _release_semaphore(self) -> None:
        """Release a permit to the concurrency semaphore."""
        if self._semaphore is not None:
            self._semaphore.release()

    async def _apply_rate_limit(self) -> None:
        """Apply rate limiting if configured."""
        if self.rate_limit_per_second is None:
            return

        if self._rate_limiter is None:
            # Simple rate limiter: acquire and release with delay
            pass

        await asyncio.sleep(1.0 / self.rate_limit_per_second)

    async def _evaluate_with_limits(self, example: dict, index: int) -> dict:
        """Evaluate with concurrency and rate limiting.

        Args:
            example: Example to evaluate
            index: Index in the batch

        Returns:
            Evaluation result
        """
        await self._apply_rate_limit()
        await self._acquire_semaphore()

        try:
            return await self.evaluate(example)
        finally:
            self._release_semaphore()

    async def run(self) -> list[dict]:
        """Run evaluations in parallel.

        Returns:
            List of evaluation results
        """
        logger.info(f"Starting parallel evaluation: {self.config.name}")
        logger.info(f"Max concurrent: {self.max_concurrent}")

        self._instantiate_judges()
        self._instantiate_metrics()

        dataset = await self._load_dataset()
        logger.info(f"Loaded {len(dataset)} examples")

        # Create tasks for all examples
        tasks = [
            self._evaluate_with_limits(example, i)
            for i, example in enumerate(dataset)
        ]

        # Run with progress tracking
        self.results = []
        completed = 0

        for coro in asyncio.as_completed(tasks):
            result = await coro
            self.results.append(result)
            completed += 1

            if completed % 10 == 0:
                logger.info(f"Progress: {completed}/{len(dataset)}")

        # Sort by example index
        self.results.sort(
            key=lambda x: x.get("example_id", ""),
        )

        logger.info(f"Parallel evaluation complete. Results: {len(self.results)}")

        # Save results
        self._save_results()

        return self.results

    async def run_with_progress_callback(
        self,
        callback=None,
    ) -> list[dict]:
        """Run evaluations with progress callback.

        Args:
            callback: Optional callback function called on each completion

        Returns:
            List of evaluation results
        """
        logger.info(f"Starting parallel evaluation with callbacks: {self.config.name}")

        self._instantiate_judges()
        self._instantiate_metrics()

        dataset = await self._load_dataset()
        logger.info(f"Loaded {len(dataset)} examples")

        # Create tasks
        tasks = [
            self._evaluate_with_limits(example, i)
            for i, example in enumerate(dataset)
        ]

        self.results = []
        completed = 0

        for coro in asyncio.as_completed(tasks):
            result = await coro
            self.results.append(result)
            completed += 1

            if callback:
                await callback(result, completed, len(dataset))
            else:
                if completed % 10 == 0:
                    logger.info(f"Progress: {completed}/{len(dataset)}")

        self.results.sort(key=lambda x: x.get("example_id", ""))

        logger.info(f"Parallel evaluation complete. Results: {len(self.results)}")
        self._save_results()

        return self.results

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ParallelEvalRunner("
            f"config={self.config.name}, "
            f"max_concurrent={self.max_concurrent}, "
            f"judges={len(self.judges)}, "
            f"metrics={len(self.metrics)})"
        )
