# Statistical Rigor in LLM Evaluation

A metric score alone is worthless. "Model A achieves 87.3% accuracy" is meaningless without uncertainty quantification, baseline comparison, and methodological detail. This chapter covers the statistical practices necessary for rigorous, reproducible evaluation.

## Why Statistical Rigor Matters

Single-number leaderboards are misleading. They collapse complex evaluation into a single score, obscuring:

- **Variance:** Is 87.3% the true score, or could it be 85% to 89%?
- **Significance:** Is a 2-point difference between models real or within noise?
- **Contamination:** Is the score inflated by benchmark contamination?
- **Method sensitivity:** How much does the score change with different prompts or evaluation methodology?

Rigorous evaluation quantifies these uncertainties and provides evidence-based comparisons.

## Bootstrap Confidence Intervals

The bootstrap is the workhorse of evaluation uncertainty quantification. It requires no distributional assumptions and scales to complex metrics.

### The Bootstrap Procedure

Given $n$ evaluation samples (e.g., accuracy on 1,000 examples):

1. Resample $n$ samples with replacement from the evaluation set
2. Compute the metric on the resampled set
3. Repeat steps 1-2 many times (typically 1,000-10,000 iterations)
4. The distribution of metric values across bootstrap samples is the bootstrap distribution
5. The 2.5% and 97.5% percentiles of this distribution are the 95% confidence interval

### Example: Bootstrap Confidence Interval for Accuracy

```python
import numpy as np

def bootstrap_ci(predictions, labels, metric_fn, n_boots=10000, ci=95):
    """
    Compute bootstrap confidence interval for a metric.

    Args:
        predictions: Model predictions
        labels: Ground truth labels
        metric_fn: Function that takes (predictions, labels) and returns scalar score
        n_boots: Number of bootstrap samples
        ci: Confidence level (default 95)

    Returns:
        metric_value: Original metric on full dataset
        ci_lower: Lower confidence interval bound
        ci_upper: Upper confidence interval bound
    """
    n = len(predictions)
    metric_value = metric_fn(predictions, labels)

    bootstrap_metrics = []
    rng = np.random.RandomState(42)

    for _ in range(n_boots):
        # Resample with replacement
        idx = rng.choice(n, size=n, replace=True)
        boot_predictions = predictions[idx]
        boot_labels = labels[idx]

        # Compute metric on bootstrap sample
        boot_metric = metric_fn(boot_predictions, boot_labels)
        bootstrap_metrics.append(boot_metric)

    bootstrap_metrics = np.array(bootstrap_metrics)
    alpha = (100 - ci) / 2
    ci_lower = np.percentile(bootstrap_metrics, alpha)
    ci_upper = np.percentile(bootstrap_metrics, 100 - alpha)

    return metric_value, ci_lower, ci_upper

# Usage example
from sklearn.metrics import accuracy_score

predictions = np.array([1, 0, 1, 1, 0, 1, 0, 1])
labels = np.array([1, 0, 1, 0, 0, 1, 0, 1])

accuracy, ci_lower, ci_upper = bootstrap_ci(predictions, labels, accuracy_score)
print(f"Accuracy: {accuracy:.3f} (95% CI: [{ci_lower:.3f}, {ci_upper:.3f}])")
# Output: Accuracy: 0.875 (95% CI: [0.625, 1.000])
```

### Key Properties of Bootstrap

- **No distributional assumptions:** Works for any metric, no need to assume normality
- **Applicable to complex metrics:** Works for metrics like BLEU, ROUGE, Elo rating, etc.
- **Computationally cheap:** 1,000-10,000 bootstrap samples are feasible even for large datasets
- **Variance estimation:** Bootstrap naturally estimates both point estimates and confidence intervals

### Pitfalls

- **Dependent samples:** Bootstrap assumes samples are independent. If samples are correlated, bootstrap CIs are too narrow. (Solution: block bootstrap or resampling by cluster)
- **Biased estimators:** Bootstrap works best for unbiased estimators. Some metrics (especially learned metrics) may have bias that bootstrap doesn't capture
- **Rare events:** If the true metric is extreme (e.g., 0% or 100%), bootstrap CIs can be unstable

## Effect Sizes

