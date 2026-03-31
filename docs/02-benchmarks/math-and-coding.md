# Mathematical Reasoning & Code Generation Benchmarks

## Overview

This document covers specialized benchmarks for mathematical reasoning and software engineering capabilities. These evaluations test distinct aspects: mathematical reasoning benchmarks measure problem-solving across increasing difficulty levels, while code benchmarks assess everything from simple function generation to real-world software engineering tasks.

## Mathematical Reasoning Benchmarks

### GSM8K (Grade School Math 8K)

#### Description
GSM8K contains 8,792 grade school level math word problems designed to test basic arithmetic reasoning. It represents the foundational mathematical capability expected from language models, focusing on understanding problem statements and applying mathematical operations.

#### Problem Characteristics
- **Grade level**: Elementary to middle school (grades K-8)
- **Operations**: Basic arithmetic, fractions, percentages, simple algebra
- **Problem type**: Word problems requiring one or multiple reasoning steps
- **Solution approach**: Straightforward arithmetic without advanced techniques
- **Average steps to solution**: 2-5 computational steps

#### Scoring & Methodology
- **Format**: Free-form numerical answer (accepts multiple formats)
- **Evaluation**: Exact match on final numeric answer (with tolerance)
- **Train/Test split**: 7,473 train / 1,319 test examples
- **Metric**: Accuracy of final numerical answer
- **Chain-of-thought evaluation**: Allows reasoning trace verification

#### Current Performance (March 2026)
| Model | Score | Status |
|-------|-------|--------|
| GPT-5 | ~96%+ | Saturated |
| Claude Opus 4.5 | ~94% | Saturated |
| Gemini 3.1 Pro | ~95.2% | Saturated |
| Frontier models average | ~94-96% | Benchmark saturated |

#### Assessment
GSM8K is effectively **saturated**. Nearly all frontier models exceed 94% accuracy, with most achieving 95%+. The benchmark no longer provides meaningful discrimination between advanced models.

#### Strengths
- Clear, well-defined problems with unambiguous solutions
- Tests genuine mathematical understanding at accessible level
- Large test set enables statistically significant comparison
- Wide adoption facilitates cross-model comparison
- Chain-of-thought reasoning can be analyzed

#### Limitations
- Saturated benchmark (limited discrimination value)
- Only elementary mathematics (not representative of advanced math)
- Word problem format doesn't test symbolic manipulation
- Fixed answer format may not reflect real-world math application
- Limited failure analysis value for advanced models

#### Recommendations for Use
- Use for baseline verification rather than primary evaluation
- Useful for confirming basic mathematical reasoning capability
- Not recommended as differentiator between frontier models
- Consider skipping in frontier model evaluations
- Valuable for non-frontier model assessment

---

### MATH (Hendrycks MATH Dataset)

#### Description
MATH is a comprehensive benchmark of 12,500 challenging mathematics competition problems spanning algebra, precalculus, geometry, number theory, and combinatorics. It tests genuine mathematical reasoning and problem-solving at the competition level.

#### Problem Characteristics
- **Source**: AMC (American Mathematics Competition) and AIME (American Invitational Mathematics Examination)
- **Difficulty range**: High school to graduate level mathematics
- **Categories**:
  - Algebra (3,000 problems)
  - Precalculus (2,800 problems)
  - Geometry (2,500 problems)
  - Number theory (2,500 problems)
  - Combinatorics (1,700 problems)
- **Problem type**: Multi-step reasoning with non-trivial solutions
- **Average steps to solution**: 5-15 mathematical reasoning steps

#### Scoring & Methodology
- **Format**: Free-form mathematical expressions
- **Evaluation**: Symbolic answer matching (LaTeX format)
- **Test set size**: ~7,500 problems
- **Metric**: Exact symbolic match on final answer
- **Reasoning evaluation**: Can verify mathematical derivation steps

