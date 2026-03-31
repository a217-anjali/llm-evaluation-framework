# Metrics Deep Dive

Choosing and interpreting evaluation metrics is central to rigorous LLM evaluation. This chapter provides authoritative reference material for the major metrics used in LLM evaluation, organized by category. For each metric, we cover the formula, intuitive explanation, when to use it, and common pitfalls.

## Generation Quality Metrics

These metrics evaluate the quality of generated text, primarily for tasks like machine translation, summarization, paraphrase, and open-ended text generation.

### Perplexity

**Formula:**
$$\text{PPL} = 2^{-\frac{1}{N}\sum_{i=1}^{N} \log_2 p(w_i)}$$

Or equivalently:
$$\text{PPL} = \exp\left(-\frac{1}{N}\sum_{i=1}^{N} \log p(w_i)\right)$$

where $p(w_i)$ is the model's predicted probability of token $w_i$ and $N$ is the number of tokens.

**Intuitive explanation:** Perplexity measures how surprised the model is by the true sequence. A PPL of 100 means the model is, on average, as uncertain as if choosing among 100 equally likely tokens. Lower perplexity indicates the model assigns higher probability to the true sequence.

**When to use:**
- Language model evaluation (pre-training, fine-tuning)
- Evaluating next-token prediction quality
- Comparing model capacity on held-out test sets
- Establishing baselines for generation tasks

**Pitfalls:**
- Perplexity is logarithmic, so small differences in PPL may be large in probability space
- Can be sensitive to tokenization (different tokenizers produce different PPL)
- Doesn't directly measure generation quality or utility
- A lower-PPL model doesn't necessarily generate higher-quality text

### BLEU (Bilingual Evaluation Understudy)

**Formula:**
$$\text{BLEU} = BP \cdot \exp\left(\sum_{n=1}^{N} w_n \log p_n\right)$$

where:
- $p_n$ is the precision of n-grams (typically $n \in \{1,2,3,4\}$)
- $w_n$ is the weight for n-gram precision (typically uniform: $w_n = 1/N$)
- $BP$ is the brevity penalty: $BP = \begin{cases} 1 & \text{if } c > r \\ e^{1-r/c} & \text{if } c \leq r \end{cases}$

where $c$ is the candidate length and $r$ is the reference length.

**Intuitive explanation:** BLEU measures the fraction of n-grams in the generated text that appear in reference translations. The brevity penalty prevents systems from generating very short outputs. Scores range from 0 to 100.

**When to use:**
- Machine translation evaluation
- Summarization (with caution)
- Any task with multiple reference outputs
- Benchmarking against published baselines (e.g., WMT)

**Pitfalls:**
- Sensitive to tokenization and reference set size
- Doesn't capture paraphrases (a perfectly acceptable translation with different wording scores poorly)
- Doesn't account for semantic meaning
- Not recommended for open-ended generation (multiple valid outputs)
- Brevity penalty can be gamed (generate short outputs, score high)

### ROUGE (Recall-Oriented Understudy for Gisting Evaluation)

**ROUGE-N:**
$$\text{ROUGE-N} = \frac{\sum_s \sum_{g \in G(s)} \min(g_c, g_r)}{\sum_s \sum_{g \in G(s)} g_r}$$

where $g_c$ is the count of n-gram $g$ in the candidate and $g_r$ is the count in reference, and $G(s)$ is the set of n-grams in reference.

**ROUGE-L (Longest Common Subsequence):**
$$\text{ROUGE-L} = F_{\text{lcs}} = \frac{2 \cdot \text{Recall}_{\text{lcs}} \cdot \text{Precision}_{\text{lcs}}}{\text{Recall}_{\text{lcs}} + \text{Precision}_{\text{lcs}}}$$

**Intuitive explanation:** ROUGE-N measures n-gram overlap (like BLEU but with recall instead of precision). ROUGE-L uses longest common subsequence to capture sentence-level structure and is less sensitive to paraphrasing than BLEU.

**When to use:**
- Summarization evaluation
- Text generation where paraphrase acceptance matters
- Multi-reference evaluation
- Benchmarking against published summaries

**Pitfalls:**
- Like BLEU, doesn't capture semantic meaning
- Reference quality matters significantly (human-written summaries must be good)
- High ROUGE scores don't guarantee semantic equivalence
- Not suitable for open-ended generation