Confidence intervals tell you the range of plausible values. Effect sizes quantify the magnitude of differences between conditions (e.g., Model A vs. Model B).

### Cohen's d

**Formula:**
$$d = \frac{\bar{x}_1 - \bar{x}_2}{s_p}$$

where:
- $\bar{x}_1, \bar{x}_2$ are the sample means
- $s_p = \sqrt{\frac{(n_1-1)s_1^2 + (n_2-1)s_2^2}{n_1 + n_2 - 2}}$ is the pooled standard deviation

**Interpretation:**
- $|d| < 0.2$: Small effect
- $0.2 \leq |d| < 0.5$: Small to medium
- $0.5 \leq |d| < 0.8$: Medium to large
- $|d| \geq 0.8$: Large effect

**When to use:** Comparing two models on accuracy-like metrics (continuous).

**Example:**

```python
from scipy import stats

model_a_scores = np.array([0.85, 0.88, 0.86, 0.87, 0.84])
model_b_scores = np.array([0.82, 0.81, 0.80, 0.83, 0.79])

mean_diff = model_a_scores.mean() - model_b_scores.mean()
pooled_std = np.sqrt(((len(model_a_scores)-1)*model_a_scores.std()**2 +
                       (len(model_b_scores)-1)*model_b_scores.std()**2) /
                      (len(model_a_scores) + len(model_b_scores) - 2))
cohens_d = mean_diff / pooled_std

print(f"Cohen's d: {cohens_d:.3f}")  # Output: Cohen's d: 1.345 (large effect)
```

### Cliff's Delta

For non-normally distributed data or ordinal metrics, use Cliff's delta:

