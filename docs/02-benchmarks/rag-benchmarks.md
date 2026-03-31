# Retrieval-Augmented Generation (RAG) Benchmarks

## Overview

RAG benchmarks evaluate LLMs in retrieval-augmented settings where models must retrieve relevant information from external knowledge sources before generating responses. These benchmarks test information retrieval quality, ranking, and the model's ability to generate accurate responses based on retrieved documents.

---

## RAGBench

### Description
RAGBench is a comprehensive retrieval-augmented generation benchmark containing 500+ diverse tasks testing end-to-end RAG pipeline performance including retrieval, ranking, and generation quality. It evaluates both retrieval effectiveness and answer generation based on retrieved documents.

### Benchmark Design
- **Task count**: 500+ RAG evaluation instances
- **Source domains**:
  - General knowledge (Wikipedia, encyclopedic)
  - News and current events
  - Scientific documents (papers, technical writing)
  - Legal documents (contracts, case law)
  - Medical literature (research, guidelines)
  - Technical documentation (code, specifications)
- **Task types**:
  - Retrieval evaluation (ranking quality)
  - Answer generation (using retrieved documents)
  - Multi-hop reasoning (across documents)
  - Citation accuracy (proper attribution)
  - Factuality assessment (answer correctness)

### Pipeline Evaluation
| Stage | Component | Metrics |
|-------|-----------|---------|
| Retrieval | Document ranking | Recall@K, NDCG |
| Ranking | Relevance ordering | MRR, precision |
| Generation | Answer quality | ROUGE, BERTScore |
| Citation | Attribution correctness | Citation precision/recall |
| Factuality | Answer accuracy | Exact match, semantic |

### Scoring & Methodology
- **Format**: Query + knowledge base → retrieve + generate answer
- **Evaluation**: Multi-stage assessment
- **Metrics**:
  - Retrieval recall (did system find relevant docs?)
  - Answer accuracy (is generated answer correct?)
  - Citation accuracy (are sources properly cited?)
  - Hallucination detection (no information fabrication)
- **Aggregation**: Combined RAG pipeline score

### Current Performance (March 2026)
| Model | Retrieval | Ranking | Generation | Citation | Overall |
|-------|-----------|---------|-----------|----------|---------|
| Claude Opus 4.5 | 89% | 87% | 84% | 87% | ~84% |
| GPT-5 | 87% | 86% | 83% | 85% | ~83% |
| Gemini 3.1 Pro | 85% | 84% | 81% | 82% | ~81% |

### Performance by Domain
| Domain | Frontier Score | Challenge |
|--------|---|---|
| General knowledge | 88%+ | Well-handled |
| News | 86%+ | Good (requires currency) |
| Science | 82%+ | Moderate (technical terms) |
| Legal | 79%+ | Hard (precision critical) |
| Medical | 81%+ | Hard (accuracy critical) |

### Error Patterns
- **Retrieval gaps** (15%): Missing relevant documents
- **Ranking errors** (12%): Relevant but not top-ranked
- **Generation errors** (10%): Incorrect despite retrieval
- **Citation errors** (8%): Missed or incorrect attribution
- **Hallucination** (5%): Generated unsupported information

### Strengths
- Comprehensive end-to-end RAG evaluation
- Multi-domain coverage reflecting real use
- Addresses critical citation and factuality
- Stage-wise metrics enable diagnostic analysis
- Large test set (500+ items)

### Limitations
- Real-world knowledge bases not used (curated subset)
- Ranking metrics may not match generation quality
- Citation formats may vary
- Hallucination detection challenging
- Domain-specific terminology interpretation

### Recommendations for Use
- Essential for RAG system deployment
- Primary metric for retrieval-augmented performance
- Use domain breakdown for application-specific assessment
- Important for fact-critical domains (legal, medical)
- Track citation and hallucination rates carefully

---

## CRAG (Comprehensive RAG Benchmark with Adversarial Documents)

### Description
CRAG is an adversarial RAG benchmark specifically designed to stress-test retrieval systems with challenging, misleading, and adversarial documents designed to fail standard retrieval approaches. It measures robustness to retrieval difficulties.

