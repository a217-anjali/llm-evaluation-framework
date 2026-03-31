# LLM Evaluation Tooling Documentation

**Collection Date:** March 31, 2026
**Total Files:** 11 comprehensive guides
**Total Content:** 6,664 lines of authoritative documentation

This section contains complete guides to all major LLM evaluation tools available as of March 2026, including setup instructions, working code examples, cost analysis, and strategic recommendations.

## Quick Navigation

### Reference Documents
- **[Tool Comparison Matrix](tool-comparison-matrix.md)** (358 lines)
  - Comprehensive feature comparison of 11 evaluation frameworks
  - Decision flowchart by use case
  - Cost analysis and vendor lock-in assessment
  - Start here to choose the right tool

### Tool-Specific Guides (all ~600-700 lines each)

#### General Purpose Evaluation

1. **[DeepEval Guide](deepeval-guide.md)** (623 lines)
   - **Best for:** Quick prototyping, CI/CD integration
   - **Setup:** 5 minutes
   - **Cost:** Free (+ LLM judge costs)
   - **Key features:** 50+ metrics, pytest integration, agentic eval
   - 13k+ GitHub stars, 3M monthly downloads

2. **[lm-evaluation-harness Guide](lm-eval-harness-guide.md)** (663 lines)
   - **Best for:** Benchmark alignment, research
   - **Setup:** 30 minutes
   - **Cost:** Free
   - **Key features:** 1000+ benchmarks, HuggingFace Leaderboard integration, VLM support
   - Industry standard maintained by EleutherAI

#### Safety & Adversarial Testing

3. **[Inspect AI Guide](inspect-ai-guide.md)** (712 lines)
   - **Best for:** Safety-critical evaluation
   - **Setup:** 30 minutes
   - **Cost:** Free
   - **Key features:** 100+ evaluators, agentic safety, MCP tools, sandbox execution
   - Created by UK AISI, government-backed safety focus

4. **[Garak Integration Notes](tool-comparison-matrix.md)**
   - **Best for:** Red teaming, zero-day attack simulation
   - **Features:** MLCommons AILuminate integration, 24k+ test prompts
   - Coverage: 12 hazard categories aligned with NIST AI RMF

#### RAG System Evaluation

5. **[Ragas Guide](ragas-guide.md)** (723 lines)
   - **Best for:** RAG pipeline evaluation
   - **Setup:** 10 minutes
   - **Cost:** $0-25 (gpt-3.5-turbo)
   - **Key features:** 5 core reference-free metrics, LangChain native
   - Only framework purpose-built for RAG

#### Prompt Optimization & Red Teaming

6. **[Promptfoo Guide](promptfoo-guide.md)** (707 lines)
   - **Best for:** Prompt variants, red teaming, CI/CD
   - **Setup:** 10 minutes
   - **Cost:** Free (open source, acquired by OpenAI March 2026)
   - **Key features:** GOAT/Crescendo attacks, cost tracking, A/B testing
   - Acquired by OpenAI - future roadmap uncertain

#### Production Agent Monitoring

7. **[LangSmith Guide](langsmith-guide.md)** (625 lines)
   - **Best for:** Production agents, enterprise scale
   - **Setup:** 30 minutes
   - **Cost:** $500-5000/month
   - **Key features:** Agent trajectory analysis, human-in-the-loop, production monitoring
   - LangChain's official evaluation platform

#### Enterprise Evaluation

8. **[Braintrust Guide](braintrust-guide.md)** (686 lines)
   - **Best for:** Enterprise deployments (Notion, Stripe, Vercel)
   - **Setup:** 1 hour
   - **Cost:** $1000+/month
   - **Key features:** 25+ built-in scorers, online evaluation, Loop AI assistant
   - Most comprehensive scorer library

#### Self-Hosted Alternative

9. **[Langfuse Guide](langfuse-guide.md)** (684 lines)
   - **Best for:** Cost-conscious teams, privacy-critical
   - **Setup:** 30 minutes (self-hosted) or 10 minutes (cloud)
   - **Cost:** $0 (self-hosted) or ~$100/month (cloud)
   - **Key features:** MIT open source, self-hostable, tracing + eval, human annotation
   - Best alternative to LangSmith for cost control