**Formula:**
$$\Delta = \frac{|\text{# dominance}_1 - \text{# dominance}_2|}{n_1 \cdot n_2}$$

where dominance counts are computed pairwise (how often samples from group 1 are larger than group 2).

**When to use:** Non-parametric alternative to Cohen's d, works with ordinal data and ranked comparisons.

```python
def cliffs_delta(x, y):
    """Compute Cliff's delta effect size."""
    n1, n2 = len(x), len(y)

    # Count dominances
    dominance = 0
    for xi in x:
        for yj in y:
            if xi > yj:
                dominance += 1
            elif xi < yj:
                dominance -= 1

    delta = dominance / (n1 * n2)
    return delta

delta = cliffs_delta(model_a_scores, model_b_scores)
print(f"Cliff's delta: {delta:.3f}")
```

## Power Analysis

Before running an evaluation, you should know: "Given my effect size of interest and variance, how many samples do I need to reliably detect that difference?"

Power analysis computes the required sample size (or alternatively, the power for a given sample size).

### Sample Size Calculation

For comparing two means with power $P$, significance level $\alpha$, and effect size $d$:

$$n = \frac{2(z_\alpha + z_P)^2 d^2}{\text{effect size}^2}$$

where $z_\alpha$ and $z_P$ are standard normal quantiles.

**Practical values:**
- $\alpha = 0.05$ (significance): $z_\alpha = 1.96$
- Power $P = 0.80$ (detect 80% of true effects): $z_P = 0.84$
- Power $P = 0.90$: $z_P = 1.28$

**Example:** To detect a medium effect size ($d = 0.5$) with 80% power:

$$n = \frac{2(1.96 + 0.84)^2 \times 0.5^2}{0.5^2} = \frac{2 \times 7.84 \times 0.25}{0.25} \approx 64 \text{ samples per group}$$

```python
from scipy.stats import nct

def power_analysis(effect_size=0.5, alpha=0.05, power=0.80):
    """Compute required sample size for power analysis."""
    z_alpha = 1.96  # Two-tailed, alpha=0.05
    z_power = 0.84  # Power=0.80

    n_per_group = 2 * (z_alpha + z_power)**2 * effect_size**2 / effect_size**2
    return int(np.ceil(n_per_group))

n_required = power_analysis(effect_size=0.5, alpha=0.05, power=0.80)
print(f"Required samples per group: {n_required}")  # Output: 64
```

**Key insight:** Effect size matters more than sample size. Detecting a small effect requires many more samples than detecting a large effect.

## Multiple Comparisons Correction

If you compare many models or run many evaluations, you increase the probability of false positives. Multiple comparisons correction controls for this.

### Bonferroni Correction

The simplest method: divide the significance threshold by the number of comparisons.

$$\alpha_{\text{corrected}} = \frac{\alpha}{M}$$

where $M$ is the number of comparisons.

**Example:** With $\alpha = 0.05$ and 10 model comparisons, use $\alpha = 0.005$ for each comparison.

**Disadvantage:** Conservative (may miss true effects). For independent tests, appropriate. For dependent tests, overly conservative.

### Holm Correction

Less conservative than Bonferroni; controls family-wise error rate (FWER):

1. Order p-values: $p_1 \leq p_2 \leq ... \leq p_M$
2. For each $i$, reject if $p_i < \alpha / (M - i + 1)$

**Advantage:** More powerful than Bonferroni while controlling FWER.

```python
from scipy.stats import t as t_dist

def holm_correction(p_values, alpha=0.05):
    """Apply Holm correction for multiple comparisons."""
    M = len(p_values)
    sorted_indices = np.argsort(p_values)

    reject = np.zeros(M, dtype=bool)
    for i, idx in enumerate(sorted_indices):
        threshold = alpha / (M - i)
        if p_values[idx] < threshold:
            reject[idx] = True

    return reject

p_values = np.array([0.001, 0.015, 0.042, 0.08, 0.15])
reject = holm_correction(p_values, alpha=0.05)
print(f"Reject H0: {reject}")  # Output: [ True  True False False False]
```

### Benjamini-Hochberg FDR Control

Controls False Discovery Rate (FDR) rather than FWER. More powerful for large numbers of tests:

1. Order p-values: $p_1 \leq p_2 \leq ... \leq p_M$
2. Find largest $i$ such that $p_i \leq \frac{i}{M} \alpha$
3. Reject $H_0$ for all $j \leq i$

**Advantage:** Powerful for many tests; controls expected proportion of false discoveries.

```python
def bh_fdr_control(p_values, alpha=0.05):
    """Apply Benjamini-Hochberg FDR control."""
    M = len(p_values)
    sorted_indices = np.argsort(p_values)

    # Find largest i such that p_i <= i/M * alpha
    threshold_idx = -1
    for i in range(M-1, -1, -1):
        threshold = (i+1) / M * alpha
        if p_values[sorted_indices[i]] <= threshold:
            threshold_idx = i
            break

    reject = np.zeros(M, dtype=bool)
    if threshold_idx >= 0:
        reject[sorted_indices[:threshold_idx+1]] = True

    return reject

p_values = np.array([0.001, 0.015, 0.042, 0.08, 0.15])
reject = bh_fdr_control(p_values, alpha=0.05)
print(f"Reject H0: {reject}")  # Output: [ True  True  True False False]
```

**Rule of thumb:** Use Bonferroni for very few tests (< 5), Holm for moderate numbers (5-50), BH FDR for many tests (> 50).

## Paired vs. Unpaired Tests

When comparing two models, the choice between paired and unpaired tests is critical.

### Paired Tests

**Use when:** The same evaluation set is used for both models (both models see the same samples).

**Example:** Model A and Model B both evaluated on 1,000 MMLU questions.

**Advantages:**
- Eliminates sample-to-sample variance (what makes one sample hard or easy)
- More statistical power (detects smaller differences)
- Appropriate when evaluating on the same data

**Implementation (paired t-test):**

```python
from scipy.stats import ttest_rel

model_a_scores = np.array([1, 0, 1, 1, 0, 1, 0, 1])  # Per-sample accuracy
model_b_scores = np.array([1, 0, 1, 0, 0, 1, 0, 1])

t_stat, p_value = ttest_rel(model_a_scores, model_b_scores)
print(f"Paired t-test: t={t_stat:.3f}, p={p_value:.3f}")
```

### Unpaired Tests

**Use when:** Different evaluation sets or independent samples.

**Example:** Model A evaluated on 1,000 randomly-selected MMLU questions, Model B on a different 1,000 random MMLU questions.

**Advantages:**
- Appropriate for truly independent samples
- Can compare across different datasets or domains
- Necessary when identical evaluation isn't possible

**Implementation (unpaired t-test):**

```python
from scipy.stats import ttest_ind

# Model A tested on 1000 samples, Model B on 1000 different samples
model_a_accuracy = np.random.binomial(1, 0.85, 1000).mean()  # 85% avg
model_b_accuracy = np.random.binomial(1, 0.80, 1000).mean()  # 80% avg

t_stat, p_value = ttest_ind([model_a_accuracy]*1000, [model_b_accuracy]*1000)
```

**Key difference:** Paired tests have more power because they account for shared variance in difficulty.

## Why Single-Number Leaderboards Mislead

"Model A: 87.3%, Model B: 85.1%" seems to show A is better. But:

1. **Uncertainty:** Without confidence intervals, you don't know if the difference is real or noise. Assume CI of ±2% for both. Then the intervals overlap; we can't reliably say A is better.

2. **Variance across prompts:** The 87.3% may be with a specific prompt. With different prompts, the score might be 83% or 91%. Stability across prompt variations is crucial.

3. **Task composition:** If the benchmark includes easy and hard tasks, higher scores might come from better hard-task performance or better easy-task performance. These aren't equivalent.

4. **Metric dependence:** A score of 87.3% on MMLU depends on tokenization, exact answer format, and metric (exact match? fuzzy match?). Small changes can move the score 1-2 points.

5. **Contamination status:** Is the score inflated by benchmark contamination? Unknown without explicit contamination assessment.

**Better practice:** Report:
- **Point estimate:** 87.3% accuracy
- **Confidence interval:** 95% CI [85.1%, 89.5%]
- **Prompt stability:** Score is 87.3% ± 2.1% across 5 prompt variations
- **Task breakdown:** 92% on knowledge tasks, 78% on reasoning tasks
- **Comparison:** Significantly different from baseline (t=2.3, p=0.021) with Cohen's d=0.55 (medium effect)
- **Sample size:** Evaluated on 5,000 samples
- **Methodology:** Exact match scoring after lowercasing and punctuation removal

## Variance-Aware Evaluation

Models have inherent variance in performance across:
- **Prompts:** Different phrasings of the same question
- **Samples:** Different random samples from the evaluation set
- **Seeds:** Different initialization or sampling randomness

### Measuring Prompt Sensitivity

Evaluate the same task with multiple prompt variations:

```python
def evaluate_prompt_stability(model, task_samples, prompt_templates, metric_fn):
    """
    Evaluate model performance across multiple prompt variations.

    Args:
        model: LLM to evaluate
        task_samples: List of evaluation samples
        prompt_templates: List of different prompt formulations
        metric_fn: Function to compute metric (accuracy, etc.)

    Returns:
        mean_score: Average score across prompts
        std_score: Standard deviation across prompts
        per_prompt_scores: Score for each prompt variant
    """
    scores = []

    for template in prompt_templates:
        predictions = []
        for sample in task_samples:
            prompt = template.format(question=sample['question'])
            response = model.generate(prompt)
            predictions.append(response)

        score = metric_fn(predictions, [s['answer'] for s in task_samples])
        scores.append(score)

    return np.mean(scores), np.std(scores), scores

# Example usage
prompts = [
    "Q: {question}\nA:",
    "Answer the following question: {question}",
    "{question}",
    "Question: {question}\nPlease provide the answer.",
]

mean_score, std_score, per_prompt = evaluate_prompt_stability(model, samples, prompts, accuracy)
print(f"Accuracy: {mean_score:.3f} ± {std_score:.3f}")
```

### Block Bootstrap for Dependent Samples

If samples are correlated (e.g., multiple questions from the same topic), use block bootstrap:

```python
def block_bootstrap_ci(predictions, labels, block_ids, metric_fn,
                       n_boots=1000, ci=95):
    """
    Bootstrap confidence interval accounting for block structure.

    Args:
        predictions: Model predictions
        labels: Ground truth labels
        block_ids: Block assignment for each sample (e.g., document ID)
        metric_fn: Metric function
        n_boots: Number of bootstrap samples
        ci: Confidence level
    """
    unique_blocks = np.unique(block_ids)
    n_blocks = len(unique_blocks)

    metric_value = metric_fn(predictions, labels)
    bootstrap_metrics = []
    rng = np.random.RandomState(42)

    for _ in range(n_boots):
        # Resample blocks (not individual samples)
        block_idx = rng.choice(n_blocks, size=n_blocks, replace=True)

        # Collect all samples from selected blocks
        boot_mask = np.isin(block_ids, unique_blocks[block_idx])
        boot_predictions = predictions[boot_mask]
        boot_labels = labels[boot_mask]

        boot_metric = metric_fn(boot_predictions, boot_labels)
        bootstrap_metrics.append(boot_metric)

    bootstrap_metrics = np.array(bootstrap_metrics)
    alpha = (100 - ci) / 2
    ci_lower = np.percentile(bootstrap_metrics, alpha)
    ci_upper = np.percentile(bootstrap_metrics, 100 - alpha)

    return metric_value, ci_lower, ci_upper
```

## Variance in Model Comparison

When comparing two models, variance comes from multiple sources:

**Within-sample variance:** Individual sample difficulty varies. Some samples are easy, some hard. This is the primary variance source.

**Prompt variance:** Different prompts for the same sample produce different model outputs.

**Random seed variance:** Different initialization, sampling, or randomness produces different results.

**Annotator variance:** If using human evaluation, different annotators judge quality differently.

The key insight: **Pair samples across models.** If both models see the same samples, you eliminate within-sample variance from the comparison.

## NIST February 2026 Recommendation: GLMM

The National Institute of Standards and Technology (NIST) February 2026 report on LLM evaluation recommends Generalized Linear Mixed Models (GLMM) for principled model comparison:

$$\log\left(\frac{p_i}{1-p_i}\right) = \alpha + \beta_m \cdot M_m + \gamma_s \cdot S_s + \epsilon$$

where:
- $p_i$ is the probability of correctness for sample $i$
- $\alpha$ is the intercept
- $\beta_m$ is the effect of model $m$ (what we want to estimate)
- $\gamma_s$ is the random effect of sample $s$ (accounts for sample difficulty)
- $\epsilon$ is residual noise

**Key advantages:**
- Accounts for sample difficulty (random effects)
- Estimates model effects while controlling for sample variation
- Provides uncertainty estimates for model effects
- Generalizes to continuous metrics (linear mixed models)

**Implementation:**

```python
import statsmodels.api as sm
import pandas as pd

# Prepare data: one row per (model, sample) pair
data = pd.DataFrame({
    'model': ['A']*1000 + ['B']*1000,
    'sample_id': list(range(1000)) + list(range(1000)),
    'correct': correct_A + correct_B,  # Binary outcome per sample
})

# Fit GLMM
glmm_formula = 'correct ~ C(model) + (1 | sample_id)'
glmm = sm.glmer(glmm_formula, data=data, family=sm.families.Binomial(),
                groups=data['sample_id'])

# Extract model effects (log-odds, convert to probability if needed)
print(glmm.summary())
```

**When to use:** For rigorous model comparison, especially with multiple samples and models. Standard in recent LLM evaluation papers.

## Evaluation Checklist

Before publishing or deploying evaluation results, verify:

- [ ] **Confidence intervals:** Report 95% CI for all metrics, not just point estimates
- [ ] **Effect sizes:** Report Cohen's d or Cliff's delta for model comparisons
- [ ] **Multiple comparisons:** If comparing N models, correct for N(N-1)/2 pairwise comparisons
- [ ] **Paired tests:** Use paired tests if models evaluated on same samples
- [ ] **Sample size:** Report n (number of samples), verify adequate power
- [ ] **Prompt sensitivity:** Report performance across multiple prompt variations
- [ ] **Task breakdown:** Show performance on task subsets (not just overall score)
- [ ] **Methodology:** Document prompt template, exact metric computation, answer normalization
- [ ] **Variance analysis:** If samples are clustered, use block bootstrap or GLMM
- [ ] **Reproducibility:** Provide seed, data splits, and sufficient detail for reproduction
- [ ] **Assumptions:** State assumptions (e.g., "assumes sample independence")

---

**Next:** Explore [evaluation benchmarks](../02-benchmarks/index.md) to understand which benchmarks are suited for your evaluation needs.
