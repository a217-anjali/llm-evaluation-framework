# Knowledge & Reasoning Benchmarks

## Overview

Knowledge and reasoning benchmarks evaluate an LLM's ability to demonstrate factual understanding, conceptual comprehension, and reasoning capabilities across diverse domains. These benchmarks form the foundation of general capability assessment and remain the most widely cited performance metrics in the field.

## MMLU (Massive Multitask Language Understanding)

### Description
MMLU is the de facto standard for broad knowledge evaluation. It covers 57 diverse domains with 15,908 multiple-choice questions requiring knowledge and reasoning across subjects from elementary mathematics to specialized domains.

### Domains Covered (57)
- **STEM**: Physics, chemistry, biology, computer science, mathematics, engineering
- **Humanities**: History, literature, philosophy, religion, law
- **Social Sciences**: Economics, psychology, sociology, political science
- **Professional**: Medicine, nursing, business, accounting, agriculture
- **Other**: High school knowledge across varied subjects

### Scoring & Methodology
- **Format**: 4-choice multiple-choice questions
- **Evaluation**: Exact match accuracy
- **Passing threshold**: Domain-dependent (60-70% varies by subject)
- **Human baseline**: ~70% (college-educated humans)
- **Difficulty range**: Elementary through specialized professional knowledge

### Current Performance (March 2026)
| Model | Score | Date |
|-------|-------|------|
| Gemini 3.1 Pro | 95.3% | 2026-Q1 |
| GPT-5 | 94.8%+ | 2026-Q1 |
| Claude Opus 4.5 | 93.2% | 2026-Q1 |
| Kimi K2.5 | 93.8% | 2026-Q1 |

### Strengths
- Comprehensive domain coverage enabling diagnostic profiling by subject
- Clear pass/fail metric simplifying interpretation
- Widely adopted enabling cross-model comparison
- Established human baseline allowing contextualization
- Extensive error analysis research revealing knowledge gaps

### Limitations
- Approaching saturation (95.3% vs human 70%) reducing discrimination ability
- Multiple-choice format reduces assessment of explanation quality
- Questions may not reflect real-world knowledge application
- Domain distribution may not reflect deployment importance
- No temporal element (knowledge cutoff effects not measured)

### Recommendations for Use
- Use as primary benchmark for general knowledge evaluation
- Supplement with domain-specific breakdowns for diagnostic analysis
- Combine with MMLU-Pro for more challenging assessment
- Track performance across subject groups to identify knowledge weaknesses

---

## MMLU-Pro (Professional MMLU)

### Description
MMLU-Pro is a significantly harder variant created by filtering MMLU questions and converting 4-choice to 10-choice format, dramatically increasing difficulty. It better discriminates between advanced models and maintains evaluation usefulness as baseline MMLU saturates.

### Key Differences from MMLU
- **Choices**: Increased from 4 to 10 per question
- **Question count**: 12,000 (filtered subset with harder questions)
- **Baseline accuracy**: ~32% (random chance 10%)
- **Human baseline**: ~72-75% (vs MMLU 70%)
- **Intended use**: Discrimination of frontier models

### Scoring & Methodology
- **Format**: 10-choice multiple-choice questions
- **Evaluation**: Exact match accuracy on chosen answer
- **Domain distribution**: Same 57 domains as MMLU (weighted toward challenges)
- **Question source**: Subset of high-error questions from original MMLU

### Current Performance (March 2026)
| Model | Score | Improvement over MMLU |
|-------|-------|----------------------|
| Gemini 3 Pro Preview | 89.8% | Hard discrimination maintained |
| GPT-5 | 87.5%+ | Strong frontier capability |
| Claude Opus 4.5 | 85.3% | Good performance maintained |
| Kimi K2.5 | 86.1% | Competitive frontier |

### Strengths
- Maintains discrimination capability as MMLU saturates
- 10-choice format provides harder alternative-generation challenge
- Filters to genuinely difficult questions avoiding easy "gimmes"
- Still comparable across same 57 domains
- Shows clearer separation between frontier and non-frontier models

### Limitations
- More limited adoption (fewer analyses than MMLU)
- 10-choice format less natural for some domains
- Increased difficulty may reduce applicability to general use cases
- Question filtering methodology affects generalizability
- Smaller score spreads can increase variance significance

### Recommendations for Use
- Use MMLU-Pro as primary benchmark when evaluating frontier models
- Maintain MMLU tracking for comparison and trend analysis
- Use domain breakdowns to identify specific knowledge gaps
- Useful for detecting plateaus in general knowledge development

---

## GPQA Diamond (Graduate-Level Google-Proof Q&A)

