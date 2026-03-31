# Glossary

Comprehensive definitions of terms used in LLM evaluation, covering metrics, methodologies, benchmarks, and tools.

---

## A

**Absolute Score**
A single score assigned to a sample or response without comparison to other samples. Common in holistic evaluation (e.g., 1-5 rating scale).

**Adversarial Examples**
Inputs designed to cause model failures; used to probe weaknesses and robustness. Examples include paraphrases, out-of-distribution text, or deliberately misleading prompts.

**Agreement (Inter-rater)**
Measure of consistency between multiple annotators. Calculated using Cohen's kappa, Fleiss' kappa, or Krippendorff's alpha.

**Agentic System**
Language model deployed as agent with ability to take actions, use tools, and iterate based on environmental feedback. Evaluation must account for trajectory quality and goal completion.

**Alignment**
Degree to which model behavior matches intended values and constraints. Includes honesty, helpfulness, harmlessness, and adherence to safety guidelines.

**Annotation Guidelines**
Written instructions specifying how annotators should label data for evaluation. Reduces ambiguity and improves consistency.

**Artifact**
Systematic bias or pattern in benchmark that models exploit without genuine capability. Example: word overlap correlating strongly with NLI label.

---

## B

**Batch Evaluation**
Evaluation of multiple samples in parallel; offers efficiency gains but may have different results than sequential evaluation.

**Benchmark**
Curated set of test cases with known outputs used to measure model capabilities. Examples: HELM, ARC-AGI, FrontierMath.

**Benchmark Contamination**
Situation where model training data contains test examples from an evaluation benchmark. Inflates reported performance and invalidates claims.

**BERTScore**
Embedding-based metric for generation evaluation. Computes similarity between candidate and reference using BERT embeddings; correlates better with human judgment than BLEU.

**Bias**
Systematic tendency in model outputs toward specific patterns or groups. Evaluated through demographic-stratified metrics and fairness assessments.

**BLEU (Bilingual Evaluation Understudy)**
N-gram overlap metric for machine translation. Compares candidate to reference using precision of unigrams, bigrams, trigrams, and 4-grams with brevity penalty.

---

## C

**Calibration**
Agreement between model's confidence and actual correctness. Well-calibrated models assign high confidence to correct answers and low confidence to incorrect ones.

**Chain-of-Thought (CoT)**
Prompting technique where model outputs reasoning steps before final answer. Evaluation can assess reasoning quality separately from final answer correctness.

**Chatbot Arena**
Large-scale human preference evaluation platform where users provide pairwise comparisons of model outputs. Produces Elo ratings through Bradley-Terry modeling.

**Classification Metric**
Metric for discrete categorical prediction (e.g., accuracy, F1, precision, recall, macro-averaged scores). Contrasts with generation and ranking metrics.

**Coherence**
Quality of logical flow and consistency in generated text. Evaluated through human judgment or automatically via discourse relation metrics.

**Confidence Interval**
Range of values likely to contain the true metric value with specified probability. Critical for reporting statistical uncertainty in evaluation results.

**Consistency**
Reproducibility of evaluation results across runs. Measures sensitivity to randomness in sampling, prompting, and judge responses.

**Context Length**
Maximum input size a model can process. Important parameter for RAG and long-document evaluation; longer context enables more information but may increase confusion.

**Context Precision**
In RAG evaluation: fraction of retrieved context that is relevant to answering the question. Computed as proportion of relevant statements in context.

**Context Recall**
In RAG evaluation: fraction of relevant information in corpus that system retrieves. Measured against ground-truth relevant passages.

**Contamination Detection**
Methods to identify if test examples appear in training data. Techniques include vocabulary overlap analysis, semantic similarity search, and watermarking.

**Counterfactual Evaluation**
Testing model behavior under hypothetical scenarios created by modifying inputs. Distinguishes causal model failures from spurious correlations.

---

## D

**Dependency-Level Entailment**
Fine-grained factuality evaluation method that checks entailment at the linguistic dependency level rather than full-sentence level.

**Downstream Task**
Task that depends on output from another model or system. Used to evaluate whether improvements in one component improve end-to-end system performance.

**Distribution Shift**
Change in data distribution between training and test data. Robustness evaluation tests model performance under various distribution shifts.

---

## E

**Elo Rating**
Rating system where paired comparisons update model ratings iteratively. Used in Chatbot Arena for ranking models; interpretation as win probability against average opponent.

