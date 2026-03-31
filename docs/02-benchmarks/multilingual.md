# Multilingual & Cross-Lingual Benchmarks

## Overview

Multilingual benchmarks evaluate LLM capabilities across diverse languages and writing systems, from high-resource languages like English and Mandarin to low-resource and endangered languages. These benchmarks are critical as models serve increasingly global audiences and need to demonstrate equitable performance across languages.

---

## MMLU-ProX

### Description
MMLU-ProX extends MMLU-Pro to 29 languages, testing whether frontier models maintain knowledge and reasoning capability across linguistically diverse contexts. It measures cross-lingual knowledge transfer and potential knowledge inequities.

### Benchmark Design
- **Language coverage**: 29 languages spanning major language families
- **Languages included**:
  - European: English, German, French, Spanish, Italian, Portuguese, Dutch, Polish, Russian
  - Asian: Mandarin, Japanese, Korean, Hindi, Thai, Vietnamese
  - Middle Eastern: Arabic, Hebrew
  - African: Swahili
  - Other: Turkish, Indonesian, Filipino, Hebrew, Greek, Czech, Swedish, Norwegian, Danish
- **Format**: 10-choice multiple-choice (same as MMLU-Pro)
- **Question count**: ~12,000 items per language
- **Domain coverage**: 57 domains (same as MMLU-Pro)

### Translation Approach
- **Methodology**: Professional translation with cultural adaptation
- **Quality control**: Native speaker review
- **Domain expertise**: Subject matter experts for technical domains
- **Equivalence**: Maintain difficulty across language versions
- **Variations**: Some cultural/linguistic adaptations

### Scoring & Methodology
- **Format**: 10-choice multiple-choice questions
- **Evaluation**: Exact match accuracy per language
- **Metric**: Average accuracy across all languages
- **Language-specific**: Separate metrics for each language
- **Comparison**: Cross-language performance variation

### Current Performance (March 2026)
| Performance Level | English | High-Resource | Mid-Resource | Low-Resource |
|---|---|---|---|---|
| Frontier models | 87%+ | 84%+ | 78%+ | 72%+ |
| GPT-5 | 88%+ | 85%+ | 79%+ | 73%+ |
| Gemini 3.1 Pro | 86%+ | 83%+ | 76%+ | 70%+ |
| Average | ~88% | ~84% | ~77% | ~71% |

### Language Group Performance
| Group | Representative | Score | Gap |
|-------|---|---|---|
| English (high-resource) | English | 88%+ | Baseline |
| European | German, French | 85%+ | -3% |
| East Asian | Chinese, Japanese | 83%+ | -5% |
| South Asian | Hindi | 79%+ | -9% |
| Low-resource | Swahili | 71%+ | -17% |

### Knowledge Equity Analysis
- **High-resource languages**: Near English performance (85%+)
- **Mid-resource languages**: 3-8% gap
- **Low-resource languages**: 15-20% gap
- **Systemic inequity**: Clear resource-performance correlation

### Strengths
- Comprehensive language coverage (29 languages)
- Identifies language-specific capability gaps
- Measures knowledge equity across languages
- Professional translation and cultural adaptation
- Large scale per language (~12,000 items)

### Limitations
- Translation introduces new variability
- Cultural adaptation affects comparability
- Some languages significantly harder (natural variation)
- Language availability limited (many languages missing)
- Establishing equivalence across languages difficult

### Recommendations for Use
- Essential for truly multilingual models
- Use language group analysis for equity assessment
- Identify specific language weaknesses
- Important for global deployment
- Track improvement in underserved languages

---

## Global-MMLU-Lite

### Description
Global-MMLU-Lite provides coverage of 50+ languages with a lighter evaluation set (fewer items per language) to facilitate broader language coverage. It prioritizes language diversity over depth per language.

### Benchmark Design
- **Language coverage**: 50+ languages
- **Language families**:
  - Indo-European (20+ languages)
  - Sino-Tibetan (5+ languages)
  - Afro-Asiatic (8+ languages)
  - Niger-Congo (8+ languages)
  - Austronesian (5+ languages)
  - Other (10+ languages)
- **Question count**: ~5,000 items per language (lighter)
- **Domain coverage**: Subset of major domains
- **Focus**: Breadth over depth

### Language Distribution
| Classification | Count | Examples |
|---|---|---|
| High-resource (100M+ speakers) | 15+ | English, Mandarin, Spanish |
| Mid-resource (10-100M) | 20+ | Polish, Vietnamese, Hebrew |
| Low-resource (<10M) | 15+ | Icelandic, Basque, Swahili |

### Scoring & Methodology
- **Format**: Multiple-choice with varying choice counts
- **Evaluation**: Accuracy per language
- **Metric**: Average across all languages
- **Language-specific**: Breakdown by language and family
- **Family analysis**: Indo-European vs. other families

