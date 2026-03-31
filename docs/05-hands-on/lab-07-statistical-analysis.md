# Lab 07: Statistical Analysis of Evaluation Results

**Difficulty:** Yellow (Intermediate)
**Duration:** 60 minutes
**Tools:** Python 3.10+, scipy, numpy, matplotlib, plotly
**Prerequisites:** Lab 01-03, basic statistics knowledge

## Overview

This lab teaches rigorous statistical analysis of evaluation results across multiple models. You will load evaluation results from 5 LLM models, compute bootstrap 95% confidence intervals, conduct paired permutation tests, calculate effect sizes using Cohen's d, apply multiple comparison correction, and create publication-quality visualizations.

## Learning Objectives

By the end of this lab, you will:

1. **Load and organize evaluation data** from multiple models
2. **Compute robust confidence intervals** using bootstrap resampling
3. **Conduct hypothesis tests** with appropriate corrections
4. **Calculate effect sizes** to quantify practical significance
5. **Create professional visualizations** suitable for reports and publications
6. **Interpret results** in business context

## Part 1: Load Evaluation Results and Setup

Create the analysis environment:

```python
# statistical_analysis_setup.py
"""
Setup for statistical analysis of evaluation results.
Load data from 5 models and organize for analysis.
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
import warnings

warnings.filterwarnings('ignore')

@dataclass
class ModelResults:
    name: str
    scores: np.ndarray
    model_id: str
    test_date: str
    eval_framework: str

def load_evaluation_results(results_dir: str = "./eval_results") -> Dict[str, ModelResults]:
    """
    Load evaluation results from 5 models.

    Expected file structure:
    eval_results/
      - gpt-4o_results.json
      - claude-sonnet-4.6_results.json
      - gemini-3-flash_results.json
      - qwen-3.5-9b_results.json
      - llama-4-scout_results.json
    """

    models = {
        "GPT-4o": "gpt-4o",
        "Claude-Sonnet-4.6": "claude-sonnet",
        "Gemini-3-Flash": "gemini-3-flash",
        "Qwen-3.5-9B": "qwen-3.5",
        "Llama-4-Scout": "llama-4-scout"
    }

    results = {}

    for model_name, file_prefix in models.items():
        # Simulate loading (in production, load actual JSON files)
        file_path = Path(results_dir) / f"{file_prefix}_results.json"

        # Generate representative scores for demonstration
        np.random.seed(hash(model_name) % 2**32)
        if "GPT-4o" in model_name:
            scores = np.random.normal(78, 8, 50)
        elif "Claude" in model_name:
            scores = np.random.normal(82, 7, 50)
        elif "Gemini" in model_name:
            scores = np.random.normal(75, 9, 50)
        elif "Qwen" in model_name:
            scores = np.random.normal(72, 10, 50)
        else:  # Llama
            scores = np.random.normal(68, 11, 50)

        scores = np.clip(scores, 0, 100)

        results[model_name] = ModelResults(
            name=model_name,
            scores=scores,
            model_id=f"model_{file_prefix}",
            test_date="2026-03-31",
            eval_framework="llm_eval_framework_v2"
        )

    return results

def create_analysis_dataframe(results: Dict[str, ModelResults]) -> pd.DataFrame:
    """Convert results to pandas DataFrame for analysis."""

    data = []
    for model_name, model_results in results.items():
        for idx, score in enumerate(model_results.scores):
            data.append({
                'model': model_name,
                'test_case': idx,
                'score': score
            })

    df = pd.DataFrame(data)
    return df

def compute_descriptive_statistics(results: Dict[str, ModelResults]) -> pd.DataFrame:
    """Compute basic statistics for each model."""

    stats_data = []
    for model_name, model_results in results.items():
        scores = model_results.scores
        stats_data.append({
            'Model': model_name,
            'N': len(scores),
            'Mean': np.mean(scores),
            'Median': np.median(scores),
            'Std Dev': np.std(scores),
            'Min': np.min(scores),
            'Max': np.max(scores),
            'Q1': np.percentile(scores, 25),
            'Q3': np.percentile(scores, 75)
        })

    return pd.DataFrame(stats_data)

if __name__ == "__main__":
    results = load_evaluation_results()
    df = create_analysis_dataframe(results)
    stats_df = compute_descriptive_statistics(results)

    print("EVALUATION RESULTS LOADED")
    print("=" * 70)
    print(f"\nModels: {', '.join(results.keys())}")
    print(f"Total evaluation records: {len(df)}")
    print("\nDescriptive Statistics:\n")
    print(stats_df.to_string(index=False))
```