**Embedding-Based Metric**
Evaluation metric computing similarity using learned representations (e.g., BERTScore). Better correlates with human judgment than surface-level metrics on generation tasks.

**Entailment**
Semantic relation where one text implies truth of another. Used in factuality and robustness evaluation.

**Error Analysis**
Systematic categorization of model failures to identify patterns and understand limitations. Critical for interpreting evaluation results beyond aggregate scores.

**Eval-Driven Development**
Development methodology where models are continuously evaluated against curated test sets and evaluation-based metrics drive iteration priorities.

---

## F

**F1 Score**
Harmonic mean of precision and recall: 2*(precision*recall)/(precision+recall). Standard metric for classification balancing both false positives and false negatives.

**Factuality**
Correctness of factual claims in model outputs. Evaluation through knowledge graph grounding, fact verification, or human judgment.

**Few-Shot Learning**
Learning from small number of examples provided in context. Evaluation assesses both immediate capability and stability across example variations.

**Fluency**
Naturalness and grammatical correctness of generated text. Evaluated through human judgment or automatic metrics like perplexity.

---

## G

**GLMM (Generalized Language Model Measurement)**
NIST framework for standardized LLM evaluation establishing measurement methodologies for safety, fairness, and capability assessment.

**Gold Standard**
Ground-truth reference annotation assumed to be correct. Used as evaluation target for comparison; quality determines ceiling on metric reliability.

**Gradient-Based Sensitivity**
Method for measuring how sensitive model output is to input perturbations by computing gradients with respect to input.

---

## H

**Hallucination**
Generation of plausible but false information. Fundamental evaluation challenge; distinguished from knowledge gaps through factuality assessment.

**HELM (Holistic Evaluation of Language Models)**
Comprehensive multi-scenario evaluation framework assessing capabilities across 42 diverse scenarios with 21 metrics each.

**Human Evaluation**
Assessment of model outputs by human annotators using defined criteria. Gold standard for evaluation despite cost and scalability challenges.

**Human-in-the-Loop**
Evaluation or training process combining automatic methods with human judgment for iterative improvement and error correction.

---

## I

**In-Context Learning**
Ability to learn from examples provided in prompt without gradient updates. Evaluation tests both capability and stability across example selections.

**Inter-Rater Agreement**
Statistical measure of consistency between multiple annotators. High agreement supports reliability of evaluation; low agreement suggests ambiguous criteria.

**Instruction Following**
Model's ability to understand and comply with task instructions. Evaluated through accuracy on diverse instruction formats and modalities.

---

## J

**Judge Model**
Language model (typically GPT-4 or Claude) used to evaluate outputs of other models. Offers scale and consistency compared to human evaluation but introduces evaluator bias.

---

## K

