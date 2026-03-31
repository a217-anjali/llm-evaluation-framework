# Eval Landscape Changelog

Quarterly chronicle of major developments in LLM evaluation from Q1 2023 through Q1 2026. Tracks model releases, benchmark innovations, tooling advances, and methodological progress.

---

## Q1 2023: Foundation Era

**Model Releases**
- GPT-4 (March 2023): OpenAI's most capable model; sets new evaluation baseline with multimodal capabilities. Establishes GPT-4 as de facto judge model for subsequent evaluation work.
- PaLM 2 (May 2023): Google's improved large language model with better reasoning.

**Benchmarks & Datasets**
- HELM framework published (March 2023): Introduces holistic multi-scenario evaluation across 42 scenarios; becomes foundational methodology.
- GLUE and SuperGLUE benchmarks mature: Establishing standard NLU evaluation practices.

**Methodology Advances**
- Early adoption of LLM-as-judge approaches begins; GPT-4 used informally for comparative evaluation.
- Human evaluation standards emerging in research community.
- First serious discussions about benchmark contamination risks.

**Notable Events**
- LLM evaluation emerges as critical research area as model capabilities rapidly scale.
- Industry recognition that simple accuracy metrics insufficient for complex tasks.

---

## Q2 2023: Benchmark Explosion

**Model Releases**
- Llama (February 2023): Meta's open-source model family enables accessible benchmarking.
- Llama 2 (July 2023): Significant improvement spawns evaluation on instruction-following tasks.

**Benchmarks & Datasets**
- RealToxicityPrompts dataset mature use for safety evaluation (April 2023).
- Chatbot Arena (March 2023): LMSYS launches continuous human preference evaluation platform using Elo ratings.
- MT-Bench released: Instruction-following benchmark enabling comparative ranking.

**Methodology Advances**
- Chatbot Arena's Bradley-Terry model provides statistically grounded ranking methodology.
- Community converges on multi-turn conversation evaluation.
- Preference-based evaluation gains momentum over single-metric approaches.

**Tools & Infrastructure**
- Early iteration of evaluation frameworks for production LLM deployment.

**Notable Events**
- GPT-4 vs. Claude comparisons drive need for standardized evaluation.
- Open-source evaluation becoming priority in research community.

---

## Q3 2023: Diversification

**Model Releases**
- Mistral 7B (September 2023): Demonstrates strong performance at smaller scale; requires different evaluation approach for efficiency.
- MPT models released: Further diversity in model capabilities.

**Benchmarks & Datasets**
- Needle in a Haystack benchmark (August 2023): Evaluates long-context retrieval capability.
- BigBench expanded: Community contributes 200+ diverse evaluation tasks.
- FEVER dataset widely adopted for factuality evaluation.

**Methodology Advances**
- Long-context evaluation emerges as distinct subfield.
- Hallucination and factuality measurement techniques improve.
- RAG evaluation methodologies begin formalizing.

**Notable Events**
- Chatbot Arena shows strong user engagement; becomes de facto leaderboard.
- Research community increasingly skeptical of single-benchmark evaluation claims.

---

## Q4 2023: Production Focus

**Model Releases**
- GPT-3.5 Turbo updated (November 2023): Improved efficiency drives production adoption.
- Mixtral 8x7B (December 2023): MoE models introduce evaluation complexity.

**Benchmarks & Datasets**
- GSM8K benchmark widely adopted for math reasoning evaluation.
- HumanEval extended for more comprehensive code evaluation.
- MMLU benchmark saturation concerns emerge.

**Methodology Advances**
- In-context learning evaluation becomes more rigorous.
- Preference-based evaluation dominates comparative study.
- Production monitoring and eval-driven development papers appear.

**Tools & Infrastructure**
- LangSmith framework development (LangChain ecosystem).
- Evaluation infrastructure startups emerge.

**Notable Events**
- Year end: Recognition that benchmark progress not tracking real-world capability improvement.
- Industry shift toward continuous evaluation in production.

---

## Q1 2024: Saturation Recognition

**Model Releases**
- GPT-4 Turbo (December 2023, continuing): Extended context improves RAG capabilities.
- Llama 3 (April 2024): New base model with different evaluation characteristics.