## Part 2: Bootstrap Confidence Intervals

Compute robust 95% confidence intervals:

```python
# bootstrap_ci.py
"""
Bootstrap confidence interval estimation for evaluation metrics.
"""

import numpy as np
from typing import Dict, Tuple, List
import pandas as pd

class BootstrapCI:
    """Compute bootstrap confidence intervals for model performance metrics."""

    def __init__(self, confidence: float = 0.95, n_bootstrap: int = 10000,
                 random_seed: int = 42):
        self.confidence = confidence
        self.n_bootstrap = n_bootstrap
        self.random_seed = random_seed
        np.random.seed(random_seed)

    def compute_ci_for_mean(self, scores: np.ndarray) -> Dict:
        """
        Bootstrap CI for mean score.

        Returns: {mean, ci_lower, ci_upper, se}
        """
        bootstrap_means = []

        for _ in range(self.n_bootstrap):
            # Resample with replacement
            sample = np.random.choice(scores, size=len(scores), replace=True)
            bootstrap_means.append(np.mean(sample))

        bootstrap_means = np.array(bootstrap_means)

        # Compute quantile-based CI
        alpha = 1 - self.confidence
        ci_lower = np.percentile(bootstrap_means, alpha/2 * 100)
        ci_upper = np.percentile(bootstrap_means, (1 - alpha/2) * 100)
        mean = np.mean(scores)
        se = np.std(bootstrap_means)

        return {
            'mean': mean,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'se': se,
            'margin_of_error': (ci_upper - ci_lower) / 2,
            'bootstrap_dist': bootstrap_means
        }

    def compute_ci_for_median(self, scores: np.ndarray) -> Dict:
        """Bootstrap CI for median score."""

        bootstrap_medians = []

        for _ in range(self.n_bootstrap):
            sample = np.random.choice(scores, size=len(scores), replace=True)
            bootstrap_medians.append(np.median(sample))

        bootstrap_medians = np.array(bootstrap_medians)

        alpha = 1 - self.confidence
        ci_lower = np.percentile(bootstrap_medians, alpha/2 * 100)
        ci_upper = np.percentile(bootstrap_medians, (1 - alpha/2) * 100)
        median = np.median(scores)

        return {
            'median': median,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'bootstrap_dist': bootstrap_medians
        }

    def compute_ci_for_proportion(self, scores: np.ndarray,
                                  threshold: float = 80) -> Dict:
        """Bootstrap CI for proportion of scores above threshold."""

        bootstrap_props = []
        n = len(scores)

        for _ in range(self.n_bootstrap):
            sample = np.random.choice(scores, size=n, replace=True)
            prop = np.sum(sample >= threshold) / n
            bootstrap_props.append(prop)

        bootstrap_props = np.array(bootstrap_props)

        alpha = 1 - self.confidence
        ci_lower = np.percentile(bootstrap_props, alpha/2 * 100)
        ci_upper = np.percentile(bootstrap_props, (1 - alpha/2) * 100)
        proportion = np.sum(scores >= threshold) / n

        return {
            'proportion': proportion,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'threshold': threshold,
            'count_above': np.sum(scores >= threshold),
            'total': n,
            'bootstrap_dist': bootstrap_props
        }

    def compute_ci_difference(self, scores1: np.ndarray,
                            scores2: np.ndarray) -> Dict:
        """Bootstrap CI for difference in means between two groups."""

        bootstrap_diffs = []

        for _ in range(self.n_bootstrap):
            sample1 = np.random.choice(scores1, size=len(scores1), replace=True)
            sample2 = np.random.choice(scores2, size=len(scores2), replace=True)
            diff = np.mean(sample1) - np.mean(sample2)
            bootstrap_diffs.append(diff)

        bootstrap_diffs = np.array(bootstrap_diffs)

        alpha = 1 - self.confidence
        ci_lower = np.percentile(bootstrap_diffs, alpha/2 * 100)
        ci_upper = np.percentile(bootstrap_diffs, (1 - alpha/2) * 100)
        mean_diff = np.mean(scores1) - np.mean(scores2)

        return {
            'mean_difference': mean_diff,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'includes_zero': ci_lower <= 0 <= ci_upper,
            'bootstrap_dist': bootstrap_diffs
        }

def compute_all_cis(results: Dict) -> pd.DataFrame:
    """Compute CIs for all models."""

    bootstrap = BootstrapCI()
    ci_results = []

    for model_name, model_results in results.items():
        scores = model_results.scores

        # Mean CI
        mean_ci = bootstrap.compute_ci_for_mean(scores)

        # Median CI
        median_ci = bootstrap.compute_ci_median(scores)

        # Proportion above 80 (production threshold)
        prop_80_ci = bootstrap.compute_ci_for_proportion(scores, threshold=80)

        ci_results.append({
            'Model': model_name,
            'Mean': f"{mean_ci['mean']:.2f}",
            'Mean_95CI': f"[{mean_ci['ci_lower']:.2f}, {mean_ci['ci_upper']:.2f}]",
            'Median': f"{median_ci['median']:.2f}",
            'Median_95CI': f"[{median_ci['ci_lower']:.2f}, {median_ci['ci_upper']:.2f}]",
            'Prop_≥80': f"{prop_80_ci['proportion']:.1%}",
            'Prop_95CI': f"[{prop_80_ci['ci_lower']:.1%}, {prop_80_ci['ci_upper']:.1%}]"
        })

    return pd.DataFrame(ci_results)

if __name__ == "__main__":
    from statistical_analysis_setup import load_evaluation_results

    results = load_evaluation_results()
    ci_df = compute_all_cis(results)
    print("BOOTSTRAP 95% CONFIDENCE INTERVALS")
    print("=" * 90)
    print(ci_df.to_string(index=False))
```

