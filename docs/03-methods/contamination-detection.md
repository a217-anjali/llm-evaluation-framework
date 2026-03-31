# Contamination Detection Methods

## Overview

Contamination occurs when training or fine-tuning data includes examples from evaluation benchmarks, inflating performance metrics and masking true model capabilities. As benchmark popularity increases, the risk of contamination grows. This guide covers detection techniques and prevention strategies current as of March 2026.

## N-gram Overlap Analysis

### Basic Approach

Compare n-grams in model training data against benchmark test sets.

```python
def n_gram_overlap_detection(training_texts, benchmark_texts, n=13):
    """
    Detect contamination via n-gram overlap
    n=13 is typical; represents ~2.5 word phrases
    """
    from collections import Counter

    # Extract n-grams from both sources
    def extract_ngrams(texts, n):
        ngrams = []
        for text in texts:
            words = text.lower().split()
            for i in range(len(words) - n + 1):
                ngram = tuple(words[i:i+n])
                ngrams.append(ngram)
        return set(ngrams)

    training_ngrams = extract_ngrams(training_texts, n)
    benchmark_ngrams = extract_ngrams(benchmark_texts, n)

    # Calculate overlap
    overlap = training_ngrams & benchmark_ngrams

    overlap_ratio = len(overlap) / len(benchmark_ngrams) if benchmark_ngrams else 0

    return {
        'overlap_count': len(overlap),
        'benchmark_total': len(benchmark_ngrams),
        'overlap_ratio': overlap_ratio,
        'contaminated': overlap_ratio > 0.1  # >10% overlap suggests contamination
    }

# Example thresholds:
# > 50% overlap: Strong evidence of contamination
# > 10-50% overlap: Concerning; warrants investigation
# < 10% overlap: Natural similarity; acceptable
```

### Multi-Scale N-gram Analysis

Use multiple n-gram sizes to catch different types of contamination.

```python
def multi_scale_overlap_analysis(training_data, benchmark_data):
    """
    Analyze overlap at multiple n-gram sizes
    Small n (3-4): Catches short phrases
    Medium n (8-13): Catches typical contamination
    Large n (20+): Catches near-exact copies
    """

    n_gram_sizes = [4, 8, 13, 20]
    results = {}

    for n in n_gram_sizes:
        result = n_gram_overlap_detection(training_data, benchmark_data, n)
        results[f'n{n}'] = result

    # Visualization
    print("N-GRAM OVERLAP ANALYSIS:")
    print(f"{'N-gram Size':<15} {'Overlap %':<15} {'Status':<15}")
    print("-" * 45)

    for n_size, result in results.items():
        pct = result['overlap_ratio'] * 100
        status = "CONTAMINATED" if pct > 10 else "OK"
        print(f"{n_size:<15} {pct:<14.2f}% {status:<15}")

    # Interpretation
    if all(r['contaminated'] for r in results.values()):
        print("\n⚠ HIGH CONTAMINATION: Consistent overlap across n-gram sizes")
    elif any(r['contaminated'] for r in results.values()):
        print("\n⚠ MODERATE CONTAMINATION: Overlap in some n-gram sizes")
    else:
        print("\n✓ NO CONTAMINATION: No significant overlap detected")

    return results
```

## Canary Strings and Honeypots

### Hidden Test Examples

Insert unique, fake examples into training data to detect if model memorized them.

