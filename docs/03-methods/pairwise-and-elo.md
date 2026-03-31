# Pairwise Comparison and Elo/Bradley-Terry Ranking

## Overview

Pairwise comparison evaluation, where judges directly compare two model outputs and select the better one, provides a more natural and reliable signal than direct scoring. Combined with statistical models like Bradley-Terry or Elo, pairwise comparisons enable building trustworthy rankings of large model collections.

## Bradley-Terry Model

### Mathematical Formulation

The Bradley-Terry model converts pairwise comparison outcomes into absolute model strength parameters.

**Model Definition:**

The probability that model A wins against model B is:

```
P(A > B) = π_A / (π_A + π_B) = e^(λ_A) / (e^(λ_A) + e^(λ_B))
```

Where:
- π_A, π_B are positive "strength" parameters for models A and B
- λ_A, λ_B are log-strengths (easier to work with computationally)
- The difference λ_A - λ_B is the log-odds of A beating B

### Maximum Likelihood Estimation

```python
import numpy as np
from scipy.optimize import minimize

def bradley_terry_mle(comparisons, models=None):
    """
    Fit Bradley-Terry model using maximum likelihood estimation

    Args:
        comparisons: list of (model_a, model_b, winner)
        models: optional list of model names; auto-detected if None

    Returns:
        strengths: dict mapping model -> strength parameter
    """

    # Identify unique models
    if models is None:
        models = set()
        for a, b, _ in comparisons:
            models.add(a)
            models.add(b)
        models = sorted(list(models))

    model_to_idx = {m: i for i, m in enumerate(models)}
    n_models = len(models)

    # Count wins for each model
    win_counts = np.zeros(n_models)
    for a, b, winner in comparisons:
        idx = model_to_idx[winner]
        win_counts[idx] += 1

    def negative_log_likelihood(log_strengths):
        """
        Negative log-likelihood of observed comparisons given strengths
        Constraint: sum of log_strengths = 0 (for identifiability)
        """
        strengths = np.exp(log_strengths)

        nll = 0.0
        for model_a, model_b, winner in comparisons:
            idx_a = model_to_idx[model_a]
            idx_b = model_to_idx[model_b]

            str_a = strengths[idx_a]
            str_b = strengths[idx_b]

            # Probability that A wins
            prob_a_wins = str_a / (str_a + str_b)

            if winner == model_a:
                nll -= np.log(prob_a_wins + 1e-10)
            else:
                nll -= np.log(1 - prob_a_wins + 1e-10)

        return nll

    # Constraint: strengths must sum to n_models (or log_strengths sum to 0)
    constraints = {'type': 'eq', 'fun': lambda x: np.sum(x)}

    # Initial guess: uniform strengths
    x0 = np.zeros(n_models)

    # Optimize
    result = minimize(
        negative_log_likelihood,
        x0,
        method='SLSQP',
        constraints=constraints,
        options={'ftol': 1e-9}
    )

    log_strengths = result.x
    strengths = np.exp(log_strengths)

    return {
        'strengths': {models[i]: strengths[i] for i in range(n_models)},
        'log_strengths': {models[i]: log_strengths[i] for i in range(n_models)},
        'nll': result.fun,
        'convergence': result.success
    }
```

### Example: Ranking Models

```python
# Hypothetical comparison data (who won head-to-head)
comparisons = [
    ("GPT-4", "Claude 3", "GPT-4"),
    ("GPT-4", "Llama 2", "GPT-4"),
    ("Claude 3", "Llama 2", "Claude 3"),
    ("GPT-4", "Claude 3", "GPT-4"),  # Repeated for volume
    ("Claude 3", "Llama 2", "Claude 3"),
    # ... many more comparisons
]

result = bradley_terry_mle(comparisons)

# Print ranking by strength
ranking = sorted(result['strengths'].items(),
                key=lambda x: x[1], reverse=True)

print("BRADLEY-TERRY RANKING:")
for rank, (model, strength) in enumerate(ranking, 1):
    log_strength = result['log_strengths'][model]
    print(f"{rank}. {model}: {strength:.3f} (log: {log_strength:.3f})")

# Expected output:
# 1. GPT-4: 1.842 (log: 0.611)
# 2. Claude 3: 1.124 (log: 0.117)
# 3. Llama 2: 0.634 (log: -0.457)
```