**Benchmarks & Datasets**
- Benchmark saturation clearly observed across multiple suites.
- Concerns about memorization and contamination increase.
- OpenAI releases detailed contamination analysis tools.

**Methodology Advances**
- Researchers propose new benchmarks targeting frontier capabilities.
- Contamination detection methods become standard practice.
- Agent evaluation frameworks begin standardizing.

**Notable Events**
- Major acknowledgment: existing benchmarks reaching ceiling for current model scale.
- Community demands harder, more diverse evaluation.

---

## Q2 2024: Evaluation Innovation

**Model Releases**
- Claude 3 (March 2024): Anthropic's flagship model demonstrates strong evaluation performance across diverse benchmarks.
- Gemini (April 2024): Google's multimodal model requires extensive multimodal evaluation.
- Mistral Large (April 2024): Competitive alternative to GPT-4.

**Benchmarks & Datasets**
- MMBench released: Comprehensive multimodal evaluation benchmark.
- LLaVA-Bench established for vision-language evaluation.
- SciEval (June 2024): Scientific reasoning evaluation benchmark.
- Math evaluation benchmarks expand with higher difficulty levels.

**Methodology Advances**
- LLM-as-Judge papers become more rigorous about calibration and bias.
- Agentic evaluation frameworks formalize.
- RAG evaluation surveys published.
- Multi-step reasoning evaluation methodologies advance.

**Tools & Infrastructure**
- Braintrust launches SaaS platform for production evaluation.
- Promptfoo gains popularity for systematic prompt evaluation.
- Evaluation-driven development becomes standard practice.

**Notable Events**
- Q2 2024: Realization that frontier models saturation requires different evaluation approaches.
- Contamination awareness becomes mainstream.

---

## Q3 2024: Frontier Benchmarks

**Model Releases**
- Claude 3.5 Sonnet (June 2024): Improved reasoning and capabilities.
- Llama 3.1 (July 2024): Extended context and improved performance.

**Benchmarks & Datasets**
- ARC-AGI released (August 2024): Abstract reasoning benchmark designed to resist memorization; becomes gold standard for reasoning evaluation.
- FrontierMath announced (August 2024): Competition-level mathematics problems for frontier evaluation.
- ARC-AGI-2 development begins.

**Methodology Advances**
- Contamination detection becomes standard for new benchmarks.
- Benchmark design emphasizes diversity and memorization resistance.
- Reasoning evaluation separates process quality from answer correctness.

**Tools & Infrastructure**
- Production evaluation platforms mature.
- Automated evaluation pipeline tools improve.

**Notable Events**
- Q3 2024: Realization that simple benchmarks inadequate for frontier model evaluation.
- Emphasis on measuring genuine reasoning vs. pattern matching.

---

## Q4 2024: Safety & Alignment Emphasis

**Model Releases**
- GPT-4o improvements (October 2024): Multimodal advances.
- Meta releases newer Llama variants.

**Benchmarks & Datasets**
- Safety evaluation benchmarks expand significantly.
- Alignment evaluation frameworks formalize.
- Multimodal safety benchmarks emerge.

**Methodology Advances**
- Red teaming evaluation becomes systematic practice.
- Fairness and bias evaluation methodology improves.
- Environmental impact evaluation metrics proposed.
- Contamination detection papers publish comprehensive analysis.

**Notable Events**
- Year-end: Recognition that safety evaluation requires distinct methodologies from capability evaluation.
- Regulatory interest in evaluation standards increases.

---

## Q1 2025: Reasoning Model Era

**Model Releases**
- OpenAI o1 (December 2024 / January 2025): Reasoning-focused model with extended thinking capability; requires specialized evaluation.
- DeepSeek-R1 (January 2025): Alternative reasoning model architecture.
- Claude 3.5 Opus (February 2025): Anthropic's reasoning-improved variant.

**Benchmarks & Datasets**
- ARC-AGI-2 released (February 2025): Expanded abstract reasoning benchmark.
- Frontier benchmarks continue expanding with harder instances.
- Scientific discovery evaluation benchmarks emerge.
- Competition problem benchmarks proliferate.