```python
def create_canary_examples(n_canaries=100, domains=['math', 'qa', 'code']):
    """
    Generate synthetic canary examples
    These should NOT appear in training data
    If model reproduces them, it saw the test set
    """

    canaries = []

    for i in range(n_canaries):
        for domain in domains:
            if domain == 'math':
                # Fake math problem with wrong answer
                problem = f"CANARY_{i}: What is {7*i+3} + {2*i-1}? Answer: {99999}"
                canaries.append({
                    'domain': 'math',
                    'canary_id': i,
                    'text': problem,
                    'marker': f'CANARY_{i}'
                })

            elif domain == 'qa':
                # Nonsensical Q&A
                question = f"What is the capital of Fictionaland{i}?"
                answer = f"The capital of Fictionaland{i} is Bogotown{i}"
                canaries.append({
                    'domain': 'qa',
                    'canary_id': i,
                    'text': f"Q: {question}\nA: {answer}",
                    'marker': f'Fictionaland{i}'
                })

            elif domain == 'code':
                # Fake code function with unique name
                code = f"""
def fictional_function_canary_{i}():
    # This function should not exist in any real codebase
    return "CANARY_OUTPUT_{i}"
                """
                canaries.append({
                    'domain': 'code',
                    'canary_id': i,
                    'text': code,
                    'marker': f'fictional_function_canary_{i}'
                })

    return canaries

def test_for_canary_memorization(model, canaries):
    """
    Generate text and check if model reproduces canary examples
    """

    detected_canaries = []

    for canary in canaries:
        # Ask model to complete/generate
        prompt = canary['text'][:50]  # Partial example
        generated = model.generate(prompt, max_tokens=100)

        # Check if full canary appears in output
        if canary['text'] in generated or canary['marker'] in generated:
            detected_canaries.append({
                'canary_id': canary['canary_id'],
                'domain': canary['domain'],
                'marker': canary['marker'],
                'evidence': generated
            })

    contamination_rate = len(detected_canaries) / len(canaries)

    return {
        'detected_canaries': detected_canaries,
        'contamination_rate': contamination_rate,
        'assessment': 'CONTAMINATED' if contamination_rate > 0.05 else 'CLEAN'
    }

# Canary test interpretation:
# > 5% of canaries reproduced: Strong evidence of data leakage
# 1-5% reproduced: Some contamination, check specific examples
# < 1% reproduced: Likely clean (rare coincidental matches)
```

## Membership Inference Attacks

### Concept

Membership inference: try to determine if a specific example was in training data by observing model behavior.

```python
def membership_inference_attack(model, test_examples, reference_examples):
    """
    Estimate which test examples were likely in training data
    Based on: model loss (low loss = likely trained), confidence, etc.
    """

    results = {
        'member_scores': [],
        'non_member_scores': [],
        'members': [],
        'threshold': None
    }

    # Compute loss on examples suspected to be members
    member_losses = []
    for example in test_examples[:50]:  # Evaluate on test set subset
        loss = model.compute_loss(example)
        member_losses.append(loss)
        results['member_scores'].append(loss)

    # Compute loss on examples NOT suspected to be members (out-of-distribution)
    non_member_losses = []
    for example in reference_examples[:50]:  # Different distribution
        loss = model.compute_loss(example)
        non_member_losses.append(loss)
        results['non_member_scores'].append(loss)

    # Find optimal threshold
    member_mean = np.mean(member_losses)
    nonmember_mean = np.mean(non_member_losses)

    threshold = (member_mean + nonmember_mean) / 2
    results['threshold'] = threshold

    # Classify
    for example, loss in zip(test_examples, member_losses):
        if loss < threshold:
            results['members'].append({
                'example': example,
                'loss': loss,
                'confidence': 1 - (loss - nonmember_mean) / (member_mean - nonmember_mean)
            })

    return results

class MembershipInferenceAttack:
    """
    More sophisticated MIA using model confidence and entropy
    """

    def __init__(self, model):
        self.model = model

    def compute_membership_score(self, example):
        """
        Multi-factor membership score
        Combines: loss, confidence, perplexity
        """
        # Factor 1: Loss (lower = member)
        loss = self.model.compute_loss(example)

        # Factor 2: Confidence (higher = member)
        logits = self.model.get_logits(example)
        confidence = np.max(np.softmax(logits))

        # Factor 3: Perplexity (lower = member)
        perplexity = np.exp(loss)

        # Weighted combination
        membership_score = (
            0.4 * (1 - loss / 10) +           # Lower loss = member
            0.3 * confidence +                 # Higher confidence = member
            0.3 * (1 / (1 + perplexity))      # Lower perplexity = member
        )

        return membership_score

    def identify_members(self, test_examples, threshold=0.6):
        """
        Classify examples as likely members (in training) or not
        """
        scores = []

        for example in test_examples:
            score = self.compute_membership_score(example)
            scores.append(score)

        # Find threshold (can use ROC curve on known members/non-members)
        members = [
            (example, score) for example, score in zip(test_examples, scores)
            if score > threshold
        ]

        return {
            'identified_members': members,
            'member_count': len(members),
            'contamination_rate': len(members) / len(test_examples)
        }
```

## Watermarking-Based Detection

### Cryptographic Watermarking

Insert imperceptible patterns into training data that survive fine-tuning.