### Current Performance (March 2026)
| Model | High-Resource | Mid-Resource | Low-Resource | Average |
|-------|---|---|---|---|
| Frontier models | 86%+ | 80%+ | 68%+ | 78%+ |
| GPT-5 | 87%+ | 81%+ | 69%+ | 79%+ |
| Gemini 3.1 Pro | 85%+ | 78%+ | 65%+ | 76%+ |
| Average | ~86% | ~79% | ~67% | ~77% |

### Language Family Performance
| Family | Count | Avg Score | Challenge |
|--------|-------|-----------|-----------|
| Indo-European | 20+ | 82%+ | Well-supported |
| Sino-Tibetan | 5+ | 80%+ | Good |
| Afro-Asiatic | 8+ | 76%+ | Moderate |
| Niger-Congo | 8+ | 72%+ | Challenging |
| Austronesian | 5+ | 75%+ | Moderate |

### Coverage Trade-offs
- **MMLU-ProX**: Deeper (12,000 items) but fewer languages (29)
- **Global-MMLU-Lite**: Broader (50+ languages) but lighter (5,000 items)
- **Use together**: Complementary coverage

### Strengths
- Broader language coverage (50+ languages)
- Identifies language family patterns
- Covers endangered and underserved languages
- Lighter evaluation (faster assessment)
- Good for detecting gross inequities

### Limitations
- Lighter evaluation (only ~5,000 items per language)
- Less detailed error analysis possible
- Smaller sample introduces higher variance
- Family-level analysis may hide within-family variation
- Some languages still missing

### Recommendations for Use
- Use for breadth-focused multilingual assessment
- Combine with MMLU-ProX for comprehensive coverage
- Identify language family-specific challenges
- Important for global accessibility
- Good for detecting major inequities

---

## MMTEB (Multilingual Massive Text Embedding Benchmark)

### Description
MMTEB is a comprehensive multilingual embedding evaluation benchmark with 131 tasks across 250+ languages testing semantic understanding, retrieval, clustering, and similarity across diverse languages and writing systems.

### Benchmark Scope
- **Task count**: 131 diverse evaluation tasks
- **Language coverage**: 250+ languages and language variants
- **Task types**:
  - Semantic similarity (sentence pairs)
  - Retrieval (document retrieval, QA)
  - Clustering (unsupervised grouping)
  - Classification (document and multilingual)
  - STS (semantic textual similarity)
  - PairClassification (semantic relationships)
- **Modality**: Text-only embeddings
- **Granularity**: Word, sentence, document level

### Task Distribution
| Category | Tasks | Languages | Scale |
|----------|-------|-----------|-------|
| Semantic similarity | 30+ | 100+ | Large-scale |
| Retrieval | 40+ | 150+ | Specialized |
| Clustering | 20+ | 120+ | Moderate |
| Classification | 25+ | 180+ | Diverse |
| Other | 16+ | Specialized | Varied |

### Scoring & Methodology
- **Metric**: NDCG (for ranking), F1 (for classification), Cosine similarity
- **Evaluation**: Task-specific metrics
- **Language grouping**: Evaluate by language and language family
- **Coverage**: Can measure performance on specific languages
- **Aggregation**: Macro and micro-averaged scores

### Current Performance (March 2026)
| Model | Languages Covered | Average Score | Best Language | Worst Language |
|-------|---|---|---|---|
| Gemini Embedding 001 | 250+ | 68.32% | 91%+ | 45%+ |
| OpenAI text-embedding-3 | 240+ | 65.8% | 90%+ | 42%+ |
| Frontier embeddings | 200+ | 62-68% | 85%+ | 40-50% |

### Performance by Language Group
| Group | Count | Avg Score | Challenge |
|-------|-------|-----------|-----------|
| High-resource European | 15+ | 78%+ | Well-supported |
| High-resource Asian | 10+ | 75%+ | Well-supported |
| Mid-resource | 40+ | 66%+ | Moderate |
| Low-resource | 80+ | 52%+ | Significant challenge |
| Endangered | 100+ | 35-50% | Frontier |

### Coverage Analysis
- **100+ languages**: Excellent coverage from frontier models
- **200+ languages**: Good coverage with degradation
- **250+ languages**: Fair coverage but with significant variance
- **Most languages**: Significant performance drops

### Strengths
- Massive language coverage (250+ languages)
- Diverse task types reflecting real use
- Automated evaluation enabling scale
- Clear language-specific metrics
- Represents frontier of multilingual embedding

### Limitations
- Large scale reduces per-language analysis depth
- Task distribution may not reflect importance
- Language coverage still incomplete (1000s languages exist)
- Quality variance in non-English datasets
- Embedding evaluation less interpretable than generation

