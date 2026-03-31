# Human Evaluation Methodology

## Overview

Human evaluation remains the gold standard for assessing language model quality, particularly for tasks requiring subjective judgment, cultural understanding, or nuanced reasoning. While more expensive than automated metrics, human evaluation provides irreplaceable ground truth for validating other evaluation methods and understanding model behavior on tasks where human preference is the ultimate measure of success.

## Protocol Design

### Study Design Framework

**Key Components:**

1. **Research Questions**: What specific aspects of model quality are we measuring?
   - Example: "Does GPT-4 produce more factually accurate summaries than Claude 3 Opus?"
   - Example: "How do users perceive the safety of different instruction-following strategies?"

2. **Hypotheses**: Testable predictions about model performance
   - Directional: "Model A will be rated higher than Model B"
   - Magnitude: "Models will agree on winner 80% of the time"
   - Interaction: "Model A is better at technical queries, Model B at creative tasks"

3. **Study Design Type**:
   - **Between-Subjects**: Different evaluators assess different models
   - **Within-Subjects**: Same evaluators assess all models (captures individual differences)
   - **Mixed Design**: Some factors between-subjects, some within-subjects (most powerful but complex)

4. **Sample Size Calculation**:
   ```python
   # Basic sample size for comparing two models
   from scipy.stats import norm

   def required_sample_size(effect_size=0.5, alpha=0.05, power=0.80):
       """
       Calculate minimum samples needed for statistical significance
       effect_size: Cohen's d (0.2=small, 0.5=medium, 0.8=large)
       alpha: significance level (typically 0.05)
       power: probability of detecting effect (typically 0.80)
       """
       z_alpha = norm.ppf(1 - alpha/2)
       z_beta = norm.ppf(power)
       n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
       return int(np.ceil(n))

   # For medium effect size: ~128 samples per condition
   # For large effect size: ~52 samples per condition
   ```

5. **Randomization Strategy**:
   - **Query Randomization**: Each evaluator sees different set of queries
   - **Model Randomization**: Order of models presented randomized
   - **Evaluator Assignment**: Evaluators randomly assigned to conditions
   - **Stratification**: Ensure balanced representation of query types

### Protocol Template

```
EVALUATION STUDY PROTOCOL v1.0

TITLE:
[e.g., "Comparative Evaluation of Instruction-Following Capabilities"]

RESEARCH QUESTIONS:
1. [Primary research question]
2. [Secondary research questions]

HYPOTHESES:
H1: [Directional prediction]
H2: [Alternative hypothesis]

EVALUATION CRITERIA:
Criterion 1: [Name]
- Definition: [Precise definition of what to evaluate]
- Examples: [Good examples, bad examples]
- Scale: [1-5 Likert / Comparative / Categorical]

[Repeat for each criterion]

STUDY DESIGN:
- Type: [Between-subjects / Within-subjects / Mixed]
- Sample size: [N evaluators, M queries per evaluator]
- Query pool size: [Total number of distinct queries]
- Model count: [Number of models to evaluate]

EVALUATOR QUALIFICATIONS:
- Required background: [e.g., "CS degree", "2+ years industry experience"]
- Training time: [hours required]
- Quality control: [Attention checks, consensus verification]

RANDOMIZATION:
- Query assignment: [Method]
- Model order: [Method]
- Evaluator-query mapping: [Method]

TIMELINE:
- Training: [Date range]
- Data collection: [Date range]
- Analysis: [Date range]

INCLUSION/EXCLUSION CRITERIA:
- Include: [Evaluators who...]
- Exclude: [Evaluators who...]
```

## Annotation Guidelines Template

### Structure