### Benchmark Design
- **Core characteristic**: Includes adversarial documents
- **Task count**: 300+ evaluation instances
- **Adversarial document types**:
  - Semantically similar but incorrect documents
  - Partial information (incomplete truths)
  - Contradictory information (conflicting truths)
  - Red herring documents (seemingly relevant but wrong)
  - Documents with subtle errors
  - Low-quality or noisy documents
- **Baseline documents**: Also includes standard clean documents
- **Difficulty levels**: Easy (clean) to hard (heavily adversarial)

### Adversarial Scenarios
| Scenario | Challenge | Frequency |
|----------|-----------|-----------|
| Semantic similarity | Misleading relevance | 20% |
| Partial information | Incomplete answer | 25% |
| Contradictory | Conflicting sources | 15% |
| Red herring | Surface relevance only | 20% |
| Low quality | Noisy/degraded text | 15% |
| Mixed | Multiple adversarial types | 5% |

### Scoring & Methodology
- **Format**: Query with adversarial knowledge base
- **Evaluation**: Retrieval quality under adversarial conditions
- **Metrics**:
  - Recall under adversarial setting
  - Ranking robustness
  - Distinction from misleading documents
  - Answer quality despite adversarial retrieval
- **Difficulty tiers**: Separate scores for clean vs. adversarial

### Current Performance (March 2026)
| Model | Clean Docs | Adversarial | Mixed | Overall |
|-------|-----------|-------------|-------|---------|
| Frontier models | 87%+ | 78%+ | 73%+ | ~78%+ |
| Claude Opus 4.5 | 89% | 76% | 71% | ~76% |
| GPT-5 | 88% | 77% | 72% | ~77%+ |

### Difficulty Performance
| Condition | Frontier Score | Challenge |
|-----------|---|---|
| Clean documents | 88%+ | Easy |
| 25% adversarial | 82%+ | Moderate |
| 50% adversarial | 75%+ | Hard |
| 75% adversarial | 65%+ | Very hard |

### Robustness Gaps
- **Performance drop** (clean to adversarial): 10-12% average
- **Ranking degradation**: Adversarial docs often ranked high
- **Semantic confusion**: Misleading documents frequently retrieved
- **Error compounding**: Retrieval errors propagate to generation

### Strengths
- Tests realistic adversarial conditions
- Identifies robustness gaps in retrieval
- Adversarial documents mimic real-world challenges
- Reveals ranking algorithm limitations
- Important for production resilience

### Limitations
- Smaller than comprehensive RAG benchmarks (300 items)
- Adversarial document design somewhat artificial
- Difficulty to scale adversarial generation
- Some adversarial types more natural than others
- Limited to retrieval-only evaluation

### Recommendations for Use
- Important for robust RAG system evaluation
- Use to identify adversarial vulnerability
- Critical for high-stakes applications
- Test retrieval robustness specifically
- Pair with RAGBench for comprehensive assessment

---

## LegalBench-RAG

### Description
LegalBench-RAG is a domain-specific RAG benchmark for legal document retrieval and reasoning. It tests retrieval and generation capabilities on legal documents with domain-specific challenges including complex terminology, inter-document references, and high accuracy requirements.

### Benchmark Design
- **Domain**: Legal documents and queries
- **Document types**:
  - Case law and court decisions
  - Legal statutes and regulations
  - Contracts and agreements
  - Legal briefs and memoranda
  - Legislative documents
- **Query types**:
  - Case law retrieval (find relevant precedents)
  - Statute interpretation (find applicable laws)
  - Contract analysis (locate specific clauses)
  - Legal reasoning (multi-step legal analysis)
  - Compliance checking (identify relevant requirements)
- **Scale**: 200+ legal RAG instances

### Legal-Specific Challenges
| Challenge | Complexity | Importance |
|-----------|-----------|-----------|
| Terminology precision | High | Critical for accuracy |
| Cross-reference tracking | High | Interconnected law |
| Precedent understanding | High | Case law foundation |
| Regulatory updates | High | Laws constantly change |
| Inter-document reasoning | Very High | Multi-document analysis |