#### Current Performance (March 2026)
| Model | Score | Category Performance |
|-------|-------|---------------------|
| GPT-5 | ~90%+ | Frontier capability |
| Claude Opus 4.5 | ~87% | Strong math reasoning |
| Gemini 3.1 Pro | ~88% | Competitive frontier |
| Kimi K2.5 | ~85% | Specialized math model |

#### Category Breakdown (Typical)
| Category | Difficulty | Frontier Score |
|----------|-----------|-----------------|
| Algebra | Medium | ~92%+ |
| Precalculus | Medium-Hard | ~88%+ |
| Geometry | Hard | ~85%+ |
| Number Theory | Hard | ~82%+ |
| Combinatorics | Very Hard | ~78%+ |

#### Strengths
- Tests genuine mathematical reasoning (not retrieval)
- Challenging enough to differentiate frontier models
- Multiple categories enabling diagnostic analysis
- Well-established with published analyses
- Reflects realistic mathematical problem-solving difficulty

#### Limitations
- Requires symbolic answer matching (implementation dependent)
- Some problems may have multiple valid representations
- Category imbalance may affect overall score interpretation
- Larger models show advantages (attention over reasoning)
- Decreasing discrimination as models improve

#### Recommendations for Use
- Essential for models claiming mathematical capability
- Use category breakdown for diagnostic assessment
- Pair with GSM8K for complete mathematical evaluation
- Useful for tracking improvement in mathematical reasoning
- Important component of frontier model evaluation

---

### AIME 2025/2026 (American Invitational Mathematics Examination)

#### Description
AIME is the highest-difficulty real mathematics competition. The 2025 and 2026 competitions have become benchmarks for evaluating frontier LLM mathematical reasoning at the absolute limit of capability. Each competition contains 15 extremely difficult problems requiring deep mathematical insight.

#### Problem Characteristics
- **Source**: Official AIME competitions (2025 and 2026)
- **Problem count**: 30 problems total (15 per year)
- **Difficulty**: Extremely high (requires competition-level mathematical insight)
- **Categories**: Algebra, geometry, number theory, combinatorics
- **Time pressure context**: Originally 3 hours for 15 problems (LLMs evaluated without time limit)

#### Scoring & Methodology
- **Format**: Integer answers from 000 to 999
- **Evaluation**: Exact match on integer answer
- **Grading**: Binary (correct/incorrect per problem)
- **Score range**: 0-15 per competition (30 total across two years)
- **Frontier capability indicator**: Near-perfect performance indicates frontier mathematical reasoning

#### Current Performance (March 2026)
| Model | AIME 2025 | AIME 2026 | Combined | Status |
|-------|-----------|-----------|----------|--------|
| GPT-5 | 15/15 | 15/15 | 30/30 (100%) | Perfect |
| Gemini 3.1 Pro | 14/15 | 13/15 | 27/30 (90%) | Near-perfect |
| Claude Opus 4.5 | 13/15 | 12/15 | 25/30 (83%) | Advanced |

#### Key Observations
- GPT-5 achieves perfect score on both competitions
- Significant gap between GPT-5 (100%) and other frontier models (80-90%)
- Performance demonstrates frontier models can solve competition-level problems
- Perfect score represents potential maximum on real mathematics competitions

#### Strengths
- Represents absolute frontier of mathematical capability
- Uses real competition problems (maximum authenticity)
- Clear integer answer format (no ambiguity)
- Extremely challenging (maintains discrimination at frontier)
- High-stakes problems indicate genuine capability

#### Limitations
- Only 30 problems total (small sample size, high variance)
- Limited yearly availability (must wait for new competitions)
- Not repeatable benchmark (new problems each year)
- Perfect scores possible (saturation risk at frontier)
- Very expensive problem (requires deep mathematical understanding)

#### Recommendations for Use
- Essential tracking metric for frontier mathematical capability
- Use as top-level indicator of mathematical reasoning ceiling
- Supplement with MATH for more comprehensive assessment
- Track annually to monitor frontier progress
- Combined AIME + MATH gives comprehensive mathematical profile

