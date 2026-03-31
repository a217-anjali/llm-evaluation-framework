# Custom Evaluation Design

## Overview

Building domain-specific evaluations for specialized tasks requires careful planning, rigorous testing, and iterative refinement. This guide provides a step-by-step methodology for designing evaluation frameworks tailored to your domain.

## Step-by-Step Guide to Building Domain-Specific Evals

### Phase 1: Requirements Definition

#### 1.1 Identify Evaluation Objectives

Start by defining *exactly* what you want to measure.

```python
class EvalRequirements:
    """Define evaluation scope and goals"""

    def __init__(self):
        self.primary_objectives = []
        self.secondary_objectives = []
        self.out_of_scope = []
        self.success_criteria = []

    def add_objective(self, objective, priority='primary', measurable_criteria=None):
        """
        Add evaluation objective
        objective: what are we measuring?
        measurable_criteria: how do we quantify success?
        """
        obj_dict = {
            'description': objective,
            'measurable_criteria': measurable_criteria or []
        }

        if priority == 'primary':
            self.primary_objectives.append(obj_dict)
        else:
            self.secondary_objectives.append(obj_dict)

# Example for medical question-answering system:
eval_req = EvalRequirements()

eval_req.add_objective(
    objective='Accuracy of medical diagnoses',
    priority='primary',
    measurable_criteria=[
        'Correct diagnosis in ICD-10 code',
        'Agrees with board-certified physician assessment',
        'Mentions all relevant differential diagnoses'
    ]
)

eval_req.add_objective(
    objective='Safety of recommendations',
    priority='primary',
    measurable_criteria=[
        'No harmful contraindications',
        'Appropriate severity assessment',
        'Mentions when to seek emergency care'
    ]
)

eval_req.add_objective(
    objective='Clarity for lay patients',
    priority='secondary',
    measurable_criteria=[
        'Avoids jargon',
        'Explains medical terms',
        'Well-structured and readable'
    ]
)
```

#### 1.2 Define Domain Boundaries

What is your model expected to do? What is out of scope?

```python
# DOMAIN SCOPE DEFINITION

IN SCOPE:
- Question-answering on medical topics
- Common chronic conditions (diabetes, hypertension, etc.)
- Symptom assessment
- General health advice

OUT OF SCOPE:
- Psychiatric/mental health diagnosis (refer to specialist)
- Prescription of controlled substances (requires MD oversight)
- Emergency medicine decisions (>30 min response time)
- Pediatric cases (children < 18 years)
- Geriatric polypharmacy (>5 medications)

CLEAR BOUNDARIES ARE CRITICAL:
- Vague boundaries lead to unclear evaluation criteria
- Misaligned expectations cause false negatives
```

### Phase 2: Task and Rubric Design

#### 2.1 Create Representative Task Suite

Design a diverse set of tasks that cover your domain.

```python
def design_task_suite(domain, n_tasks_per_category=20):
    """
    Create comprehensive task suite covering domain breadth
    """

    task_suite = {
        'routine_cases': [],
        'edge_cases': [],
        'adversarial_examples': [],
        'real_world_examples': []
    }

    # ROUTINE CASES: straightforward, well-defined problems
    # Example for medical domain: common cold, acute gastroenteritis
    task_suite['routine_cases'] = [
        {
            'query': 'I have fever 38.5C, cough, fatigue for 2 days',
            'expected_output': 'Likely viral infection (common cold/flu)',
            'difficulty': 'easy'
        },
        # ... 19 more routine cases
    ]

    # EDGE CASES: ambiguous, require nuance
    # Example: symptoms could be multiple conditions
    task_suite['edge_cases'] = [
        {
            'query': 'Chest pain, shortness of breath, dizziness, past smoker',
            'expected_output': 'Multiple serious conditions possible; urgent care required',
            'difficulty': 'hard',
            'requires_expert': True
        },
        # ... 19 more edge cases
    ]

    # ADVERSARIAL EXAMPLES: designed to trick the system
    task_suite['adversarial_examples'] = [
        {
            'query': 'Symptom of condition X, but I forgot to mention I have rare disease Y',
            'expected_output': 'Should ask clarifying questions',
            'should_fail_on': 'Assumes simple diagnosis without asking questions'
        },
        # ... adversarial examples
    ]

    # REAL-WORLD EXAMPLES: actual cases from medical literature/practice
    task_suite['real_world_examples'] = [
        {
            'query': '[Actual case from published medical journal]',
            'gold_standard': '[Physician diagnosis from case report]',
            'source': 'NEJM Case Report #12345'
        }
        # ... more real cases
    ]

    return task_suite

# Statistics for good task suite:
# - At least 30-50 tasks total
# - 60% routine, 25% edge cases, 15% adversarial
# - Covers 80%+ of use cases
# - Representative of actual usage distribution
```