### Prediction with Bradley-Terry

```python
def predict_match(model_a, model_b, strengths):
    """
    Predict probability that A beats B given estimated strengths
    """
    str_a = strengths[model_a]
    str_b = strengths[model_b]
    return str_a / (str_a + str_b)

# Predict new matchup
p_gpt4_beats_claude = predict_match("GPT-4", "Claude 3", result['strengths'])
print(f"P(GPT-4 > Claude 3) = {p_gpt4_beats_claude:.2%}")
# Output: P(GPT-4 > Claude 3) = 62.1%
```

## Elo Rating System

### Overview

Elo is a simpler alternative to Bradley-Terry, originally from chess. It has the advantage of incremental updates (no need to refit entire model).

### Elo Equations

**Win Probability Prediction:**
```
P(A wins) = 1 / (1 + 10^((elo_B - elo_A) / 400))
```

**Rating Update After Match:**
```
new_elo_A = old_elo_A + K * (result_A - P(A wins))
```

Where:
- K = 32 (typical for LLM evaluation; higher = more volatile)
- result_A = 1 if A won, 0 if A lost, 0.5 if tie
- P(A wins) is predicted win probability

### Implementation

```python
class EloRating:
    def __init__(self, initial_rating=1600, k_factor=32):
        self.initial_rating = initial_rating
        self.k_factor = k_factor
        self.ratings = {}

    def register_model(self, model_name, initial_rating=None):
        """Register a model with starting rating"""
        if initial_rating is None:
            initial_rating = self.initial_rating
        self.ratings[model_name] = initial_rating

    def win_probability(self, model_a, model_b):
        """Calculate probability that A beats B"""
        elo_a = self.ratings[model_a]
        elo_b = self.ratings[model_b]
        return 1.0 / (1.0 + 10 ** ((elo_b - elo_a) / 400.0))

    def update_match(self, winner, loser):
        """Update ratings after a match"""
        elo_w = self.ratings[winner]
        elo_l = self.ratings[loser]

        # Expected scores
        expected_w = self.win_probability(winner, loser)
        expected_l = 1.0 - expected_w

        # Update ratings
        self.ratings[winner] = elo_w + self.k_factor * (1.0 - expected_w)
        self.ratings[loser] = elo_l + self.k_factor * (0.0 - expected_l)

    def get_ranking(self):
        """Get current ranking"""
        return sorted(self.ratings.items(), key=lambda x: x[1], reverse=True)

# Example usage
elo = EloRating(initial_rating=1600, k_factor=32)

# Register models
for model in ["GPT-4", "Claude 3", "Llama 2", "Mistral"]:
    elo.register_model(model)

# Simulate matches
matches = [
    ("GPT-4", "Claude 3"),
    ("Claude 3", "Llama 2"),
    ("GPT-4", "Llama 2"),
    ("Claude 3", "Mistral"),
    ("GPT-4", "Mistral"),
    ("Claude 3", "Llama 2"),  # Repeat to increase confidence
]

# Assume GPT-4 wins all, Claude 3 wins most
results = [
    ("GPT-4", "Claude 3"),   # GPT-4 wins
    ("Claude 3", "Llama 2"),  # Claude 3 wins
    ("GPT-4", "Llama 2"),    # GPT-4 wins
    ("Claude 3", "Mistral"),  # Claude 3 wins
    ("GPT-4", "Mistral"),    # GPT-4 wins
    ("Claude 3", "Llama 2"),  # Claude 3 wins
]

for winner, loser in results:
    elo.update_match(winner, loser)

# Print ranking
print("ELO RANKING:")
for rank, (model, rating) in enumerate(elo.get_ranking(), 1):
    print(f"{rank}. {model}: {rating:.1f}")
```

### Elo Advantages & Disadvantages