---

### FrontierMath

#### Description
FrontierMath is a research-level mathematics benchmark containing genuinely novel mathematical problems generated by professional mathematicians. It specifically targets unsolved research problems and mathematical reasoning at the frontier, designed to measure capabilities beyond current frontier models.

#### Benchmark Structure
- **Problem sourcing**: Original problems created by professional mathematicians
- **Difficulty tier system**:
  - Tier 1: Very hard (research-level difficulty)
  - Tier 2: Extremely hard (requires novel approaches)
  - Tier 3: Impossible (unsolved research problems)
- **Problem count**: Multiple tiers with expanding difficulty
- **Modality**: Pure mathematical reasoning (symbolic manipulation)
- **Verification**: Expert mathematician validation

#### Scoring & Methodology
- **Format**: Formal mathematical proofs or symbolic answers
- **Evaluation**: Correctness of mathematical reasoning
- **Difficulty**: Intentionally beyond current frontier capability
- **Score interpretation**: Score indicates research-level mathematical progress
- **Multi-tier evaluation**: Separate evaluation at each difficulty tier

#### Current Performance (March 2026)
| Tier | Difficulty | Frontier Score | Interpretation |
|------|-----------|-----------------|-----------------|
| Tier 1 | Very Hard | 40%+ | Frontier models solve 40%+ |
| Tier 2 | Extremely Hard | 15-25% | Significant frontier challenge |
| Tier 3 | Unsolved | <5% | Beyond current capability |

#### Tier Characteristics
**Tier 1 (40%+ frontier)**: Problems requiring sophisticated but known mathematical techniques
**Tier 2 (15-25% frontier)**: Problems requiring novel approaches or combinations of techniques
**Tier 3 (<5% frontier)**: Genuinely unsolved research problems or equivalent difficulty

#### Strengths
- Represents true frontier of mathematical reasoning
- Maintains discrimination at frontier level (no saturation)
- Uses authentic research problems (maximum relevance)
- Tiers allow capability depth analysis
- Drives research toward harder problems

#### Limitations
- Very small problem set per tier (high variance)
- Requires expert validation (expensive to expand)
- Answers may not always be unambiguously defined
- Time-consuming evaluation required
- Difficult to verify proposed solutions

#### Recommendations for Use
- Essential for frontier mathematical capability tracking
- Use as indicator of research-level mathematical progress
- Combine Tier 1 and Tier 2 for comprehensive frontier assessment
- Monitor annually for model improvement
- Important for understanding mathematical reasoning ceiling

---

## Code Generation & Software Engineering Benchmarks

### HumanEval

#### Description
HumanEval is a benchmark of 164 Python programming tasks from "Introductory to Intermediate" difficulty, covering basic algorithm implementation, data manipulation, and simple problem solving. It's the foundational code generation benchmark.

#### Problem Characteristics
- **Language**: Python 3
- **Problem count**: 164 problems
- **Difficulty**: Beginner to intermediate (1-5 functions per problem)
- **Problem type**: Function implementation from specifications
- **Average lines of code**: 10-20 lines per solution
- **Categories**: Parsing, algorithms, mathematical functions, string manipulation

#### Scoring & Methodology
- **Format**: Generate function implementation from docstring specification
- **Evaluation**: Execute generated code against test cases
- **Test cases**: 10-20 test cases per problem
- **Metric**: Pass@k (percentage of problems where at least 1 out of k samples passes)
- **Standard metric**: Pass@1 (first generation attempt)

#### Current Performance (March 2026)
| Model | Pass@1 | Pass@3 | Pass@10 | Status |
|-------|--------|--------|----------|--------|
| GPT-5 | >95% | >98% | 99%+ | Saturated |
| Claude Opus 4.5 | 92% | 96% | 98.5% | Saturated |
| Gemini 3.1 Pro | 93% | 96.5% | 98% | Saturated |
| Most frontier models | >90% | >95% | >97% | Saturated |