#### 2.2 Rubric Engineering

Create detailed rubrics for human evaluation. Rubric quality directly affects evaluation reliability.

```python
class DetailedRubric:
    """
    Multi-level rubric for nuanced evaluation
    """

    def __init__(self, domain):
        self.domain = domain
        self.dimensions = []

    def add_dimension(self, name, description, level_descriptions):
        """
        Add evaluation dimension with explicit level definitions

        level_descriptions: dict of {level: detailed description}
        """
        dimension = {
            'name': name,
            'description': description,
            'levels': level_descriptions
        }
        self.dimensions.append(dimension)

# Example: Medical diagnosis evaluation rubric
medical_rubric = DetailedRubric('Medical Diagnosis')

medical_rubric.add_dimension(
    name='Diagnostic Accuracy',
    description='Does the response correctly identify the condition?',
    level_descriptions={
        5: {
            'description': 'Excellent',
            'criteria': [
                'Identifies correct primary diagnosis',
                'Lists appropriate differential diagnoses',
                'Matches board-certified physician diagnosis',
                'No misdiagnosis that would cause harm'
            ],
            'examples': [
                {
                    'case': 'Fever, cough, chest pain → pneumonia',
                    'good_response': 'Likely bacterial pneumonia with atypical presentation. Differential includes viral pneumonia, acute bronchitis.',
                    'explanation': 'Correct primary, lists differentials, suggests imaging'
                }
            ]
        },
        4: {
            'description': 'Good',
            'criteria': [
                'Correct primary diagnosis',
                'May miss some differentials',
                'Minor diagnostic gaps'
            ],
            'examples': [
                {
                    'case': 'Fever, cough, chest pain → pneumonia',
                    'adequate_response': 'Could be pneumonia or bronchitis. Should see a doctor.',
                    'explanation': 'Correct primary, some differentials, adequate guidance'
                }
            ]
        },
        3: {
            'description': 'Adequate',
            'criteria': [
                'Partially correct diagnosis',
                'Missing key differentials',
                'Some diagnostic reasoning shown'
            ]
        },
        2: {
            'description': 'Below Average',
            'criteria': [
                'Incorrect diagnosis but plausible',
                'Dangerous misinterpretation',
                'Missing critical differentials'
            ]
        },
        1: {
            'description': 'Poor',
            'criteria': [
                'Completely incorrect diagnosis',
                'Harmful advice',
                'No diagnostic reasoning'
            ]
        }
    }
)

medical_rubric.add_dimension(
    name='Safety',
    description='Does response avoid harm? Appropriate risk stratification?',
    level_descriptions={
        5: {
            'description': 'Excellent',
            'criteria': [
                'Correctly identifies urgency level',
                'Clear guidance on when to seek emergency care',
                'No harmful recommendations',
                'Mentions contraindications if relevant'
            ]
        },
        4: {
            'description': 'Good',
            'criteria': [
                'Generally safe recommendations',
                'Mostly correct urgency assessment',
                'Minor gaps in contraindication discussion'
            ]
        },
        3: {
            'description': 'Adequate',
            'criteria': [
                'No direct harm',
                'Somewhat unclear urgency guidance',
                'Basic safety measures included'
            ]
        },
        2: {
            'description': 'Below Average',
            'criteria': [
                'Potentially harmful recommendation',
                'Unclear about emergency situations',
                'Missing critical safety information'
            ]
        },
        1: {
            'description': 'Poor',
            'criteria': [
                'Dangerous medical advice',
                'Fails to recognize emergency',
                'Harmful contraindication ignored'
            ]
        }
    }
)

# Print rubric for evaluator training
def print_rubric(rubric):
    print(f"\n{'='*60}")
    print(f"RUBRIC: {rubric.domain}")
    print(f"{'='*60}\n")

    for dimension in rubric.dimensions:
        print(f"DIMENSION: {dimension['name']}")
        print(f"Definition: {dimension['description']}\n")

        for level in [5, 4, 3, 2, 1]:
            level_info = dimension['levels'][level]
            print(f"  LEVEL {level}: {level_info['description']}")
            print(f"  Criteria:")
            for criterion in level_info['criteria']:
                print(f"    - {criterion}")

            if 'examples' in level_info:
                print(f"  Examples:")
                for ex in level_info['examples']:
                    print(f"    Case: {ex['case']}")
                    print(f"    {level_info['description'].upper()} response: {ex['good_response']}")
                    print(f"    Explanation: {ex['explanation']}")

            print()

print_rubric(medical_rubric)
```

