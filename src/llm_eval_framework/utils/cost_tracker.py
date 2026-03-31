"""Cost tracking for API usage and evaluation budget management."""

from typing import Optional

try:
    import tiktoken
except ImportError:
    tiktoken = None


class CostTracker:
    """Tracks API costs for model evaluations."""

    # Token prices (in USD per 1K tokens)
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    }

    def __init__(self, budget_usd: Optional[float] = None):
        """Initialize the cost tracker.

        Args:
            budget_usd: Optional budget limit in USD
        """
        self.budget_usd = budget_usd
        self.usage: dict[str, dict] = {}
        self.total_cost = 0.0

    def add_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Record API usage for a model call.

        Args:
            model: Model name (e.g., 'gpt-4')
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost for this call in USD

        Raises:
            ValueError: If budget exceeded or model pricing unknown
        """
        if model not in self.PRICING:
            raise ValueError(f"Unknown model: {model}. Known models: {list(self.PRICING.keys())}")

        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        call_cost = input_cost + output_cost

        # Track usage per model
        if model not in self.usage:
            self.usage[model] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "calls": 0,
                "cost": 0.0,
            }

        self.usage[model]["input_tokens"] += input_tokens
        self.usage[model]["output_tokens"] += output_tokens
        self.usage[model]["calls"] += 1
        self.usage[model]["cost"] += call_cost

        self.total_cost += call_cost

        # Check budget
        if self.budget_usd is not None and self.total_cost > self.budget_usd:
            raise ValueError(
                f"Budget exceeded: ${self.total_cost:.4f} > ${self.budget_usd:.4f}"
            )

        return call_cost

    def estimate_cost(self, model: str, text: str, is_output: bool = False) -> float:
        """Estimate cost for a given text.

        Args:
            model: Model name
            text: Text to estimate cost for
            is_output: If True, treat as output tokens; if False, as input

        Returns:
            Estimated cost in USD
        """
        if not tiktoken:
            # Fallback: ~4 characters per token
            tokens = len(text) // 4
        else:
            try:
                encoding = tiktoken.encoding_for_model(model)
                tokens = len(encoding.encode(text))
            except Exception:
                tokens = len(text) // 4

        if model not in self.PRICING:
            raise ValueError(f"Unknown model: {model}")

        pricing = self.PRICING[model]
        token_type = "output" if is_output else "input"
        cost = (tokens / 1000) * pricing[token_type]

        return float(cost)

    def get_summary(self) -> dict:
        """Get usage summary.

        Returns:
            Dict with usage statistics
        """
        total_input = sum(u["input_tokens"] for u in self.usage.values())
        total_output = sum(u["output_tokens"] for u in self.usage.values())
        total_calls = sum(u["calls"] for u in self.usage.values())

        summary = {
            "total_cost": float(self.total_cost),
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_calls": total_calls,
            "models": self.usage,
            "budget_remaining": (
                float(self.budget_usd - self.total_cost)
                if self.budget_usd
                else None
            ),
        }

        if self.budget_usd:
            summary["budget_used_percentage"] = (
                (self.total_cost / self.budget_usd) * 100
            )

        return summary

    def check_budget(self) -> bool:
        """Check if within budget.

        Returns:
            True if within budget, False if exceeded
        """
        if self.budget_usd is None:
            return True
        return self.total_cost <= self.budget_usd

    def get_cost_per_call(self, model: str) -> float:
        """Get average cost per call for a model.

        Args:
            model: Model name

        Returns:
            Average cost per call in USD
        """
        if model not in self.usage:
            return 0.0

        calls = self.usage[model]["calls"]
        if calls == 0:
            return 0.0

        return self.usage[model]["cost"] / calls

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"CostTracker(total_cost=${self.total_cost:.4f}, "
            f"models={list(self.usage.keys())})"
        )