#### Key Observations
- **Saturation**: HumanEval is effectively saturated (>90% pass@1 across frontier models)
- **Pass@k effect**: Sampling multiple times dramatically improves scores
- **Discrimination**: No longer differentiates between frontier and near-frontier models
- **Ceiling effect**: Little room for improvement on this benchmark

#### Strengths
- Clear problem specifications with unambiguous test cases
- Directly executable evaluation (no subjective grading)
- Small test set allows rapid evaluation
- Widely adopted enabling easy comparison
- Well-understood failure modes

#### Limitations
- **Saturated**: Limited discrimination value at frontier
- **Too simple**: Doesn't test real software engineering challenges
- **Execution-based**: Tests runtime behavior, not code quality
- **No scalability**: Doesn't test problems with >50 lines of code
- **Language singular**: Python-only (limited for polyglot evaluation)

#### Recommendations for Use
- Use for baseline code generation verification
- Not recommended as primary code evaluation metric
- Useful for non-frontier models to establish baseline
- Supplement with SWE-bench Verified for comprehensive assessment
- Skip in frontier model comparisons

---

### SWE-bench Verified

#### Description
SWE-bench Verified contains 500+ real GitHub issues from popular Python repositories, testing the model's ability to understand codebases, locate bugs, write fixes, and navigate the full software development lifecycle. It represents a significant step toward real-world code capability.

#### Benchmark Design
- **Source**: Real GitHub issues from popular repositories (django, flask, scikit-learn, etc.)
- **Issue count**: 500+ verified issues
- **Scope**: Bug fixes, feature implementation, code refactoring
- **Codebase size**: Real production codebases (1,000+ files)
- **Verification**: Issues verified to have correct solutions
- **Format**: Issue description + codebase provided to model

#### Scoring & Methodology
- **Task**: Read issue, locate problematic code, write fix
- **Evaluation**: Execute test suite (both pre-existing and fix verification tests)
- **Success criteria**: All tests pass after fix applied
- **Metric**: Percentage of issues correctly resolved
- **Context window**: Extended context required (may exceed 8K tokens)

#### Current Performance (March 2026)
| Model | Score | Category |
|-------|-------|----------|
| Claude Opus 4.5 | 80.9% | Frontier capability |
| GPT-5 | 78.2% | Near-frontier |
| Gemini 3.1 Pro | 71.5% | Advanced capability |
| Most non-frontier | <30% | Significant gap to frontier |

#### Performance Analysis
- **Frontier/Non-frontier gap**: ~50% performance difference (real challenge)
- **Error analysis**: Common failures include context management, test understanding
- **Improvement trajectory**: Steady improvement month-over-month
- **Domain variance**: Some repositories much harder than others

#### Strengths
- Real-world relevance (actual GitHub issues)
- Tests full software development lifecycle
- Large test set (500+ issues)
- Executable verification (objective evaluation)
- Strong discrimination between capability levels

#### Limitations
- Limited to Python (not polyglot)
- Repository-specific knowledge influences performance
- Test suite quality varies by repository
- Context window demands create technical barriers
- Evaluation compute expensive

#### Recommendations for Use
- Essential for code-intensive applications
- Primary benchmark for software engineering capability
- Use category breakdown (by repository) for analysis
- Pair with HumanEval for comprehensive code assessment
- Critical for production systems relying on code generation

---

### LiveCodeBench

#### Description
LiveCodeBench is a monthly-updated benchmark of diverse programming tasks including LeetCode-style algorithm problems, function implementations, and problem-solving across multiple programming languages. It updates monthly, providing continuous capability tracking.

#### Benchmark Characteristics
- **Update frequency**: Monthly new problem sets
- **Language coverage**: Python, Java, C++, JavaScript, and others
- **Problem types**:
  - Algorithm problems (LeetCode-style)
  - Function implementations
  - Code understanding and completion
  - Bug fixing tasks