**Methodology Advances**
- Process-based evaluation becomes critical for reasoning models.
- Chain-of-thought quality evaluation methodologies advance.
- Agent trajectory evaluation frameworks formalize.
- Reasoning transparency and interpretability evaluation emerges.

**Tools & Infrastructure**
- Specialized evaluation tools for reasoning models emerge.
- Extended thinking output evaluation tools develop.

**Notable Events**
- Q1 2025: Major shift toward evaluating reasoning quality not just correctness.
- Recognition that existing benchmarks inadequate for reasoning model evaluation.
- Academic interest in formal reasoning verification.

---

## Q2 2025: Contamination Awareness Peak

**Model Releases**
- GPT-5 development rumored near completion.
- Multiple reasoning model variants release.

**Benchmarks & Datasets**
- Contamination analysis becomes routine for all new benchmarks.
- Historical benchmark contamination audits published.
- Benchmark regeneration projects to avoid leakage.
- Multimodal reasoning benchmarks expand.

**Methodology Advances**
- Contamination detection techniques mature.
- Benchmark design principles explicitly include contamination resistance.
- Test set annotation transparency increases.
- Watermarking approaches for contamination detection explored.

**Notable Events**
- Q2 2025: Community consensus that contamination risk is fundamental to benchmarking.
- Calls for "third-party" benchmark governance increase.

---

## Q3 2025: Agentic Evaluation Advances

**Model Releases**
- New agentic-specific models released by multiple organizations.
- Reasoning models improve with iterative feedback.

**Benchmarks & Datasets**
- Specialized agentic evaluation benchmarks proliferate.
- Interactive evaluation frameworks standardize.
- Tool-use benchmarks become comprehensive.
- World modeling evaluation benchmarks proposed.

**Methodology Advances**
- Agent trajectory evaluation becomes standard.
- Goal completion metrics formalize.
- Safety constraint evaluation for agents advances.
- Multi-turn interaction evaluation improves.

**Tools & Infrastructure**
- Agentic evaluation frameworks mature.
- Tool-calling benchmarking tools standardize.
- Agent evaluation dashboards develop.

**Notable Events**
- Q3 2025: Recognition that agentic systems require fundamentally different evaluation.
- Enterprise adoption of agentic evaluation frameworks.

---

## Q4 2025: NIST Standards & Regulatory Focus

**Model Releases**
- Model capability floor continues rising across organizations.
- Reasoning model variants proliferate.

**Benchmarks & Datasets**
- NIST AI Risk Institute releases GLMM (Generalized Language Model Measurement) framework (November 2025): Government guidance on evaluation standards.
- GLM-5 (Chinese language model) released with comprehensive multilingual benchmarks.
- Contaminated benchmark removal accelerates.

**Methodology Advances**
- Regulatory frameworks begin citing evaluation standards.
- Government guidance on evaluation rigor increases.
- Fairness evaluation standards propose (NIST contributions).
- Multi-cultural evaluation importance emphasized.

**Tools & Infrastructure**
- Evaluation tools adapt to NIST GLMM framework.
- Regulatory compliance evaluation tools emerge.
- Third-party benchmarking services expand.

**Notable Events**
- Q4 2025: Major regulatory interest in standardized evaluation.
- NIST GLMM report released (planned November 2025): Government establishes evaluation measurement standards.
- Industry moves toward certified evaluation protocols.

---

## Q1 2026: Frontier Capability Evaluation

**Model Releases**
- GPT-5.4 (March 2026): OpenAI's latest with improved reasoning and extended capabilities. Achieves state-of-the-art on FrontierMath (89% accuracy) and ARC-AGI-3 (94% accuracy).
- Claude Opus 4.6 (March 2026): Anthropic's flagship with 200K token context window and improved agentic reasoning. Demonstrates strong performance on reasoning benchmarks.
- Gemini 3.1 Pro (March 2026): Google's updated model with multimodal and reasoning improvements.
- DeepSeek continues iterations on reasoning models.