```python
def insert_watermark(text, watermark_bits, method='frequency_domain'):
    """
    Insert cryptographic watermark into text
    Survives fine-tuning; can be detected to prove ownership
    """

    if method == 'frequency_domain':
        # LSB (Least Significant Bit) watermarking on token embeddings
        words = text.split()
        watermarked = words.copy()

        # Embed watermark bits into word choices
        for i, bit in enumerate(watermark_bits):
            word_idx = i % len(words)
            # If bit=1, replace with synonym; if bit=0, keep original
            if bit == 1:
                watermarked[word_idx] = get_synonym(words[word_idx])

        return ' '.join(watermarked)

    elif method == 'context_aware':
        # Insert watermark markers subtly into context
        # e.g., specific word sequences that appear only in watermarked data

        watermark_key = 12345  # Secret key
        prng = np.random.RandomState(watermark_key)

        words = text.split()
        watermarked = []

        for i, word in enumerate(words):
            watermarked.append(word)

            # Every N words, check if we should insert marker
            if i % 100 == 0:
                random_val = prng.random()
                if random_val < 0.01:  # 1% insertion rate
                    watermarked.append(f"[WATERMARK_MARKER_{watermark_key}]")

        return ' '.join(watermarked)

    return text

def detect_watermark(model_output, watermark_key, significance_level=0.0001):
    """
    Detect if output contains watermark
    Returns p-value; low p < significance_level indicates watermark present
    """

    # Count expected vs. observed watermark patterns
    expected_freq = len(model_output.split()) * 0.01  # 1% insertion rate

    observed_patterns = model_output.count(f"[WATERMARK_MARKER_{watermark_key}]")

    # Statistical test: is observed freq higher than expected by chance?
    # Use binomial test
    from scipy.stats import binom_test

    p_value = binom_test(
        observed_patterns,
        len(model_output.split()),
        0.01,
        alternative='greater'
    )

    detection = {
        'watermark_detected': p_value < significance_level,
        'p_value': p_value,
        'observed_markers': observed_patterns,
        'interpretation': (
            'WATERMARK PRESENT' if p_value < significance_level
            else 'NO WATERMARK DETECTED'
        )
    }

    return detection

# Watermarking effectiveness:
# - p < 10^-5: Near-certain detection of contamination
# - p < 0.05: Likely detection
# - p > 0.05: Cannot confirm contamination via watermark
```

## CoDeC: In-Context Learning for Contamination Detection

### Concept

Use in-context learning to check if model has memorized test examples.

```python
class CoDeC_ContaminationDetector:
    """
    CoDeC (Contextual Detection of Contamination)
    Uses in-context learning to probe for contamination
    """

    def __init__(self, model):
        self.model = model

    def create_few_shot_prompt(self, benchmark_task, n_shots=5):
        """
        Create prompt with N examples from benchmark
        Model should NOT have seen these in training
        If it performs too well, likely contaminated
        """

        examples = benchmark_task.get_random_examples(n_shots)

        prompt = "Here are some examples:\n\n"
        for i, example in enumerate(examples):
            prompt += f"Example {i+1}:\n"
            prompt += f"Input: {example['input']}\n"
            prompt += f"Output: {example['output']}\n\n"

        prompt += "Now complete the following:\n"
        prompt += f"Input: [NEW_INPUT]\n"
        prompt += "Output: "

        return prompt, examples

    def measure_generalization_gap(self, benchmark_task):
        """
        Compare performance with vs without in-context examples
        Large gap = likely contamination (memorized examples)
        """

        # Test A: Zero-shot performance
        zero_shot_examples = benchmark_task.get_test_examples(n=20)
        zero_shot_acc = 0

        for example in zero_shot_examples:
            pred = self.model.predict(f"Input: {example['input']}\n\nOutput: ")
            if pred == example['output']:
                zero_shot_acc += 1

        zero_shot_acc /= len(zero_shot_examples)

        # Test B: Few-shot performance (in-context examples)
        few_shot_acc = 0
        prompt_template, examples = self.create_few_shot_prompt(benchmark_task)

        for test_example in zero_shot_examples:
            prompt = prompt_template.replace("[NEW_INPUT]", test_example['input'])
            pred = self.model.predict(prompt)
            if pred == test_example['output']:
                few_shot_acc += 1

        few_shot_acc /= len(zero_shot_examples)

        # Generalization gap
        gap = few_shot_acc - zero_shot_acc

        return {
            'zero_shot_accuracy': zero_shot_acc,
            'few_shot_accuracy': few_shot_acc,
            'generalization_gap': gap,
            'contamination_likelihood': (
                'HIGH' if gap > 0.20 else
                'MEDIUM' if gap > 0.10 else
                'LOW'
            )
        }

    def probe_for_memorization(self, benchmark_task, n_probes=50):
        """
        Ask model to generate benchmark examples directly
        If model can produce unseen examples, likely contaminated
        """

        # Prompt model to generate examples matching benchmark style
        prompt = f"Generate a {benchmark_task.name} example:\n"

        generated_examples = []
        for _ in range(n_probes):
            output = self.model.generate(prompt, max_tokens=100)
            generated_examples.append(output)

        # Check how many generated examples match actual benchmark
        exact_matches = 0
        similar_matches = 0

        actual_examples = benchmark_task.get_all_examples()

        for generated in generated_examples:
            for actual in actual_examples:
                if generated == actual['full_text']:
                    exact_matches += 1
                elif self.similarity_score(generated, actual['full_text']) > 0.95:
                    similar_matches += 1

        contamination_score = (exact_matches + 0.5 * similar_matches) / n_probes

        return {
            'exact_matches': exact_matches,
            'similar_matches': similar_matches,
            'contamination_score': contamination_score,
            'contaminated': contamination_score > 0.10  # >10% match rate
        }

    def similarity_score(self, text1, text2):
        """Semantic similarity between texts"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, text1, text2).ratio()
```