```markdown
# ANNOTATION GUIDELINES: [Evaluation Task Name]

## Introduction

This document defines how to evaluate [target aspect] for [use case].

**Evaluation Goal**: [What we're trying to measure]

**Why This Matters**: [Business/research importance]

## Evaluation Dimension: [Name]

### Definition

[Precise definition of what to evaluate - 2-3 sentences]

Distinguish this dimension from others by clarifying:
- What IS included in this dimension
- What is NOT included (other dimensions handle that)

### Scale Definition

**Rating 5 (Excellent):**
- Criteria met: [specific criteria]
- Example: [concrete example response]

**Rating 4 (Good):**
- Criteria met: [specific criteria]
- Example: [concrete example response]

**Rating 3 (Adequate):**
- Criteria met: [specific criteria]
- Example: [concrete example response]

**Rating 2 (Below Average):**
- Criteria met: [specific criteria]
- Example: [concrete example response]

**Rating 1 (Poor):**
- Criteria met: [specific criteria]
- Example: [concrete example response]

### Decision Tree

Use this flowchart when borderline:

```
Is the response accurate? --> No --> Consider 1-2
                           --> Yes --> Continue

Does it address the full query? --> No --> Consider 2-3
                                 --> Yes --> Continue

Is it clearly explained? --> No --> Consider 3
                        --> Yes --> Continue

Does it go above/beyond expectations? --> No --> 4
                                     --> Yes --> 5
```

### Common Mistakes

- **Mistake 1**: [Description of frequent error]
  - Wrong: [Example of incorrect evaluation]
  - Right: [Example of correct evaluation]

- **Mistake 2**: [Description of frequent error]
  - Wrong: [Example of incorrect evaluation]
  - Right: [Example of correct evaluation]

## Evaluation Dimension: [Name]

[Repeat structure for each dimension]

## Special Cases

### Ambiguous Queries

**If the query is unclear or could be interpreted multiple ways:**

Option A: Evaluate based on the most reasonable interpretation
Option B: Mark as ambiguous and do not evaluate
Option C: Evaluate multiple interpretations and average

Guidance: [Specific guidance for your task]

### Harmful or Sensitive Content

**If the response contains harmful, illegal, or sensitive content:**

- Do not refuse to evaluate
- Evaluate the response as you would any other
- Rate based on the evaluation criteria
- If genuinely unsafe (instructions for violence, etc.), mark for human review

## Process

1. Read the query carefully
2. Read the response completely
3. For each dimension:
   - Reference the definition and examples
   - Use the decision tree if borderline
   - Assign a rating
   - (Optional) Leave brief justification
4. Review your scores for consistency
5. Submit

## Quality Checks Built In

You will encounter attention checks throughout the task. These are:
- [Example 1]: This is a clearly 5-star response - should rate highly
- [Example 2]: This response has a major factual error - should rate low

These checks ensure quality and do not count toward final results.

## FAQs

**Q: What if the response is good but not quite perfect?**
A: That's a 4. Perfect doesn't mean flawless (5 is exceptional), just very good.

**Q: Should I penalize responses for style I don't like?**
A: No. Only evaluate based on the criteria. Personal style preference is not in the rubric.

**Q: What if I'm unsure?**
A: Use the decision tree. If still unsure, pick the lower rating (bias toward conservative evaluation).

**Q: Can I see model names or other identifying info?**
A: No. Evaluators are blind to model identity to avoid bias.
```

## Inter-Annotator Agreement (IAA)

Measuring whether multiple evaluators consistently rate the same outputs is critical for validating evaluation quality.

### Cohen's Kappa (for categorical/binary ratings)

Measures agreement between two evaluators while accounting for chance.

```python
def cohens_kappa(evaluator1_ratings, evaluator2_ratings):
    """
    Calculate Cohen's kappa for two raters
    Ratings should be categorical (0/1, 1-5, etc.)
    """
    from sklearn.metrics import cohen_kappa_score

    kappa = cohen_kappa_score(evaluator1_ratings, evaluator2_ratings)
    return kappa

# Interpretation:
# 0.81-1.00: Almost perfect agreement
# 0.61-0.80: Substantial agreement
# 0.41-0.60: Moderate agreement
# 0.21-0.40: Fair agreement
# 0.00-0.20: Slight agreement
# <0.00:     Less than chance agreement (problematic!)
```

### Krippendorff's Alpha (for multiple raters)