**Kappa (Cohen's / Fleiss' / Krippendorff's)**
Statistical measures of inter-rater agreement correcting for chance agreement. Values: 0.0-0.2 (poor), 0.2-0.4 (fair), 0.4-0.6 (moderate), 0.6-0.8 (good), 0.8-1.0 (excellent).

---

## L

**Leaderboard**
Public ranking of models on benchmark. Enables comparison and drives research competition; concerns include metric gaming and contamination.

**Length Bias**
Tendency for evaluation metrics or human raters to favor longer outputs independent of quality. Important to control for in generation evaluation.

**LLM-as-Judge**
Using large language model to evaluate other models' outputs. Scalable alternative to human evaluation but prone to position bias, recency bias, and style preference.

---

## M

**Mean**
Average of scores across samples. Provides single-number summary but sensitive to outliers; should be reported with standard deviation or confidence interval.

**Median**
Middle value in rank-ordered scores. More robust to outliers than mean; recommended alongside mean for robust summary statistics.

**METEOR (Metric for Evaluation of Translation with Explicit ORdering)**
Machine translation metric improving on BLEU by incorporating stemming, synonyms, and word order.

**Metric**
Quantitative function measuring model performance. Examples: accuracy, F1, BLEU, BERTScore, or LLM-as-judge scores.

**Multimodal Evaluation**
Assessment of models processing multiple input modalities (vision, text, audio). Requires specialized benchmarks like MMBench and LLaVA-Bench.

---

## N

**N-gram Overlap**
Surface-level similarity metric counting shared word sequences. Foundation for BLEU and ROUGE but doesn't capture semantic equivalence.

**Natural Language Inference (NLI)**
Task of determining whether premise entails, contradicts, or is neutral toward hypothesis. Fundamental for many evaluation approaches.

---

## O

**Observation Bias**
Bias in evaluation introduced by annotators observing model source or other contextual information. Mitigated through blind evaluation.

**Off-Distribution**
Test examples different from training distribution. Critical for robustness evaluation; models often perform worse on off-distribution data.

---

## P

**P@K (Precision at K)**
Fraction of top K results that are correct or relevant. Common metric for ranking and retrieval tasks.

**Pareto Frontier**
Set of models where improving one metric requires degrading another. Important for understanding model trade-offs (e.g., speed vs. accuracy).

**Perplexity**
Language modeling metric: negative log likelihood per token. Lower perplexity indicates better language model fit but doesn't directly measure task performance.

**Position Bias**
Tendency for LLM judges to favor earlier or later options in comparison tasks. Mitigated through multiple orderings or prompt variations.

**Precision**
Fraction of positive predictions that are correct: TP/(TP+FP). Emphasizes avoiding false positives; paired with recall for balanced assessment.

**Production Evaluation**
Ongoing evaluation of deployed models using real user interactions and feedback. Complements static benchmark evaluation with dynamic performance monitoring.

**Prompt Engineering**
Process of crafting inputs to optimize model outputs for evaluation or deployment. Evaluation must assess robustness across reasonable prompt variations.

**Prompt Sensitivity**
Degree to which model outputs vary with small prompt changes. High sensitivity suggests brittle performance; low sensitivity indicates robustness.

---

## Q

**Qualitative Evaluation**
Assessment focusing on understanding failure modes and generating insights rather than aggregate statistics. Complements quantitative evaluation.

**Quantitative Evaluation**
Assessment producing numerical metrics aggregated across samples. Enables comparative ranking but may mask important failure patterns.

---

## R

**RAG (Retrieval-Augmented Generation)**
System combining retrieval and generation where model generates output conditioned on retrieved context. Evaluation must assess retrieval quality, answer relevance, and context utilization.

**Ranking Metric**
Metric for ordering or preference-based tasks. Examples: Elo rating, Bradley-Terry model, NDCG, MRR.

**Recall**
Fraction of positive examples that model identifies: TP/(TP+FN). Emphasizes avoiding false negatives; paired with precision for balanced assessment.

**Reference-Based Metric**
Evaluation metric comparing output to ground-truth reference. Examples: BLEU, ROUGE, Exact Match. Contrasts with reference-free metrics.

**Reference-Free Metric**
Evaluation metric assessing output quality without ground-truth reference. Examples: semantic similarity, language model scoring, LLM judgment.

**Red Teaming**
Adversarial testing approach where evaluators attempt to find safety failures through creative prompting and exploitation. Standard practice for safety evaluation.

**Robustness**
Model's ability to perform consistently across input variations and distributions. Evaluated through perturbation tests, paraphrasing, and distribution shift scenarios.

**ROUGE (Recall-Oriented Understudy for Gisting Evaluation)**
Summarization metric measuring n-gram overlap between candidate and reference(s). ROUGE-1 (unigrams), ROUGE-2 (bigrams), ROUGE-L (longest common subsequence).

---

## S

**Sample Size**
Number of examples in evaluation set. Larger samples provide more reliable estimates but have diminishing returns; statistical power analysis determines adequate size.

**Semantic Similarity**
Degree to which two texts carry similar meaning independent of surface form. Measured through embedding distance or entailment; more meaningful than surface-level metrics.

**Sensitivity Analysis**
Study of how evaluation results change with parameter variations (e.g., temperature, sampling method, judge model). Establishes stability of claims.

**Standard Deviation**
Measure of score variability: sqrt(mean((x_i - mean(x))^2)). Essential for understanding evaluation result confidence; should accompany mean in reporting.

**Statistical Significance**
Probability that observed difference exceeds random chance. Common thresholds: p<0.05 (significant), p<0.01 (highly significant); misuse common in ML evaluation.

**Stratified Evaluation**
Evaluating performance separately for different subgroups (e.g., by demographic group, domain, difficulty level). Reveals disparities masked by aggregate metrics.

**Style Bias**
Tendency for LLM judges or human raters to prefer specific writing styles independent of semantic quality. Introduces systematic error in evaluation.

---

## T

**Test Set Leakage**
See Benchmark Contamination.

**Tool Use**
Agent's ability to invoke external tools (search, calculator, APIs) to complete tasks. Evaluation assesses planning, tool selection, and result integration.

**Top-K Accuracy**
Accuracy where prediction counts as correct if gold label appears in top-K model predictions. Useful for ranking and recommendation evaluation.

**Trajectory Quality**
In agentic evaluation: assessment of decision-making process and path to goal completion independent of final outcome. Measures planning and reasoning quality.

**Translatability**
Degree to which benchmark performance generalizes to real-world applications. High translatability means benchmark progress correlates with practical improvement.

---

## U

**Uncertainty Quantification**
Methods for expressing model confidence or confidence bounds on predictions. Important for risk-aware deployment and decision-making.

**Underscore Metric**
See Metric.

---

## V

**Validity**
Extent to which evaluation measures intended construct. Threat to validity: metric correlating with capability without measuring it directly.

---

## W

**Win Rate**
In pairwise comparison: percentage of comparisons where one model is preferred over another. Foundation for Elo and Bradley-Terry rankings.

---

## X

**XAI (Explainable AI) Evaluation**
Assessment of whether model explanations are faithful, sufficient, and human-understandable. Growing importance for trustworthiness and debugging.

---

## Y

**Zero-Shot Learning**
Evaluation on tasks with no task-specific examples in context. Tests generalization and capability to follow natural language instructions.

---

## Z

**Zero-Shot Prompting**
Providing task instruction without examples. Evaluates instruction-following ability and robustness to task phrasing variations.

---

## Benchmark Names

**ARC-AGI** (Abstract Reasoning Corpus - Artificial General Intelligence)
Benchmark of 100 abstract reasoning puzzles requiring visual pattern recognition and logical inference. Designed to resist memorization through diversity.

**ARC-AGI-2 / ARC-AGI-3**
Successive versions of ARC-AGI with expanded test sets and refined contamination resistance for benchmarking advanced reasoning.

**GLUE** (General Language Understanding Evaluation)
Suite of 9 diverse NLU tasks. Influential foundational benchmark establishing multi-task evaluation paradigm.

**FrontierMath**
Benchmark of challenging competition mathematics problems requiring novel reasoning. Evaluates advanced mathematical capability at frontier level.

**HELM** (Holistic Evaluation of Language Models)
Multi-scenario evaluation framework across 42 scenarios with 21 metrics. Emphasizes scenario diversity and multi-objective assessment.

**MMBench**
Multimodal benchmark systematically evaluating vision-language models. Assesses visual perception, reasoning, and instruction following.

**RealToxicityPrompts**
Dataset of 99k prompts for toxicity evaluation. Enables assessment of harmful output generation across diverse contexts.

**FEVER** (Fact Extraction and VERification)
Benchmark for fact verification requiring evidence retrieval and entailment judgment. Foundational for factuality evaluation.

---

## Tool & Framework Names

**LangSmith**
LangChain evaluation framework for tracking and testing LLM applications. Enables versioning, testing, and comparative analysis.

**Braintrust**
SaaS platform for production LLM evaluation with human feedback integration and drift monitoring.

**Promptfoo**
CLI tool for evaluating and comparing prompts and models systematically. Enables A/B testing and regression detection.

**RAGAS** (Retrieval-Augmented Generation Assessment)
Framework for evaluating RAG systems with metrics for retrieval quality and generation accuracy.

**BIG-bench**
Community benchmark with 200+ tasks across diverse domains. Collaborative evaluation infrastructure.

---

## Metric Calculation Examples

**Accuracy Formula**
Accuracy = (TP + TN) / (TP + TN + FP + FN)

**F1 Score Formula**
F1 = 2 * (Precision * Recall) / (Precision + Recall)

**BLEU Formula**
BLEU = BP * exp(Σ w_n * log(p_n)) where BP is brevity penalty, p_n is n-gram precision, w_n are weights

**Exact Match**
Binary metric: 1 if prediction matches reference exactly, 0 otherwise. Strict but interpretable.

**Macro-Averaged F1**
F1_macro = (1/N) * Σ F1_i where F1_i is F1 for class i. Equal weight to each class.

**Micro-Averaged F1**
F1_micro = F1 calculated on aggregated TP/FP/FN across all classes. Weighted by class frequency.