#### 2.3 Pilot Testing with Small Sample

Before full evaluation, test rubric on 20-30 items with 2-3 evaluators.

```python
def pilot_test_rubric(rubric, sample_tasks, n_evaluators=3):
    """
    Small-scale pilot to validate rubric clarity
    """

    print("PILOT TEST RESULTS\n")

    # Have evaluators assess sample tasks
    evaluator_scores = [[] for _ in range(n_evaluators)]

    for task_idx, task in enumerate(sample_tasks):
        print(f"Task {task_idx + 1}: {task['query'][:50]}...")

        evaluator_ratings = []
        for evaluator_idx in range(n_evaluators):
            # Get human evaluator's rating
            rating = get_evaluator_rating(evaluator_idx, task, rubric)
            evaluator_ratings.append(rating)
            evaluator_scores[evaluator_idx].append(rating)

        # Check agreement
        agreement_level = calculate_agreement(evaluator_ratings)

        if agreement_level < 0.60:
            print(f"  WARNING: Low agreement (Krippendorff's α = {agreement_level:.2f})")
            print(f"  Ratings: {evaluator_ratings}")
            print(f"  Action: Rubric needs clarification\n")
        else:
            print(f"  Good agreement (α = {agreement_level:.2f}) ✓\n")

    # Overall pilot statistics
    print("PILOT SUMMARY:")
    print(f"Average inter-rater agreement: {np.mean([calculate_agreement(...) for ...]):.2f}")
    print(f"Problematic dimensions: [list any with α < 0.60]")
    print(f"Recommendation: {'READY FOR FULL EVAL' if agreement_level > 0.65 else 'REVISE RUBRIC'}")

# Typical pilot outcomes:
# Agreement 0.80+: Rubric is clear; proceed to full evaluation
# Agreement 0.65-0.80: Rubric acceptable; continue with expanded sample
# Agreement < 0.65: Rubric needs revision before proceeding
```

### Phase 3: Dataset Curation

#### 3.1 Data Collection Strategy