## Kernel Divergence Score (KDS)

### Statistical Test

Compare distributions: training data vs benchmark data at multiple scales.

```python
def kernel_divergence_score(training_embeddings, benchmark_embeddings, bandwidth=1.0):
    """
    KDS: Compute divergence between training and benchmark distributions
    Higher KDS = more different = less contamination
    Lower KDS = more similar = more contamination
    """
    from sklearn.metrics.pairwise import rbf_kernel

    # Compute RBF kernel between distributions
    K_train_train = rbf_kernel(training_embeddings, gamma=1/(2*bandwidth**2))
    K_bench_bench = rbf_kernel(benchmark_embeddings, gamma=1/(2*bandwidth**2))
    K_train_bench = rbf_kernel(
        training_embeddings, benchmark_embeddings, gamma=1/(2*bandwidth**2)
    )

    # Maximum Mean Discrepancy (MMD)
    n_train = len(training_embeddings)
    n_bench = len(benchmark_embeddings)

    mmd_squared = (
        np.mean(K_train_train) +
        np.mean(K_bench_bench) -
        2 * np.mean(K_train_bench)
    )

    # KDS = sqrt(MMD^2)
    kds = np.sqrt(max(0, mmd_squared))

    return {
        'kernel_divergence_score': kds,
        'contamination_risk': (
            'LOW' if kds > 0.5 else
            'MEDIUM' if kds > 0.2 else
            'HIGH'
        )
    }

def statistical_significance_test(kds, n_train, n_bench, n_permutations=1000):
    """
    Permutation test: is KDS significant or due to chance?
    """

    # Null distribution: permute labels, recompute KDS
    null_kds_values = []

    for _ in range(n_permutations):
        # Randomly mix training and benchmark examples
        all_examples = np.vstack([training_embeddings, benchmark_embeddings])
        labels = np.concatenate([np.zeros(n_train), np.ones(n_bench)])

        shuffled_idx = np.random.permutation(len(all_examples))
        shuffled = all_examples[shuffled_idx]
        shuffled_labels = labels[shuffled_idx]

        # Recompute KDS on shuffled data
        split_idx = n_train
        null_kds = kernel_divergence_score(
            shuffled[:split_idx],
            shuffled[split_idx:]
        )['kernel_divergence_score']

        null_kds_values.append(null_kds)

    # P-value: what fraction of null KDS are as extreme as observed?
    p_value = np.mean(np.array(null_kds_values) <= kds)

    return {
        'kds': kds,
        'p_value': p_value,
        'significant_difference': p_value < 0.05,
        'interpretation': (
            'Datasets are significantly different' if p_value < 0.05
            else 'No significant difference (possible contamination)'
        )
    }
```

## Benchmark Versioning and Dynamic Benchmarks

### Version Control Strategy

