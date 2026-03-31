"""Unified LLM client wrapping LiteLLM for consistent API access."""

import asyncio
import json
import logging
import re
from typing import Any, Optional

import litellm

logger = logging.getLogger(__name__)


class UnifiedLLMClient:
    """Unified client for accessing multiple LLM providers through LiteLLM."""

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        """Initialize the LLM client.

        Args:
            model: Model identifier (e.g., 'gpt-4', 'claude-3-opus')
            api_key: Optional API key (uses env var if not provided)
            api_base: Optional API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.timeout = timeout
        self.max_retries = max_retries

        if api_key:
            litellm.api_key = api_key
        if api_base:
            litellm.api_base = api_base

    async def acompletion(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
        **kwargs,
    ) -> str:
        """Call the LLM asynchronously.

        Args:
            prompt: The prompt to send
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            json_mode: If True, request JSON output
            **kwargs: Additional parameters for litellm

        Returns:
            The model's response text

        Raises:
            Exception: If request fails after retries
        """
        for attempt in range(self.max_retries):
            try:
                # Build messages
                messages = [{"role": "user", "content": prompt}]

                # Set up request parameters
                kwargs.update({
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "timeout": self.timeout,
                })

                if max_tokens:
                    kwargs["max_tokens"] = max_tokens

                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}

                # Use asyncio to run the async call
                response = await asyncio.to_thread(
                    lambda: litellm.completion(**kwargs)
                )

                # Extract response text
                if hasattr(response, 'choices') and response.choices:
                    return response.choices[0].message.content
                else:
                    return str(response)

            except Exception as e:
                logger.warning(
                    f"LLM call attempt {attempt + 1}/{self.max_retries} failed: {e}"
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise RuntimeError(
                        f"LLM call failed after {self.max_retries} attempts: {e}"
                    ) from e

        raise RuntimeError("Unexpected error in acompletion")

    def completion(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        json_mode: bool = False,
        **kwargs,
    ) -> str:
        """Call the LLM synchronously.

        Args:
            prompt: The prompt to send
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            json_mode: If True, request JSON output
            **kwargs: Additional parameters

        Returns:
            The model's response text
        """
        for attempt in range(self.max_retries):
            try:
                messages = [{"role": "user", "content": prompt}]

                kwargs.update({
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "timeout": self.timeout,
                })

                if max_tokens:
                    kwargs["max_tokens"] = max_tokens

                if json_mode:
                    kwargs["response_format"] = {"type": "json_object"}

                response = litellm.completion(**kwargs)

                if hasattr(response, 'choices') and response.choices:
                    return response.choices[0].message.content
                else:
                    return str(response)

            except Exception as e:
                logger.warning(
                    f"LLM call attempt {attempt + 1}/{self.max_retries} failed: {e}"
                )
                if attempt < self.max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)
                else:
                    raise RuntimeError(
                        f"LLM call failed after {self.max_retries} attempts: {e}"
                    ) from e

        raise RuntimeError("Unexpected error in completion")

    async def parse_json(self, prompt: str, **kwargs) -> dict:
        """Get JSON output from the LLM.

        Args:
            prompt: The prompt to send
            **kwargs: Additional parameters

        Returns:
            Parsed JSON dict

        Raises:
            ValueError: If response is not valid JSON
        """
        response = await self.acompletion(prompt, json_mode=True, **kwargs)

        # Try to extract JSON from the response
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        raise ValueError(f"Could not parse JSON from response: {response}")

    def count_tokens(self, text: str) -> int:
        """Estimate token count for text.

        Args:
            text: Text to count tokens for

        Returns:
            Approximate token count
        """
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(self.model)
            return len(encoding.encode(text))
        except Exception:
            # Fallback: ~4 characters per token
            return len(text) // 4

    def __repr__(self) -> str:
        """String representation."""
        return f"UnifiedLLMClient(model={self.model})"