### BERTScore

**Formula:**
$$\text{BERTScore}_{\text{Recall}} = \frac{1}{|x|} \sum_{x_i \in x} \max_{y_j \in y} \cos(f(x_i), f(y_j))$$

where $f(\cdot)$ is the BERT embedding function and $\cos$ is cosine similarity. Precision and F1 are computed analogously.

**Intuitive explanation:** BERTScore embeds both reference and candidate texts using BERT, then computes similarity between contextually-aware token embeddings. It captures semantic similarity better than n-gram overlaps.

**When to use:**
- Summarization and paraphrase evaluation
- When semantic equivalence matters more than exact word overlap
- Any task where multiple valid outputs exist
- As a learned metric that correlates with human judgment better than BLEU/ROUGE

**Pitfalls:**
- Depends on the BERT model used (different BERT variants produce different scores)
- Expensive to compute (requires embedding all tokens)
- Not as established or standardized as BLEU/ROUGE (less comparable across papers)
- Doesn't capture discourse-level structure beyond token similarity

### METEOR (Metric for Evaluation of Translation with Explicit ORdering)

**Formula:**
$$\text{METEOR} = F_{\text{mean}} \cdot (1 - \gamma \cdot \text{Frag})$$

where:
- $F_{\text{mean}}$ is the harmonic mean of precision and recall of unigram matches (with weights for synonyms)
- $\text{Frag}$ is the fragmentation score (penalty for misalignment)
- $\gamma$ is a weight parameter

**Intuitive explanation:** METEOR combines n-gram matching with synonym/paraphrase recognition and penalizes fragmentation (words matched far apart). More flexible than BLEU, captures synonyms and reorderings.

**When to use:**
- Machine translation evaluation
- Tasks where synonym and paraphrase variation is acceptable
- When you want something better than BLEU but simpler than learned metrics

**Pitfalls:**
- Requires synonym lexicons (or pre-computed WordNet)
- Fragmentation penalty is somewhat arbitrary
- Less commonly reported than BLEU (harder to compare)

### chrF++ (Character n-gram F-score)

**Formula:**
$$\text{chrF} = \frac{1}{2}(\text{Recall}_{\text{chrf}} + \text{Precision}_{\text{chrf}})$$

where character n-gram precision and recall are computed at character level (typically $n \in \{1,2,3,4,5,6\}$).

**chrF++** adds word-level n-grams:
$$\text{chrF++} = 0.9 \cdot \text{chrF} + 0.1 \cdot \text{wordsF}$$

**Intuitive explanation:** chrF++ operates at character level, making it language-agnostic and robust to morphological variation. Less sensitive to tokenization issues than BLEU.

**When to use:**
- Machine translation, especially for morphologically rich languages
- Cross-lingual evaluation
- When language-agnostic evaluation is needed
- As a complement to BLEU for translation

**Pitfalls:**
- Lower human correlation than BLEU in some language pairs
- Character-level granularity can miss semantic errors
- Less established than BLEU in published benchmarks

### COMET (Crosslingual Optimized Metric for Evaluation of Translation)

**Formula:** Learned metric trained end-to-end to predict human judgments:
$$\text{COMET}(s, t, c) = f_\theta(s, t, c)$$

where $s$ is source text, $t$ is reference, $c$ is candidate, and $f_\theta$ is a neural network.

**Intuitive explanation:** COMET is a learned metric trained on human TER/DA judgments. It takes source, reference, and candidate as input and predicts human judgment scores. Best correlation with human evaluation among automatic metrics.

**When to use:**
- Machine translation evaluation (best-in-class)
- When human judgment correlation is critical
- When you have resources to compute neural metrics
- As a replacement for BLEU if available

**Pitfalls:**
- Expensive to compute (requires neural network inference)
- Less reproducible than BLEU/ROUGE (model versions matter)
- Requires training data or pre-trained models
- Not as widely implemented as BLEU

## Classification Metrics

These metrics evaluate classification and ranking tasks.

### Accuracy

**Formula:**
$$\text{Accuracy} = \frac{1}{n}\sum_{i=1}^{n} \mathbb{1}(y_i = \hat{y}_i)$$

where $y_i$ is the true label and $\hat{y}_i$ is the predicted label.

**Intuitive explanation:** Accuracy is the fraction of correct predictions. Simple and interpretable but can be misleading with imbalanced datasets.