**Benchmarks & Datasets**
- ARC-AGI-3 released (January 2026): Third generation abstract reasoning benchmark with further diversity and contamination resistance.
- FrontierMath expanded to 10K+ problems (February 2026).
- Extended context benchmarks mature with 100K+ token examples.
- Multilingual frontier benchmarks proliferate.
- GLM-5 benchmark suite (Chinese foundation model) establishes alternative evaluation standards.

**Methodology Advances**
- Process evaluation becomes primary for reasoning models.
- Agentic evaluation frameworks standardize across industry.
- Extended context evaluation protocols formalize.
- Multimodal reasoning evaluation advances significantly.
- Causal reasoning evaluation emerges as research frontier.

**Tools & Infrastructure**
- Promptfoo acquisition (January 2026): Major platform consolidation in evaluation tools.
- Enterprise evaluation platforms mature.
- Open-source evaluation frameworks mature (LangSmith, others).
- Specialized reasoning evaluation tools standardize.
- Agent evaluation dashboards become comprehensive.

**Notable Events**
- Q1 2026: Recognition of frontier plateau for traditional benchmarks.
- GPT-5.4 and Claude Opus 4.6 achieve near-saturation on most public benchmarks.
- Industry shift to proprietary, continuously-updated evaluation suites.
- Regulatory frameworks citing NIST GLMM becoming standard practice.
- Emergence of "evaluation arms races" with new frontier benchmarks quarterly.
- Academic community proposes more diverse evaluation beyond English-only benchmarks.
- Focus on long-horizon reasoning evaluation increases significantly.

**Prompts & Paradigm Shifts**
- Traditional benchmark-driven development becomes insufficient.
- Evaluation emphasis shifts to process quality, reasoning transparency, and safety assurance.
- Regulatory environment increasingly shapes evaluation priorities.
- Multi-stakeholder evaluation becomes standard practice.
- Third-party certification of evaluation claims becomes expected.

---

## Key Trends Across Timeline

**2023: Foundation**
- Evaluation emerges as critical research area
- HELM and Chatbot Arena establish foundational methodologies
- Community recognizes limitations of single metrics

**2024: Diversification & Saturation**
- Benchmark proliferation and saturation observed simultaneously
- Contamination recognition increases
- Agentic and multimodal evaluation branches formalize
- Safety evaluation specializes

**2025: Reasoning & Standards**
- Reasoning-focused models drive methodological innovation
- NIST GLMM framework establishes regulatory standards
- Contamination awareness becomes mainstream
- Agentic evaluation reaches maturity

**2026: Frontier & Regulation**
- Frontier benchmarks (ARC-AGI-3, FrontierMath) dominate capability discussion
- Regulatory frameworks shape evaluation priorities
- Process-based evaluation dominates reasoning model evaluation
- Industry consolidation in evaluation tools (Promptfoo acquisition)

---

## Evaluation Philosophy Evolution

**2023: "Bigger is Better"**
- Focus on scaling laws and larger benchmark scores
- Single metric comparisons common

**2024: "Score Skepticism"**
- Realization that benchmark progress doesn't guarantee capability improvement
- Multi-dimensional evaluation emphasis
- Contamination concerns rise

**2025: "Process Matters"**
- Shift from outcomes to reasoning quality
- Agentic trajectory evaluation critical
- Reasoning transparency emphasized

**2026: "Context is King"**
- Extended context capabilities redefine evaluation
- Process + outcome + safety framework emerges
- Regulatory framework shapes evaluation
- Multiple stakeholder perspectives required

---

## Notable Milestone Dates

- **March 2023**: GPT-4 release, HELM published
- **March 2023**: Chatbot Arena launches
- **July 2023**: Llama 2 released
- **August 2024**: ARC-AGI released
- **August 2024**: FrontierMath announced
- **December 2024**: OpenAI o1 released (reasoning model)
- **January 2025**: DeepSeek-R1 released
- **February 2025**: ARC-AGI-2 released
- **February 2025**: Claude 3.5 Opus released
- **November 2025**: NIST GLMM framework released
- **January 2026**: Promptfoo acquisition
- **January 2026**: ARC-AGI-3 released
- **March 2026**: GPT-5.4 and Claude Opus 4.6 released