### Scoring & Methodology
- **Format**: Legal query + document database
- **Evaluation**: Expert legal review + automated metrics
- **Metrics**:
  - Relevant case law retrieval
  - Statute identification accuracy
  - Contract clause extraction
  - Legal reasoning quality
  - Precedent applicability assessment
- **Legal validation**: Lawyer review of generated answers

### Current Performance (March 2026)
| Model | Retrieval | Reasoning | Citation | Overall |
|-------|-----------|-----------|----------|---------|
| GPT-5 | 91%+ | 88%+ | 90%+ | ~91%+ |
| Claude Opus 4.5 | 88% | 85% | 87% | ~87% |
| Frontier models | 85-91% | 82-88% | 84-90% | 85-91% |

### Performance by Legal Task
| Task Type | Challenge | Frontier Score |
|-----------|-----------|---|
| Case law retrieval | Medium | 92%+ |
| Statute finding | Medium | 90%+ |
| Contract analysis | Hard | 85%+ |
| Legal reasoning | Hard | 82%+ |
| Regulatory compliance | Very Hard | 78%+ |

### Accuracy Requirements
- **Traditional RAG**: ~80% acceptable for general use
- **Legal requirement**: 95%+ accuracy for high-stakes decisions
- **Liability risk**: Incorrect legal information costly
- **Professional standard**: Must meet legal professional standards

### Strengths
- High-stakes domain requiring accuracy
- Expert legal evaluation
- Captures domain-specific complexity
- Tests genuine legal reasoning
- Important for legal AI applications

### Limitations
- Smaller test set (200 items)
- Expertise requirement limits accessibility
- Legal terminology constantly evolving
- Jurisdiction-specific variations
- Limited to English common law (for now)

### Recommendations for Use
- Essential for legal AI system evaluation
- Primary metric for legal document understanding
- Use expert review for validation
- Important for compliance and liability
- Track accuracy carefully for high-stakes use

---

## T2-RAGBench (Table-to-Text RAG Benchmark)

### Description
T2-RAGBench is a specialized RAG benchmark for table-structured data retrieval and text generation from tables. It evaluates models' ability to retrieve relevant tabular data and generate accurate text descriptions and answers based on table information.

### Benchmark Design
- **Data type**: Structured tables (spreadsheets, databases)
- **Table sources**:
  - Structured data (tabular databases)
  - Financial reports and statements
  - Scientific data tables
  - Statistical summaries
  - Multi-table databases (joins required)
- **Query types**:
  - Fact retrieval from tables
  - Table search (find relevant table)
  - Numerical aggregation (sums, averages)
  - Multi-table reasoning (joins)
  - Text generation from tables
- **Task scale**: 400+ table-based RAG instances

### Task Complexity Levels
| Type | Complexity | Frequency |
|------|-----------|-----------|
| Single-cell retrieval | Low | 15% |
| Row/column search | Low-Medium | 25% |
| Aggregation | Medium | 25% |
| Multi-table | Medium-High | 20% |
| Complex reasoning | High | 15% |

### Scoring & Methodology
- **Format**: Query + table dataset → retrieve + generate answer
- **Evaluation**: Multi-stage assessment
- **Metrics**:
  - Table retrieval accuracy
  - Cell/row selection accuracy
  - Numerical accuracy (sums, calculations)
  - Natural language generation quality
  - Reasoning correctness
- **Verification**: Both exact match and semantic matching

### Current Performance (March 2026)
| Model | Table Retrieval | Cell Accuracy | Aggregation | Generation | Overall |
|-------|---|---|---|---|---|
| Gemini 3.1 Pro | 86% | 89% | 87% | 84% | ~86% |
| Claude Opus 4.5 | 84% | 87% | 85% | 82% | ~84% |
| GPT-5 | 85% | 88% | 86% | 83% | ~85%+ |

### Performance by Task Type
| Type | Frontier Score | Challenge |
|-----|---|---|
| Single-cell | 96%+ | Very easy |
| Row/column | 91%+ | Easy |
| Aggregation | 85%+ | Medium |
| Multi-table | 78%+ | Hard |
| Complex reasoning | 70%+ | Very hard |