### Recommendations for Use
- Essential for multilingual embedding systems
- Primary metric for semantic understanding across languages
- Use for identifying critical language gaps
- Important for global search and retrieval systems
- Track language-specific improvement

---

## TurkBench

### Description
TurkBench is a multilingual benchmark focusing on 10+ underserved and Turkish-related languages, providing deep evaluation of often-overlooked languages important to significant populations but underrepresented in AI evaluation.

### Benchmark Focus
- **Primary focus**: Turkish and related Turkic languages
- **Languages**:
  - Turkish (47M speakers)
  - Azerbaijani (25M speakers)
  - Uzbek (25M speakers)
  - Uyghur (10M speakers)
  - Kyrgyz (4M speakers)
  - Kazakh (18M speakers)
  - Turkmen (6M speakers)
  - Plus related minority languages
- **Task diversity**: QA, translation, classification, generation
- **Evaluation depth**: Deep evaluation per language

### Task Types
| Type | Languages | Scale | Focus |
|------|-----------|-------|-------|
| QA | All | Large | Comprehension |
| Classification | All | Moderate | Topic understanding |
| Generation | Turkish + 2 major | Moderate | Creative capability |
| Translation | Turkish + variants | Large | Cross-lingual transfer |

### Scoring & Methodology
- **Format**: Diverse task types adapted per language
- **Evaluation**: Task-specific automatic metrics
- **Metric**: Accuracy, BLEU/METEOR, semantic similarity
- **Language-specific**: Detailed breakdown per language
- **Quality**: Native speaker review important

### Current Performance (March 2026)
| Language | Population | Models Tested | Avg Score |
|----------|-----------|---|---|
| Turkish | 47M | 12+ | ~80% |
| Azerbaijani | 25M | 8+ | ~76% |
| Uzbek | 25M | 6+ | ~72% |
| Uyghur | 10M | 4+ | ~65% |
| Smaller | Varied | 2-4 | 50-70% |

### Turkic Language Group Performance
| Language Size | Representation | Score | Gap |
|---|---|---|---|
| >20M speakers | Good | 76%+ | Minimal |
| 10-20M speakers | Fair | 72%+ | Moderate |
| <10M speakers | Poor | 65%+ | Significant |

### Importance Metrics
- **Speaker population**: Turkic languages represent 150M+ speakers
- **Economic importance**: Strategic regions (Central Asia, Middle East)
- **Underrepresentation**: Historically overlooked in AI development
- **Equity**: Important for global language equity

### Strengths
- Deep evaluation of underserved languages
- Addresses specific speaker population needs
- Multiple task types per language
- Native speaker involvement
- Focuses on equity for large overlooked population

### Limitations
- Limited to Turkic and related languages
- Smaller test set than universal benchmarks
- Language-specific evaluation complexity
- Fewer models supporting these languages
- Resource constraints limit expansion

### Recommendations for Use
- Important for Turkic language system evaluation
- Essential for Middle East and Central Asian deployment
- Use for equity assessment in language coverage
- Track support for underserved languages
- Prioritize if serving these language communities

---

## Alder Polyglot

### Description
Alder Polyglot is a 40+ language code generation benchmark measuring programming capability across diverse languages, from high-resource (Python, Java) to low-resource languages (underrepresented programming languages).

### Benchmark Design
- **Language coverage**: 40+ programming languages
- **Language range**:
  - High-resource: Python, JavaScript, Java, C++, Go, Rust
  - Mid-resource: PHP, Ruby, Swift, Kotlin, Scala
  - Low-resource: Lisp dialects, Prolog, Scheme, Julia
  - Domain-specific: SQL, R, MATLAB, Lua
- **Task types**:
  - Function implementation
  - Algorithm problems
  - Code completion
  - Bug fixing
  - Program synthesis
- **Test scale**: 300+ problems total across languages

### Language Distribution
| Category | Count | Examples |
|----------|-------|----------|
| High-resource | 8+ | Python, JavaScript, Java |
| Mid-resource | 15+ | PHP, Ruby, Swift |
| Low-resource | 12+ | Prolog, Lisp, Julia |
| Domain-specific | 5+ | SQL, R, MATLAB |

### Scoring & Methodology
- **Format**: Function specification + generate implementation
- **Evaluation**: Execute against test cases
- **Metric**: Pass@1 (first generation)
- **Language-specific**: Separate evaluation per language
- **Complexity**: Varies by language ecosystem

### Current Performance (March 2026)
| Language Category | Frontier Score | Languages |
|---|---|---|
| High-resource | 87%+ | Python, JavaScript |
| Mid-resource | 75%+ | Ruby, PHP, Swift |
| Low-resource | 52%+ | Lisp, Prolog |
| Domain-specific | 68%+ | SQL, R, MATLAB |
| Average | ~76% | All languages |