More flexible than Kappa; handles multiple raters, missing data, and different measurement scales.

```python
def krippendorffs_alpha(value_matrix):
    """
    Calculate Krippendorff's alpha for multiple raters
    value_matrix: N items × M raters array of ratings
    """
    import numpy as np

    n, m = value_matrix.shape
    # Pairable values
    pairable = m * (m - 1) / 2

    # Observed disagreement
    total_disagreement = 0
    for i in range(n):
        ratings = [r for r in value_matrix[i] if not np.isnan(r)]
        for j in range(len(ratings)):
            for k in range(j + 1, len(ratings)):
                total_disagreement += (ratings[j] - ratings[k]) ** 2

    observed_disagreement = total_disagreement / (n * pairable)

    # Expected disagreement (if ratings were random)
    all_ratings = value_matrix[~np.isnan(value_matrix)]
    expected_disagreement = np.var(all_ratings)

    # Alpha
    if expected_disagreement == 0:
        return 1.0 if observed_disagreement == 0 else 0.0

    alpha = 1 - (observed_disagreement / expected_disagreement)
    return max(-1, min(1, alpha))  # Clamp to [-1, 1]
```

### Intra-Class Correlation (ICC)

For continuous/ordinal ratings from multiple raters.

```python
def intraclass_correlation(ratings_matrix, icc_type='ICC(2,1)'):
    """
    ICC for absolute agreement between raters
    ratings_matrix: N items × M raters
    """
    from pingouin import intraclass_corr

    # ICC(2,1): Two-way mixed effects, absolute agreement, single measurement
    icc_result = intraclass_corr(
        data=ratings_matrix,
        targets='items',
        raters='raters',
        ratings='ratings'
    )

    return icc_result

# Interpretation:
# 0.90-1.00: Excellent
# 0.75-0.90: Good
# 0.50-0.75: Moderate
# <0.50: Poor
```

### Investigating Disagreement

When IAA is low (<0.60), identify root causes:

```python
def analyze_disagreement(evaluator1, evaluator2, queries):
    """
    Find cases where evaluators most strongly disagree
    """
    import pandas as pd

    df = pd.DataFrame({
        'query': queries,
        'eval1': evaluator1,
        'eval2': evaluator2
    })

    df['disagreement'] = abs(df['eval1'] - df['eval2'])

    # Most disputed cases
    high_disagreement = df.nlargest(10, 'disagreement')

    print("Most disputed cases:")
    for idx, row in high_disagreement.iterrows():
        print(f"\nQuery: {row['query']}")
        print(f"Evaluator 1: {row['eval1']}, Evaluator 2: {row['eval2']}")
        print(f"Disagreement: {row['disagreement']}")

    return high_disagreement
```

**Common Causes of Low IAA:**
- Ambiguous evaluation criteria (need clearer definition)
- Insufficient evaluator training (need more examples)
- Fatigue effect (evaluators tire and become less consistent)
- Dimension overlap (multiple criteria measuring similar thing)
- Range restriction (all responses rated similarly)

## Crowd vs. Expert Evaluators

### Trade-offs Summary

**Crowd Evaluators (Amazon Mechanical Turk, Scale, etc.):**

Advantages:
- Cost: $0.10-$0.50 per evaluation
- Speed: Can evaluate 1000s of items in hours
- Scale: Easy to do multi-rater consensus
- Diverse perspectives: Crowd represents varied backgrounds

Disadvantages:
- Quality variance: Less consistent than experts
- Training overhead: Crowd workers have less background
- Attention: Higher failure rate on attention checks
- Reproducibility: Different workers may have different interpretations
- IAA: Typically 0.50-0.70 (vs. 0.75-0.90 for experts)

**Expert Evaluators (domain specialists, researchers):**

Advantages:
- Quality: Highly consistent and accurate
- Deep understanding: Can evaluate nuanced aspects
- Contextualization: Understand domain implications
- IAA: Typically 0.75-0.90
- Reproducibility: Same expert gives same ratings over time