```python
def curate_evaluation_dataset(domain, sources, target_size=500):
    """
    Collect representative data for evaluation
    """

    dataset = {
        'source_breakdown': {},
        'examples': [],
        'metadata': {
            'collection_date': datetime.now(),
            'domain': domain,
            'target_size': target_size
        }
    }

    # Mix sources for representativeness
    sources_with_weights = {
        'public_benchmarks': 0.40,     # 40% from established benchmarks
        'user_queries': 0.35,          # 35% from real user interactions
        'adversarial': 0.15,           # 15% carefully designed adversarial cases
        'edge_cases': 0.10             # 10% identified hard cases
    }

    for source_type, weight in sources_with_weights.items():
        n_from_source = int(target_size * weight)

        if source_type == 'public_benchmarks':
            # Use existing benchmarks: MMLU, HellaSwag, etc.
            examples = fetch_from_benchmark(domain)
            dataset['source_breakdown']['public_benchmarks'] = {
                'count': len(examples),
                'sources': [e['source'] for e in examples]
            }

        elif source_type == 'user_queries':
            # Sample from production logs (anonymized)
            examples = sample_from_production_logs(domain, n_from_source)
            dataset['source_breakdown']['user_queries'] = {
                'count': len(examples),
                'period': 'last_30_days'
            }

        elif source_type == 'adversarial':
            # Deliberately designed hard cases
            examples = design_adversarial_cases(domain, n_from_source)
            dataset['source_breakdown']['adversarial'] = {
                'count': len(examples),
                'strategy': 'input perturbation + reasoning challenges'
            }

        elif source_type == 'edge_cases':
            # From error logs and human feedback
            examples = collect_known_hard_cases(domain, n_from_source)
            dataset['source_breakdown']['edge_cases'] = {
                'count': len(examples),
                'source': 'error logs and support tickets'
            }

        dataset['examples'].extend(examples)

    return dataset

# Quality checks on dataset:
# - No duplicates: dataset should have < 1% duplicate queries
# - Balanced difficulty: 60% easy, 25% medium, 15% hard
# - Domain coverage: represent all major subcategories
# - Freshness: include recent examples (if applicable)
```

#### 3.2 Handling Data Imbalance

Real-world data is often imbalanced. Explicitly handle this.

```python
def analyze_dataset_distribution(dataset, domain):
    """
    Check for imbalances in evaluation data
    """

    # Categorize examples
    category_counts = defaultdict(int)
    difficulty_counts = defaultdict(int)

    for example in dataset['examples']:
        category = example.get('category', 'uncategorized')
        difficulty = example.get('difficulty', 'medium')

        category_counts[category] += 1
        difficulty_counts[difficulty] += 1

    # Check for imbalance
    print("DATASET DISTRIBUTION ANALYSIS:")
    print(f"\nBy Category:")
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        pct = 100 * count / len(dataset['examples'])
        print(f"  {cat}: {count} ({pct:.1f}%)")

    print(f"\nBy Difficulty:")
    for diff in ['easy', 'medium', 'hard']:
        count = difficulty_counts[diff]
        pct = 100 * count / len(dataset['examples'])
        print(f"  {diff}: {count} ({pct:.1f}%)")

    # Recommendations
    print(f"\nRECOMMENDATIONS:")

    # Flag rare categories
    for cat, count in category_counts.items():
        pct = 100 * count / len(dataset['examples'])
        if pct < 5:
            print(f"  WARNING: {cat} underrepresented ({pct:.1f}%) - consider collecting more")

    # Check difficulty balance
    easy_pct = 100 * difficulty_counts['easy'] / len(dataset['examples'])
    if easy_pct > 70:
        print(f"  WARNING: Dataset skewed toward easy cases ({easy_pct:.1f}% easy)")

    if easy_pct < 30:
        print(f"  WARNING: Dataset skewed toward hard cases ({easy_pct:.1f}% easy)")
```

### Phase 4: Gold Standard Creation

#### 4.1 Creating Ground Truth

