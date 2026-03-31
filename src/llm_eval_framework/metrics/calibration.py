"""Calibration metrics: Expected Calibration Error and Brier Score."""

from typing import Optional

import numpy as np


class CalibrationMetrics:
    """Computes calibration metrics for model confidence and accuracy alignment."""

    @staticmethod
    def expected_calibration_error(
        predictions: list[float],
        labels: list[int],
        num_bins: int = 10,
    ) -> dict:
        """Compute Expected Calibration Error (ECE).

        ECE measures the difference between predicted confidence and actual accuracy.
        A model is well-calibrated when high confidence predictions are indeed correct.

        Args:
            predictions: List of predicted probabilities [0, 1]
            labels: List of binary labels (0 or 1)
            num_bins: Number of bins for confidence binning (default: 10)

        Returns:
            Dict with ece_score, bin_statistics, and visualization data
        """
        predictions = np.array(predictions)
        labels = np.array(labels)

        if len(predictions) != len(labels):
            raise ValueError("predictions and labels must have same length")

        if not all(0 <= p <= 1 for p in predictions):
            raise ValueError("predictions must be between 0 and 1")

        bin_boundaries = np.linspace(0, 1, num_bins + 1)
        bin_width = 1 / num_bins

        ece = 0.0
        bin_stats = []

        for i in range(num_bins):
            lower = bin_boundaries[i]
            upper = bin_boundaries[i + 1]

            # Get samples in this bin
            in_bin = (predictions >= lower) & (predictions <= upper)
            if i == num_bins - 1:  # Include 1.0 in last bin
                in_bin = (predictions >= lower) & (predictions <= upper)

            if not np.any(in_bin):
                continue

            bin_preds = predictions[in_bin]
            bin_labels = labels[in_bin]

            bin_confidence = np.mean(bin_preds)
            bin_accuracy = np.mean(bin_labels)
            bin_count = np.sum(in_bin)

            calibration_gap = abs(bin_confidence - bin_accuracy)
            ece += calibration_gap * (bin_count / len(predictions))

            bin_stats.append({
                "bin": f"[{lower:.2f}, {upper:.2f})",
                "confidence": float(bin_confidence),
                "accuracy": float(bin_accuracy),
                "count": int(bin_count),
                "calibration_gap": float(calibration_gap),
            })

        return {
            "ece_score": float(ece),
            "num_bins": num_bins,
            "bin_statistics": bin_stats,
            "interpretation": "Perfect calibration: 0, Poor calibration: 1",
        }

    @staticmethod
    def brier_score(predictions: list[float], labels: list[int]) -> dict:
        """Compute Brier Score.

        Brier Score measures the mean squared difference between predicted
        probabilities and actual outcomes.

        Args:
            predictions: List of predicted probabilities [0, 1]
            labels: List of binary labels (0 or 1)

        Returns:
            Dict with brier_score, mse, and interpretation
        """
        predictions = np.array(predictions)
        labels = np.array(labels)

        if len(predictions) != len(labels):
            raise ValueError("predictions and labels must have same length")

        if not all(0 <= p <= 1 for p in predictions):
            raise ValueError("predictions must be between 0 and 1")

        if not all(l in [0, 1] for l in labels):
            raise ValueError("labels must be binary (0 or 1)")

        brier = np.mean((predictions - labels) ** 2)

        return {
            "brier_score": float(brier),
            "range": [0, 1],
            "interpretation": "Lower is better, 0 = perfect, 0.25 = random guessing",
        }

    @staticmethod
    def confidence_accuracy_correlation(
        predictions: list[float],
        labels: list[int],
    ) -> dict:
        """Compute correlation between confidence and accuracy.

        Args:
            predictions: List of predicted probabilities [0, 1]
            labels: List of binary labels (0 or 1)

        Returns:
            Dict with pearson_r, p_value, and trend
        """
        from scipy import stats

        predictions = np.array(predictions)
        labels = np.array(labels)

        if len(predictions) < 3:
            raise ValueError("Need at least 3 samples for correlation")

        # Compute per-sample accuracy (1 if correct, 0 if incorrect)
        correct = (predictions > 0.5) == labels

        # Pearson correlation between prediction confidence and correctness
        r, p_value = stats.pearsonr(predictions, correct.astype(int))

        return {
            "pearson_r": float(r),
            "p_value": float(p_value),
            "significant": p_value < 0.05,
            "interpretation": "Positive r: higher confidence → higher accuracy",
        }

    @staticmethod
    def calibration_plot_data(
        predictions: list[float],
        labels: list[int],
        num_bins: int = 10,
    ) -> dict:
        """Generate data for calibration plot visualization.

        Args:
            predictions: List of predicted probabilities [0, 1]
            labels: List of binary labels (0 or 1)
            num_bins: Number of bins for the plot

        Returns:
            Dict with points for plotting a calibration curve
        """
        predictions = np.array(predictions)
        labels = np.array(labels)

        bin_boundaries = np.linspace(0, 1, num_bins + 1)

        confidences = []
        accuracies = []
        counts = []

        for i in range(num_bins):
            lower = bin_boundaries[i]
            upper = bin_boundaries[i + 1]

            in_bin = (predictions >= lower) & (predictions <= upper)
            if i == num_bins - 1:
                in_bin = (predictions >= lower) & (predictions <= upper)

            if not np.any(in_bin):
                continue

            bin_preds = predictions[in_bin]
            bin_labels = labels[in_bin]

            confidences.append(float(np.mean(bin_preds)))
            accuracies.append(float(np.mean(bin_labels)))
            counts.append(int(np.sum(in_bin)))

        return {
            "confidences": confidences,
            "accuracies": accuracies,
            "counts": counts,
            "perfect_calibration": [0, 1],
            "num_bins": num_bins,
        }

    def __repr__(self) -> str:
        """String representation."""
        return "CalibrationMetrics"