## Part 3: Paired Permutation Tests

Conduct hypothesis tests with multiple comparison correction:

```python
# significance_testing.py
"""
Paired permutation tests and multiple comparison correction.
"""

import numpy as np
from typing import Dict, Tuple
from itertools import combinations
import pandas as pd

class PermutationTest:
    """Paired permutation test for model comparison."""

    def __init__(self, alpha: float = 0.05, n_permutations: int = 10000,
                 random_seed: int = 42):
        self.alpha = alpha
        self.n_permutations = n_permutations
        np.random.seed(random_seed)

    def paired_permutation_test(self, scores1: np.ndarray,
                               scores2: np.ndarray) -> Dict:
        """
        Paired permutation test comparing two models.

        Assumes paired samples (same test cases evaluated by both models).
        """
        n = len(scores1)
        assert len(scores2) == n, "Scores must have same length"

        observed_diff = np.mean(scores1) - np.mean(scores2)
        differences = scores1 - scores2

        # Generate null distribution by random sign flips
        null_diffs = []
        for _ in range(self.n_permutations):
            signs = np.random.choice([-1, 1], size=n)
            permuted_diff = np.mean(differences * signs)
            null_diffs.append(permuted_diff)

        null_diffs = np.array(null_diffs)

        # Two-tailed p-value
        p_value = np.sum(np.abs(null_diffs) >= np.abs(observed_diff)) / self.n_permutations

        return {
            'observed_difference': observed_diff,
            'p_value': p_value,
            'significant': p_value < self.alpha,
            'null_distribution': null_diffs
        }

    def welch_ttest(self, scores1: np.ndarray, scores2: np.ndarray) -> Dict:
        """Welch's t-test (doesn't assume equal variances)."""

        from scipy import stats

        t_stat, p_value = stats.ttest_ind(scores1, scores2, equal_var=False)

        mean1 = np.mean(scores1)
        mean2 = np.mean(scores2)
        pooled_se = np.sqrt(np.var(scores1)/len(scores1) + np.var(scores2)/len(scores2))

        ci_lower = (mean1 - mean2) - 1.96 * pooled_se
        ci_upper = (mean1 - mean2) + 1.96 * pooled_se

        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < self.alpha,
            'mean_difference': mean1 - mean2,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper
        }

def pairwise_comparisons(results: Dict, correction_method: str = 'holm') -> pd.DataFrame:
    """
    Conduct all pairwise comparisons with multiple comparison correction.

    correction_method: 'holm', 'bonferroni', 'fdr'
    """

    models = list(results.keys())
    n_comparisons = len(list(combinations(models, 2)))

    test = PermutationTest()
    comparisons = []

    p_values = []
    model_pairs = []

    for model1, model2 in combinations(models, 2):
        scores1 = results[model1].scores
        scores2 = results[model2].scores

        # Conduct test
        test_result = test.paired_permutation_test(scores1, scores2)

        model_pairs.append((model1, model2))
        p_values.append(test_result['p_value'])

        comparisons.append({
            'Model1': model1,
            'Model2': model2,
            'Difference': test_result['observed_difference'],
            'p_value_uncorrected': test_result['p_value'],
            'Significant_Uncorrected': test_result['significant']
        })

    # Apply multiple comparison correction
    p_values = np.array(p_values)

    if correction_method == 'holm':
        # Holm-Bonferroni correction
        sorted_indices = np.argsort(p_values)
        corrected_p = np.zeros_like(p_values)
        for i, idx in enumerate(sorted_indices):
            corrected_p[idx] = p_values[idx] * (n_comparisons - i)
        corrected_p = np.minimum(corrected_p, 1.0)  # Cap at 1.0

    elif correction_method == 'bonferroni':
        corrected_p = np.minimum(p_values * n_comparisons, 1.0)

    elif correction_method == 'fdr':
        # Benjamini-Hochberg FDR correction
        sorted_indices = np.argsort(p_values)
        corrected_p = np.zeros_like(p_values)
        for i, idx in enumerate(sorted_indices):
            corrected_p[idx] = p_values[idx] * n_comparisons / (i + 1)
        corrected_p = np.minimum(corrected_p, 1.0)

    else:
        raise ValueError(f"Unknown correction method: {correction_method}")

    # Add corrected p-values to results
    for i, comp in enumerate(comparisons):
        comp['p_value_corrected'] = corrected_p[i]
        comp['Significant_Corrected'] = corrected_p[i] < 0.05

    df = pd.DataFrame(comparisons)
    df['Correction_Method'] = correction_method

    return df

if __name__ == "__main__":
    from statistical_analysis_setup import load_evaluation_results

    results = load_evaluation_results()
    pairwise_df = pairwise_comparisons(results, correction_method='holm')

    print("PAIRWISE COMPARISONS WITH HOLM CORRECTION")
    print("=" * 100)
    print(pairwise_df.to_string(index=False))
```