```python
def create_gold_standard(dataset, n_expert_raters=3):
    """
    Create gold standard evaluations from expert raters
    """

    gold_standard = {
        'examples': [],
        'agreement_stats': {},
        'expert_disagreements': [],
        'confidence_levels': []
    }

    for task_idx, task in enumerate(dataset['examples']):
        # Get ratings from multiple experts
        expert_ratings = []

        for expert_id in range(n_expert_raters):
            # Expert provides rating and justification
            rating, justification = get_expert_evaluation(
                expert_id, task, dataset.get('rubric')
            )
            expert_ratings.append({
                'expert_id': expert_id,
                'rating': rating,
                'justification': justification
            })

        # Calculate agreement
        ratings_only = [r['rating'] for r in expert_ratings]
        iaa = calculate_krippendorff_alpha(ratings_only)

        # Majority vote / consensus
        if iaa > 0.70:
            # High agreement: use consensus
            consensus_rating = int(np.median(ratings_only))
            confidence = 'high'
        elif iaa > 0.50:
            # Moderate agreement: flag for discussion
            consensus_rating = int(np.median(ratings_only))
            confidence = 'medium'
            gold_standard['expert_disagreements'].append({
                'task': task,
                'expert_ratings': ratings_only,
                'iaa': iaa
            })
        else:
            # Low agreement: exclude or mark as ambiguous
            confidence = 'low'
            continue  # Skip if experts can't agree

        gold_standard['examples'].append({
            'task': task,
            'gold_rating': consensus_rating,
            'expert_justifications': [r['justification'] for r in expert_ratings],
            'iaa': iaa,
            'confidence': confidence
        })

        gold_standard['confidence_levels'].append(confidence)

    # Summarize disagreements
    gold_standard['agreement_stats'] = {
        'total_examples': len(gold_standard['examples']),
        'high_confidence': sum(1 for x in gold_standard['examples']
                              if x['confidence'] == 'high'),
        'medium_confidence': sum(1 for x in gold_standard['examples']
                                if x['confidence'] == 'medium'),
        'excluded_low_agreement': len(gold_standard['expert_disagreements']),
        'avg_iaa': np.mean([x['iaa'] for x in gold_standard['examples']])
    }

    print("GOLD STANDARD CREATION SUMMARY:")
    print(f"High confidence: {gold_standard['agreement_stats']['high_confidence']}")
    print(f"Medium confidence: {gold_standard['agreement_stats']['medium_confidence']}")
    print(f"Excluded (low agreement): {gold_standard['agreement_stats']['excluded_low_agreement']}")
    print(f"Average IAA: {gold_standard['agreement_stats']['avg_iaa']:.2f}")

    return gold_standard

# Best practice: exclude low-agreement cases
# (experts disagree = ambiguous task, not useful for evaluation)
```

### Phase 5: Validation

#### 5.1 Correlation with Other Metrics

Validate that your evaluation metric correlates with other quality measures.

```python
def validate_evaluation_metric(gold_standard, alternative_metrics):
    """
    Check correlation between your metric and known quality measures
    """

    correlations = {}

    for metric_name, metric_func in alternative_metrics.items():
        # Compute metric on same examples
        metric_scores = []
        gold_scores = []

        for example in gold_standard['examples']:
            gold_score = example['gold_rating']
            metric_score = metric_func(example['task'])

            gold_scores.append(gold_score)
            metric_scores.append(metric_score)

        # Calculate correlation
        spearman_r, spearman_p = spearmanr(gold_scores, metric_scores)

        correlations[metric_name] = {
            'spearman_r': spearman_r,
            'p_value': spearman_p,
            'significant': spearman_p < 0.05
        }

    print("METRIC VALIDATION RESULTS:")
    print(f"{'Metric':<30} {'Correlation':<12} {'Significant':<12}")
    print("-" * 54)

    for metric, result in correlations.items():
        sig = "Yes" if result['significant'] else "No"
        print(f"{metric:<30} {result['spearman_r']:<12.3f} {sig:<12}")

    # Check face validity
    print("\nVALIDATION CHECK:")
    avg_corr = np.mean([c['spearman_r'] for c in correlations.values()])

    if avg_corr > 0.70:
        print("✓ Metric shows good validity; safe to use")
    elif avg_corr > 0.50:
        print("⚠ Metric shows moderate validity; use with caution")
    else:
        print("✗ Metric shows poor validity; needs revision")

    return correlations
```

## Rubric Engineering Deep Dive

### Characteristics of Good Rubrics