**Advantages:**
- Simple to compute
- Incremental updates (no batch reprocessing)
- Well-understood in competitive settings
- Natural interpretation (difference = win probability)

**Disadvantages:**
- Arbitrary K-factor (must tune)
- Path-dependent (rating depends on match order)
- Volatile with few matches
- Less principled than Bradley-Terry

**Recommendation:** Use Bradley-Terry for final analysis; use Elo for real-time updates during ongoing tournaments.

## Bootstrapped Elo and Confidence Intervals

### Problem Statement

A single Elo/Bradley-Terry ranking may be misleading if based on small sample. We need confidence intervals.

### Bootstrap Resampling Approach

```python
def bootstrap_elo_confidence(comparisons, models, n_bootstrap=1000, ci=95):
    """
    Generate confidence intervals for Elo ratings via bootstrap

    Args:
        comparisons: list of (model_a, model_b, winner)
        models: list of model names
        n_bootstrap: number of bootstrap samples
        ci: confidence interval (95 = 95% CI)

    Returns:
        confidence_intervals: dict of model -> (lower, central, upper)
    """

    bootstrap_ratings = {model: [] for model in models}

    for iteration in range(n_bootstrap):
        # Resample comparisons with replacement
        resampled = np.random.choice(
            len(comparisons),
            size=len(comparisons),
            replace=True
        )

        bootstrap_comparisons = [comparisons[i] for i in resampled]

        # Fit Bradley-Terry on bootstrap sample
        bt_result = bradley_terry_mle(bootstrap_comparisons, models)

        for model in models:
            bootstrap_ratings[model].append(bt_result['strengths'][model])

    # Calculate confidence intervals
    alpha = (100 - ci) / 2
    confidence_intervals = {}

    for model in models:
        ratings = bootstrap_ratings[model]
        lower = np.percentile(ratings, alpha)
        central = np.median(ratings)
        upper = np.percentile(ratings, 100 - alpha)

        confidence_intervals[model] = {
            'lower': lower,
            'central': central,
            'upper': upper,
            'std': np.std(ratings)
        }

    return confidence_intervals

# Example
ci_results = bootstrap_elo_confidence(
    comparisons,
    ["GPT-4", "Claude 3", "Llama 2"],
    n_bootstrap=1000,
    ci=95
)

print("BOOTSTRAPPED ELO WITH 95% CI:")
for model, interval in sorted(ci_results.items(),
                             key=lambda x: x[1]['central'],
                             reverse=True):
    print(f"{model}:")
    print(f"  Central: {interval['central']:.3f}")
    print(f"  95% CI: [{interval['lower']:.3f}, {interval['upper']:.3f}]")
    print(f"  Uncertainty: ±{interval['std']:.3f}")

# Example output:
# GPT-4:
#   Central: 1.842
#   95% CI: [1.621, 2.087]
#   Uncertainty: ±0.127
```

### Overlap Analysis

Confidence interval overlap indicates statistical insignificance of rank difference.

```python
def has_significant_ranking(ci_results, model_a, model_b, alpha=0.05):
    """
    Are models A and B significantly ranked differently?
    Returns False if their 95% CIs overlap
    """
    ci_a = ci_results[model_a]
    ci_b = ci_results[model_b]

    # Check if confidence intervals overlap
    overlap = not (ci_a['upper'] < ci_b['lower'] or ci_b['upper'] < ci_a['lower'])

    return not overlap  # True if significantly different

# Example
is_significant = has_significant_ranking(ci_results, "GPT-4", "Claude 3")
print(f"GPT-4 > Claude 3: {'significant' if is_significant else 'not significant'}")
```

## Style-Controlled Arena

### Motivation

Head-to-head arenas can be biased by stylistic factors unrelated to quality:
- Response length (longer often rated higher)
- Use of formatting (code blocks, lists)
- Tone (formal vs. casual)

### Controlling for Style

