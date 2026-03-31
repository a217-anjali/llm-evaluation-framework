"""Pairwise judge for comparing two responses with position debiasing."""

import json
import re

from llm_eval_framework.judges.base_judge import (
    BaseJudge,
    JudgeInput,
    JudgeOutput,
    ScoreDimension,
)


class PairwiseJudge(BaseJudge):
    """Judge that compares two responses head-to-head.

    This judge compares two responses and determines which is better, with
    optional position debiasing by running the comparison in both orders.
    """

    def __init__(
        self,
        model: str,
        debiasing: bool = True,
        temperature: float = 0.0,
        max_retries: int = 3,
    ):
        """Initialize the pairwise judge.

        Args:
            model: LLM model to use for judging
            debiasing: Whether to debias by comparing in both orders (default: True)
            temperature: Temperature for LLM sampling
            max_retries: Maximum retries for failed evaluations
        """
        super().__init__(model=model, temperature=temperature, max_retries=max_retries)
        self.debiasing = debiasing

    async def judge_pair(
        self,
        prompt: str,
        response_a: str,
        response_b: str,
        context: str | None = None,
        position_a: bool = True,
    ) -> dict:
        """Compare two responses.

        Args:
            prompt: The original prompt
            response_a: First response
            response_b: Second response
            context: Optional context
            position_a: If True, A is in position 1; if False, B is in position 1

        Returns:
            Dict with winner, tie, confidence, and reasoning
        """
        judge_input = JudgeInput(
            prompt=prompt,
            response=f"Response A:\n{response_a}\n\nResponse B:\n{response_b}",
            context=context,
        )

        if position_a:
            result = await self.judge_single(judge_input)
        else:
            # Swap positions for debiasing
            judge_input.response = f"Response A:\n{response_b}\n\nResponse B:\n{response_a}"
            result = await self.judge_single(judge_input)

        # Extract winner from dimensions or explanation
        dimensions_dict = {d.name: d for d in result.dimensions}

        if position_a:
            winner = dimensions_dict.get("winner", {}).score > 0.5
        else:
            # Flip the result for position swap
            winner = dimensions_dict.get("winner", {}).score <= 0.5

        return {
            "winner": "A" if winner else "B",
            "tie": "tie" in result.explanation.lower(),
            "confidence": float(result.overall_score),
            "reasoning": result.explanation,
        }

    async def judge_pairs_with_debiasing(
        self,
        prompt: str,
        response_a: str,
        response_b: str,
        context: str | None = None,
    ) -> dict:
        """Compare two responses with position debiasing.

        Runs the comparison in both positions and aggregates results.

        Args:
            prompt: The original prompt
            response_a: First response
            response_b: Second response
            context: Optional context

        Returns:
            Aggregated comparison result with debiasing info
        """
        result_1 = await self.judge_pair(
            prompt, response_a, response_b, context, position_a=True
        )
        result_2 = await self.judge_pair(
            prompt, response_a, response_b, context, position_a=False
        )

        agreement = (result_1["winner"] == result_2["winner"]) and (
            result_1["tie"] == result_2["tie"]
        )
        position_bias = abs(result_1["confidence"] - result_2["confidence"])

        final_winner = result_1["winner"]
        if not agreement:
            final_winner = "TIE"
            final_confidence = 0.5
        else:
            final_confidence = (result_1["confidence"] + result_2["confidence"]) / 2

        return {
            "winner": final_winner,
            "confidence": final_confidence,
            "tie": result_1["tie"] or result_2["tie"],
            "agreement": agreement,
            "position_bias": position_bias,
            "result_position_a": result_1,
            "result_position_b": result_2,
        }

    def get_prompt(self, judge_input: JudgeInput) -> str:
        """Generate the pairwise comparison prompt.

        Args:
            judge_input: The input containing both responses

        Returns:
            Formatted prompt for pairwise comparison
        """
        context_section = ""
        if judge_input.context:
            context_section = f"\n\nContext/Reference:\n{judge_input.context}"

        prompt = f"""You are an expert evaluator. Your task is to compare two responses to the given prompt.

Prompt/Question:
{judge_input.prompt}{context_section}

{judge_input.response}

Compare these responses across the following dimensions:
- Accuracy and factual correctness
- Completeness and thoroughness
- Clarity and organization
- Relevance to the prompt
- Overall quality

Provide your evaluation in the following JSON format:
{{
    "dimensions": [
        {{"name": "winner", "score": 0 (B wins) or 1 (A wins), "explanation": "brief reasoning"}},
        {{"name": "accuracy", "score": 0-1, "explanation": ""}},
        {{"name": "completeness", "score": 0-1, "explanation": ""}},
        {{"name": "clarity", "score": 0-1, "explanation": ""}},
        {{"name": "relevance", "score": 0-1, "explanation": ""}}
    ],
    "overall_score": 0-1,
    "explanation": "which response is better and why, or 'tie' if equal"
}}

Respond with ONLY the JSON object."""
        return prompt

    def parse_response(self, raw_response: str) -> JudgeOutput:
        """Parse the pairwise comparison response.

        Args:
            raw_response: The raw response from the LLM

        Returns:
            Parsed JudgeOutput

        Raises:
            ValueError: If response cannot be parsed
        """
        try:
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")

            data = json.loads(json_match.group())

            dimensions = []
            for dim_data in data.get("dimensions", []):
                dimensions.append(
                    ScoreDimension(
                        name=dim_data.get("name", "unknown"),
                        score=float(dim_data.get("score", 0.5)),
                        explanation=dim_data.get("explanation", ""),
                    )
                )

            return JudgeOutput(
                overall_score=float(data.get("overall_score", 0.5)),
                dimensions=dimensions,
                explanation=data.get("explanation", ""),
                raw_response=raw_response,
                model=self.model,
            )

        except (json.JSONDecodeError, ValueError, TypeError) as e:
            raise ValueError(f"Failed to parse pairwise response: {e}") from e

    def __repr__(self) -> str:
        """String representation of the judge."""
        debiasing_str = "with debiasing" if self.debiasing else "no debiasing"
        return f"PairwiseJudge(model={self.model}, {debiasing_str})"
