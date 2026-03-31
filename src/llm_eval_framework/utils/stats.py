"""Statistical utilities for evaluation analysis."""

from typing import Optional

import numpy as np
from scipy import stats


def bootstrap_ci(
    data: list[float],
    ci: float = 0.95,
    n_bootstrap: int = 1000,
    statistic_fn=None,
) -> dict:
    """Compute bootstrap confidence intervals.

    Args:
        data: List of values to bootstrap
        ci: Confidence interval level (e.g., 0.95 for 95%)
        n_bootstrap: Number of bootstrap samples
        statistic_fn: Function to compute statistic (default: mean)

    Returns:
        Dict with ci_lower, ci_upper, point_estimate, and bootstrap_samples
    """
    if statistic_fn is None:
        statistic_fn = np.mean

    data = np.array(data)
    point_estimate = statistic_fn(data)

    bootstrap_statistics = []
    np.random.seed(42)

    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_statistics.append(statistic_fn(sample))

    bootstrap_statistics = np.array(bootstrap_statistics)

    alpha = 1 - ci
    ci_lower = np.percentile(bootstrap_statistics, alpha / 2 * 100)
    ci_upper = np.percentile(bootstrap_statistics, (1 - alpha / 2) * 100)

    return {
        "point_estimate": float(point_estimate),
        "ci_lower": float(ci_lower),
        "ci_upper": float(ci_upper),
        "ci_level": ci,
        "n_bootstrap": n_bootstrap,
    }


def paired_permutation_test(
    group_a: list[float],
    group_b: list[float],
    n_permutations: int = 10000,
) -> dict:
    """Conduct a paired permutation test for significance.

    Tests if two paired groups have significantly different means.

    Args:
        group_a: First group of values
        group_b: Second group of values (same length as group_a)
        n_permutations: Number of permutation samples

    Returns:
        Dict with p_value, observed_diff, and test_results
    """
    group_a = np.array(group_a)
    group_b = np.array(group_b)

    if len(group_a) != len(group_b):
        raise ValueError("Groups must have equal length for paired test")

    observed_diff = np.mean(group_a) - np.mean(group_b)
    differences = group_a - group_b

    permutation_diffs = []
    np.random.seed(42)

    for _ in range(n_permutations):
        signs = np.random.choice([-1, 1], size=len(differences))
        perm_diff = np.mean(differences * signs)
        permutation_diffs.append(perm_diff)

    permutation_diffs = np.array(permutation_diffs)

    p_value = np.mean(np.abs(permutation_diffs) >= np.abs(observed_diff))

    return {
        "p_value": float(p_value),
        "observed_difference": float(observed_diff),
        "significant_at_0.05": p_value < 0.05,
        "significant_at_0.01": p_value < 0.01,
        "n_permutations": n_permutations,
    }


def cohens_d(group_a: list[float], group_b: list[float]) -> float:
    """Compute Cohen's d effect size.

    Args:
        group_a: First group
        group_b: Second group

    Returns:
        Cohen's d (standardized mean difference)
    """
    group_a = np.array(group_a)
    group_b = np.array(group_b)

    mean_a = np.mean(group_a)
    mean_b = np.mean(group_b)

    var_a = np.var(group_a, ddof=1)
    var_b = np.var(group_b, ddof=1)

    n_a = len(group_a)
    n_b = len(group_b)

    pooled_std = np.sqrt(((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2))

    if pooled_std == 0:
        return 0.0

    d = (mean_a - mean_b) / pooled_std
    return float(d)


def cliffs_delta(group_a: list[float], group_b: list[float]) -> float:
    """Compute Cliff's delta non-parametric effect size.

    Args:
        group_a: First group
        group_b: Second group

    Returns:
        Cliff's delta (-1 to 1)
    """
    group_a = np.array(group_a)
    group_b = np.array(group_b)

    dominance_sum = 0

    for a in group_a:
        for b in group_b:
            if a > b:
                dominance_sum += 1
            elif a < b:
                dominance_sum -= 1

    n_a = len(group_a)
    n_b = len(group_b)

    delta = dominance_sum / (n_a * n_b)
    return float(delta)


def holm_bonferroni(p_values: list[float], alpha: float = 0.05) -> dict:
    """Apply Holm-Bonferroni correction for multiple comparisons.

    Args:
        p_values: List of p-values
        alpha: Significance level

    Returns:
        Dict with corrected results
    """
    p_values = np.array(p_values)
    n = len(p_values)

    # Sort p-values and track original indices
    sorted_indices = np.argsort(p_values)
    sorted_p = p_values[sorted_indices]

    # Apply Holm correction: compare p_i to alpha / (n - i + 1)
    thresholds = alpha / np.arange(n, 0, -1)
    rejected = sorted_p < thresholds

    results = {
        "corrected_results": [],
        "num_rejected": int(np.sum(rejected)),
        "alpha": alpha,
    }

    for i, orig_idx in enumerate(sorted_indices):
        results["corrected_results"].append({
            "original_index": int(orig_idx),
            "p_value": float(sorted_p[i]),
            "threshold": float(thresholds[i]),
            "rejected": bool(rejected[i]),
        })

    return results


def ttest_independent(
    group_a: list[float],
    group_b: list[float],
) -> dict:
    """Conduct independent samples t-test.

    Args:
        group_a: First group
        group_b: Second group

    Returns:
        Dict with t_statistic, p_value, and significance
    """
    t_stat, p_value = stats.ttest_ind(group_a, group_b)

    return {
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "significant_at_0.05": p_value < 0.05,
        "significant_at_0.01": p_value < 0.01,
        "cohens_d": cohens_d(group_a, group_b),
    }


def mann_whitney_u(group_a: list[float], group_b: list[float]) -> dict:
    """Conduct Mann-Whitney U non-parametric test.

    Args:
        group_a: First group
        group_b: Second group

    Returns:
        Dict with u_statistic, p_value, and significance
    """
    u_stat, p_value = stats.mannwhitneyu(group_a, group_b, alternative='two-sided')

    return {
        "u_statistic": float(u_stat),
        "p_value": float(p_value),
        "significant_at_0.05": p_value < 0.05,
        "significant_at_0.01": p_value < 0.01,
        "cliffs_delta": cliffs_delta(group_a, group_b),
    }