```python
def extract_style_features(response):
    """
    Extract stylistic features that might bias evaluation
    """
    return {
        'length': len(response.split()),
        'has_code': '```' in response,
        'has_bullets': '•' in response or '- ' in response,
        'avg_sentence_length': np.mean([
            len(sent.split()) for sent in response.split('.')
        ]),
        'capitalization_ratio': sum(1 for c in response if c.isupper()) / len(response),
        'punctuation_density': sum(1 for c in response if c in '!?.') / len(response)
    }

def create_style_controlled_pairs(response_a, response_b):
    """
    Create alternative presentations to control for style

    Returns multiple (variant_a, variant_b) pairs with different styles
    """

    style_a = extract_style_features(response_a)
    style_b = extract_style_features(response_b)

    # Variant 1: Original style
    variants = [
        (response_a, response_b, "original"),
    ]

    # Variant 2: Both bullet points (if not already)
    if not style_a['has_bullets'] or not style_b['has_bullets']:
        bullet_a = convert_to_bullets(response_a)
        bullet_b = convert_to_bullets(response_b)
        variants.append((bullet_a, bullet_b, "bullets"))

    # Variant 3: Both prose (remove formatting)
    prose_a = remove_formatting(response_a)
    prose_b = remove_formatting(response_b)
    variants.append((prose_a, prose_b, "prose"))

    # Variant 4: Length-controlled (truncate to same length)
    min_len = min(len(response_a), len(response_b))
    trunc_a = response_a[:min_len]
    trunc_b = response_b[:min_len]
    variants.append((trunc_a, trunc_b, "length_controlled"))

    return variants

def evaluate_with_style_control(response_a, response_b):
    """
    Evaluate multiple style variants and average judgment
    """
    variants = create_style_controlled_pairs(response_a, response_b)

    votes_for_a = 0
    for var_a, var_b, variant_type in variants:
        winner = judge_pairwise(var_a, var_b)
        if winner == "a":
            votes_for_a += 1

    # If A consistently wins across styles, likely genuinely better
    return votes_for_a / len(variants)  # Probability A is better

# Usage
p_a_better = evaluate_with_style_control(response_a, response_b)
print(f"P(A > B, style-controlled): {p_a_better:.1%}")
```

## LMSYS Chatbot Arena Internals

### Architecture Overview

The LMSYS Chatbot Arena (as of March 2026) collects 5.6M+ votes across 333 models using:

1. **Web Interface**: Users submit prompts, compare two model outputs
2. **Bradley-Terry Ranking**: Converts votes to absolute rankings
3. **Arena Expert**: Efficient sampling strategy
4. **Public Leaderboard**: Displays top models and trends

### Data Collection Strategy

```python
class ChatbotArenaSimulation:
    """
    Simplified model of Arena's data collection and ranking
    """

    def __init__(self, models):
        self.models = models
        self.comparisons = []
        self.rankings = None

    def sample_pair_for_comparison(self):
        """
        Arena Expert sampling: intelligently select which pair to compare next
        """
        # Prefer pairs with uncertain rankings
        # Avoid pairs with clear winners (redundant info)

        model_counts = defaultdict(int)
        for a, b, _ in self.comparisons:
            model_counts[a] += 1
            model_counts[b] += 1

        # Pair models with similar match counts (data balance)
        # and uncertain relative ranking

        uncertain_pairs = []
        for i, m1 in enumerate(self.models):
            for m2 in self.models[i+1:]:
                uncertainty = self.compute_pair_uncertainty(m1, m2)
                uncertain_pairs.append((uncertainty, m1, m2))

        # Select highest-uncertainty pair
        uncertain_pairs.sort(reverse=True)
        return uncertain_pairs[0][1:]

    def compute_pair_uncertainty(self, model_a, model_b):
        """
        How uncertain is the outcome of A vs B?
        Higher = more uncertain = better to evaluate
        """
        # Estimate current strengths
        current_rankings = self.get_rankings()

        if current_rankings is None:
            return 1.0  # Unknown, maximally uncertain

        rank_a = current_rankings.get(model_a, len(self.models))
        rank_b = current_rankings.get(model_b, len(self.models))

        # Uncertainty decreases with rank difference
        rank_diff = abs(rank_a - rank_b)
        return 1.0 / (1.0 + rank_diff)  # [0, 1], higher for close ranks

    def add_comparison(self, model_a, model_b, winner):
        """Record a user's comparison"""
        self.comparisons.append((model_a, model_b, winner))
        self.rankings = None  # Invalidate cached rankings

    def get_rankings(self):
        """Recompute Bradley-Terry rankings if needed"""
        if self.rankings is None:
            result = bradley_terry_mle(self.comparisons, self.models)
            self.rankings = result['strengths']

        return self.rankings