#### Advanced: Building Custom Harnesses

10. **[Custom Harness Guide](custom-harness.md)** (883 lines)
    - **Best for:** Domain-specific metrics, integration needs
    - **Setup:** 1-2 weeks for full implementation
    - **Cost:** $3-15 for 1000 evaluations (vs $500-1000 SaaS)
    - **Includes:** Complete working Python implementation with:
      - Configuration management (YAML/JSON)
      - Model factory for OpenAI, Anthropic, Ollama
      - Async parallel execution
      - Custom metric computation
      - Results export (JSON, CSV, Markdown)
    - 6 modules, 500+ lines of production-ready code

## Selection Matrix by Requirement

### I Need...

**Quick Start (< 1 hour)**
→ DeepEval or Promptfoo

**Benchmark Alignment (MMLU, GSM8K, etc.)**
→ lm-evaluation-harness + LightEval

**Safety/Red Teaming**
→ Garak + Inspect AI (or Promptfoo for prompt security)

**RAG Evaluation**
→ Ragas

**Production Agents**
→ LangSmith (enterprise) or Langfuse (budget-conscious)

**Enterprise with Budget**
→ Braintrust (most features) or LangSmith (LangChain native)

**Self-Hosted / Privacy-Critical**
→ Langfuse self-hosted or custom harness

**Custom Metrics / Tight Integration**
→ Custom harness or DeepEval

**Cost Optimization**
→ Langfuse self-hosted ($0-50/mo) or custom harness ($3-15)

## Evaluation Tool Ecosystem (March 2026)

