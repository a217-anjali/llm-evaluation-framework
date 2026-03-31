"""Instruction following metric: Check if response follows specific instructions."""

import re
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class InstructionConstraint:
    """A single instruction constraint to check."""

    name: str
    description: str
    check_fn: Callable[[str], bool]


class InstructionFollowingScorer:
    """Scores how well a response follows specific instructions.

    Supports both rule-based constraints (word count, format) and
    LLM-based semantic checking.
    """

    def __init__(self, model: str = "gpt-3.5-turbo"):
        """Initialize the instruction following scorer.

        Args:
            model: LLM model for semantic instruction checking
        """
        self.model = model
        self.constraints: dict[str, InstructionConstraint] = {}

    def add_constraint(
        self,
        name: str,
        description: str,
        check_fn: Callable[[str], bool],
    ) -> None:
        """Add a constraint to check.

        Args:
            name: Constraint identifier
            description: Human-readable description
            check_fn: Function that takes response and returns True if constraint is met
        """
        self.constraints[name] = InstructionConstraint(name, description, check_fn)

    def add_word_count_constraint(
        self,
        min_words: Optional[int] = None,
        max_words: Optional[int] = None,
    ) -> None:
        """Add a word count constraint.

        Args:
            min_words: Minimum allowed word count (None = no minimum)
            max_words: Maximum allowed word count (None = no maximum)
        """
        def check_word_count(response: str) -> bool:
            words = len(response.split())
            if min_words is not None and words < min_words:
                return False
            if max_words is not None and words > max_words:
                return False
            return True

        desc = []
        if min_words:
            desc.append(f"≥{min_words} words")
        if max_words:
            desc.append(f"≤{max_words} words")
        description = f"Word count: {', '.join(desc)}"

        self.add_constraint("word_count", description, check_word_count)

    def add_format_constraint(
        self,
        pattern: str,
        description: str = "Matches required format",
    ) -> None:
        """Add a format constraint using regex.

        Args:
            pattern: Regex pattern the response must match
            description: Description of the format requirement
        """
        def check_format(response: str) -> bool:
            return bool(re.search(pattern, response, re.IGNORECASE | re.MULTILINE))

        self.add_constraint("format", description, check_format)

    def add_keyword_constraint(
        self,
        keywords: list[str],
        require_all: bool = True,
    ) -> None:
        """Add a keyword presence constraint.

        Args:
            keywords: List of keywords to check for
            require_all: If True, all keywords must be present; if False, at least one
        """
        def check_keywords(response: str) -> bool:
            response_lower = response.lower()
            matches = [kw.lower() in response_lower for kw in keywords]
            if require_all:
                return all(matches)
            return any(matches)

        keyword_str = ", ".join(keywords[:3])
        if len(keywords) > 3:
            keyword_str += f", and {len(keywords) - 3} more"
        mode = "all" if require_all else "at least one of"
        description = f"Contains {mode}: {keyword_str}"

        self.add_constraint("keywords", description, check_keywords)

    def add_length_constraint(
        self,
        min_chars: Optional[int] = None,
        max_chars: Optional[int] = None,
    ) -> None:
        """Add a character length constraint.

        Args:
            min_chars: Minimum allowed character count
            max_chars: Maximum allowed character count
        """
        def check_length(response: str) -> bool:
            length = len(response)
            if min_chars is not None and length < min_chars:
                return False
            if max_chars is not None and length > max_chars:
                return False
            return True

        desc = []
        if min_chars:
            desc.append(f"≥{min_chars} chars")
        if max_chars:
            desc.append(f"≤{max_chars} chars")
        description = f"Length: {', '.join(desc)}"

        self.add_constraint("length", description, check_length)

    async def score(
        self,
        response: str,
        instructions: Optional[str] = None,
    ) -> dict:
        """Score instruction following.

        Args:
            response: The response to evaluate
            instructions: Optional natural language instruction to check semantically

        Returns:
            Dict with overall_score, per_constraint_scores, and details
        """
        constraint_results = {}
        for name, constraint in self.constraints.items():
            try:
                passed = constraint.check_fn(response)
                constraint_results[name] = {
                    "passed": passed,
                    "description": constraint.description,
                }
            except Exception as e:
                constraint_results[name] = {
                    "passed": False,
                    "description": constraint.description,
                    "error": str(e),
                }

        semantic_score = 1.0
        if instructions:
            semantic_score = await self._check_semantic_instruction(response, instructions)
            constraint_results["semantic"] = {
                "passed": semantic_score >= 0.8,
                "description": f"Follows: {instructions[:50]}...",
                "score": semantic_score,
            }

        # Calculate overall score
        total_constraints = len(constraint_results)
        if total_constraints == 0:
            overall_score = 1.0
        else:
            passed_count = sum(1 for r in constraint_results.values() if r.get("passed", False))
            overall_score = passed_count / total_constraints

        return {
            "overall_score": overall_score,
            "num_constraints": len(self.constraints),
            "num_passed": sum(1 for r in constraint_results.values() if r.get("passed")),
            "constraint_results": constraint_results,
        }

    async def _check_semantic_instruction(self, response: str, instruction: str) -> float:
        """Check semantic compliance with an instruction using LLM.

        Args:
            response: The response to check
            instruction: The instruction to check against

        Returns:
            Score between 0 and 1
        """
        from llm_eval_framework.utils.llm_client import UnifiedLLMClient

        client = UnifiedLLMClient(model=self.model)
        prompt = f"""Does the following response follow the given instruction?

Instruction:
{instruction}

Response:
{response}

Rate compliance on a scale of 0-1 where:
- 0: Does not follow the instruction at all
- 1: Perfectly follows the instruction

Respond with ONLY a single number between 0 and 1."""

        try:
            response_text = await client.acompletion(prompt=prompt, temperature=0.0)
            match = re.search(r'0\.\d+|1\.0|1\.00|0', response_text)
            if match:
                return float(match.group())
        except Exception:
            pass

        return 0.5

    def __repr__(self) -> str:
        """String representation of the scorer."""
        return f"InstructionFollowingScorer(constraints={len(self.constraints)})"
