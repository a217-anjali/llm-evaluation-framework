"""Rubric-based judge for structured evaluation using scoring rubrics."""

import json
import re
from typing import Any

from llm_eval_framework.judges.base_judge import (
    BaseJudge,
    JudgeInput,
    JudgeOutput,
    ScoreDimension,
)


class RubricJudge(BaseJudge):
    """Judge that evaluates responses against a predefined rubric.

    The rubric specifies dimensions and their scoring criteria. The judge
    generates a structured prompt using the rubric and parses the response
    into dimension-specific scores.
    """

    def __init__(
        self,
        model: str,
        rubric: dict[str, str],
        scale: tuple[int, int] = (1, 5),
        temperature: float = 0.0,
        max_retries: int = 3,
    ):
        """Initialize the rubric judge.

        Args:
            model: LLM model to use for judging
            rubric: Dict mapping dimension names to descriptions
            scale: Tuple of (min_score, max_score) for the rubric scale
            temperature: Temperature for LLM sampling
            max_retries: Maximum retries for failed evaluations

        Example:
            rubric = {
                "clarity": "Is the response clear and well-structured?",
                "correctness": "Is the response factually correct?",
                "completeness": "Does it address all parts of the question?",
            }
            judge = RubricJudge(model="gpt-4", rubric=rubric)
        """
        super().__init__(model=model, temperature=temperature, max_retries=max_retries)
        self.rubric = rubric
        self.scale = scale

    def get_prompt(self, judge_input: JudgeInput) -> str:
        """Generate the evaluation prompt using the rubric.

        Args:
            judge_input: The input to evaluate

        Returns:
            Formatted prompt with rubric and instructions
        """
        min_score, max_score = self.scale
        rubric_text = "\n".join(
            f"- {name}: {description}" for name, description in self.rubric.items()
        )

        context_section = ""
        if judge_input.context:
            context_section = f"\n\nContext/Reference:\n{judge_input.context}"

        prompt = f"""You are an expert evaluator. Your task is to score the following response using the provided rubric.

Prompt/Question:
{judge_input.prompt}{context_section}

Response to Evaluate:
{judge_input.response}

Scoring Rubric (score from {min_score} to {max_score}):
{rubric_text}

Provide your evaluation in the following JSON format:
{{
    "dimensions": [
        {{"name": "dimension_name", "score": {min_score}-{max_score}, "explanation": "brief explanation"}},
        ...
    ],
    "overall_score": {min_score}-{max_score},
    "explanation": "overall summary of strengths and weaknesses"
}}

Respond with ONLY the JSON object, no additional text."""
        return prompt

    def parse_response(self, raw_response: str) -> JudgeOutput:
        """Parse the JSON response from the LLM.

        Args:
            raw_response: The raw response from the LLM

        Returns:
            Parsed JudgeOutput

        Raises:
            ValueError: If response cannot be parsed as valid JSON
        """
        try:
            # Extract JSON from the response
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")

            data = json.loads(json_match.group())

            # Normalize scores to 0-1 range
            min_score, max_score = self.scale
            scale_range = max_score - min_score

            dimensions = []
            for dim_data in data.get("dimensions", []):
                score = dim_data.get("score", 0)
                normalized_score = (score - min_score) / scale_range
                normalized_score = max(0.0, min(1.0, normalized_score))

                dimensions.append(
                    ScoreDimension(
                        name=dim_data.get("name", "unknown"),
                        score=normalized_score,
                        explanation=dim_data.get("explanation", ""),
                    )
                )

            overall_score = data.get("overall_score", 0)
            normalized_overall = (overall_score - min_score) / scale_range
            normalized_overall = max(0.0, min(1.0, normalized_overall))

            return JudgeOutput(
                overall_score=normalized_overall,
                dimensions=dimensions,
                explanation=data.get("explanation", ""),
                raw_response=raw_response,
                model=self.model,
            )

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}") from e
        except (KeyError, TypeError) as e:
            raise ValueError(f"Invalid response structure: {e}") from e

    def __repr__(self) -> str:
        """String representation of the judge."""
        dims = ", ".join(self.rubric.keys())
        return f"RubricJudge(model={self.model}, dimensions=[{dims}])"