- **Problem count**: 200-300 new problems monthly
- **Historical tracking**: Maintains baseline for trend analysis

#### Scoring & Methodology
- **Format**: Programming problem with specifications and test cases
- **Evaluation**: Execute against test suite
- **Metric**: Pass@1 (first attempt correctness)
- **Difficulty calibration**: Mix of easy, medium, hard problems
- **Language flexibility**: Allows solutions in multiple languages

#### Current Performance (March 2026)
| Model | Average Score | Trend |
|-------|---|---------|
| GPT-5 | ~78%+ | Improving |
| Claude Opus 4.5 | ~75% | Stable |
| Gemini 3.1 Pro | ~72% | Improving |
| Frontier models | 70-78% | Upward trend |

#### Key Features
- **Monthly updates**: Prevents benchmark saturation
- **Diverse problems**: Multiple languages and problem types
- **Trend tracking**: Long-term capability measurement
- **Real-time leaderboards**: Live performance tracking

#### Strengths
- Prevents saturation through monthly updates
- Diverse problem types reflecting real coding tasks
- Continuous trend monitoring capability
- Includes multiple programming languages
- Live leaderboard enables competitive tracking

#### Limitations
- Fewer historical results (newer benchmark)
- Problem difficulty varies month-to-month
- Smaller problem set per month than comprehensive benchmarks
- Implementation details affect execution scoring
- Limited analysis of failure patterns

#### Recommendations for Use
- Use for continuous capability monitoring
- Subscribe to monthly releases for trend tracking
- Useful for detecting performance plateaus
- Supplement with larger benchmarks for comprehensive assessment
- Valuable for model developers tracking improvements

---

### BigCodeBench

#### Description
BigCodeBench is a comprehensive code generation benchmark containing 1,139 diverse programming problems across function implementation, algorithm solving, and software engineering tasks. It provides breadth of coverage across difficulty levels and problem types.

#### Benchmark Scope
- **Problem count**: 1,139 diverse problems
- **Language**: Primarily Python with multi-language support
- **Problem categories**:
  - Basic function implementation (15%)
  - Algorithm problems (35%)
  - Data structure manipulation (20%)
  - Code understanding and refactoring (20%)
  - Advanced problem-solving (10%)
- **Difficulty distribution**: Easy (25%), Medium (50%), Hard (25%)
- **Problem source**: LeetCode, CodeForces, academic sources

#### Scoring & Methodology
- **Format**: Specify function signature, solve problem
- **Evaluation**: Execute against comprehensive test suites
- **Metric**: Pass@1 (first attempt correctness)
- **Test coverage**: 10-20 test cases per problem
- **Difficulty**: Calibrated to match real coding challenge difficulty

#### Current Performance (March 2026)
| Model | Easy | Medium | Hard | Overall |
|-------|------|--------|------|---------|
| GPT-5 | 94% | 87% | 76% | ~85%+ |
| Claude Opus 4.5 | 91% | 83% | 70% | ~81% |
| Gemini 3.1 Pro | 89% | 80% | 68% | ~79% |

#### Strengths
- Comprehensive problem coverage (1,139 problems)
- Difficulty distribution enables capability profiling
- Multiple problem categories for diagnostic analysis
- Larger scale than HumanEval (better statistics)
- Good difficulty calibration for frontier models

#### Limitations
- Primarily Python-focused (not fully polyglot)
- Execution-based evaluation (code quality not measured)
- Imbalanced categories may affect overall score interpretation
- Newer benchmark (limited historical analysis)
- Some problem ambiguity in specifications

#### Recommendations for Use
- Use as primary comprehensive code generation benchmark
- Analyze category breakdown for specific capability gaps
- Pair with SWE-bench for complete code assessment
- Use difficulty breakdown for capability profiling
- Important for models claiming coding capability