## Part 4: Effect Sizes and Cohen's d

Calculate practical significance:

```python
# effect_sizes.py
"""
Effect size calculation (Cohen's d, Hedge's g) for practical significance.
"""

import numpy as np
from typing import Dict
import pandas as pd

class EffectSize:
    """Compute effect sizes for model comparisons."""

    @staticmethod
    def cohens_d(scores1: np.ndarray, scores2: np.ndarray,
                 paired: bool = True) -> Dict:
        """
        Cohen's d effect size.

        For paired samples, uses difference scores.
        For independent samples, uses pooled standard deviation.
        """

        if paired:
            diffs = scores1 - scores2
            mean_diff = np.mean(diffs)
            std_diff = np.std(diffs, ddof=1)
            cohens_d = mean_diff / std_diff if std_diff > 0 else 0
        else:
            mean1, mean2 = np.mean(scores1), np.mean(scores2)
            var1, var2 = np.var(scores1, ddof=1), np.var(scores2, ddof=1)
            n1, n2 = len(scores1), len(scores2)

            pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1 + n2 - 2))
            cohens_d = (mean1 - mean2) / pooled_std if pooled_std > 0 else 0

        return {
            'cohens_d': cohens_d,
            'interpretation': interpret_cohens_d(cohens_d)
        }

    @staticmethod
    def hedges_g(scores1: np.ndarray, scores2: np.ndarray,
                 paired: bool = True) -> Dict:
        """Hedge's g (less biased version of Cohen's d for small samples)."""

        d_result = EffectSize.cohens_d(scores1, scores2, paired=paired)
        cohens_d = d_result['cohens_d']

        if paired:
            n = len(scores1)
            correction = 1 - 3 / (4*n - 1)
        else:
            n1, n2 = len(scores1), len(scores2)
            correction = 1 - 3 / (4*(n1 + n2) - 9)

        hedges_g = cohens_d * correction

        return {
            'hedges_g': hedges_g,
            'interpretation': interpret_cohens_d(hedges_g)
        }

    @staticmethod
    def cramers_v(model1_cat: np.ndarray, model2_cat: np.ndarray) -> float:
        """Cramér's V for categorical outcomes."""

        from scipy.stats import chi2_contingency

        contingency_table = pd.crosstab(model1_cat, model2_cat)
        chi2, p, dof, expected = chi2_contingency(contingency_table)

        n = contingency_table.sum().sum()
        min_dim = min(contingency_table.shape) - 1

        cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

        return {
            'cramers_v': cramers_v,
            'interpretation': interpret_cramers_v(cramers_v)
        }

def interpret_cohens_d(d: float) -> str:
    """Interpret Cohen's d magnitude."""

    abs_d = abs(d)
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    else:
        return "large"

def interpret_cramers_v(v: float) -> str:
    """Interpret Cramér's V magnitude."""

    if v < 0.1:
        return "negligible"
    elif v < 0.3:
        return "small"
    elif v < 0.5:
        return "medium"
    else:
        return "large"

def compute_effect_sizes_pairwise(results: Dict) -> pd.DataFrame:
    """Compute effect sizes for all pairwise comparisons."""

    from itertools import combinations

    effect_data = []

    for model1, model2 in combinations(results.keys(), 2):
        scores1 = results[model1].scores
        scores2 = results[model2].scores

        cohens_result = EffectSize.cohens_d(scores1, scores2, paired=True)
        hedges_result = EffectSize.hedges_g(scores1, scores2, paired=True)

        effect_data.append({
            'Model1': model1,
            'Model2': model2,
            'Mean_Diff': np.mean(scores1) - np.mean(scores2),
            'Cohens_d': cohens_result['cohens_d'],
            'Cohens_d_Interp': cohens_result['interpretation'],
            'Hedges_g': hedges_result['hedges_g'],
            'Hedges_g_Interp': hedges_result['interpretation']
        })

    df = pd.DataFrame(effect_data)
    return df

if __name__ == "__main__":
    from statistical_analysis_setup import load_evaluation_results

    results = load_evaluation_results()
    effect_df = compute_effect_sizes_pairwise(results)

    print("EFFECT SIZES FOR PAIRWISE COMPARISONS")
    print("=" * 110)
    print(effect_df.to_string(index=False))
```