**When to use:**
- Balanced classification problems
- Benchmarks with equal class distribution
- As a baseline metric

**Pitfalls:**
- Misleading with imbalanced data (a classifier that always predicts the majority class can achieve high accuracy)
- Doesn't distinguish between types of errors (false positives vs. false negatives)
- Not suitable for multi-label classification

### Macro F1 and Micro F1

**Macro F1:**
$$\text{Macro F1} = \frac{1}{K}\sum_{k=1}^{K} F1_k$$

where $K$ is the number of classes and $F1_k$ is the F1 score for class $k$.

**Micro F1:**
$$\text{Micro F1} = F1(\sum_k \text{TP}_k, \sum_k \text{FP}_k, \sum_k \text{FN}_k)$$

**Intuitive explanation:**
- **Macro F1** computes F1 per class then averages. Gives equal weight to each class regardless of frequency. Good for imbalanced data.
- **Micro F1** computes F1 globally by counting total true positives and false positives. Equivalent to accuracy for multi-class classification.

**When to use:**
- Multi-class classification
- Imbalanced datasets (use Macro F1)
- When class-level performance matters

**Pitfalls:**
- Macro and Micro F1 can differ significantly; report both
- With highly imbalanced data, Macro F1 can be misleading if dominated by rare classes

## Code Generation Metrics

### Pass@k