### Description
GPQA Diamond is a science-focused benchmark containing 1,531 graduate-level multiple-choice questions across physics, chemistry, and biology. It tests deep scientific understanding and reasoning with questions sourced from PhD-level exams and designed to prevent simple fact-retrieval solutions.

### Question Characteristics
- **Sourcing**: PhD-level exams, academic papers, specialized textbooks
- **Verification**: Human domain experts rate difficulty (requires physicist/chemist level understanding)
- **Content**: Physics (35%), chemistry (35%), biology (30%)
- **Question structure**: All 4-choice format with expert-validated distractors
- **Challenge**: Questions intentionally cannot be solved through keyword matching

### Scoring & Methodology
- **Format**: 4-choice multiple-choice questions
- **Evaluation**: Exact match accuracy
- **Filtering criteria**: Questions where GPT-3.5 accuracy < 80% after multiple attempts
- **Human baseline**: ~65-75% (graduate students in fields)
- **Difficulty**: Approximately college senior to PhD-level understanding

### Current Performance (March 2026)
| Model | Score | Date |
|-------|-------|------|
| Gemini 3.1 Pro | 94.1% | 2026-Q1 |
| GPT-5 | 92.8% | 2026-Q1 |
| Claude Opus 4.5 | 90.3% | 2026-Q1 |
| Gemini 3 Pro | 90.9% | 2025-Q4 |

### Strengths
- Targets deep reasoning over breadth (science specialist benchmark)
- Expert-validated questions ensure genuine difficulty
- Four-choice format maintains clarity while being challenging
- Clear measurement of scientific reasoning capability
- Highly cited in research (strong validation of utility)

### Limitations
- Science-only coverage (not general knowledge)
- Relatively small test set (1,531 questions) increases variance
- Expert validation adds cost, limiting expansion potential
- Saturation risk (94.1% top score suggests approaching limit)
- Four-choice format still allows some process-of-elimination guessing

### Recommendations for Use
- Use for detailed assessment of scientific reasoning
- Essential for models targeting scientific domains
- Pair with MMLU for coverage of both breadth and depth
- Monitor for saturation; watch for variant versions (GPQA Extended, etc.)
- Valuable for detecting AI's scientific understanding limits

---

## Humanity's Last Exam

### Description
Humanity's Last Exam is an intentionally difficult benchmark created by leading AI safety researchers containing 1,000 questions across science and liberal arts. Designed to test deeply integrated knowledge combining multiple domains and requiring sophisticated reasoning—a true frontier benchmark.

### Design Philosophy
- **Intent**: Measure what humans at top universities can do after extensive study
- **Creator collaboration**: Developed with subject matter experts across 20+ fields
- **Question crafting**: Intentionally combine knowledge to require synthesis
- **Verification**: Created to be genuinely challenging to advanced models
- **Difficulty calibration**: Targets 30-50% accuracy for frontier models

### Scoring & Methodology
- **Format**: Multiple-choice (4-choice primary format)
- **Evaluation**: Exact match accuracy
- **Domains**: Science, math, humanities, social sciences
- **Question style**: Synthesis questions requiring integrated knowledge
- **Human baseline**: ~60-70% (well-educated humans with preparation)

### Current Performance (March 2026)
| Model | Score | Interpretation |
|-------|-------|-----------------|
| Gemini 3.1 Pro | 44.7% | Frontier capability demonstrated |
| GPT-5 | 42.3% | Frontier models struggle significantly |
| Claude Opus 4.5 | 38.9% | Below human expert baseline |
| Gemini 3 Pro | 41.2% | Consistent frontier challenge |

### Key Observations
- Represents true frontier—all models significantly below human baseline
- Consistent performance below 50% across all frontier models
- Domain-specific analysis shows particular weakness in humanities reasoning
- Synthesis questions expose reasoning limitations more clearly
- Effective at identifying model reasoning weaknesses

### Strengths
- Genuinely challenging (avoids saturation issues)
- Measures integrated reasoning across domains
- Expert-designed for maximum discriminative power
- Clear frontier benchmark (real performance ceiling)
- Excellent for identifying specific reasoning weaknesses

### Limitations
- Limited domain coverage (1,000 questions total)
- Smaller scale than MMLU (higher variance)
- Still developing as benchmark (fewer published analyses)
- Human baseline complexity (varies by subject area)
- Some questions may be ambiguously phrased

### Recommendations for Use
- Essential for frontier model evaluation
- Valuable for identifying reasoning capability limits
- Use domain analysis to spot weakness areas
- Expect lower performance than MMLU (intentional design)
- Useful for monitoring long-term improvement in reasoning

---

## BFCL (Blur Foundation Chinese Language)

### Description
BFCL is an extensive Chinese language benchmark measuring knowledge and reasoning across diverse domains in Chinese. While primarily focused on non-English language capability, it provides critical assessment for understanding cross-lingual knowledge transfer.