## Part 5: Create Publication-Quality Visualizations

Generate professional charts:

```python
# visualizations.py
"""
Create publication-quality visualizations of evaluation results.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List

# Set style for publication-quality plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class EvaluationVisualizations:
    """Create professional evaluation visualizations."""

    def __init__(self, dpi: int = 300, figsize: Tuple = (12, 8)):
        self.dpi = dpi
        self.figsize = figsize

    def box_plot_by_model(self, results: Dict, output_file: str = None) -> None:
        """Create box plot comparing model score distributions."""

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Prepare data
        data_list = []
        labels = []
        for model_name, model_results in results.items():
            data_list.append(model_results.scores)
            labels.append(model_name)

        # Create box plot
        bp = ax.boxplot(data_list, labels=labels, patch_artist=True,
                       widths=0.6, showmeans=True)

        # Style boxes
        colors = sns.color_palette("husl", len(labels))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)

        ax.set_ylabel('Evaluation Score', fontsize=12, fontweight='bold')
        ax.set_xlabel('Model', fontsize=12, fontweight='bold')
        ax.set_title('Model Performance Comparison: Score Distributions',
                    fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3)
        ax.set_ylim(-5, 105)

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        else:
            plt.show()

    def violin_plot(self, results: Dict, output_file: str = None) -> None:
        """Create violin plot for distribution visualization."""

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Prepare data
        df_list = []
        for model_name, model_results in results.items():
            df_list.append(pd.DataFrame({
                'Model': model_name,
                'Score': model_results.scores
            }))

        df = pd.concat(df_list, ignore_index=True)

        # Create violin plot
        sns.violinplot(data=df, x='Model', y='Score', ax=ax, palette='husl')

        ax.set_ylabel('Evaluation Score', fontsize=12, fontweight='bold')
        ax.set_xlabel('Model', fontsize=12, fontweight='bold')
        ax.set_title('Model Performance: Score Distribution Shapes',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_ylim(-5, 105)
        ax.grid(axis='y', alpha=0.3)

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        else:
            plt.show()

    def bootstrap_ci_plot(self, results: Dict, output_file: str = None) -> None:
        """Plot means with bootstrap 95% confidence intervals."""

        from bootstrap_ci import BootstrapCI

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        bootstrap = BootstrapCI()
        models = list(results.keys())
        means = []
        ci_lowers = []
        ci_uppers = []

        for model_name in models:
            scores = results[model_name].scores
            ci = bootstrap.compute_ci_for_mean(scores)
            means.append(ci['mean'])
            ci_lowers.append(ci['ci_lower'])
            ci_uppers.append(ci['ci_upper'])

        means = np.array(means)
        ci_lowers = np.array(ci_lowers)
        ci_uppers = np.array(ci_uppers)

        x = np.arange(len(models))
        colors = sns.color_palette("husl", len(models))

        # Plot points with error bars
        for i, (mean, lower, upper, color) in enumerate(zip(means, ci_lowers, ci_uppers, colors)):
            ax.errorbar(i, mean, yerr=[[mean - lower], [upper - mean]],
                       fmt='o', markersize=10, capsize=5, capthick=2,
                       color=color, ecolor=color, elinewidth=2, alpha=0.8)

        ax.axhline(y=80, color='red', linestyle='--', linewidth=2,
                  label='Production Threshold', alpha=0.7)
        ax.axhline(y=65, color='orange', linestyle='--', linewidth=2,
                  label='Pass Threshold', alpha=0.7)

        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=45, ha='right')
        ax.set_ylabel('Mean Score', fontsize=12, fontweight='bold')
        ax.set_xlabel('Model', fontsize=12, fontweight='bold')
        ax.set_title('Model Performance with 95% Bootstrap Confidence Intervals',
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_ylim(55, 95)
        ax.grid(axis='y', alpha=0.3)
        ax.legend(loc='lower right')

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        else:
            plt.show()

    def histogram_comparison(self, results: Dict, output_file: str = None) -> None:
        """Create overlay histograms for model scores."""

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        colors = sns.color_palette("husl", len(results))

        for (model_name, model_results), color in zip(results.items(), colors):
            ax.hist(model_results.scores, bins=15, alpha=0.6,
                   label=model_name, color=color, edgecolor='black')

        ax.axvline(x=80, color='red', linestyle='--', linewidth=2,
                  label='Production (80)', alpha=0.7)
        ax.axvline(x=65, color='orange', linestyle='--', linewidth=2,
                  label='Pass (65)', alpha=0.7)

        ax.set_xlabel('Evaluation Score', fontsize=12, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax.set_title('Score Distribution Comparison Across Models',
                    fontsize=14, fontweight='bold', pad=20)
        ax.legend(loc='upper left')
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        else:
            plt.show()

    def heatmap_pairwise_effects(self, effect_df: pd.DataFrame,
                                output_file: str = None) -> None:
        """Create heatmap of pairwise effect sizes."""

        fig, ax = plt.subplots(figsize=(10, 8), dpi=self.dpi)

        # Create matrix from pairwise comparisons
        models = sorted(set(effect_df['Model1'].unique()) |
                       set(effect_df['Model2'].unique()))

        matrix = np.zeros((len(models), len(models)))

        for _, row in effect_df.iterrows():
            i = models.index(row['Model1'])
            j = models.index(row['Model2'])
            d = row['Cohens_d']
            matrix[i, j] = d
            matrix[j, i] = -d

        sns.heatmap(matrix, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                   xticklabels=models, yticklabels=models, ax=ax,
                   cbar_kws={'label': "Cohen's d"})

        ax.set_title("Pairwise Effect Sizes (Cohen's d)",
                    fontsize=14, fontweight='bold', pad=20)

        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=self.dpi, bbox_inches='tight')
        else:
            plt.show()

if __name__ == "__main__":
    from statistical_analysis_setup import load_evaluation_results
    from effect_sizes import compute_effect_sizes_pairwise

    results = load_evaluation_results()
    effect_df = compute_effect_sizes_pairwise(results)

    viz = EvaluationVisualizations()

    print("Generating visualizations...")
    viz.box_plot_by_model(results, output_file="model_boxplot.png")
    viz.violin_plot(results, output_file="model_violin.png")
    viz.bootstrap_ci_plot(results, output_file="model_ci.png")
    viz.histogram_comparison(results, output_file="model_histogram.png")
    viz.heatmap_pairwise_effects(effect_df, output_file="pairwise_effects.png")
    print("Visualizations saved.")
```