### Language-Specific Performance
| Language | Score | Ecosystem | Difficulty |
|----------|-------|-----------|-----------|
| Python | 89%+ | Mature | Easy |
| JavaScript | 87%+ | Mature | Easy |
| Java | 85%+ | Mature | Medium |
| Ruby | 76%+ | Smaller | Medium-Hard |
| Prolog | 48%+ | Niche | Very Hard |

### Factors Affecting Performance
- **Ecosystem maturity**: More training data = higher performance
- **Language popularity**: Popular languages more data
- **Syntax complexity**: Unusual syntax harder (Lisp, Prolog)
- **Community size**: Affects code availability for training
- **Use frequency**: More used languages higher performance

### Strengths
- Broad language coverage (40+ languages)
- Identifies language capability gaps
- Tests practical programming skill across domains
- Reveals training data biases
- Important for true language-agnostic capability

### Limitations
- Code generation less mature than natural language
- Smaller test sets per language
- Syntax differences make comparison harder
- Test case design language-specific
- Lower overall performance than English-centric

### Recommendations for Use
- Essential for claims of polyglot capability
- Use for identifying language ecosystem gaps
- Important for cross-language development teams
- Track support for less common languages
- Useful for detecting training data bias

---

## Multilingual Benchmark Comparison

| Benchmark | Focus | Languages | Scale | Best For |
|-----------|-------|-----------|-------|----------|
| MMLU-ProX | Knowledge depth | 29 | 12,000 per | Deep comparison |
| Global-MMLU-Lite | Knowledge breadth | 50+ | 5,000 per | Broad coverage |
| MMTEB | Embeddings | 250+ | 131 tasks | Semantic understanding |
| TurkBench | Underserved | 10+ Turkic | Deep | Equity focus |
| Alder Polyglot | Code | 40+ languages | 300+ items | Programming |

---

## Multilingual Evaluation Strategy

### For Global Models
1. MMLU-ProX (comprehensive language comparison)
2. Global-MMLU-Lite (broader language coverage)
3. MMTEB (embedding capability)

### For Language-Specific Optimization
1. TurkBench (if Turkic focus)
2. Domain-specific benchmarks in target language
3. Human evaluation in target language

### For Code Generation
1. Alder Polyglot (primary - programming)
2. General code benchmarks in English
3. Language-specific code evaluation

### For Embedding Systems
1. MMTEB (primary - 250+ languages)
2. Language-specific retrieval benchmarks
3. Cross-lingual transfer tests

---

## Performance Trends & Key Observations (March 2026)

### Language Hierarchy
- **English**: Baseline performance (~88% on MMLU-ProX)
- **High-resource non-English**: -2% to -5% gap
- **Mid-resource**: -8% to -12% gap
- **Low-resource**: -15% to -25% gap
- **Endangered**: Often <50% or no coverage

### Equity Issues
- **Systemic inequity**: Consistent 15-20% gap for low-resource languages
- **Coverage inequity**: Many languages completely missing from evaluation
- **Data availability**: Training data scarcity creates performance gaps
- **Algorithm bias**: Models may not be optimized for linguistic diversity

### Language Family Patterns
- **Indo-European**: Generally best support (~85%+ high-resource)
- **Sino-Tibetan**: Good support (~80%+)
- **Afro-Asiatic**: Moderate support (~75%+)
- **Niger-Congo**: Limited support (~70%)
- **Endangered families**: Often <50% or missing

### Model Specialization
- **Multilingual-optimized models**: Show better low-resource performance
- **English-first models**: Large gap (20%+ on low-resource)
- **Regional models**: Excel in local language family
- **Polyglot models**: Better equity but lower absolute performance

---

## Recommendations for Equitable Evaluation

### Assessment Best Practices
1. Use multiple language groupings (geographic, linguistic family, resource level)
2. Include low-resource and endangered languages
3. Measure equity explicitly (gap analysis)
4. Consider speaker population size
5. Track improvement for underserved languages

### Deployment Considerations
1. Evaluate target languages thoroughly
2. Address language-specific gaps before deployment
3. Provide transparent language performance disclosure
4. Prioritize improvement in target languages
5. Support language community feedback

### Research Directions
1. Improve low-resource language support
2. Create benchmarks for underserved languages
3. Develop more efficient multilingual training
4. Study language transfer learning
5. Measure and optimize for language equity

---

## References

**Official Resources**:
- MMLU-ProX: https://github.com/YFCC-100M/MMLU-Pro
- Global-MMLU-Lite: Open datasets on Hugging Face
- MMTEB: https://github.com/embeddings-benchmark/mteb
- Alder Polyglot: https://github.com/polyglot-benchmarking/alder

**Key Papers**:
- MMTEB: Muennighoff et al., "Multilingual Text Embeddings Benchmark"
- Language Equity: Research on evaluating language equity in AI