---

### MBPP (Mostly Basic Python Programming)

#### Description
MBPP is a benchmark of 974 Python programming problems of varying difficulty, created from crowdsourced solutions. It tests function implementation across diverse problem types with clear specifications and test cases.

#### Benchmark Structure
- **Problem count**: 974 Python functions
- **Difficulty**: Mostly basic to intermediate
- **Source**: Crowdsourced implementations and problem sets
- **Problem type**: Diverse function implementation
- **Test format**: Multiple test cases per problem
- **Average problem size**: 5-15 lines of code

#### Scoring & Methodology
- **Format**: Function signature with specification
- **Evaluation**: Execute against test cases
- **Metric**: Percentage of problems where implementation passes all tests
- **Standard metric**: Pass@1 (first attempt)
- **Test validation**: Multiple test cases ensure correctness

#### Current Performance (March 2026)
| Model | Pass@1 | Pass@3 |
|-------|--------|--------|
| Claude Opus 4.5 | 88% | 92% |
| GPT-5 | 87%+ | 91%+ |
| Gemini 3.1 Pro | 85% | 90% |

#### Strengths
- Large problem set (974 problems) for statistical significance
- Clear function specifications reducing ambiguity
- Multiple test cases per problem
- Good difficulty calibration
- Well-adopted benchmark

#### Limitations
- Similar saturation risk to HumanEval (approaching 90%+)
- Primarily basic/intermediate difficulty
- Limited for frontier model discrimination
- Smaller than BigCodeBench (less comprehensive)
- Python-only

#### Recommendations for Use
- Use alongside HumanEval for baseline coding assessment
- Good complement to more comprehensive benchmarks
- Useful for non-frontier model evaluation
- Can be combined with HumanEval for broader baseline
- Monitor for saturation

---

## Code Benchmark Comparison Matrix

| Benchmark | Scale | Difficulty | Type | Saturation Risk | Best For |
|-----------|-------|-----------|------|-----------------|----------|
| HumanEval | 164 | Easy-Medium | Function impl | High | Baseline |
| MBPP | 974 | Basic-Medium | Function impl | Medium-High | Coverage |
| BigCodeBench | 1,139 | Easy-Hard | Diverse | Medium | Comprehensive |
| LiveCodeBench | 200-300/mo | Easy-Hard | Diverse | Low | Trending |
| SWE-bench | 500+ | Hard | Real issues | Low | Production |

---

## Integrated Code Evaluation Strategy

### For General Models
1. HumanEval (baseline)
2. BigCodeBench (comprehensive)
3. SWE-bench Verified (production relevance)

### For Frontier Models
1. SWE-bench Verified (primary)
2. BigCodeBench (comprehensive)
3. LiveCodeBench (monthly tracking)
4. AIME (stretch goal)

### For Production Systems
1. SWE-bench Verified (primary)
2. Domain-specific code benchmarks
3. Live evaluations on custom test suites

---

## Performance Trends & Future Outlook

**Current State (March 2026)**:
- HumanEval saturation requires alternative benchmarks
- SWE-bench becoming primary code evaluation metric
- LiveCodeBench preventing saturation through continuous updates
- Frontier models reaching 80%+ on real GitHub issues

**Expected Developments**:
- More realistic software engineering benchmarks
- Increased focus on code understanding over generation
- Multi-file, multi-language problems becoming standard
- Agent-based code evaluation (not just generation)
- Integration of code quality metrics beyond pass@1

## References

**Official Repositories**:
- HumanEval: https://github.com/openai/human-eval
- MATH: https://github.com/hendrycks/math
- SWE-bench: https://github.com/princeton-nlp/swe-bench
- BigCodeBench: https://github.com/bigcode-project/bigcodebench
- LiveCodeBench: https://livecodebench.github.io/
- MBPP: https://github.com/google-research/google-research/tree/master/mbpp
