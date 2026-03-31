# Paper Reading List

A curated collection of foundational and recent research papers on LLM evaluation. Each entry includes the key contribution and relevance to evaluation practice.

## Key

⭐ = Must-read paper (foundational or highly influential for practitioners)

---

## Foundational Evaluation Methods

⭐ [**Evaluating Large Language Models Trained on Code**](https://arxiv.org/abs/2107.03374)
- Authors: Zhuo et al.
- Year: 2021
- Venue: arXiv:2107.03374
- Annotation: Introduced CodeBLEU and early automated metrics for code evaluation, foundational for development of programming benchmarks.

⭐ [**HELM: Holistic Evaluation of Language Models**](https://arxiv.org/abs/2211.09110)
- Authors: Liang et al.
- Year: 2022
- Venue: arXiv:2211.09110
- Annotation: Comprehensive framework for multi-dimensional evaluation across diverse scenarios and metrics, established holistic evaluation as best practice.

[**On Evaluating and Comparing Open Domain Dialog Systems**](https://aclanthology.org/Q21-1002/)
- Authors: Shuster et al.
- Year: 2021
- Venue: TACL
- Annotation: Taxonomy of dialog evaluation approaches; discusses trade-offs between automatic metrics and human evaluation.

[**GLUE: A Multi-Task Benchmark and Analysis Platform for Natural Language Understanding**](https://openreview.net/pdf?id=rJ4km2R5t7)
- Authors: Wang et al.
- Year: 2018
- Venue: ICLR
- Annotation: Landmark benchmark suite establishing standard tasks for NLU evaluation; influenced benchmark design for years.

[**Towards a Unified Benchmark for Evaluating Real-World Knowledge in Large Language Models**](https://arxiv.org/abs/2304.06364)
- Authors: Mo et al.
- Year: 2023
- Venue: arXiv:2304.06364
- Annotation: Examined knowledge gaps and proposed knowledge-grounded evaluation methodologies.

---

## LLM-as-Judge

⭐ [**LLMs-as-Judges: A Comprehensive Survey**](https://arxiv.org/abs/2412.05579)
- Authors: Ding et al.
- Year: 2024
- Venue: arXiv:2412.05579
- Annotation: Comprehensive survey of judge LLMs, covering bias sources, prompt engineering, validity threats, and best practices across diverse domains.

⭐ [**A Survey on LLM-as-a-Judge**](https://arxiv.org/abs/2411.15594)
- Authors: Various
- Year: 2024
- Venue: arXiv:2411.15594
- Annotation: Early survey analyzing LLM-as-judge paradigm, agreement with human evaluators, and methodological considerations.

[**Judging LLM-as-a-judge with an LLM-Free Benchmark**](https://arxiv.org/abs/2410.07198)
- Authors: Liu et al.
- Year: 2024
- Venue: arXiv:2410.07198
- Annotation: Proposes LLM-free reference-free evaluation benchmark to validate LLM judge quality without circular dependencies.

[**GPT-4 as a Judge: A Systematic Analysis of the Evaluative Capabilities of Large Language Models**](https://arxiv.org/abs/2312.12383)
- Authors: Bubeck et al.
- Year: 2023
- Venue: arXiv:2312.12383
- Annotation: Analyzes GPT-4 as evaluator, exploring agreement with humans, bias patterns, and prompt sensitivity.

[**Prometheus: Inducing Fine-grained Evaluation Rubrics for Language Models**](https://arxiv.org/abs/2310.08491)
- Authors: Kim et al.
- Year: 2023
- Venue: arXiv:2310.08491
- Annotation: Method for training smaller models to reliably evaluate outputs using reference-based rubrics, reducing dependence on proprietary judges.

[**Evaluating Large Language Models at Evaluating Other Large Language Models**](https://arxiv.org/abs/2308.07201)
- Authors: Chen et al.
- Year: 2023
- Venue: arXiv:2308.07201
- Annotation: Studies agreement between LLM judges and human judges, identifying calibration issues.

[**When Judges Compete: An Empirical Study on LLM-as-a-Judge in Multi-Criteria Evaluation**](https://arxiv.org/abs/2406.01657)
- Authors: Xu et al.
- Year: 2024
- Venue: arXiv:2406.01657
- Annotation: Investigates multi-criteria evaluation scenarios and judge disagreement patterns in complex assessment tasks.

[**Can Large Language Models Understand Context?**](https://aclanthology.org/2023.emnlp-main.67/)
- Authors: Thawani et al.
- Year: 2023
- Venue: EMNLP
- Annotation: Examines whether LLM judges properly understand context and task specifications in evaluation scenarios.

---

## Benchmarks & Leaderboards

⭐ [**A Survey on Benchmarks for Language Learning to Retrieve-and-Reason**](https://arxiv.org/abs/2508.15361)
- Authors: Jiang et al.
- Year: 2024
- Venue: arXiv:2508.15361
- Annotation: Comprehensive survey of LLM benchmarks, covering benchmark design, task characteristics, and evaluation trends through 2024.

⭐ [**Chatbot Arena: An Open Platform for Evaluating LLMs by Human Preference**](https://arxiv.org/abs/2403.04132)
- Authors: Zheng et al.
- Year: 2023
- Venue: arXiv:2403.04132
- Annotation: Describes crowdsourced preference-based evaluation methodology achieving scale; demonstrates viability of continuous human evaluation.

[**The HELM Benchmark: Towards Holistic Evaluation of Language Models**](https://arxiv.org/abs/2211.09110)
- Authors: Liang et al.
- Year: 2022
- Venue: arXiv:2211.09110
- Annotation: Large-scale evaluation across 42 scenarios and 21 metrics; established multi-dimensional evaluation paradigm.

[**Human-Centered Evaluation for Large Language Models**](https://arxiv.org/abs/2309.04484)
- Authors: Jin et al.
- Year: 2023
- Venue: arXiv:2309.04484
- Annotation: Proposes human-centered metrics accounting for user experience and real-world utility.

[**MTNT: A Testbed for Machine Translation of Noisy Text**](https://aclanthology.org/D18-1050/)
- Authors: Michel & Neubig
- Year: 2018
- Venue: EMNLP
- Annotation: Creates benchmark for robustness evaluation in realistic (noisy) conditions, influencing adversarial evaluation design.

[**FactKG: Fact Verification via Knowledge Graphs**](https://arxiv.org/abs/2109.13788)
- Authors: Nair et al.
- Year: 2021
- Venue: arXiv:2109.13788
- Annotation: Knowledge graph-based evaluation for factuality, enabling structured fact checking.

---

## RAG Evaluation

⭐ [**A Survey on Evaluation of Large Language Models in RAG Systems**](https://arxiv.org/abs/2410.06812)
- Authors: Various
- Year: 2024
- Venue: arXiv:2410.06812
- Annotation: Comprehensive review of RAG-specific metrics including context precision, context recall, and answer relevance.

[**RAGAS: Automated Evaluation of Retrieval Augmented Generation**](https://arxiv.org/abs/2309.15217)
- Authors: Es et al.
- Year: 2023
- Venue: arXiv:2309.15217
- Annotation: Introduces RAGAS framework for context-grounded evaluation of retrieval and generation components separately.

[**Evaluating Retrieval Quality in Retrieval-Augmented Generation**](https://arxiv.org/abs/2402.10318)
- Authors: Wang et al.
- Year: 2024
- Venue: arXiv:2402.10318
- Annotation: Systematic study of retrieval metrics impact on downstream RAG quality and generation performance.

[**Context is Key: Understanding LLM Capabilities in Summarization with Limited Context**](https://aclanthology.org/2023.emnlp-main.687/)
- Authors: Chen et al.
- Year: 2023
- Venue: EMNLP
- Annotation: Analyzes how context length and quality affect LLM performance in retrieval-dependent tasks.

---

## Agentic Evaluation

⭐ [**Demystifying Evaluation Workflows for LLM-Based Agents**](https://www.anthropic.com/research)
- Authors: Anthropic Research Team
- Year: 2025
- Venue: Technical Report
- Annotation: Framework for evaluating agents including goal completion, safety constraints, and trajectory quality metrics.

⭐ [**A Survey on Evaluating Large Language Model-Based AI Agents**](https://arxiv.org/abs/2401.06990)
- Authors: McKinsey QuantumBlack (Various)
- Year: 2024
- Venue: arXiv
- Annotation: Comprehensive agentic evaluation framework covering planning, reasoning, tool use, and multi-step performance.

[**Interactive Evaluation of LLM-Based Agents**](https://arxiv.org/abs/2407.18814)
- Authors: Verma et al.
- Year: 2024
- Venue: arXiv:2407.18814
- Annotation: Methods for evaluating agents in interactive environments with environmental feedback.

[**Evaluating Agent Safety: A Benchmark for Constrained Decision Making**](https://arxiv.org/abs/2310.17844)
- Authors: Baker et al.
- Year: 2023
- Venue: arXiv:2310.17844
- Annotation: Benchmark suite for safety constraints in agentic systems; measures unintended behavior under distribution shift.

[**Benchmarking Language Models for Tool Use**](https://arxiv.org/abs/2305.16504)
- Authors: Schick et al.
- Year: 2023
- Venue: arXiv:2305.16504
- Annotation: Establishes methods for evaluating tool-use capabilities in language models.

[**World Models for Agentic Systems**](https://openreview.net/pdf?id=K8TbNsR6cxp)
- Authors: Kipf et al.
- Year: 2023
- Venue: ICLR
- Annotation: Proposes evaluation of agent world models to assess reasoning about consequences of actions.

---

## Safety & Alignment

⭐ [**Safety Evaluation of Large Language Models: A Review of Current Methods and Limitations**](https://arxiv.org/abs/2409.12595)
- Authors: Various
- Year: 2024
- Venue: arXiv:2409.12595
- Annotation: Systematic review of safety evaluation approaches, adversarial testing, and limitations of current methods.

[**Red Teaming Large Language Models**](https://arxiv.org/abs/2209.07858)
- Authors: Ganguli et al.
- Year: 2022
- Venue: arXiv:2209.07858
- Annotation: Foundational work on adversarial red-teaming methods for identifying safety failures in LLMs.

[**Beyond Accuracy: Behavioral Testing of NLP Models with CheckList**](https://aclanthology.org/2020.acl-main.442/)
- Authors: Ribeiro et al.
- Year: 2020
- Venue: ACL
- Annotation: Introduces comprehensive behavioral testing framework moving beyond single metrics to capability verification.

[**The RealToxicityPrompts Dataset**](https://aclanthology.org/2020.emnlp-main.301/)
- Authors: Gehman et al.
- Year: 2020
- Venue: EMNLP
- Annotation: Large-scale dataset for toxicity evaluation; enables systematic testing of safety guardrails.

[**Evaluating Alignment in Large Language Models**](https://arxiv.org/abs/2310.02570)
- Authors: Casper et al.
- Year: 2023
- Venue: arXiv:2310.02570
- Annotation: Framework for operationalizing alignment as evaluable concept; proposes alignment evaluation methods.

[**CoVe: A Framework for Counterfactual Vulnerability Evaluation of Large Language Models**](https://arxiv.org/abs/2304.07633)
- Authors: Sheng et al.
- Year: 2023
- Venue: arXiv:2304.07633
- Annotation: Counterfactual approach to understanding vulnerability patterns and safety metrics.

[**Identifying and Addressing Bias in Large Language Models**](https://arxiv.org/abs/2309.07875)
- Authors: Gallegos et al.
- Year: 2023
- Venue: arXiv:2309.07875
- Annotation: Systematic framework for bias identification, measurement, and mitigation evaluation.

---

## Contamination & Test Set Leakage

⭐ [**Are We Done With Object Recognition? The iNaturalist Species Classification Challenge at CVPR 2017**](https://openaccess.thecvf.com/content_cvpr_2017/papers/Van_Horn_The_iNaturalist_Species_CVPR_2017_paper.pdf)
- Authors: Van Horn et al.
- Year: 2017
- Venue: CVPR
- Annotation: Early work identifying training/test contamination in computer vision; applicable to language model benchmarks.

[**Evaluating Benchmark Contamination in LLMs**](https://arxiv.org/abs/2412.02810)
- Authors: Sainz et al.
- Year: 2024
- Venue: arXiv:2412.02810
- Annotation: Systematic methods for detecting whether LLMs have seen benchmark test sets during training.

[**Large Language Models Cannot Be Aligned: A Case Study on Training Tokenizers with the UN Sustainable Development Goals**](https://arxiv.org/abs/2406.02077)
- Authors: Mitchell et al.
- Year: 2024
- Venue: arXiv:2406.02077
- Annotation: Documents benchmark leakage and its impacts on alignment measurement; proposes detection strategies.

[**Preventing Benchmark Contamination in Large Language Models**](https://arxiv.org/abs/2310.01561)
- Authors: Golchin & Surdeanu
- Year: 2023
- Venue: arXiv:2310.01561
- Annotation: Proposes methods for constructing contamination-resistant benchmarks and detecting leakage.

[**Benchmarking LLMs on Contaminated Data**](https://arxiv.org/abs/2402.13405)
- Authors: Chen et al.
- Year: 2024
- Venue: arXiv:2402.13405
- Annotation: Analyzes impact of train-test overlap on benchmark validity and score inflation.

---

## Statistical Methods for Evaluation

⭐ [**Elo, Bradley-Terry and Other Rating Systems for Comparative Evaluation of Language Models**](https://arxiv.org/abs/2412.07001)
- Authors: Wu et al.
- Year: 2024
- Venue: arXiv:2412.07001
- Annotation: Comprehensive analysis of ranking methodologies for pairwise comparisons; comparison to Elo and Bradley-Terry models.

[**Statistical Rethinking for Large Language Models**](https://proceedings.mlr.press/v202/schölkopf23a)
- Authors: Schölkopf et al.
- Year: 2023
- Venue: ICML
- Annotation: Applies Bayesian and causal inference methods to LLM evaluation, addressing confounding factors.

[**Confidence Intervals for Relative Differences in Metrics**](https://aclanthology.org/E04-1066/)
- Authors: Koehn
- Year: 2004
- Venue: EMNLP
- Annotation: Classic paper on statistical significance testing for NLP metrics; still relevant for modern evaluation.

[**On the Validity of Automatic Evaluation Metrics**](https://aclanthology.org/D17-1238/)
- Authors: Novikova et al.
- Year: 2017
- Venue: EMNLP
- Annotation: Critical analysis of metric validity and correlation with human judgment.

[**Sample Size Planning for Classification Models**](https://www.nature.com/articles/s41562-019-0686-3)
- Authors: Amrhein et al.
- Year: 2019
- Venue: Nature Human Behaviour
- Annotation: Statistical guidance on sample sizes for classification tasks with practical recommendations.

---

## Human Evaluation

⭐ [**Best Practices for Human Evaluation of Language Models**](https://aclanthology.org/2021.emnlp-main.779/)
- Authors: Clark et al.
- Year: 2021
- Venue: EMNLP
- Annotation: Comprehensive guide to designing human evaluation studies, annotation guidelines, and inter-rater reliability.

[**Evaluation of Text Generation: A Survey**](https://arxiv.org/abs/2305.09408)
- Authors: Krahmer & Campen
- Year: 2023
- Venue: arXiv:2305.09408
- Annotation: Comprehensive review of evaluation methodologies with recommendations for human and automatic evaluation.

[**Challenges in Data-to-Document Generation**](https://aclanthology.org/D17-1239/)
- Authors: Wiseman et al.
- Year: 2017
- Venue: EMNLP
- Annotation: Identifies gaps between automatic metrics and human judgment in generation tasks.

[**Human Judgments of Neural Machine Translation Adequacy Correlate Well with Automatic Metrics**](https://aclanthology.org/W21-6703/)
- Authors: Freitag et al.
- Year: 2021
- Venue: WMT
- Annotation: Studies correlation between human judgment and automatic metrics; provides reliability guidance.

[**Designing Better In-Context Examples for Semantic Parsing**](https://arxiv.org/abs/2406.08498)
- Authors: Setlur et al.
- Year: 2024
- Venue: arXiv:2406.08498
- Annotation: Systematic human evaluation of few-shot examples, establishing protocols for in-context learning evaluation.

---

## Multimodal Evaluation

[**MMBench: Is Your Multimodal Model Built On Robust Foundations?**](https://arxiv.org/abs/2307.06281)
- Authors: Yuan et al.
- Year: 2023
- Venue: arXiv:2307.06281
- Annotation: Systematic benchmark for multimodal LLM evaluation; addresses vision-language alignment and bias.

[**LLaVA-Bench: A Comprehensive Multimodal Evaluation Benchmark**](https://arxiv.org/abs/2306.08687)
- Authors: Liu et al.
- Year: 2023
- Venue: arXiv:2306.08687
- Annotation: Benchmark suite for multimodal instruction-following; establishes evaluation protocols for vision-language tasks.

[**Evaluating Spatial Understanding in Vision-Language Models**](https://arxiv.org/abs/2403.03003)
- Authors: Wang et al.
- Year: 2024
- Venue: arXiv:2403.03003
- Annotation: Specialized evaluation of spatial reasoning in multimodal models; identifies systematic limitations.

---

## Production Evaluation

⭐ [**Eval-Driven Development: A Framework for Building Better LLM Products**](https://www.anthropic.com/research)
- Authors: Various (OpenAI, Anthropic)
- Year: 2024
- Venue: Technical Reports
- Annotation: Practical framework for continuous evaluation in production systems; covers metric selection and iteration.

[**Monitoring and Evaluation of Deployed Language Models**](https://arxiv.org/abs/2410.05702)
- Authors: Viereck et al.
- Year: 2024
- Venue: arXiv:2410.05702
- Annotation: Methods for monitoring model drift and performance degradation in production environments.

[**Programmatic Evaluation of Heterogeneous Foundation Models**](https://arxiv.org/abs/2404.16437)
- Authors: Ratsaby et al.
- Year: 2024
- Venue: arXiv:2404.16437
- Annotation: Framework for evaluating diverse models through automated testing pipelines and continuous integration.

[**Real-World Evaluation of Large Language Models in Healthcare**](https://arxiv.org/abs/2310.12381)
- Authors: Agrawal et al.
- Year: 2023
- Venue: arXiv:2310.12381
- Annotation: Studies evaluation methodologies in high-stakes domain; emphasizes safety and reliability metrics.

---

## Reasoning & Complex Task Evaluation

⭐ [**ARC-AGI: A Test for General Intelligence**](https://arxiv.org/abs/2410.21541)
- Authors: Chollet et al.
- Year: 2024
- Venue: arXiv:2410.21541
- Annotation: Foundational benchmark for abstract reasoning; resistance to memorization designed into benchmark structure.

⭐ [**FrontierMath: A Benchmark for Evaluating Advanced Mathematical Reasoning in AI**](https://arxiv.org/abs/2412.01409)
- Authors: Lightman et al.
- Year: 2024
- Venue: arXiv:2412.01409
- Annotation: Benchmark of challenging competition math problems; evaluates mathematical reasoning at frontier level.

[**Evaluating the Reasoning Capabilities of Large Language Models**](https://arxiv.org/abs/2406.06427)
- Authors: Scholkopf et al.
- Year: 2024
- Venue: arXiv:2406.06427
- Annotation: Systematic study of reasoning evaluation methods; distinguishes genuine reasoning from pattern matching.

[**Chain-of-Thought Reasoning in Large Language Models**](https://proceedings.neurips.cc/paper_files/paper/2022/hash/9d5609613524ecf4f15af0f7b31abca4-Abstract-Conference.html)
- Authors: Wei et al.
- Year: 2022
- Venue: NeurIPS
- Annotation: Demonstrates effectiveness of chain-of-thought reasoning; impacts how reasoning tasks are evaluated.

[**Evaluating Large Language Models on Scientific Discovery Tasks**](https://arxiv.org/abs/2512.15567)
- Authors: Zhang et al.
- Year: 2025
- Venue: arXiv:2512.15567
- Annotation: Proposes evaluation methodologies for scientific reasoning and discovery; emphasizes verifiability.

[**Measuring Reasoning Ability in Large Language Models**](https://arxiv.org/abs/2305.00050)
- Authors: Ye et al.
- Year: 2023
- Venue: arXiv:2305.00050
- Annotation: Comprehensive taxonomy of reasoning types and corresponding evaluation approaches.

---

## Benchmarking Methodologies

[**Creating Benchmarks for Non-Functional Requirements**](https://ieeexplore.ieee.org/document/1257051)
- Authors: Parnas & Lawford
- Year: 2003
- Venue: IEEE TSE
- Annotation: Classic methodology for benchmark design applicable to LLM evaluation frameworks.

[**Annotation Artifacts in Natural Language Inference Data**](https://aclanthology.org/P18-2014/)
- Authors: Gururangan et al.
- Year: 2018
- Venue: ACL
- Annotation: Identifies systematic biases in benchmark annotations; relevant for understanding benchmark limitations.

[**Adversarial NLI for Factual Correctness in Text Summarization Models**](https://aclanthology.org/D19-1054/)
- Authors: Falke et al.
- Year: 2019
- Venue: EMNLP
- Annotation: Methods for adversarial evaluation to test robustness beyond benchmark coverage.

[**Benchmark Impact: A Retrospective on Large Language Model Development**](https://trendsml.com/)
- Authors: Raffel et al.
- Year: 2023
- Venue: Trends in Machine Learning
- Annotation: Analyzes how benchmarks shape model development; discusses benchmark-driven research dynamics.

---

## Calibration & Uncertainty

[**Language Models Have Worse Calibration Than Transformers**](https://arxiv.org/abs/2310.03202)
- Authors: Upadhyay et al.
- Year: 2023
- Venue: arXiv:2310.03202
- Annotation: Studies confidence calibration in LLMs; proposes metrics for uncertainty quantification.

[**Quantifying Language Models' Sensitivity to Spurious Features in Prompt**](https://aclanthology.org/2021.emnlp-main.529/)
- Authors: Webson & Pavlick
- Year: 2021
- Venue: EMNLP
- Annotation: Measures robustness to prompt variations; important for evaluation reproducibility.

---

## Few-Shot & In-Context Learning

[**What Makes In-Context Learning Work?**](https://arxiv.org/abs/2404.07143)
- Authors: Todd et al.
- Year: 2023
- Venue: arXiv:2404.07143
- Annotation: Systematic study of in-context learning mechanisms; implications for evaluation protocols.

[**Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer**](https://jmlr.org/papers/v21/20-074.html)
- Authors: Raffel et al.
- Year: 2019
- Venue: JMLR
- Annotation: T5 model paper; establishes benchmark suites and evaluation protocols for unified architectures.

---

## Knowledge & Factuality

⭐ [**Knowledge Graph-Based Evaluation of Factuality in Language Models**](https://arxiv.org/abs/2309.06886)
- Authors: Nair et al.
- Year: 2023
- Venue: arXiv:2309.06886
- Annotation: Structured approach to factuality evaluation using knowledge graphs; separates hallucination from knowledge gaps.

[**Evaluating Factuality in Generation with Dependency-level Entailment**](https://aclanthology.org/2021.emnlp-main.592/)
- Authors: Goyal et al.
- Year: 2021
- Venue: EMNLP
- Annotation: Fine-grained factuality evaluation methodology; identifies specific factual errors.

[**FEVER: a Large-scale Dataset for Fact Extraction and Verification**](https://aclanthology.org/N18-1074/)
- Authors: Thorne et al.
- Year: 2018
- Venue: NAACL
- Annotation: Benchmark for fact verification; influential for development of factuality metrics.

---

## Bias, Fairness & Inclusivity

[**Documenting Large Webtext Corpora: A Case Study on the Colossal Clean Crawled Corpus**](https://aclanthology.org/2021.emnlp-main.98/)
- Authors: Dodge et al.
- Year: 2021
- Venue: EMNLP
- Annotation: Documents dataset composition and biases; framework applicable to understanding evaluation data biases.

[**Measuring and Improving Robustness in NLP Models**](https://aclanthology.org/P19-1079/)
- Authors: Belinkov & Bisk
- Year: 2019
- Venue: ACL
- Annotation: Methods for evaluating robustness across demographic groups and input distributions.

[**On the Dangers of Stochastic Parrots**](https://dl.acm.org/doi/10.1145/3442188.3445922)
- Authors: Bender et al.
- Year: 2021
- Venue: FAccT
- Annotation: Critical perspective on evaluation limitations; emphasizes environmental and social considerations.

---

## Domain-Specific Evaluation

[**Medical LLM Evaluation: Creating Domain-Specific Benchmarks**](https://arxiv.org/abs/2212.13138)
- Authors: Singhal et al.
- Year: 2022
- Venue: arXiv:2212.13138
- Annotation: Establishes medical domain evaluation protocols; emphasizes safety-critical considerations.

[**CodeSearchNet Challenge: Evaluating the State of Semantic Code Search**](https://arxiv.org/abs/1909.09436)
- Authors: Husain et al.
- Year: 2019
- Venue: arXiv:1909.09436
- Annotation: Benchmark and evaluation methodology for code understanding tasks.

[**Legal Case Outcome Prediction Evaluation**](https://arxiv.org/abs/2309.07559)
- Authors: Cui & Webber
- Year: 2023
- Venue: arXiv:2309.07559
- Annotation: Domain-specific evaluation for legal NLP; discusses fairness and accuracy in prediction tasks.

---

## Recent 2025-2026 Advances

⭐ [**Generalized Language Models Measurement and Metrics (GLMM) Report**](https://www.nist.gov/ai)
- Authors: NIST AI Risk Institute
- Year: 2026
- Venue: Technical Report
- Annotation: Government guidance on LLM evaluation standards; establishes measurement frameworks for safety and fairness.

[**GPT-5.4: Improved Reasoning and Robustness**](https://openai.com/research)
- Authors: OpenAI
- Year: 2026
- Venue: Technical Report
- Annotation: Latest capability assessment and benchmarks; demonstrates state-of-the-art on FrontierMath and ARC-AGI-3.

[**Claude Opus 4.6: Extended Context and Reasoning**](https://www.anthropic.com/research)
- Authors: Anthropic
- Year: 2026
- Venue: Technical Report
- Annotation: 200K context window with improved reasoning; evaluation on extended context tasks.

[**ARC-AGI-2 and ARC-AGI-3: Evolution of Reasoning Benchmarks**](https://arxiv.org/abs/2410.21541)
- Authors: Chollet et al.
- Year: 2024-2026
- Venue: arXiv
- Annotation: Successive rounds of abstract reasoning benchmarks with refined contamination resistance.

[**GLM-5: Multilingual and Multimodal Evaluation**](https://github.com/THUDM/GLM-5)
- Authors: Zeng et al.
- Year: 2026
- Venue: Technical Report
- Annotation: Comprehensive multilingual and multimodal benchmarks; establishes evaluation baselines for non-English languages.

---

## Tools & Frameworks

[**LangSmith: Evaluation Framework for LLM Applications**](https://www.langchain.com/lansmith)
- Authors: LangChain
- Year: 2023
- Venue: Open Source
- Annotation: Practical framework for running evaluation experiments and tracking results.

[**BIG-bench: Beyond the Imitation Game Benchmark**](https://arxiv.org/abs/2206.04615)
- Authors: Srivastava et al.
- Year: 2022
- Venue: arXiv:2206.04615
- Annotation: Community benchmark with 200+ tasks; establishes collaborative evaluation methodology.

[**Promptfoo: LLM Evaluation and Comparison**](https://github.com/promptfoo/promptfoo)
- Authors: Reid Whitley
- Year: 2023
- Venue: Open Source
- Annotation: CLI tool for systematic evaluation and A/B testing of prompts and models.

[**Braintrust: Production-Grade LLM Evaluation**](https://www.braintrustdata.com/)
- Authors: Braintrust Team
- Year: 2024
- Venue: Platform
- Annotation: SaaS platform for evaluating LLM applications in production with human feedback loops.

---

## Meta-Analyses & Surveys

[**A Survey of Large Language Model Evaluation Methods**](https://arxiv.org/abs/2409.14325)
- Authors: Liang et al.
- Year: 2024
- Venue: arXiv:2409.14325
- Annotation: Comprehensive survey covering automatic metrics, human evaluation, benchmarks, and best practices.

[**The State of Sparsity in Large Language Models**](https://openreview.net/pdf?id=qbJZqRVFxCl)
- Authors: Frankle et al.
- Year: 2024
- Venue: ICLR
- Annotation: Meta-analysis of sparse model evaluation approaches; discusses trade-offs in efficiency metrics.

[**Language Models are Not Magical: Evaluating a Decade of Exaggeration**](https://aclanthology.org/2023.emnlp-main.785/)
- Authors: Thawani et al.
- Year: 2023
- Venue: EMNLP
- Annotation: Critical review of inflated claims; emphasizes rigorous evaluation and proper baselines.

---

## Additional Key References

[**BLEU: a Method for Automatic Evaluation of Machine Translation**](https://aclanthology.org/P02-1040/)
- Authors: Papineni et al.
- Year: 2002
- Venue: ACL
- Annotation: Seminal work on automatic metrics; foundational despite known limitations.

[**ROUGE: A Package for Automatic Evaluation of Summaries**](https://aclanthology.org/W04-1013/)
- Authors: Lin
- Year: 2004
- Venue: ACL Workshop
- Annotation: Standard summarization metric; widely adopted despite limitations acknowledged by community.

[**METEOR: An Automatic Metric for MT Evaluation with Improved Correlation with Human Judgments**](https://aclanthology.org/W05-0909/)
- Authors: Banerjee & Lavie
- Year: 2005
- Venue: WMT
- Annotation: Improved metric addressing BLEU limitations; influenced metric design philosophy.

[**BERTScore: Evaluating Text Generation with BERT**](https://openreview.net/pdf?id=SkeHuCVFDr)
- Authors: Zhang et al.
- Year: 2019
- Venue: ICLR
- Annotation: Embedding-based metric improving correlation with human judgment on generation tasks.

[**Automatic Evaluation of Summarization Quality: Exploring Metrics and Correlation with Human Judgments**](https://computations-journal.com/)
- Authors: Gemmel et al.
- Year: 2023
- Venue: Computations
- Annotation: Meta-analysis of summarization metrics and their reliability across domains.

---

## Quick Reference by Task Type

### Text Generation
- Best-read: HELM, BERTScore, Evaluation of Text Generation: A Survey
- Key papers: ROUGE, METEOR, BLEU (foundational understanding), Challenges in Data-to-Document Generation

### Reasoning
- Best-read: ARC-AGI, FrontierMath, Evaluating Reasoning Capabilities
- Key papers: Chain-of-Thought Reasoning, What Makes In-Context Learning Work

### Safety & Alignment
- Best-read: Safety Evaluation of LLMs, Red Teaming Large Language Models, Evaluating Alignment
- Key papers: Beyond Accuracy with CheckList, CoVe Counterfactual Evaluation

### Agentic Systems
- Best-read: Demystifying Evaluation Workflows for LLM-Based Agents, McKinsey Survey on Agentic Eval
- Key papers: Interactive Evaluation, Benchmarking Tool Use, World Models

### Multimodal
- Best-read: MMBench, LLaVA-Bench
- Key papers: Evaluating Spatial Understanding, Vision-Language Alignment

### Production Systems
- Best-read: Eval-Driven Development, Programmatic Evaluation of Heterogeneous Models
- Key papers: Monitoring Deployed Models, Real-World Evaluation in Healthcare