### Coverage
- **Language**: Simplified Chinese (with traditional variants)
- **Domains**: Similar to MMLU coverage (57+ domains)
- **Question count**: Similar scale to MMLU (15,000+ questions)
- **Modality**: Text-based multiple-choice (primarily)
- **Cultural context**: Chinese-specific knowledge and reasoning

### Scoring & Methodology
- **Format**: Multiple-choice questions with varying choice counts
- **Evaluation**: Exact match accuracy
- **Difficulty calibration**: Equivalent to MMLU difficulty in translated questions
- **Mixed sources**: Some translation of MMLU, some original Chinese content
- **Domain balance**: Representation of domains relevant to Chinese-speaking users

### Current Performance (March 2026)
| Model | Score | Notes |
|-------|-------|-------|
| Claude Opus 4.5 | ~88% | Strong Chinese language capability |
| GPT-5 | ~86%+ | Frontier multilingual performance |
| Gemini 3.1 Pro | ~85% | Competitive multilingual capability |

### Strengths
- Essential for non-English language evaluation
- Substantial domain coverage in Chinese
- Measures both translation quality and native understanding
- Large test set ensures statistical significance
- Important for global model assessment

### Limitations
- Translation issues may affect validity of some questions
- Cultural context differences (e.g., Chinese education system)
- Smaller community relative to English benchmarks
- Fewer published domain-specific analyses
- Ongoing updates affect historical comparisons

### Recommendations for Use
- Use for comprehensive evaluation of Chinese language capability
- Important for models targeting Chinese-language users
- Combine with MMLU-ProX for multilingual assessment
- Track separately from English benchmarks (not directly comparable)
- Essential component of global evaluation strategy

---

## Benchmark Comparison Matrix

| Aspect | MMLU | MMLU-Pro | GPQA Diamond | Humanity's Last Exam | BFCL |
|--------|------|----------|--------------|----------------------|------|
| **Difficulty** | Medium | Hard | Hard | Very Hard | Medium |
| **Domain Breadth** | 57 domains | 57 domains | 3 domains (science) | 20+ domains | 57+ domains |
| **Scale** | 15,908 Qs | 12,000 Qs | 1,531 Qs | 1,000 Qs | 15,000+ Qs |
| **Format** | 4-choice | 10-choice | 4-choice | 4-choice | Multiple |
| **Saturation Risk** | High (95.3%) | Medium (89.8%) | Medium (94.1%) | Low (44.7%) | Medium |
| **Use Case** | General | Frontier discrimination | Science specialist | Frontier reasoning | Multilingual |

## Integrated Evaluation Strategy

### For General-Purpose Models
1. Start with MMLU for baseline knowledge assessment
2. Add MMLU-Pro for frontier model discrimination
3. Include GPQA Diamond for science reasoning verification
4. Add BFCL if non-English capability is required

### For Frontier Research Models
1. Use MMLU-Pro as primary knowledge benchmark
2. Prioritize Humanity's Last Exam for reasoning frontier
3. Include GPQA Diamond for specialized reasoning depth
4. Add domain-specific benchmarks for targeted analysis

### For Production Systems
1. Track MMLU for baseline knowledge maintenance
2. Use MMLU-Pro for performance verification on harder tasks
3. Combine with task-specific benchmarks matching deployment domain
4. Include GPQA Diamond if scientific reasoning is required

## Performance Trends & Future Outlook

**Current Trends (Q1 2026)**:
- MMLU saturation: Major frontier models approaching 95%+
- MMLU-Pro stabilizing differentiation for frontier models
- GPQA Diamond showing saturation risk (94.1% top score)
- Humanity's Last Exam maintaining frontier challenge effectively
- Multilingual benchmarks (BFCL, MMLU-ProX) gaining importance

**Expected Developments**:
- MMLU variants with harder variants (MMLU-ProX+) likely emerging
- Humanity's Last Exam becoming primary frontier benchmark
- Greater focus on reasoning depth over knowledge breadth
- Increased emphasis on multilingual and domain-specific variants
- Possible introduction of even harder reasoning benchmarks

## References and Resources

**Official Repositories**:
- MMLU: https://github.com/hendrycks/test
- MMLU-Pro: https://github.com/TIGER-AI-Lab/MMLU-Pro
- GPQA Diamond: https://github.com/google-deepmind/gpqa
- Humanity's Last Exam: https://huggingface.co/datasets/GAIR/HLE

**Leaderboards**:
- OpenCompass: https://opencompass.org.cn
- HELM: https://crfm.stanford.edu/helm/
- Hugging Face Open LLM Leaderboard: https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard
