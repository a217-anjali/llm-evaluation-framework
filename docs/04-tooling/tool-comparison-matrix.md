# LLM Evaluation Tools: Comprehensive Comparison Matrix

**Last Updated:** March 2026

This document provides an exhaustive feature comparison of the major LLM evaluation tools available today. Use this to select the right tool for your specific evaluation needs.

## Feature Comparison Table

| Feature | DeepEval | lm-eval-harness | Inspect AI | LightEval | Ragas | Promptfoo | LangSmith | Braintrust | Langfuse | PyRIT | Garak |
|---------|----------|------------------|-----------|-----------|-------|-----------|-----------|-----------|---------|-------|-------|
| **License** | Apache 2.0 | MIT | MIT | Apache 2.0 | Apache 2.0 | MIT | Proprietary | Proprietary | MIT | MIT | Apache 2.0 |
| **Pricing** | Open Source | Open Source | Open Source | Open Source | Open Source | Open Source | SaaS | SaaS | Open Source | Open Source | Open Source |
| **Maintains** | DeepEval Inc. | EleutherAI | UK AISI | HuggingFace | HuggingFace | OpenAI (Mar 2026) | LangChain | Braintrust Inc. | Langfuse GmbH | Microsoft | Open Source |
| **Current Version** | v3.2.6+ | v0.4.3+ | v0.3.199+ | Latest | v1.2+ | v0.9.30+ | - | - | v2.1.0+ | v0.3.8+ | v0.5.2+ |
| **PyPI Monthly Downloads** | 3M+ | 500k+ | 200k+ | 100k+ | 250k+ | 150k+ | N/A | N/A | 50k+ | 50k+ | 30k+ |
| **GitHub Stars** | 13k+ | 9k+ | 4k+ | 1k+ | 8k+ | 3k+ | N/A | N/A | 3k+ | 1.5k+ | 2.5k+ |

## Evaluation Capabilities

### Benchmark & Task Coverage

| Feature | Coverage | Notes |
|---------|----------|-------|
| **DeepEval** | 50+ pre-built metrics | Answerability, Ragas metrics, custom code evaluation |
| **lm-eval-harness** | 1000+ tasks via LightEval | MMLU, HellaSwag, TruthfulQA, GSM8K, custom tasks |
| **Inspect AI** | 100+ pre-built evaluators | Safety-focused (jailbreaks, refusals), agentic evals |
| **LightEval** | 1000+ tasks | Wraps lm-eval-harness, adds HuggingFace ecosystem |
| **Ragas** | 5 core metrics | Context precision, relevance, faithfulness, F1 scores |
| **Promptfoo** | 50+ LLM comparisons | Red teaming, prompt variants, cost tracking |
| **LangSmith** | Custom metrics | Focus on agent trajectories, production monitoring |
| **Braintrust** | 25+ scorers | AutoML-powered, online evaluation, A/B testing |
| **Langfuse** | LLM-as-judge | Custom via prompt templates, human annotation |
| **PyRIT** | Red teaming only | MITRE Framework: attack generation, defense testing |
| **Garak** | 1000+ tests | MLCommons AILuminate: 12 hazard categories |

### Evaluation Types

| Type | DeepEval | Inspect AI | Ragas | Promptfoo | LangSmith | Braintrust | Langfuse | PyRIT | Garak |
|------|----------|-----------|-------|-----------|-----------|-----------|---------|-------|-------|
| **Reference-based** | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| **Reference-free** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| **Agentic** | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| **Safety/Red Team** | ✓ | ✓ (primary) | ✗ | ✓ | ✓ | ✓ | ✗ | ✓ (primary) | ✓ (primary) |
| **RAG-specific** | ✗ | ✗ | ✓ (primary) | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| **Agent Trajectory** | ✗ | ✓ | ✗ | ✗ | ✓ (primary) | ✓ | ✗ | ✗ | ✗ |
| **Hallucination** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| **Bias & Fairness** | ✗ | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ | ✓ | ✓ |
| **Multimodal** | ✗ | ✓ (VLM) | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |

## Integration & DevOps

| Feature | DeepEval | lm-eval-harness | Inspect AI | Ragas | Promptfoo | LangSmith | Langfuse |
|---------|----------|------------------|-----------|-------|-----------|-----------|---------|
| **pytest Integration** | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✗ |
| **CI/CD Pipeline** | ✓ | ✓ | ✓ | ✓ | ✓ (CLI) | ✓ | ✓ |
| **Docker Support** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **API Server** | ✓ | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ |
| **Self-hostable** | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| **Cloud-hosted** | ✗ | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ |
| **HuggingFace Hub** | ✓ | ✓ (primary) | ✓ | ✓ | ✓ | ✓ | ✓ |

## Framework & Ecosystem Integrations

| Framework | DeepEval | Inspect AI | Ragas | Promptfoo | LangSmith | Langfuse |
|-----------|----------|-----------|-------|-----------|-----------|---------|
| **LangChain** | ✓ | ✓ | ✓ (primary) | ✓ | ✓ (primary) | ✓ (primary) |
| **LlamaIndex** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **OpenAI** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Anthropic** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Ollama** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **vLLM** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## Advanced Features Matrix

| Feature | Implementation | Notes |
|---------|-----------------|-------|
| **MCP Tool Support** | Inspect AI | Model Context Protocol for extended tool chains |
| **Agentic Evaluation** | DeepEval, Inspect AI, LangSmith, Braintrust | Full trajectories with action chains |
| **Human-in-the-loop** | LangSmith, Braintrust, Langfuse | Annotation queues, disagreement resolution |
| **Drift Detection** | Arize Phoenix, Langfuse | Track eval metric changes over time |
| **Cost Tracking** | Promptfoo, LangSmith, Braintrust, Langfuse | Per-request token/dollar accounting |
| **Version Control** | Promptfoo, LangSmith, Braintrust | Eval config versioning, rollback |
| **A/B Testing** | Promptfoo, Braintrust | Statistical significance testing |
| **Red Teaming** | Promptfoo, Inspect AI, PyRIT, Garak | Adversarial attack generation |
| **Jailbreak Testing** | Inspect AI, Garak | Specific attack patterns (GOAT, Crescendo) |
| **Prompt Injection** | Promptfoo, PyRIT | SQL injection, code injection patterns |
| **Automated Reporting** | All SaaS tools | Dashboards, trend analysis, alerts |

## Specialized Tool Breakdown

### Safety & Red Teaming Focus

**MLCommons AILuminate Integration:**
- v1.0 released 2026, 12 hazard categories
- 24,000+ test prompts
- Aligned with NIST AI RMF
- Used by: Inspect AI, Garak, Promptfoo (partial)

**Garak Features:**
- Zero-day attack simulation
- Mutate prompts based on attack patterns
- Hazard category: misleading info, offensive language, privacy risks
- CLI-first design, minimal dependencies

**PyRIT (Microsoft):**
- MITRE ATT&CK-aligned framework
- Attack orchestration: endpoint attacks, gradient-based, jailbreaks
- Modular scorer system
- Defense mechanism testing

### RAG-Specific Tools

**Ragas:**
- Context Precision: fraction of grounded context
- Context Recall: coverage of context needed for answer
- Faithfulness: answer grounded in context
- Answer Relevance: LLM-judged relevance
- F1 Score: traditional metrics

**Arize Phoenix:**
- Drift detection for embedding drift
- RAG-specific traces: retrieval ranking, latency
- Open source, self-hostable
- Integration with LlamaIndex

### Production Monitoring

**LangSmith:**
- Agent trajectory analysis: action sequences, error recovery
- Production feedback loops: user ratings, human corrections
- Dataset management: test set versioning
- Performance alerts: latency, error rate changes

**Braintrust:**
- Online evaluation: real-time score calculation
- 25+ pre-built scorers: exact match, fuzzy match, BLEU, semantic similarity
- Loop AI: voice-activated evaluation assistant
- Used by Notion, Stripe, Vercel (as of March 2026)

**Langfuse:**
- Self-hosted backend: costs ~$0.10 per 1M tokens traced
- Human annotation: integrated labeling interface
- Per-session cost tracking
- Privacy-first: no data sent to external APIs

## Selection Guide by Use Case

### For Research & Benchmarking
**Primary:** lm-eval-harness + LightEval
- Largest task coverage (1000+ tasks)
- Industry-standard benchmarks
- HuggingFace Leaderboard integration
- Best for: MMLU, TruthfulQA, GSM8K evaluations

**Secondary:** DeepEval
- Custom metrics via code evaluation
- Good for unique research metrics

### For CI/CD & Pre-deployment
**Primary:** DeepEval + pytest
- Native pytest integration
- Automated assertion-style evaluation
- Good for: gate-keeping bad models in production

**Secondary:** Promptfoo
- Prompt-first CI/CD
- Variant comparison
- Cost tracking

### For RAG Systems
**Primary:** Ragas
- Purpose-built for RAG metrics
- Reference-free evaluation
- LangChain native

**Secondary:** Langfuse + custom metrics
- Production monitoring
- Human feedback loop

### For Safety & Adversarial Testing
**Primary:** Garak + MLCommons AILuminate
- 24K+ test cases
- MLCommons alignment
- Best coverage of attack types

**Secondary:** Inspect AI
- Integration with UK AISI
- Agentic safety evaluation

### For Production Agents
**Primary:** LangSmith
- Agent trajectory analysis
- Production monitoring
- Human-in-the-loop correction

**Secondary:** Braintrust
- Online evaluation at inference time
- Enterprise scorers

### For Small Teams / Startups
**Primary:** DeepEval (open source) or Promptfoo (open source)
- Zero ongoing costs
- Simple setup
- Quick iteration

**Secondary:** Langfuse (self-hosted)
- Low operational costs
- Full observability

### For Enterprise Deployments
**Primary:** LangSmith or Braintrust
- Professional support
- Scalable infrastructure
- Multiple team management

**Secondary:** Langfuse (self-hosted variant)
- Cost control
- Data residency requirements

## Licensing & Acquisition Context (March 2026)

**Major Event:** OpenAI acquired Promptfoo (March 2026)
- Promptfoo remains MIT licensed (at time of writing)
- Roadmap: integration with OpenAI Evals
- Future: possible pricing changes expected
- Community forks: actively maintained alternatives emerging

**Stable Open Source:**
- DeepEval: DeepEval Inc. (well-funded)
- lm-eval-harness: EleutherAI (nonprofit research)
- Inspect AI: UK AISI (government-backed)
- Ragas: HuggingFace (stable, continuing investment)
- Langfuse: Venture-backed, MIT license
- PyRIT: Microsoft (internal use + open)
- Garak: Open source community

**SaaS Stability:**
- LangSmith: LangChain (Series A+)
- Braintrust: Raising Series B (Jan 2026)

## Cost Analysis (Estimated Annual)

### Open Source (Self-hosted)
| Tool | Hosting | Monitoring | Total |
|------|---------|-----------|-------|
| DeepEval | $0 | $0-50 | $0-50 |
| lm-eval-harness | $0-500 | $0 | $0-500 |
| Inspect AI | $0-1000 | $0 | $0-1000 |
| Langfuse (self) | $100-500 | $50 | $150-550 |

### Cloud-based SaaS
| Tool | Monthly Usage | Notes |
|------|--------------|-------|
| Promptfoo Cloud | $100-500 | Pay-as-you-go |
| LangSmith | $500-5000 | Usage-based, volume discounts |
| Braintrust | $1000+ | Custom pricing |

### Cloud GPU Costs (for serving)
- A100 inference: $1-2/hour
- Llama 2 70B: ~$0.50-1.50/1M tokens
- Evaluation at scale: typically 10-20% of LLM costs

## Decision Flowchart

```
START: Choosing an LLM Evaluation Tool
│
├─ Are you evaluating RAG systems?
│  ├─ YES → Ragas (primary) + Langfuse (monitoring)
│  └─ NO → Continue
│
├─ Is safety/red teaming critical?
│  ├─ YES → Garak + MLCommons AILuminate
│  ├─ PARTIAL → Inspect AI (agentic safety)
│  └─ NO → Continue
│
├─ Do you need production monitoring?
│  ├─ YES, enterprise → LangSmith or Braintrust
│  ├─ YES, cost-sensitive → Langfuse (self-hosted)
│  └─ NO → Continue
│
├─ Are you evaluating agents?
│  ├─ YES → LangSmith (trajectory analysis)
│  └─ NO → Continue
│
├─ Do you need benchmark/leaderboard alignment?
│  ├─ YES → lm-eval-harness + LightEval
│  └─ NO → Continue
│
├─ Do you want CI/CD integration?
│  ├─ YES → DeepEval (pytest) or Promptfoo
│  └─ NO → Continue
│
└─ Default recommendation:
   └─ DeepEval (open source, comprehensive, well-maintained)
```

## Quick Start by Tool

### Minimal Setup Time (< 1 hour)
1. DeepEval: `pip install deepeval` → write 5 lines → run
2. Promptfoo: `npm install promptfoo` → YAML config → CLI

### Moderate Setup (1-4 hours)
1. Ragas: Install + integrate with LangChain pipeline
2. Inspect AI: Download + run examples + write custom eval
3. Langfuse: Docker setup + integration + dashboard

### Full Setup (1-2 days)
1. LangSmith: Workspace setup + team onboarding + custom metrics
2. Braintrust: Enterprise onboarding + integration + training
3. lm-eval-harness: Custom task development + benchmark running

## Recommendations Summary

| Use Case | Tool | Why |
|----------|------|-----|
| **Getting started** | DeepEval | Easiest, most comprehensive |
| **Research & benchmarks** | lm-eval-harness | 1000+ tasks, leaderboard-aligned |
| **RAG evaluation** | Ragas | Purpose-built, reference-free |
| **Safety testing** | Garak | 24K+ tests, MLCommons standard |
| **Production agents** | LangSmith | Best trajectory analysis |
| **Cost control** | Langfuse | Cheapest SaaS alternative, self-host option |
| **Enterprise** | Braintrust | Highest maturity, 25+ scorers |
| **Prompt-centric** | Promptfoo | Best prompt variants testing |
| **Budget conscious** | DeepEval (open) | Same features as SaaS, no costs |

## Tool Maturity & Roadmap (Q2 2026 Outlook)

**Mature & Stable:**
- DeepEval: v4.0 planned (multimodal expansion)
- lm-eval-harness: Stable maintenance mode
- Ragas: v1.5 (custom metric builders)
- LangSmith: Enterprise features expanding

**Growth Phase:**
- Inspect AI: Sandbox expansion, MCP standardization
- Langfuse: Analytics features, billing integration
- Braintrust: Enterprise scoring marketplace

**Uncertain Future:**
- Promptfoo: Post-acquisition roadmap unclear (OpenAI-aligned)
- PyRIT: Microsoft commitment level TBD
- Garak: Community-dependent, no corporate backing

## Next Steps

1. **Narrow by use case:** Identify your primary evaluation need from the section above
2. **Read the dedicated guide:** Jump to the tool-specific guide (see other docs in this section)
3. **Prototype:** Most tools have free tiers or self-hosted open source versions
4. **Integrate:** Once confident, integrate into your CI/CD or monitoring pipeline
5. **Iterate:** Evaluation is continuous; adjust metrics and tools as needed

---

**Document Version:** 1.0
**Last Verified:** March 31, 2026
**Tools Covered:** 11 major frameworks + 2 complementary integrations