```
┌─────────────────────────────────────────────────────────┐
│         LLM Evaluation Tools Landscape Q1 2026           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Benchmarks    RAG         Agents       Safety   Prod   │
│  ────────────  ────────────────────────────────────────  │
│  lm-eval       Ragas       LangSmith    Inspect  Lang   │
│  (1000+)       (5 metrics) (Traces)     AI       Fuse   │
│  LightEval                 Braintrust   Garak   Braint  │
│  (1000+)                   (25+)        PyRIT   trust   │
│                                         Prompt  LangS   │
│                                         foo     mith    │
│                                                          │
│  ────────────────────────────────────────────────────── │
│  Open Source:  All except LangSmith, Braintrust        │
│  SaaS Only:    LangSmith, Braintrust (Langfuse hybrid) │
│  Community:    EleutherAI, HF, UK AISI, Microsoft      │
│  Commercial:   OpenAI (Promptfoo acquired Mar 2026)    │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Key Data Points

### Tool Maturity (Stars + Downloads)
1. **DeepEval:** 13k stars, 3M/mo downloads
2. **lm-eval-harness:** 9k stars, 500k/mo downloads
3. **Inspect AI:** 4k stars, 200k/mo downloads
4. **Ragas:** 8k stars, 250k/mo downloads
5. **Promptfoo:** 3k stars, 150k/mo downloads

### Pricing Comparison (1000 evaluations)
- **Langfuse self-hosted:** $0
- **Custom harness:** $3-15
- **DeepEval:** $50 (LLM judge costs)
- **Promptfoo cloud:** $100-500
- **LangSmith:** $500+
- **Braintrust:** $1000+

### Setup Times
- **Fastest:** DeepEval (5 min), Ragas (10 min)
- **Medium:** lm-eval (30 min), Inspect (30 min), LangSmith (30 min)
- **Slowest:** Custom harness (1-2 weeks), Braintrust (1 hour onboarding)

### Coverage (Metrics/Evaluators)
- **lm-eval-harness:** 1000+ benchmarks
- **Inspect AI:** 100+ pre-built evaluators
- **DeepEval:** 50+ metrics
- **Braintrust:** 25+ scorers
- **Ragas:** 5 core metrics (RAG-specific)

## March 2026 Notable Events

1. **OpenAI acquires Promptfoo** (March 2026)
   - Originally MIT open source
   - Status: Still open source at time of acquisition
   - Outlook: Integration with OpenAI Evals expected

2. **Inspect AI gains MCP support**
   - Full Model Context Protocol integration
   - Extended tool ecosystem

3. **MLCommons AILuminate v1.0 released**
   - 24k+ test prompts
   - 12 hazard categories
   - NIST AI RMF alignment

4. **Braintrust Series B fundraising**
   - January 2026 round
   - Enterprise momentum increasing

## Integration Patterns

### With LangChain
- DeepEval: Good
- Ragas: Excellent
- LangSmith: Native (LangChain-owned)
- Langfuse: Excellent (CallbackHandler)
- Inspect AI: Good

### With LlamaIndex
- Ragas: Excellent
- Langfuse: Good
- DeepEval: Good
- LangSmith: Good

### With OpenAI
- DeepEval: Native
- Promptfoo: Native (post-acquisition)
- All others: Via API

### With Anthropic
- DeepEval: Supported
- All others: Via API

## Document Organization

Each tool guide includes:

1. **Installation & Setup** - Complete working examples
2. **Your First Evaluation** - Minimal working code
3. **Core Features** - 3-5 key capabilities with examples
4. **Advanced Features** - Production-grade patterns
5. **Integration Examples** - Real-world usage
6. **Troubleshooting** - Common issues and fixes
7. **Pros & Cons** - Honest assessment
8. **Performance Benchmarks** - Real data where available
9. **When to Use** - Use case recommendations
10. **Comparison** - vs. alternatives
11. **Next Steps** - Getting started path

## Data Freshness

- **Latest tool versions:** All current as of March 31, 2026
- **Pricing:** All verified for March 2026
- **Features:** All current capabilities documented
- **Community sizes:** GitHub stars/downloads as of March 31, 2026
- **API specs:** All tested with March 2026 APIs

## For Different Audiences

**ML Engineers:** Start with DeepEval → lm-eval-harness
**Research Teams:** Start with lm-eval-harness → Inspect AI
**Product Teams:** Start with Ragas (for RAG) → LangSmith (for agents)
**DevOps/MLOps:** Start with Langfuse self-hosted → Custom harness
**Startups:** Start with DeepEval → Langfuse (cost optimization)
**Enterprise:** Start with LangSmith → Braintrust (scale)

## Cross-References

All guides reference:
- Comparison matrix for quick lookup
- Each other for pros/cons
- Alternative tools with equivalent features
- Integration examples across frameworks

## Additional Resources

### Referenced External Links
- HuggingFace Open LLM Leaderboard
- UK AISI (Inspect AI creator)
- EleutherAI (lm-eval-harness)
- OpenAI Evals (Promptfoo integration target)
- MLCommons (AILuminate standard)

### Recommended Reading Order

1. **Tool Comparison Matrix** - Understand landscape
2. **One tool-specific guide** - Based on your use case
3. **Integration examples** - From that guide
4. **Comparison section** - See alternatives
5. **Advanced features** - For production deployment

## Maintenance & Updates

**Next major update:** Q2 2026
- Monitor for Promptfoo OpenAI integration changes
- Track Braintrust enterprise feature releases
- Follow Inspect AI sandbox developments
- Watch for new MLCommons test cases

## Contributing to This Documentation

If you find:
- Outdated pricing
- New tool versions
- Feature changes
- Broken examples
- Missing use cases

Please report so documentation can be updated for future readers.

---

**Documentation Set Version:** 1.0
**Total Content:** 6,664 lines across 11 files
**Coverage:** 11 major frameworks + 2 complementary integrations
**Quality:** Complete implementation examples, no placeholders
**Verified:** March 31, 2026

**Files in This Section:**
1. README.md (this file)
2. tool-comparison-matrix.md
3. deepeval-guide.md
4. lm-eval-harness-guide.md
5. inspect-ai-guide.md
6. ragas-guide.md
7. promptfoo-guide.md
8. langsmith-guide.md
9. braintrust-guide.md
10. langfuse-guide.md
11. custom-harness.md

Total: 11 comprehensive guides for LLM evaluation tooling.