Disadvantages:
- Cost: $10-$100+ per evaluation
- Speed: Limited availability, slower turnaround
- Scale: Hard to evaluate 10,000+ items
- Bias: Individual experts may have idiosyncratic preferences
- Coverage: May miss perspectives outside their expertise

### Cost-Benefit Analysis

```python
def cost_benefit_analysis(n_items, crowd_cost_per_eval, expert_cost_per_eval,
                         crowd_iaa=0.65, expert_iaa=0.82):
    """
    Compare cost vs. quality trade-off
    """

    # Crowd approach
    crowd_total_cost = n_items * crowd_cost_per_eval * 3  # 3 raters for consensus
    crowd_quality = crowd_iaa

    # Expert approach
    expert_total_cost = n_items * expert_cost_per_eval * 2  # 2 raters for consensus
    expert_quality = expert_iaa

    # Hybrid approach: crowd filter + expert refinement
    hybrid_cost = (n_items * crowd_cost_per_eval * 3 +
                   int(n_items * 0.3) * expert_cost_per_eval)  # 30% expert review

    return {
        'crowd': {'cost': crowd_total_cost, 'quality': crowd_quality},
        'expert': {'cost': expert_total_cost, 'quality': expert_quality},
        'hybrid': {'cost': hybrid_cost, 'quality': 0.73}  # Blended quality
    }

# For 10,000 items:
# Crowd (3 raters @ $0.25): $7,500, IAA 0.65
# Expert (2 raters @ $25): $500,000, IAA 0.82
# Hybrid (crowd + 30% expert): $82,500, IAA 0.73
```

### Recommended Hybrid Approach

1. **Round 1**: Crowd evaluation with 3 raters, Majority voting consensus
2. **Quality Filtering**: Keep only high-agreement items (IAA > 0.70)
3. **Round 2**: Expert review of low-agreement items (< 0.60 crowd IAA)
4. **Final Integration**: Combine crowd consensus + expert judgment

This achieves 75-80% quality of all-expert at 15% of cost.

## Chatbot Arena Deep Dive

### Overview

LMSYS Chatbot Arena (as of March 2026) has collected 5.6M+ votes comparing 333 models, becoming the largest pairwise comparison dataset for language models.

### Bradley-Terry Model

The arena uses the Bradley-Terry model to convert pairwise votes into absolute model rankings.

**Model:**
```
P(Model A > Model B) = e^(elo_A) / (e^(elo_A) + e^(elo_B))
```

Where:
- elo_A, elo_B are latent strength parameters
- The log-odds of A beating B equals elo_A - elo_B

**Estimation:**
```python
import numpy as np
from scipy.optimize import minimize

def bradley_terry_mle(comparisons):
    """
    Estimate Bradley-Terry parameters from pairwise comparisons
    comparisons: list of (model_a, model_b, winner)
    """
    unique_models = set()
    for a, b, _ in comparisons:
        unique_models.add(a)
        unique_models.add(b)

    model_list = sorted(list(unique_models))
    model_to_idx = {m: i for i, m in enumerate(model_list)}
    n_models = len(model_list)

    def negative_log_likelihood(strengths):
        """Strengths should sum to 0 for identifiability"""
        nll = 0
        for model_a, model_b, winner in comparisons:
            idx_a = model_to_idx[model_a]
            idx_b = model_to_idx[model_b]

            strength_a = strengths[idx_a]
            strength_b = strengths[idx_b]

            # Probability that A wins
            prob_a_wins = np.exp(strength_a) / (np.exp(strength_a) + np.exp(strength_b))

            if winner == model_a:
                nll -= np.log(prob_a_wins)
            else:
                nll -= np.log(1 - prob_a_wins)

        return nll

    # Initial guess
    x0 = np.zeros(n_models)

    # Optimize
    result = minimize(negative_log_likelihood, x0, method='BFGS')

    # Convert back to strengths (e^lambda_i)
    strengths = np.exp(result.x)
    strengths = strengths / strengths.sum() * n_models  # Normalize

    return {model: strengths[i] for i, model in enumerate(model_list)}
```