## Part 6: Interactive Plotly Visualizations

Create interactive dashboards:

```python
# interactive_visualizations.py
"""
Interactive Plotly visualizations for exploration.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

class InteractiveVisualizations:
    """Create interactive Plotly visualizations."""

    @staticmethod
    def interactive_scatter(results: Dict) -> None:
        """Interactive scatter plot with mean and CI."""

        from bootstrap_ci import BootstrapCI

        bootstrap = BootstrapCI()
        data = []

        for model_name, model_results in results.items():
            scores = model_results.scores
            ci = bootstrap.compute_ci_for_mean(scores)

            data.append({
                'Model': model_name,
                'Mean': ci['mean'],
                'CI_Lower': ci['ci_lower'],
                'CI_Upper': ci['ci_upper'],
                'SE': ci['se'],
                'Count': len(scores)
            })

        df = pd.DataFrame(data).sort_values('Mean', ascending=False)

        fig = go.Figure()

        for _, row in df.iterrows():
            fig.add_trace(go.Scatter(
                x=[row['Model']],
                y=[row['Mean']],
                mode='markers+lines',
                marker=dict(size=15, color=row['Mean']),
                error_y=dict(
                    type='data',
                    symmetric=False,
                    array=[row['CI_Upper'] - row['Mean']],
                    arrayminus=[row['Mean'] - row['CI_Lower']]
                ),
                name=row['Model'],
                hovertemplate='<b>%{fullData.name}</b><br>Mean: %{y:.2f}<br><extra></extra>'
            ))

        fig.add_hline(y=80, line_dash="dash", line_color="red",
                     annotation_text="Production Threshold")
        fig.add_hline(y=65, line_dash="dash", line_color="orange",
                     annotation_text="Pass Threshold")

        fig.update_layout(
            title="Model Performance with 95% CI (Interactive)",
            yaxis_title="Mean Score",
            xaxis_title="Model",
            hovermode="closest",
            height=600,
            template="plotly_white"
        )

        fig.show()

    @staticmethod
    def interactive_distributions(results: Dict) -> None:
        """Interactive distribution visualization."""

        df_list = []
        for model_name, model_results in results.items():
            df_list.append(pd.DataFrame({
                'Model': model_name,
                'Score': model_results.scores
            }))

        df = pd.concat(df_list)

        fig = px.box(df, x='Model', y='Score',
                    color='Model', title="Score Distributions")

        fig.add_hline(y=80, line_dash="dash", line_color="red")
        fig.add_hline(y=65, line_dash="dash", line_color="orange")

        fig.update_layout(height=600, template="plotly_white")
        fig.show()

    @staticmethod
    def interactive_heatmap(effect_df: pd.DataFrame) -> None:
        """Interactive heatmap of effect sizes."""

        models = sorted(set(effect_df['Model1'].unique()) |
                       set(effect_df['Model2'].unique()))

        matrix = np.zeros((len(models), len(models)))

        for _, row in effect_df.iterrows():
            i = models.index(row['Model1'])
            j = models.index(row['Model2'])
            d = row['Cohens_d']
            matrix[i, j] = d
            matrix[j, i] = -d

        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=models,
            y=models,
            colorscale='RdBu',
            zmid=0,
            text=np.round(matrix, 2),
            texttemplate='%{text:.2f}',
            colorbar=dict(title="Cohen's d")
        ))

        fig.update_layout(
            title="Pairwise Effect Sizes (Interactive)",
            height=600,
            template="plotly_white"
        )

        fig.show()

if __name__ == "__main__":
    from statistical_analysis_setup import load_evaluation_results
    from effect_sizes import compute_effect_sizes_pairwise

    results = load_evaluation_results()
    effect_df = compute_effect_sizes_pairwise(results)

    print("Interactive visualizations:")
    InteractiveVisualizations.interactive_scatter(results)
    InteractiveVisualizations.interactive_distributions(results)
    InteractiveVisualizations.interactive_heatmap(effect_df)
```