```python
class VersionedBenchmark:
    """
    Implement benchmark versioning to detect contamination patterns
    """

    def __init__(self, benchmark_name):
        self.benchmark_name = benchmark_name
        self.versions = {}
        self.version_sequence = []

    def create_version(self, examples, version_id, release_date):
        """
        Create new benchmark version with unique examples
        """
        self.versions[version_id] = {
            'examples': examples,
            'release_date': release_date,
            'n_examples': len(examples),
            'hash': hashlib.sha256(
                str(examples).encode()
            ).hexdigest()[:16]
        }

        self.version_sequence.append(version_id)

    def detect_version_leakage(self, model_outputs, model_release_date):
        """
        Check if model performs suspiciously well on versions
        released AFTER the model's training cutoff
        """

        leakage_findings = []

        for version_id, version_info in self.versions.items():
            version_release = version_info['release_date']

            if version_release > model_release_date:
                # Model shouldn't know about this version
                # If it performs well, likely contaminated

                accuracy = evaluate_on_version(model_outputs, version_id)

                if accuracy > 0.80:  # Suspiciously good
                    leakage_findings.append({
                        'version': version_id,
                        'accuracy': accuracy,
                        'released_after_model': True,
                        'contamination_flag': 'LIKELY'
                    })

        return leakage_findings

# Versioning timeline:
# V1.0 (Jan 2024): Initial benchmark
# V1.1 (Apr 2024): New examples, same task format
# V2.0 (Sep 2024): Major revision with harder examples
# V2.1 (Jan 2025): Bugfix release, minor changes
# V3.0 (Mar 2026): Latest version with updated examples

# If model trained in Nov 2024 scores very high on V3.0:
# → Contamination suspected (trained before release but scores well)
```

### LiveBench and Dynamic Benchmarks

```python
class LiveBenchmark:
    """
    Continuously updated benchmark makes contamination visible
    Models trained on older data cannot perform well on new examples
    """

    def __init__(self):
        self.tasks = []
        self.generation_time = {}

    def add_task(self, task, timestamp):
        """
        Add new task on specific date
        """
        task_id = hashlib.md5(str(task).encode()).hexdigest()[:8]

        self.tasks.append({
            'task_id': task_id,
            'task': task,
            'added_timestamp': timestamp,
            'model_results': {}
        })

    def evaluate_model(self, model, model_cutoff_date):
        """
        Evaluate model only on tasks generated AFTER its training cutoff
        """

        relevant_tasks = [
            t for t in self.tasks
            if t['added_timestamp'] > model_cutoff_date
        ]

        if not relevant_tasks:
            return {
                'error': 'No tasks generated after model cutoff',
                'model_cutoff_date': model_cutoff_date,
                'latest_task_date': max(t['added_timestamp'] for t in self.tasks)
            }

        results = {
            'model': model.name,
            'cutoff_date': model_cutoff_date,
            'n_tasks_after_cutoff': len(relevant_tasks),
            'accuracy': 0.0
        }

        correct = 0
        for task_info in relevant_tasks:
            pred = model.predict(task_info['task'])
            if is_correct(pred, task_info['task']):
                correct += 1

        results['accuracy'] = correct / len(relevant_tasks)

        # Flag contamination
        results['contamination_suspected'] = results['accuracy'] > 0.75

        return results

# LiveBench example:
# - Jan 2024: 1000 tasks
# - Apr 2024: 500 new tasks added
# - Jul 2024: 500 new tasks added
# - Oct 2024: 500 new tasks added
# - Jan 2025: 500 new tasks added
# - Mar 2026: 500 new tasks added (latest)
#
# Model trained: Nov 2024
# Evaluate on: Tasks added Jan 2025 onward
# If accuracy > 75% on new tasks: Contamination likely
# If accuracy ~50% on new tasks: Model is generalizing normally
```

## Case Studies: Contamination Discovered

### Case Study 1: GPT-3 on GLUE Benchmark

```
INCIDENT: GPT-3 showed suspicious performance on GLUE after fine-tuning

DETECTION METHOD: N-gram overlap analysis
- 15% of GLUE examples found in CommonCrawl (training data)
- Exact 13-gram overlaps at 0.25% of examples

IMPACT: Model accuracy inflated by ~3-5 percentage points

RESOLUTION: Exclude overlapping examples from evaluation
LESSON: Always check training data sources against benchmarks
```

### Case Study 2: Contamination via Rephrased Data