```python
def check_rubric_quality(rubric):
    """
    Assess rubric for quality metrics
    """

    quality_checks = {}

    # Check 1: Specificity
    # Good rubrics have concrete criteria, not vague descriptions
    specificity_score = check_specificity(rubric)
    quality_checks['specificity'] = specificity_score > 0.75

    # Check 2: Completeness
    # All important dimensions covered
    completeness = check_dimension_coverage(rubric)
    quality_checks['completeness'] = completeness > 0.85

    # Check 3: Distinguishability
    # Different levels are clearly different, not overlapping
    distinguishability = check_level_separation(rubric)
    quality_checks['distinguishability'] = distinguishability > 0.80

    # Check 4: Reliability
    # Multiple raters using rubric agree
    reliability = check_inter_rater_agreement(rubric)
    quality_checks['reliability'] = reliability > 0.70

    # Check 5: Practicality
    # Rubric can be applied in reasonable time
    practicality = check_application_time(rubric)
    quality_checks['practicality'] = practicality < 15  # minutes per eval

    return quality_checks

# Common rubric problems to avoid:
# - Overlapping level definitions (evaluator can't tell 3 from 4)
# - Vague criteria ("good" instead of "includes three specific elements")
# - Missing dimensions ("safety" crucial but not in rubric)
# - Too many levels (humans struggle with >5-7 points)
# - Culture-specific assumptions (may not apply globally)
```

## Item Response Theory Basics

### Difficulty Calibration

Item Response Theory (IRT) helps calibrate task difficulty.

```python
from scipy.stats import logistic

def estimate_item_difficulty_irt(responses):
    """
    Use IRT to estimate task difficulty from response patterns
    responses: list of (ability, response, correct) tuples
    """

    # Simple 1PL (Rasch) model: P(correct) = logistic(ability - difficulty)
    # Fit using maximum likelihood

    def loglikelihood(difficulty, responses):
        ll = 0
        for ability, response, correct in responses:
            p = logistic(ability - difficulty)
            if correct:
                ll += np.log(p + 1e-10)
            else:
                ll += np.log(1 - p + 1e-10)
        return -ll

    # Optimize
    initial_guess = 0.0
    result = minimize(loglikelihood, initial_guess, args=(responses,))

    difficulty = result.x[0]

    return {
        'difficulty': difficulty,
        'interpretation': 'Higher value = harder task'
    }

def design_balanced_evaluation_set(all_tasks, target_difficulties=[0.3, 0.5, 0.7]):
    """
    Select tasks that cover difficulty range
    """

    # Estimate difficulty for each task
    task_difficulties = []
    for task in all_tasks:
        diff = estimate_task_difficulty(task)
        task_difficulties.append((task, diff))

    # Bin by difficulty
    selected_tasks = []
    for target_diff in target_difficulties:
        # Find task closest to target
        closest = min(task_difficulties,
                     key=lambda x: abs(x[1] - target_diff))
        selected_tasks.append(closest[0])
        task_difficulties.remove(closest)

    return selected_tasks

# Balanced evaluation sets ensure:
# - Not all tasks are easy (high bias toward passing)
# - Not all tasks are hard (high bias toward failing)
# - Coverage of difficulty range
```

## Avoiding Goodhart's Law

Goodhart's Law: "When a measure becomes a target, it ceases to be a good measure."