### Error Modes
- **Table selection** (12%): Wrong table retrieved
- **Cell location** (10%): Wrong cells selected
- **Numerical error** (8%): Calculation mistake
- **Semantic misunderstanding** (8%): Wrong interpretation
- **Generation quality** (7%): Poor text description

### Strengths
- Addresses specific structured data challenge
- Important for business intelligence applications
- Clear numerical evaluation criteria
- Diverse task complexity
- Practical real-world relevance

### Limitations
- Specialized to tabular data
- Smaller test set (400 items)
- Table complexity varies significantly
- Natural language generation quality subjective
- Limited to English (for now)

### Recommendations for Use
- Essential for business intelligence and analytics
- Primary metric for table-based RAG systems
- Important for data-driven applications
- Track numerical accuracy carefully
- Use for evaluating structured data understanding

---

## RAG Benchmark Comparison

| Benchmark | Focus | Scale | Challenge | Best For |
|-----------|-------|-------|-----------|----------|
| RAGBench | Comprehensive | 500+ | Multi-stage | General RAG |
| CRAG | Adversarial | 300+ | Robustness | Adversarial resilience |
| LegalBench-RAG | Legal domain | 200+ | High precision | Legal applications |
| T2-RAGBench | Structured data | 400+ | Numerical | Analytics/BI |

---

## RAG Evaluation Framework

### End-to-End Pipeline Assessment
```
Query Input
    ↓
Retrieval Stage → Evaluate recall, ranking, relevance
    ↓
Ranking Stage → Evaluate relevance ordering, diversity
    ↓
Generation Stage → Evaluate answer quality, coherence
    ↓
Post-Processing → Evaluate citation, factuality, hallucination
```

### Multi-Stage Metrics
1. **Retrieval metrics**: Recall@K, NDCG, MRR
2. **Answer quality**: ROUGE, BERTScore, semantic matching
3. **Citation accuracy**: Citation precision/recall
4. **Factuality**: Hallucination detection, fact verification
5. **Overall**: Combined pipeline performance

---

## Integrated RAG Evaluation Strategy

### For General RAG Systems
1. RAGBench (primary comprehensive evaluation)
2. CRAG (robustness testing)
3. Custom domain-specific RAG benchmarks

### For Domain-Specific RAG
1. **Legal systems**: LegalBench-RAG + RAGBench
2. **Analytics/BI**: T2-RAGBench + RAGBench
3. **Medical**: Medical-specific RAG benchmarks
4. **Scientific**: Scientific domain RAG benchmarks

### For Production Deployment
1. Domain-appropriate benchmark (primary)
2. CRAG for adversarial resilience
3. Custom evaluation on deployment data
4. Continuous monitoring of hallucination
5. Citation accuracy verification

---

## RAG Performance Trends (March 2026)

### Capability Development
- **Retrieval**: 85-89% frontier performance (good)
- **Generation**: 81-84% accuracy (good, with room for improvement)
- **Citation**: 82-87% accuracy (critical gap for trustworthiness)
- **Hallucination**: 5-10% rate (significant for production)

### Domain-Specific Insights
- **General knowledge**: Well-supported (~84%+)
- **Technical/specialized**: More challenging (78-82%)
- **Legal/medical**: Very high accuracy needed (>95%)
- **Current gap**: Frontier models at 85-91%, requirements 95%+

### Critical Challenges
- **Hallucination rates**: 5-10% too high for critical domains
- **Citation accuracy**: Frequently missing or incorrect
- **Adversarial robustness**: 10-12% performance drop in adversarial setting
- **Multi-document reasoning**: Difficult for complex cases

### Emerging Best Practices
1. Always use citation evaluation for production
2. Implement hallucination detection
3. Test with adversarial documents
4. Domain-specific human evaluation required
5. Continuous monitoring for quality degradation

---

## References

**Official Resources**:
- RAGBench: https://github.com/aobaseki/ragbench
- CRAG: https://github.com/felicitywang/CRAG
- LegalBench: https://github.com/HazyResearch/legalbench
- T2-RAGBench: Specialized research benchmark documentation

**Key Papers**:
- RAG systems: Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
- Hallucination in RAG: Research on factuality in retrieval-augmented systems
- Adversarial RAG: Studies on robustness to challenging retrieval scenarios