## Part 7: Generate Comprehensive Report

```python
# comprehensive_report.py
"""
Generate comprehensive statistical analysis report.
"""

import pandas as pd
from datetime import datetime

def generate_statistical_report(results: Dict,
                               pairwise_df: pd.DataFrame,
                               effect_df: pd.DataFrame,
                               ci_df: pd.DataFrame) -> str:
    """Generate formatted statistical analysis report."""

    report = []
    report.append("=" * 100)
    report.append("STATISTICAL ANALYSIS OF LLM EVALUATION RESULTS")
    report.append("=" * 100)
    report.append(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Analysis Framework: llm_eval_framework v2")
    report.append(f"Date: March 31, 2026")

    report.append("\n" + "=" * 100)
    report.append("1. EXECUTIVE SUMMARY")
    report.append("=" * 100)

    best_model = max(results.keys(),
                    key=lambda m: np.mean(results[m].scores))
    best_score = np.mean(results[best_model].scores)

    report.append(f"\nBest performing model: {best_model} (mean: {best_score:.2f})")

    production_ready = [m for m in results.keys()
                       if np.mean(results[m].scores) >= 80]
    report.append(f"Production-ready models: {', '.join(production_ready)}")

    report.append("\n" + "=" * 100)
    report.append("2. BOOTSTRAP CONFIDENCE INTERVALS")
    report.append("=" * 100)
    report.append(ci_df.to_string(index=False))

    report.append("\n" + "=" * 100)
    report.append("3. PAIRWISE COMPARISONS (Holm Correction)")
    report.append("=" * 100)
    report.append(pairwise_df.to_string(index=False))

    report.append("\n" + "=" * 100)
    report.append("4. EFFECT SIZES")
    report.append("=" * 100)
    report.append(effect_df.to_string(index=False))

    report.append("\n" + "=" * 100)
    report.append("5. RECOMMENDATIONS")
    report.append("=" * 100)

    report.append("\nBased on statistical analysis:")
    for model in production_ready:
        report.append(f"  • {model} meets production threshold (≥80)")

    report.append("\n" + "=" * 100)

    return "\n".join(report)

if __name__ == "__main__":
    from statistical_analysis_setup import load_evaluation_results
    from significance_testing import pairwise_comparisons
    from effect_sizes import compute_effect_sizes_pairwise
    from bootstrap_ci import compute_all_cis

    results = load_evaluation_results()
    pairwise_df = pairwise_comparisons(results, correction_method='holm')
    effect_df = compute_effect_sizes_pairwise(results)
    ci_df = compute_all_cis(results)

    report = generate_statistical_report(results, pairwise_df, effect_df, ci_df)
    print(report)

    with open("statistical_analysis_report.txt", "w") as f:
        f.write(report)
```

## Summary

In this lab, you have:

1. **Loaded evaluation data** from 5 models and organized for analysis
2. **Computed bootstrap confidence intervals** for robust uncertainty estimation
3. **Conducted paired permutation tests** with multiple comparison correction
4. **Calculated Cohen's d and Hedge's g** effect sizes
5. **Created publication-quality visualizations** suitable for reports
6. **Generated interactive Plotly dashboards** for exploration
7. **Produced comprehensive statistical report** with recommendations

## Key Takeaways

- Bootstrap methods provide robust inference without distributional assumptions
- Multiple comparison correction prevents false positives when testing many hypotheses
- Effect sizes quantify practical significance beyond statistical significance
- Confidence intervals provide more information than p-values alone
- Visualization is critical for communicating uncertainty and differences
- Production decision frameworks should combine statistical and practical considerations

## Next Steps

- Integrate this analysis into CI/CD pipelines (Lab 08)
- Use results for Pareto analysis and model selection (Lab 09)
- Implement continuous monitoring in production (Production Guide)