### Arena Expert: Smart Sampling

The Arena Expert system addresses the challenge that evaluating all pairs is O(N^2) comparisons.

**Key Innovation:**
- Uses only 5.5% of all possible comparisons
- Achieves 95%+ ranking correlation with full comparison set
- Adaptive sampling: focuses on uncertain rankings

**Sampling Strategy:**
```python
def arena_expert_sampling(n_models, budget_fraction=0.055):
    """
    Adaptively sample model comparisons
    """
    # Budget: only this many comparisons
    max_comparisons = int((n_models * (n_models - 1) / 2) * budget_fraction)

    # Phase 1: Round-robin (high confidence in local rankings)
    # Sample sqrt(N) models × sqrt(N) models in blocks
    n_blocks = int(np.sqrt(n_models))
    block_size = n_models / n_blocks

    phase1_comparisons = 0
    for i in range(n_blocks):
        for j in range(i + 1, n_blocks):
            # Compare all models in block i with all in block j
            phase1_comparisons += block_size ** 2

    # Phase 2: Focused comparisons on uncertain rankings
    remaining_budget = max_comparisons - phase1_comparisons

    # Uncertainty sampling: compare models with overlapping confidence intervals
    uncertain_pairs = [...]  # Identify pairs with overlap

    sampled_pairs = uncertain_pairs[:remaining_budget]

    return sampled_pairs

# For 333 models: 5.5% = 6,130 comparisons (vs. 55,278 all pairs)
# Ranking correlation achieved: 0.98+
```

## Direct Assessment vs. Comparative Evaluation

### Direct Assessment

Evaluators score outputs individually on absolute criteria.

**Advantages:**
- Simple to implement
- No inter-model comparison bias
- Absolute quality visible
- Can evaluate single model in isolation