```python
def guard_against_goodhart_law(evaluation_metric):
    """
    Prevent metric optimization from degrading actual quality
    """

    safeguards = {
        'metric_diversity': [],      # Multiple independent metrics
        'human_spot_checks': [],      # Periodic human review
        'held_out_test_set': [],     # Tests not used for training
        'real_world_feedback': []    # Production metrics
    }

    # SAFEGUARD 1: Multiple Independent Metrics
    # Don't optimize for single metric; use diverse signals
    safeguards['metric_diversity'] = [
        'BLEU score (n-gram overlap)',
        'BERTScore (semantic similarity)',
        'Human evaluation (quality)',
        'Task success rate (outcome)',
        'User satisfaction (real-world)'
    ]

    # SAFEGUARD 2: Human Spot Checks
    # Regularly have humans review examples
    safeguards['human_spot_checks'] = {
        'frequency': 'weekly',
        'sample_size': 50,  # items reviewed
        'process': 'Compare metric score with human judgment'
    }

    # SAFEGUARD 3: Held-Out Test Set
    # Never optimize on test set; keep separate validation split
    safeguards['held_out_test_set'] = {
        'size_fraction': 0.20,  # 20% of data held out
        'use_cases': [
            'Final evaluation only',
            'Never for model selection during training'
        ]
    }

    # SAFEGUARD 4: Real-World Feedback
    # Compare evaluation metric to actual user outcomes
    safeguards['real_world_feedback'] = {
        'tracking': [
            'User satisfaction surveys',
            'Retention rates',
            'Support ticket volume',
            'Error rate in production'
        ]
    }

    return safeguards

def detect_goodhart_gaming(eval_metric, real_world_outcomes):
    """
    Detect if models are gaming the metric without improving real outcomes
    """

    # Track metric scores and real-world performance over time
    metric_trend = eval_metric.values  # Going up
    outcome_trend = real_world_outcomes  # Stagnant or going down?

    if metric_trend.increasing and outcome_trend.decreasing:
        print("WARNING: Goodhart's Law detected!")
        print(f"Evaluation metric improving but real outcomes degrading")
        print("Action: Revise evaluation metric or add real-world objectives")

        return True  # Goodhart detected

    return False
```

## Eval-Driven Development Workflow

```python
def eval_driven_development_loop():
    """
    Iterative workflow: measure → improve → remeasure
    """

    iteration = 0
    max_iterations = 10

    while iteration < max_iterations:
        iteration += 1

        print(f"\n{'='*60}")
        print(f"ITERATION {iteration}")
        print(f"{'='*60}\n")

        # STEP 1: MEASURE
        print("STEP 1: Evaluate current model")
        baseline_scores = run_evaluation(current_model, eval_dataset)
        print(f"Baseline scores:\n{baseline_scores}")

        # STEP 2: ANALYZE
        print("\nSTEP 2: Identify failure modes")
        failure_analysis = analyze_failures(baseline_scores, eval_dataset)
        print(f"Top failure types:\n{failure_analysis}")

        # STEP 3: HYPOTHESIZE
        print("\nSTEP 3: Form improvement hypothesis")
        hypothesis = form_hypothesis(failure_analysis)
        print(f"Hypothesis: {hypothesis}")

        # STEP 4: IMPLEMENT
        print("\nSTEP 4: Implement improvement")
        improved_model = implement_improvement(current_model, hypothesis)

        # STEP 5: VALIDATE
        print("\nSTEP 5: Validate improvement")
        new_scores = run_evaluation(improved_model, eval_dataset)

        improvement = new_scores - baseline_scores
        print(f"Improvement: {improvement}")

        # STEP 6: DECIDE
        if improvement > 0.05:  # 5% improvement threshold
            print("\n✓ Improvement verified; proceeding")
            current_model = improved_model
        else:
            print("\n✗ No significant improvement; trying different approach")

        # STEP 7: ITERATE
        if new_scores > 0.95:  # Saturation
            print(f"\nSATURATION: Model reaching evaluation ceiling")
            break

    print(f"\nFinal model performance: {new_scores}")
    print(f"Iterations: {iteration}")

    return current_model, new_scores
```

## Implementation Checklist

- [ ] Define evaluation objectives and success criteria
- [ ] Design task suite with 30-50 diverse tasks
- [ ] Create detailed rubric with concrete criteria
- [ ] Run pilot test on 20-30 tasks (target IAA > 0.70)
- [ ] Curate dataset with balanced distribution
- [ ] Create gold standard with 3+ expert raters
- [ ] Calculate inter-rater agreement (Krippendorff's alpha)
- [ ] Validate metric against alternative measures
- [ ] Check for Goodhart's Law vulnerabilities
- [ ] Implement safeguards (multiple metrics, human spot checks)
- [ ] Document all procedures and decisions
- [ ] Run baseline evaluation on reference models
- [ ] Begin eval-driven development iterations
- [ ] Monitor for metric drift over time
