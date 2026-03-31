"""Faithfulness metric: Measure if response is faithful to provided context."""

import json
import re
from typing import Optional

from pydantic import BaseModel, Field


class FaithfulnessScorer:
    """Scores response faithfulness relative to provided context.

    Uses a claim extraction and verification approach: extracts claims from
    the response and checks if they can be verified against the context.
    """

    def __init__(self, model: str = "gpt-3.5-turbo"):
        """Initialize the faithfulness scorer.

        Args:
            model: LLM model to use for claim extraction and verification
        """
        self.model = model

    async def score(
        self,
        response: str,
        context: str,
    ) -> dict:
        """Score the faithfulness of a response relative to context.

        Args:
            response: The response to evaluate
            context: The reference context the response should be faithful to

        Returns:
            Dict with overall_score, verified_claims, unverifiable_claims, and details
        """
        claims = await self._extract_claims(response)
        if not claims:
            return {
                "overall_score": 1.0,
                "num_claims": 0,
                "verified_claims": [],
                "unverifiable_claims": [],
                "details": "No claims found in response",
            }

        verified, unverifiable = await self._verify_claims(claims, context)

        score = len(verified) / len(claims) if claims else 1.0
        score = max(0.0, min(1.0, score))

        return {
            "overall_score": score,
            "num_claims": len(claims),
            "num_verified": len(verified),
            "num_unverifiable": len(unverifiable),
            "verified_claims": verified,
            "unverifiable_claims": unverifiable,
            "faithfulness_ratio": f"{len(verified)}/{len(claims)}",
        }

    async def _extract_claims(self, response: str) -> list[str]:
        """Extract factual claims from the response.

        Args:
            response: The response to extract claims from

        Returns:
            List of extracted claims
        """
        from llm_eval_framework.utils.llm_client import UnifiedLLMClient

        client = UnifiedLLMClient(model=self.model)
        prompt = f"""Extract all factual claims from the following response. A claim is a statement that can be verified or falsified.

Response:
{response}

Provide your extraction in JSON format:
{{
    "claims": ["claim 1", "claim 2", ...]
}}

Respond with ONLY the JSON object."""

        try:
            raw_response = await client.acompletion(prompt=prompt, temperature=0.0)
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("claims", [])
        except Exception:
            pass

        return []

    async def _verify_claims(self, claims: list[str], context: str) -> tuple[list[str], list[str]]:
        """Verify claims against the provided context.

        Args:
            claims: List of claims to verify
            context: Reference context to verify against

        Returns:
            Tuple of (verified_claims, unverifiable_claims)
        """
        from llm_eval_framework.utils.llm_client import UnifiedLLMClient

        client = UnifiedLLMClient(model=self.model)
        claims_text = "\n".join(f"{i+1}. {claim}" for i, claim in enumerate(claims))

        prompt = f"""Given the following context, verify each claim. A claim is verifiable if it can be confirmed from the context.

Context:
{context}

Claims to verify:
{claims_text}

Provide your verification in JSON format:
{{
    "verifications": [
        {{"claim": "claim text", "verifiable": true/false, "reasoning": "brief explanation"}},
        ...
    ]
}}

Respond with ONLY the JSON object."""

        verified = []
        unverifiable = []

        try:
            raw_response = await client.acompletion(prompt=prompt, temperature=0.0)
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                for verification in data.get("verifications", []):
                    claim = verification.get("claim", "")
                    is_verifiable = verification.get("verifiable", False)
                    if is_verifiable:
                        verified.append(claim)
                    else:
                        unverifiable.append(claim)
        except Exception:
            unverifiable = claims

        return verified, unverifiable

    def __repr__(self) -> str:
        """String representation of the scorer."""
        return f"FaithfulnessScorer(model={self.model})"