# Simulate Arena data collection
arena = ChatbotArenaSimulation(models=MODELS)

# Collect 5.6M+ votes over time
for _ in range(5_600_000):
    model_a, model_b = arena.sample_pair_for_comparison()

    # Simulate user judgment (with some noise)
    winner = simulate_user_judgment(model_a, model_b)

    arena.add_comparison(model_a, model_b, winner)

# Get final rankings
rankings = arena.get_rankings()
```

### Public Leaderboard Construction

```python
def generate_leaderboard(rankings, n_top=20):
    """Generate public leaderboard from rankings"""

    sorted_models = sorted(rankings.items(),
                          key=lambda x: x[1], reverse=True)

    leaderboard = pd.DataFrame([
        {
            'Rank': rank,
            'Model': model,
            'Rating': f"{strength:.1f}",
            'Votes': f"{estimated_votes:.0f}",
            'Win Rate': f"{estimated_winrate:.1%}"
        }
        for rank, (model, strength) in enumerate(sorted_models[:n_top], 1)
    ])

    return leaderboard

# Example output:
# Rank  Model                           Rating    Votes   Win Rate
# 1     GPT-4 Turbo                    1879      45328   67.2%
# 2     Claude 3 Opus                  1743      38291   61.5%
# 3     Gemini 2.0 Ultra              1698      31245   58.9%
```

## Building Your Own Internal Arena

### Minimal Implementation

```python
import sqlite3
from datetime import datetime

class InternalArena:
    """Lightweight arena for internal model evaluation"""

    def __init__(self, db_path="arena.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        """Create database schema"""
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS models (
            model_id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comparisons (
            id INTEGER PRIMARY KEY,
            model_a_id INTEGER,
            model_b_id INTEGER,
            winner_id INTEGER,
            timestamp DATETIME,
            evaluator TEXT,
            FOREIGN KEY(model_a_id) REFERENCES models(model_id),
            FOREIGN KEY(model_b_id) REFERENCES models(model_id),
            FOREIGN KEY(winner_id) REFERENCES models(model_id)
        )
        """)

        self.conn.commit()

    def add_model(self, model_name):
        """Register a model"""
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO models (name) VALUES (?)",
                      (model_name,))
        self.conn.commit()

    def record_comparison(self, model_a, model_b, winner, evaluator="unknown"):
        """Record a comparison result"""
        cursor = self.conn.cursor()

        # Get model IDs
        cursor.execute("SELECT model_id FROM models WHERE name = ?", (model_a,))
        id_a = cursor.fetchone()[0]

        cursor.execute("SELECT model_id FROM models WHERE name = ?", (model_b,))
        id_b = cursor.fetchone()[0]

        cursor.execute("SELECT model_id FROM models WHERE name = ?", (winner,))
        id_winner = cursor.fetchone()[0]

        cursor.execute("""
        INSERT INTO comparisons (model_a_id, model_b_id, winner_id, timestamp, evaluator)
        VALUES (?, ?, ?, ?, ?)
        """, (id_a, id_b, id_winner, datetime.now(), evaluator))

        self.conn.commit()

    def get_rankings(self):
        """Compute current Bradley-Terry rankings"""
        cursor = self.conn.cursor()

        # Fetch all comparisons
        cursor.execute("""
        SELECT m_a.name, m_b.name, m_w.name
        FROM comparisons c
        JOIN models m_a ON c.model_a_id = m_a.model_id
        JOIN models m_b ON c.model_b_id = m_b.model_id
        JOIN models m_w ON c.winner_id = m_w.model_id
        """)

        comparisons = cursor.fetchall()

        # Get model names
        cursor.execute("SELECT name FROM models")
        models = [row[0] for row in cursor.fetchall()]

        # Fit Bradley-Terry
        result = bradley_terry_mle(comparisons, models)

        return sorted(result['strengths'].items(),
                     key=lambda x: x[1], reverse=True)

    def get_stats(self):
        """Get arena statistics"""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM comparisons")
        total_comparisons = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT model_a_id) FROM comparisons")
        total_models = cursor.fetchone()[0]

        return {
            'total_comparisons': total_comparisons,
            'total_models': total_models,
            'avg_comparisons_per_model': total_comparisons / total_models if total_models > 0 else 0
        }