**Formula:**
$$\text{Pass@k} = \frac{1}{n}\sum_{i=1}^{n} \frac{\text{# test cases passed in top-k samples}}{k}$$

More formally, if we sample $k$ completions for problem $i$ and test them:
$$\text{Pass@k} = \mathbb{P}(\text{at least 1 of } k \text{ samples passes all tests})$$

Can be estimated as:
$$\text{Pass@k} = 1 - \left(\frac{c}{n}\right)^{n-k}$$

where $c$ is the number of unsolved problems (estimate when computational cost is high).

**Intuitive explanation:** Pass@k measures the fraction of problems where at least one of k sampled completions passes all test cases. Higher k allows more tries; pass@100 is more lenient than pass@1.

**When to use:**
- Code generation (HumanEval, MBPP)
- Any task where sampling multiple completions is feasible
- Evaluating models in low-resource regimes (k=1 is most constrained)

**Pitfalls:**
- Heavily dependent on test case quality (poor tests lead to inflated scores)
- Doesn't measure code quality (inefficient code passes if tests don't check efficiency)
- k must be specified; pass@1 and pass@100 are measuring different things
- Test case overfitting is a risk

### Exact Match (EM)

**Formula:**
$$\text{EM} = \frac{1}{n}\sum_{i=1}^{n} \mathbb{1}(\text{prediction}_i == \text{reference}_i)$$

**Intuitive explanation:** Exact match measures the fraction of samples where the predicted output exactly matches the reference (no partial credit). Strict metric.

**When to use:**
- Question answering (SQuAD style)
- Tasks with well-defined, unambiguous answers
- When partial credit is inappropriate

**Pitfalls:**
- Penalizes semantically correct but syntactically different answers
- Sensitive to whitespace, punctuation, casing
- No partial credit for nearly-correct answers

## Calibration Metrics

Calibration metrics measure whether a model's confidence estimates are reliable.

### Expected Calibration Error (ECE)

**Formula:**
$$\text{ECE} = \sum_{m=1}^{M} \frac{|B_m|}{n} |\text{acc}(B_m) - \text{conf}(B_m)|$$

where:
- $B_m$ is a bin of predictions with confidence in range $(m-1)/M$ to $m/M$
- $\text{acc}(B_m)$ is the accuracy within bin $m$
- $\text{conf}(B_m)$ is the average confidence within bin $m$
- $M$ is the number of bins (typically 10 or 15)

**Intuitive explanation:** ECE measures the discrepancy between predicted confidence and actual accuracy. A perfectly calibrated model has ECE = 0 (confidence matches accuracy). High ECE indicates miscalibration.

**When to use:**
- Any classification task where confidence is important
- Evaluating model uncertainty
- Deciding when to defer to human review
- Assessing whether confidence thresholds are reliable

**Pitfalls:**
- Binning is arbitrary (results vary by number of bins)
- Can be unstable with small datasets
- Doesn't capture under/overconfidence direction

### Brier Score

**Formula:**
$$\text{Brier Score} = \frac{1}{n}\sum_{i=1}^{n}(p_i - y_i)^2$$

where $p_i$ is the predicted probability and $y_i$ is the true label (0 or 1).

**Intuitive explanation:** Brier score is the mean squared error of probability predictions. Ranges from 0 (perfect) to 1 (worst). Penalizes confident wrong predictions more than unsure wrong predictions.

**When to use:**
- Evaluating probabilistic forecasts
- Any task where probability calibration matters
- Combining with other metrics to assess prediction quality

**Pitfalls:**
- Penalizes overconfidence, which can be misleading if you want to reward high confidence on easy problems
- Scale (0-1) can be unintuitive

## Preference and Ranking Metrics

### Win Rate

**Formula:**
$$\text{Win Rate}_A = \frac{\text{# times Model A is preferred}}{\text{# comparisons}}$$

**Intuitive explanation:** Win rate is the fraction of pairwise comparisons where a model is preferred. Simple and interpretable.

**When to use:**
- Pairwise model comparison
- Arena-style evaluation
- When relative ranking matters more than absolute quality

**Pitfalls:**
- Doesn't account for draw/ties (models equally good)
- Doesn't leverage strength of preference (5-point margin vs. 1-point margin treated equally)
- Can be noisy with small sample sizes

### Elo Rating

**Formula (simplified):**
$$\text{Elo}_{\text{new}} = \text{Elo}_{\text{old}} + K \cdot (s - E_A)$$

where:
- $K$ is the K-factor (learning rate, typically 4-32)
- $s$ is the score (1 for win, 0 for loss, 0.5 for draw)
- $E_A = \frac{1}{1 + 10^{-(\text{Elo}_A - \text{Elo}_B)/400}}$ is the expected score

**Intuitive explanation:** Elo rating updates are proportional to the difference between expected and actual outcomes. Beating a stronger opponent raises rating more than beating a weaker opponent. Converges to a ranking that is transitive and robust to random noise.

**When to use:**
- Tournament-style ranking of multiple models
- Chatbot Arena
- When you want a principled ranking from pairwise comparisons

**Pitfalls:**
- Elo is relative (only differences matter, absolute values are arbitrary)
- Convergence is slow with few comparisons
- Sensitive to K-factor choice
- Assumes transitive preference (if A > B and B > C, then A > C), which may not hold

### Bradley-Terry Model

**Formula:**
$$P(A > B) = \frac{\pi_A}{\pi_A + \pi_B}$$

where $\pi_A$ and $\pi_B$ are the strength parameters estimated via maximum likelihood from pairwise comparisons.

**Intuitive explanation:** Bradley-Terry models the probability of pairwise preference using strength parameters. Unlike Elo, it's statistically principled and provides confidence intervals on estimates.

**When to use:**
- Ranking models from pairwise comparisons
- When confidence intervals on rankings are important
- More sophisticated than Elo (statistically principled)
- When you want to estimate probability of preference, not just ranking

**Pitfalls:**
- Assumes transitivity (stronger assumption than Elo)
- Maximum likelihood estimation requires careful implementation
- Requires sufficient comparisons for convergence

## Agreement Metrics

Agreement metrics measure whether annotators agree with each other or with a reference.

### Cohen's Kappa

**Formula:**
$$\kappa = \frac{p_o - p_e}{1 - p_e}$$

where:
- $p_o$ = observed agreement (fraction of samples where annotators agree)
- $p_e$ = expected agreement by chance

For binary classification:
$$p_e = p_+ p_+ + p_- p_-$$

where $p_+$ is the marginal probability of the positive class.

**Intuitive explanation:** Cohen's kappa measures agreement while accounting for chance. A value of 1 indicates perfect agreement, 0 indicates chance agreement, and negative values indicate worse-than-chance agreement.

**When to use:**
- Measuring agreement between two annotators
- Assessing inter-rater reliability
- Evaluating annotation quality
- Typical interpretation: kappa > 0.8 is excellent, 0.6-0.8 is good, 0.4-0.6 is moderate

**Pitfalls:**
- Only works for two raters (use Krippendorff's alpha for more)
- Sensitive to class imbalance
- Assumes categorical labels (extended version for continuous ratings)

### Krippendorff's Alpha

**Formula:**
$$\alpha = 1 - \frac{D_o}{D_e}$$

where $D_o$ is observed disagreement and $D_e$ is expected disagreement (computed from marginal distributions).

**Intuitive explanation:** Krippendorff's alpha is a generalization of Cohen's kappa for multiple annotators, multiple labels, and continuous ratings. Measures agreement while accounting for chance.

**When to use:**
- Measuring agreement among 3+ annotators
- Mixed numbers of annotations per sample (incomplete annotation matrices)
- Nominal, ordinal, or continuous data
- Standard in NLP for reporting inter-annotator agreement

**Pitfalls:**
- Interpretation is similar to kappa but slightly different scale
- Computation is more complex than kappa
- Requires careful handling of missing annotations

## Faithfulness and Retrieval Metrics

### Faithfulness Score

No single standard formula; varies by approach:

1. **QA-based:** Generate questions from reference, score if model answers correctly
$$\text{Faithfulness} = \frac{\text{# generated questions answered correctly}}{\text{total # generated questions}}$$

2. **NLI-based:** Use NLI model to check if summary entails facts from source
$$\text{Faithfulness} = \frac{\text{# summary sentences entailed by source}}{\text{total # summary sentences}}$$

**Intuitive explanation:** Faithfulness measures whether generated text is consistent with source material (no hallucination). Different approaches give different scores.

**When to use:**
- Summarization with source documents
- RAG system evaluation
- Any task where factual consistency with source matters

**Pitfalls:**
- Highly dependent on the evaluation method chosen
- QA-based methods require good QA models
- NLI-based methods have their own reliability issues
- No consensus on best approach

### NDCG (Normalized Discounted Cumulative Gain)

**Formula:**
$$\text{NDCG@k} = \frac{1}{\text{IDCG@k}} \sum_{i=1}^{k} \frac{2^{rel_i} - 1}{\log_2(i+1)}$$

where $rel_i$ is the relevance of the $i$-th ranked item and $\text{IDCG@k}$ is the ideal DCG (best possible ranking).

**Intuitive explanation:** NDCG measures ranking quality, giving credit for relevant items ranked high. The discount factor penalizes relevant items ranked low. Normalized by ideal ranking so scores are comparable across queries.

**When to use:**
- Information retrieval evaluation
- Search ranking evaluation
- Any task with ranked relevance (1, 2, 3 relevant, etc.)
- Standard metric in IR benchmarks

**Pitfalls:**
- Requires relevance judgments (expensive to obtain)
- Sensitive to @k choice (NDCG@5 and NDCG@10 can differ significantly)
- Doesn't handle extreme relevance differences well

### MRR (Mean Reciprocal Rank)

**Formula:**
$$\text{MRR} = \frac{1}{n}\sum_{i=1}^{n} \frac{1}{\text{rank}_i}$$

where $\text{rank}_i$ is the rank of the first relevant item for query $i$.

**Intuitive explanation:** MRR is the average of the reciprocals of the rank of the first relevant result. High MRR means relevant results appear early. Ranges from 0 to 1.

**When to use:**
- Question answering evaluation
- Search ranking (especially when only one relevant answer per query)
- When only position of first correct answer matters

**Pitfalls:**
- Only considers first relevant result (ignores quality of other results)
- Assumes binary relevance (relevant/not relevant)
- Can be 0 if no relevant result in top-k

---

## Choosing Metrics: A Decision Guide

**For text generation (translation, summarization):**
- Start with BLEU/ROUGE if benchmarking against published results
- Add BERTScore for semantic similarity
- Use COMET if available (best correlation with humans)

**For classification:**
- Use Accuracy if balanced classes
- Use Macro F1 if imbalanced classes
- Always report Micro F1 for reference
- Add Precision/Recall if operating point matters

**For code generation:**
- Use Pass@k (typically pass@1 and pass@100)
- Ensure test cases are comprehensive
- Don't rely solely on Pass@k; manual inspection of failures is essential

**For ranking/retrieval:**
- Use NDCG@10 if multiple relevant items exist
- Use MRR if only one relevant answer per query
- Use Elo/Bradley-Terry for pairwise model comparison

**For calibration:**
- Use ECE for classification confidence
- Use Brier score for probability predictions

**For agreement:**
- Report Cohen's kappa for two raters
- Report Krippendorff's alpha for multiple raters

---

**Next:** Learn about [statistical rigor](./statistical-rigor.md) to ensure your evaluation results are reliable and comparable.
