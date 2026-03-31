"""Base judge class and data models for LLM-based evaluation."""

import json
from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel, Field


class ScoreDimension(BaseModel):
    """Represents a single scoring dimension."""

    name: str = Field(..., description="Name of the dimension (e.g., 'clarity', 'correctness')")
    score: float = Field(..., ge=0.0, le=1.0, description="Score between 0 and 1")
    explanation: str = Field(..., description="Explanation for the score")


class JudgeInput(BaseModel):
    """Input to a judge evaluation."""

    prompt: str = Field(..., description="The original prompt/question")
    response: str = Field(..., description="The response to evaluate")
    context: Optional[str] = Field(None, description="Optional context (e.g., reference materials)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class JudgeOutput(BaseModel):
    """Output from a judge evaluation."""

    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall score between 0 and 1")
    dimensions: list[ScoreDimension] = Field(
        default_factory=list,
        description="Scores across different dimensions"
    )
    explanation: str = Field(..., description="Overall explanation for the score")
    raw_response: str = Field(..., description="Raw LLM response before parsing")
    model: str = Field(..., description="Model used for judging")


class BaseJudge(ABC):
    """Abstract base class for all judge implementations.

    Judges evaluate LLM responses using various strategies (rubric-based, pairwise, etc.)
    and return structured scores with explanations.
    """

    def __init__(self, model: str, temperature: float = 0.0, max_retries: int = 3):
        """Initialize the base judge.

        Args:
            model: LLM model to use for judging (e.g., 'gpt-4')
            temperature: Temperature for LLM sampling
            max_retries: Maximum retries for failed evaluations
        """
        self.model = model
        self.temperature = temperature
        self.max_retries = max_retries

    @abstractmethod
    def get_prompt(self, judge_input: JudgeInput) -> str:
        """Generate the evaluation prompt for the given input.

        Args:
            judge_input: The input to be evaluated

        Returns:
            A formatted prompt string for the LLM

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError

    @abstractmethod
    def parse_response(self, raw_response: str) -> JudgeOutput:
        """Parse the raw LLM response into a structured JudgeOutput.

        Args:
            raw_response: The raw text response from the LLM

        Returns:
            Parsed JudgeOutput with scores and explanations

        Raises:
            ValueError: If response cannot be parsed
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError

    async def judge_single(self, judge_input: JudgeInput) -> JudgeOutput:
        """Evaluate a single response asynchronously.

        Args:
            judge_input: The input to evaluate

        Returns:
            JudgeOutput with scores and explanations

        Raises:
            Exception: If evaluation fails after max_retries
        """
        from llm_eval_framework.utils.llm_client import UnifiedLLMClient

        client = UnifiedLLMClient(model=self.model)
        prompt = self.get_prompt(judge_input)

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = await client.acompletion(
                    prompt=prompt,
                    temperature=self.temperature,
                    json_mode=False,
                )
                output = self.parse_response(response)
                output.raw_response = response
                output.model = self.model
                return output
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    continue
                raise RuntimeError(
                    f"Judge failed after {self.max_retries} attempts: {last_error}"
                ) from last_error

        raise RuntimeError(f"Unexpected error in judge_single: {last_error}")

    async def judge_batch(
        self, judge_inputs: list[JudgeInput], parallel: bool = True
    ) -> list[JudgeOutput]:
        """Evaluate multiple responses.

        Args:
            judge_inputs: List of inputs to evaluate
            parallel: Whether to evaluate in parallel (default: True)

        Returns:
            List of JudgeOutput objects in the same order as inputs
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

    def __repr__(self) -> str:
        """String representation of the judge."""
        return f"{self.__class__.__name__}(model={self.model})"
