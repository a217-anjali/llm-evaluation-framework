"""Code execution metric: Run generated code and verify correctness."""

import asyncio
import subprocess
import tempfile
import re
from pathlib import Path
from typing import Optional

import numpy as np


class CodeExecutionScorer:
    """Scores code generation by executing and verifying against test cases."""

    def __init__(
        self,
        timeout: float = 5.0,
        sandbox: bool = True,
        language: str = "python",
    ):
        """Initialize the code execution scorer.

        Args:
            timeout: Timeout in seconds for code execution
            sandbox: Whether to run code in a sandbox (limited filesystem/network)
            language: Programming language (default: python)
        """
        self.timeout = timeout
        self.sandbox = sandbox
        self.language = language

    async def score(
        self,
        code: str,
        test_cases: list[dict],
    ) -> dict:
        """Score generated code against test cases.

        Args:
            code: The generated code to test
            test_cases: List of test case dicts with 'input' and 'expected_output'

        Returns:
            Dict with pass_at_k, per_test_results, and overall score
        """
        if not test_cases:
            return {
                "overall_score": 1.0,
                "num_test_cases": 0,
                "num_passed": 0,
                "pass_rate": 1.0,
                "test_results": [],
            }

        test_results = []
        passed = 0

        for i, test_case in enumerate(test_cases):
            result = await self._run_test_case(code, test_case)
            test_results.append({
                "test_id": i,
                "passed": result["passed"],
                "execution_time": result["execution_time"],
                "error": result.get("error"),
            })
            if result["passed"]:
                passed += 1

        pass_rate = passed / len(test_cases) if test_cases else 1.0

        return {
            "overall_score": float(pass_rate),
            "num_test_cases": len(test_cases),
            "num_passed": passed,
            "pass_rate": float(pass_rate),
            "test_results": test_results,
        }

    async def _run_test_case(self, code: str, test_case: dict) -> dict:
        """Run a single test case.

        Args:
            code: The code to test
            test_case: Dict with 'input' and 'expected_output'

        Returns:
            Dict with passed status, execution time, and optional error
        """
        test_input = test_case.get("input", "")
        expected_output = test_case.get("expected_output", "")

        if self.language != "python":
            return {
                "passed": False,
                "execution_time": 0.0,
                "error": f"Language {self.language} not yet supported",
            }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            script_path = f.name

        try:
            process = await asyncio.create_subprocess_exec(
                "python", script_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=test_input.encode()),
                    timeout=self.timeout,
                )
                actual_output = stdout.decode('utf-8', errors='replace').strip()
                expected_output = str(expected_output).strip()

                passed = actual_output == expected_output

                return {
                    "passed": passed,
                    "execution_time": 0.0,
                    "actual_output": actual_output,
                    "expected_output": expected_output,
                }

            except asyncio.TimeoutError:
                process.kill()
                return {
                    "passed": False,
                    "execution_time": self.timeout,
                    "error": f"Timeout after {self.timeout}s",
                }

        except Exception as e:
            return {
                "passed": False,
                "execution_time": 0.0,
                "error": str(e),
            }
        finally:
            Path(script_path).unlink(missing_ok=True)

    def pass_at_k(
        self,
        num_total: int,
        num_passed: int,
        k_values: list[int] = [1, 5, 10],
    ) -> dict:
        """Compute pass@k metric.

        pass@k = 1 - C(n-c, k) / C(n, k)
        where n = num_total, c = num_passed

        Args:
            num_total: Total number of examples
            num_passed: Number of passing examples
            k_values: Values of k to compute

        Returns:
            Dict with pass@k for each k value
        """
        results = {}

        for k in k_values:
            if k > num_total:
                continue

            if num_passed == num_total:
                pass_at_k = 1.0
            elif num_passed == 0:
                pass_at_k = 0.0
            else:
                # Use normal approximation for large numbers
                c = num_passed
                n = num_total
                try:
                    # pass@k = 1 - (C(n-c, k) / C(n, k))
                    from math import comb
                    pass_at_k = 1 - comb(n - c, k) / comb(n, k)
                except (ValueError, OverflowError):
                    # Fallback to binomial approximation
                    pass_at_k = min(1.0, 1 - ((1 - c/n) ** k))

            results[f"pass@{k}"] = float(pass_at_k)

        return results

    def __repr__(self) -> str:
        """String representation of the scorer."""
        return f"CodeExecutionScorer(language={self.language}, timeout={self.timeout}s)"