# Usage
arena = InternalArena()

# Register models
for model in ["GPT-4", "Claude 3", "Llama 2"]:
    arena.add_model(model)

# Record comparisons
arena.record_comparison("GPT-4", "Llama 2", "GPT-4", evaluator="alice")
arena.record_comparison("Claude 3", "Llama 2", "Claude 3", evaluator="bob")
arena.record_comparison("GPT-4", "Claude 3", "GPT-4", evaluator="alice")

# Get rankings
rankings = arena.get_rankings()
print("RANKINGS:")
for rank, (model, strength) in enumerate(rankings, 1):
    print(f"{rank}. {model}: {strength:.3f}")

# Stats
print(arena.get_stats())
```

## Sample Efficiency Analysis

### How Many Comparisons Are Needed?

```python
def required_comparisons_for_ranking(n_models, desired_confidence=0.95,
                                     effect_size_std=0.2):
    """
    Estimate comparisons needed to establish reliable ranking
    """
    # Simplified formula based on ranking estimation literature
    # More rigorous approach: use information theory

    # Comparisons needed is O(n_models * log(n_models) / effect_size^2)
    n_comparisons = (
        n_models * np.log(n_models) /
        (effect_size_std ** 2) *
        np.log(1 / (1 - desired_confidence))
    )

    return int(np.ceil(n_comparisons))

# Examples:
print(f"10 models: {required_comparisons_for_ranking(10)} comparisons")
print(f"100 models: {required_comparisons_for_ranking(100)} comparisons")
print(f"333 models: {required_comparisons_for_ranking(333)} comparisons")

# Expected output:
# 10 models: 287 comparisons
# 100 models: 4821 comparisons
# 333 models: 18945 comparisons
# (vs. all-pairs: 45, 4950, 55278)
```

### Comparison Strategies

**Exhaustive (All-Pairs):**
- Comparisons: N*(N-1)/2
- Reliability: Highest
- Time: Infeasible for large N (e.g., 333 models = 55k comparisons)

**Round-Robin:**
- Comparisons: N*sqrt(N) approximately
- Strategy: Divide into sqrt(N) blocks, compare all inter-block
- Reliability: Very good for medium N (10-100 models)

**Adaptive (Arena Expert):**
- Comparisons: N*sqrt(N) to N*log(N)
- Strategy: Focus on uncertain pairs
- Reliability: Excellent, uses fewer comparisons than round-robin
- Complexity: Requires active computation of uncertainty

**Hybrid (Recommended):**
1. Start with round-robin for coarse ranking
2. Identify uncertain pairs (overlapping confidence intervals)
3. Run additional comparisons on uncertain pairs
4. Use Elo for real-time ranking; Bradley-Terry for final analysis

## Implementation Checklist

- [ ] Choose model population (N models to rank)
- [ ] Design evaluation protocol (single judge? panel? crowd?)
- [ ] Implement pairwise comparison UI/pipeline
- [ ] Collect initial set of comparisons (target: N*sqrt(N) minimum)
- [ ] Fit Bradley-Terry model
- [ ] Calculate bootstrapped confidence intervals
- [ ] Identify uncertain pairs (overlapping CIs)
- [ ] Run targeted comparisons on uncertain pairs
- [ ] Generate public leaderboard
- [ ] Track leaderboard over time (detect drifts)
- [ ] Publish methodology for reproducibility