**Disadvantages:**
- Difficult calibration (what's a "4"?)
- Anchor effect (first response sets expectations)
- Requires carefully defined rubrics
- More variance than comparative eval

**When to Use:**
- Building absolute quality standards
- Single model evaluation
- Certification/qualification use cases

### Comparative (Pairwise) Evaluation

Evaluators directly compare two outputs and pick the better one.

**Advantages:**
- More natural human judgment
- Easier to differentiate close cases
- Less prone to drift/calibration issues
- More reliable for ranking
- Lower variance than direct assessment

**Disadvantages:**
- Cannot evaluate single outputs
- O(N^2) comparisons needed for full ranking
- Position bias must be controlled
- Cannot assess absolute quality

**When to Use:**
- Competitive model evaluation
- Building ranking systems (Elo, Bradley-Terry)
- Pairwise preference data
- Arena-style evaluation

### Hybrid Approach

```
1. Comparative eval: Rapid pairwise comparisons (6 judges per pair)
   → Produces rough rankings
2. Direct assessment: Gold standard examples at each quality level
   → Creates calibration anchors
3. Spot-check comparative: Compare judges' 4 vs. 5 ratings to verify
   → Catches miscalibration
```

## Fatigue Effects and Quality Control

### Fatigue Monitoring

Evaluator fatigue (deteriorating judgment quality over time) is a major source of bias.

**Detection:**
```python
def detect_fatigue(evaluator_ratings, task_completion_time):
    """
    Identify if evaluator ratings degrade over time (fatigue effect)
    """
    from scipy.stats import linregress, spearmanr

    # Time index (0 = first evaluation, increases with time)
    time_index = np.arange(len(evaluator_ratings))

    # Check 1: Increasing variance in ratings over time
    early_ratings = evaluator_ratings[:int(len(evaluator_ratings)*0.25)]
    late_ratings = evaluator_ratings[int(len(evaluator_ratings)*0.75):]

    early_var = np.var(early_ratings)
    late_var = np.var(late_ratings)

    variance_increase = late_var / early_var if early_var > 0 else 0

    # Check 2: Regression toward middle
    slope, intercept, r_value, p_value, std_err = linregress(time_index,
                                                              evaluator_ratings)

    # Negative slope = fatigue (ratings getting lower)
    # Slope toward 3 on 5-scale = regression to center

    # Check 3: Decision latency increase
    latency_slope, _, _, latency_p, _ = linregress(time_index,
                                                     task_completion_time)

    return {
        'variance_increase_factor': variance_increase,
        'rating_drift_slope': slope,
        'p_value': p_value,
        'latency_increase_slope': latency_slope,
        'fatigue_detected': (variance_increase > 1.3 or
                            latency_slope > 0.1 or
                            abs(slope) > 0.02)
    }
```

### Quality Control Mechanisms

**Built-In Attention Checks:**
```
Every 10th item is an attention check:
- Clear 5-star response (evaluator should rate 4-5)
- Clear 1-star response (evaluator should rate 1-2)
- Exact duplicate of previous item (should get same score)

If evaluator fails 2+ checks: flag for review/removal
```

**Consistency Probes:**
- Same query evaluated twice (weeks apart) with different response
- Expected consistency: r > 0.75
- Below threshold: evaluator may have inconsistent standards

**Inter-Rater Reliability:**
- Calculate pairwise IAA for each evaluator against others
- Low IAA (< 0.50): evaluator may be calibrated differently
- Solution: Additional training or removal

### Break Scheduling

```python
def recommend_break_schedule(task_duration_minutes):
    """
    Recommend break frequency to minimize fatigue
    """
    break_interval = min(45, max(15, task_duration_minutes / 4))

    return {
        'work_period_minutes': int(break_interval),
        'break_duration_minutes': max(5, int(break_interval / 3)),
        'total_recommended_sessions': 3,
        'session_interval_hours': 4
    }

# Example: 2-hour task → work 30 min, break 10 min (4x)
```

## Incentive Design

### Payment Models

**Hourly Rate:**
- Simple, predictable
- Evaluator can plan time
- Disadvantage: creates speed incentive (quality tradeoff)
- Typical rate: $15-30/hour for crowd, $50-200+/hour for experts

**Per-Item Rate:**
- $0.10-0.50 per evaluation (crowd)
- $5-20 per evaluation (experts)
- Risk: evaluators rush
- Solution: Quality bonuses (maintain IAA or lower disagreement)

**Hybrid (Recommended):**
- Base rate: $25/hour
- Bonus: +50% if IAA > 0.75, +25% if IAA 0.60-0.75
- Penalty: -50% if IAA < 0.50

```python
def calculate_payment(base_hourly_rate, hours_worked, iaa_score):
    """
    Calculate payment with quality bonus
    """
    base_payment = base_hourly_rate * hours_worked

    if iaa_score >= 0.75:
        bonus_factor = 1.50
    elif iaa_score >= 0.60:
        bonus_factor = 1.25
    elif iaa_score >= 0.50:
        bonus_factor = 1.00
    else:
        bonus_factor = 0.50

    return base_payment * bonus_factor
```

### Non-Monetary Incentives

For research contexts or volunteer evaluation:
- Publication acknowledgment
- Leaderboard ranking (top evaluators)
- Special access to unreleased models
- Contribution badges/certificates
- Recognition in research papers

### Evaluator Retention

Maintain quality across seasons:
- Post-task survey for feedback
- Regular communication about study progress
- Recognize and reward repeat evaluators (experience bonus)
- Career development opportunities (promoted to quality reviewer)

## Implementation Checklist

- [ ] Define evaluation criteria and create annotation guidelines
- [ ] Recruit and train evaluators (minimum 2 per item)
- [ ] Run pilot study on 50-100 items
- [ ] Calculate and report IAA (target > 0.70)
- [ ] Design evaluator incentives and payment
- [ ] Implement attention checks and quality monitoring
- [ ] Monitor for fatigue effects (break schedules)
- [ ] Perform disagreement analysis on low-IAA items
- [ ] Document all procedures in protocol
- [ ] Run validation comparing to alternative evaluation methods
- [ ] Publish methodology and data (if permissible) for reproducibility