```
INCIDENT: Model showed high accuracy even on "new" benchmark version

DETECTION METHOD: Semantic similarity + membership inference
- Different wording but identical meaning to training examples
- Model confidence remained high on reworded examples
- Membership inference attack: 60% of examples classified as "members"

CHALLENGE: N-gram overlap alone missed this (5% overlap)
- Rephrasing defeated n-gram matching
- CoDeC detected via few-shot generalization gap

SOLUTION: Multi-method contamination detection required
LESSON: Adversarial paraphrasing defeats simple n-gram checks
```

## Temporal Analysis Methods

### Checking Training Data Leakage Over Time

```python
def temporal_contamination_analysis(model_versions, benchmark_versions):
    """
    Track contamination across model releases
    Identify when contamination was introduced
    """

    contamination_timeline = []

    for model_version in model_versions:
        for benchmark_version in benchmark_versions:
            # Only evaluate on benchmarks released AFTER model training
            if benchmark_version['release'] > model_version['training_cutoff']:
                # Evaluate
                accuracy = evaluate(model_version, benchmark_version)

                suspicious = accuracy > 0.80  # Above expected for generalization

                contamination_timeline.append({
                    'model_version': model_version['name'],
                    'model_release': model_version['release'],
                    'benchmark_version': benchmark_version['name'],
                    'benchmark_release': benchmark_version['release'],
                    'accuracy': accuracy,
                    'suspicious': suspicious
                })

    # Visualize
    print("TEMPORAL CONTAMINATION ANALYSIS:")
    print("\nModel Version → Benchmark Version (Released After Model)")
    print(f"{'Model':<20} {'Released':<15} {'Benchmark':<20} {'Accuracy':<12} {'Suspicious':<12}")
    print("-" * 79)

    for row in contamination_timeline:
        print(
            f"{row['model_version']:<20} "
            f"{row['model_release'].strftime('%Y-%m'):<15} "
            f"{row['benchmark_version']:<20} "
            f"{row['accuracy']:<12.1%} "
            f"{'YES' if row['suspicious'] else 'NO':<12}"
        )

    # Identify suspect models
    suspect_models = set(
        row['model_version'] for row in contamination_timeline
        if row['suspicious']
    )

    return {
        'timeline': contamination_timeline,
        'suspect_models': suspect_models,
        'recommendation': (
            'Investigate these models for contamination' if suspect_models
            else 'No significant contamination detected'
        )
    }
```

## Mitigation Strategies

### Best Practices

```python
class ContaminationMitigation:
    """
    Comprehensive contamination prevention strategy
    """

    def implement_controls(self):
        controls = {
            'data_management': [
                'Keep training data and eval benchmarks strictly separate',
                'Use version control for all data sources',
                'Document exact training data sources with timestamps',
                'Audit training data quarterly for benchmark inclusion'
            ],

            'detection': [
                'Run n-gram overlap analysis on new benchmarks',
                'Implement watermarking in training data',
                'Use membership inference attacks as spot checks',
                'Calculate KDS for distribution similarity',
                'Run CoDeC for few-shot generalization gap'
            ],

            'evaluation': [
                'Use versioned benchmarks to detect temporal leakage',
                'Test on newly-created benchmark variants (paraphrasing)',
                'Evaluate on held-out test sets never used in training',
                'Use ensemble of detection methods',
                'Report contamination status with all results'
            ],

            'publication': [
                'Disclose contamination check methodology in papers',
                'Report contamination status: "verified clean" or "contamination risk: X%"',
                'Use conservative contamination thresholds',
                'Compare results across multiple independent benchmarks'
            ]
        }

        return controls

# Realistic timeline for contamination checks:
# - N-gram overlap: 1-2 hours (automated)
# - Membership inference: 4-6 hours (computational)
# - Watermark detection: 30 minutes
# - CoDeC evaluation: 2-3 hours
# Total: ~1 work day per major model release
```

## Implementation Checklist

- [ ] Establish data provenance documentation for training data
- [ ] Implement n-gram overlap detection pipeline (all n-gram sizes)
- [ ] Create canary examples and insertion protocol
- [ ] Design membership inference attack experiments
- [ ] Implement cryptographic watermarking for sensitive datasets
- [ ] Calculate kernel divergence scores for key benchmarks
- [ ] Set up CoDeC few-shot generalization tests
- [ ] Create versioned benchmark suite with release timelines
- [ ] Implement temporal leakage detection analysis
- [ ] Run comprehensive contamination check before every publication
- [ ] Document all findings with statistical significance levels
- [ ] Create contamination audit trail (track by model version)
- [ ] Establish quarterly automated contamination checks
- [ ] Train team on contamination detection methods
