"""Contamination detector: Identify test set contamination in model training data."""

from collections import Counter
from typing import Optional

import numpy as np


class ContaminationDetector:
    """Detects potential test set contamination using n-gram overlap analysis."""

    def __init__(self, n_grams: int = 13, overlap_threshold: float = 0.8):
        """Initialize the contamination detector.

        Args:
            n_grams: Size of n-grams for overlap detection
            overlap_threshold: Threshold for flagging contamination (0-1)
        """
        self.n_grams = n_grams
        self.overlap_threshold = overlap_threshold

    def _extract_ngrams(self, text: str) -> set[str]:
        """Extract n-grams from text.

        Args:
            text: Text to extract n-grams from

        Returns:
            Set of n-grams (as strings)
        """
        # Normalize text
        text = text.lower().strip()

        # Split into words
        words = text.split()

        if len(words) < self.n_grams:
            return {" ".join(words)}

        ngrams = set()
        for i in range(len(words) - self.n_grams + 1):
            ngram = " ".join(words[i : i + self.n_grams])
            ngrams.add(ngram)

        return ngrams

    def compute_overlap(self, test_text: str, reference_text: str) -> float:
        """Compute n-gram overlap between test and reference text.

        Args:
            test_text: Test set text
            reference_text: Reference (training) data text

        Returns:
            Overlap score between 0 and 1
        """
        test_ngrams = self._extract_ngrams(test_text)
        ref_ngrams = self._extract_ngrams(reference_text)

        if not test_ngrams or not ref_ngrams:
            return 0.0

        overlap = len(test_ngrams & ref_ngrams)
        return overlap / len(test_ngrams) if test_ngrams else 0.0

    def check_contamination(
        self,
        test_examples: list[str],
        reference_samples: list[str],
    ) -> dict:
        """Check for contamination between test set and reference data.

        Args:
            test_examples: List of test set examples
            reference_samples: List of reference (training) samples

        Returns:
            Dict with contamination results and statistics
        """
        results = []
        overlap_scores = []

        for i, test_text in enumerate(test_examples):
            max_overlap = 0.0
            most_similar_ref = None

            for ref_text in reference_samples:
                overlap = self.compute_overlap(test_text, ref_text)
                overlap_scores.append(overlap)

                if overlap > max_overlap:
                    max_overlap = overlap
                    most_similar_ref = ref_text[:100]  # Truncate for storage

            is_contaminated = max_overlap >= self.overlap_threshold

            results.append({
                "test_index": i,
                "max_overlap": float(max_overlap),
                "is_contaminated": is_contaminated,
                "most_similar_ref": most_similar_ref,
            })

        # Compute statistics
        overlap_array = np.array(overlap_scores) if overlap_scores else np.array([])

        contaminated_count = sum(1 for r in results if r["is_contaminated"])

        stats = {
            "total_tests": len(test_examples),
            "contaminated_count": contaminated_count,
            "contamination_rate": contaminated_count / len(test_examples) if test_examples else 0.0,
            "mean_overlap": float(np.mean(overlap_array)) if len(overlap_array) > 0 else 0.0,
            "max_overlap": float(np.max(overlap_array)) if len(overlap_array) > 0 else 0.0,
            "min_overlap": float(np.min(overlap_array)) if len(overlap_array) > 0 else 0.0,
            "std_overlap": float(np.std(overlap_array)) if len(overlap_array) > 0 else 0.0,
        }

        return {
            "results": results,
            "statistics": stats,
            "threshold": self.overlap_threshold,
        }

    def check_canary_strings(
        self,
        model_output: str,
        canary_strings: list[str],
    ) -> dict:
        """Check if model output contains known canary strings.

        Canary strings are unique strings inserted into training data to detect leakage.

        Args:
            model_output: Output from the model
            canary_strings: List of known canary strings

        Returns:
            Dict with canary detection results
        """
        output_lower = model_output.lower()
        found_canaries = []
        found_count = 0

        for canary in canary_strings:
            canary_lower = canary.lower()
            if canary_lower in output_lower:
                found_canaries.append(canary)
                found_count += 1

        return {
            "contains_canaries": found_count > 0,
            "canaries_found": found_canaries,
            "count": found_count,
            "total_canaries_checked": len(canary_strings),
        }

    def flag_contaminated_examples(
        self,
        test_examples: list[str],
        reference_samples: list[str],
    ) -> list[int]:
        """Return indices of contaminated examples.

        Args:
            test_examples: List of test examples
            reference_samples: List of reference samples

        Returns:
            List of indices of contaminated examples
        """
        results = self.check_contamination(test_examples, reference_samples)

        contaminated_indices = [
            r["test_index"]
            for r in results["results"]
            if r["is_contaminated"]
        ]

        return contaminated_indices

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ContaminationDetector("
            f"n_grams={self.n_grams}, "
            f"threshold={self.overlap_threshold})"
        )
