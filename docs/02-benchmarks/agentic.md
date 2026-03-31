# Agentic & Tool Use Benchmarks

## Overview

Agentic benchmarks evaluate an LLM's ability to act autonomously in interactive environments, use tools, make sequential decisions, and accomplish multi-step goals. These benchmarks measure practical capability beyond language understanding toward autonomous problem-solving.

---

## WebArena

### Description
WebArena is a benchmark of real-world web navigation tasks where models must interact with actual websites, navigate interfaces, find information, and complete complex transactions. It represents a significant step toward autonomous web interaction.

### Benchmark Design
- **Environment**: Real websites (shopping sites, email, search engines, databases)
- **Task count**: 812+ web interaction tasks
- **Task types**:
  - Information retrieval (find specific information on website)
  - Shopping/transactions (navigate, add to cart, checkout)
  - Account management (login, settings, profile)
  - Form filling (complex multi-step forms)
  - Comparison tasks (compare products, prices)
- **Interaction model**: Keyboard/mouse simulation with visual feedback
- **Challenge**: Real website complexity and variability

### Task Categories
| Category | Count | Difficulty | Example |
|----------|-------|-----------|---------|
| Information retrieval | 250+ | Easy-Medium | Find product on site |
| E-commerce | 200+ | Medium | Complete purchase |
| Account tasks | 150+ | Medium | Update preferences |
| Form completion | 150+ | Hard | Complex form filling |
| Research tasks | 62+ | Hard | Multi-step research |

### Scoring & Methodology
- **Format**: Natural language task description + real website environment
- **Evaluation**: Did model complete the task successfully?
- **Success criteria**: Task-specific (purchase completed, info found, etc.)
- **Execution**: HTML/visual state at each step fed to model
- **Error recovery**: Model must handle errors and navigation misses

### Current Performance (March 2026)
| Model | Success Rate | Category |
|-------|---|----------|
| Claude Opus 4.5 | ~35% | Advanced agent |
| GPT-5 | ~32% | Advanced agent |
| Gemini 3.1 Pro | ~28% | Competent agent |

### Task Difficulty Performance
| Difficulty | Success Rate | Challenge |
|-----------|---|---------|
| Easy | 55%+ | Manageable |
| Medium | 35%+ | Significant challenge |
| Hard | 15-20% | Very difficult |

### Failure Modes
- **Navigation errors** (45%): Wrong page/element location
- **Context tracking** (25%): Forgetting task requirements mid-execution
- **Form handling** (15%): Complex form fields, validation
- **Error recovery** (10%): Handling unexpected page states
- **Button/link identification** (5%): Finding correct interactive elements

### Strengths
- Real-world relevance (actual website interaction)
- Complex multi-step tasks requiring planning
- Error recovery and robustness testing
- Measurable success criteria
- Represents frontier of autonomous web agent capability

### Limitations
- Real websites change dynamically (benchmark drift)
- High variance in task difficulty
- Error modes vary significantly by website
- Limited to desktop web (mobile underrepresented)
- Expensive to maintain and run

### Recommendations for Use
- Important for web automation capability assessment
- Useful for understanding agent limitations
- Track improvements in navigation and planning
- Not recommended as primary general capability metric
- Essential for web automation applications

---

## GAIA (General AI Assistants)

### Description
GAIA is a benchmark of 466 real-world tasks requiring general reasoning, retrieval, tool use, and multi-step problem solving. It focuses on tasks requiring integration of multiple capabilities rather than single narrow skills.

### Benchmark Design
- **Task count**: 466 real-world problems
- **Task sourcing**: Crowd-sourced from real user queries
- **Categories**:
  - Question answering (requires research)
  - Math problems (requires calculation)
  - Code generation (requires programming)
  - Planning (requires multi-step reasoning)
  - Creative tasks (requires synthesis)
- **Difficulty levels**: Easy, medium, hard (based on solver feedback)
- **Answer format**: Free-form text with evaluation flexibility

### Task Characteristics
| Category | Count | Typical Challenge |
|----------|-------|--|
| Research & QA | 150+ | Find and synthesize information |
| Mathematical | 120+ | Complex reasoning + calculation |
| Programming | 100+ | Code writing and debugging |
| Reasoning | 96+ | Multi-step logical reasoning |

### Scoring & Methodology
- **Format**: Natural language task description
- **Evaluation**: Can use tools (search, calculator, code execution)
- **Metric**: Success rate (task completed correctly)
- **Tool availability**: Search, calculation, code execution allowed
- **Verification**: Human judgment or automated checking by domain

### Current Performance (March 2026)
| Model | Success Rate | with Tools | Category |
|-------|---|---|----------|
| GPT-5 | ~92%+ | 95%+ | Frontier capability |
| Claude Opus 4.5 | ~88% | 91% | Advanced capability |
| Gemini 3.1 Pro | ~85% | 88% | Advanced capability |

### Performance by Difficulty
| Level | Frontier Score | Gap to Perfect |
|-------|---|---|
| Easy | 97%+ | <3% |
| Medium | 92%+ | 8% |
| Hard | 82%+ | 18% |

### Tool Usage Impact
| Tool | Improvement | Critical |
|------|-------------|----------|
| Search | +15-20% | For research |
| Calculator | +8-12% | For math |
| Code execution | +10-15% | For programming |

### Strengths
- Real-world tasks reflecting user needs
- Tests integration of multiple capabilities
- Tool use evaluates practical agent capability
- Clear success/failure metrics
- Diverse task categories

### Limitations
- Smaller test set (466 tasks) vs. other benchmarks
- Difficulty calibration varies by task
- Tool access assumptions may not reflect real systems
- Evaluation can be subjective for open-ended tasks
- Task sourcing introduces quality variability

### Recommendations for Use
- Primary metric for general-purpose agent capability
- Essential for evaluating integrated reasoning
- Tool usage pattern analysis valuable
- Useful for identifying multi-step reasoning gaps
- Important for production agent systems

---

## Terminal-Bench Hard

### Description
Terminal-Bench Hard is a benchmark of 500+ command-line tasks requiring shell/terminal proficiency including file operations, text processing, system administration, and complex command composition. It tests agentic capability in the command-line environment.

### Benchmark Design
- **Environment**: Simulated Linux/Unix terminal
- **Task count**: 500+ shell commands and operations
- **Task types**:
  - File operations (create, modify, organize files)
  - Text processing (grep, sed, awk, regex)
  - System administration (permissions, processes, services)
  - Package management (apt, pip, etc.)
  - Network operations (networking, SSH, etc.)
  - Scripting (bash script creation and execution)
- **Difficulty**: "Hard" subset emphasizes complex multi-step operations
- **Evaluation**: Command correctness and side effects

### Task Difficulty Progression
| Level | Task Example | Complexity |
|-------|---|---|
| Basic | List files, show contents | Simple |
| Intermediate | Find files with patterns | Moderate |
| Hard | Multi-step data processing | Complex |
| Very Hard | Debugging scripts, optimization | Very Complex |

### Scoring & Methodology
- **Format**: Natural language task description → shell commands
- **Evaluation**: Execute commands, verify correctness
- **Metric**: Success rate (task completed correctly)
- **Verification**: Check output correctness, side effects
- **Error modes**: Syntax errors, wrong flags, logic errors

### Current Performance (March 2026)
| Model | Overall | Hard Tasks | Advanced |
|-------|---------|-----------|----------|
| Claude Opus 4.5 | ~68% | ~60% | Competent |
| GPT-5 | ~65% | ~58% | Competent |
| Specialized models | 50-62% | 40-50% | Moderate |

### Command Proficiency by Category
| Category | Frontier Score | Difficulty |
|----------|---|---|
| Basic operations | 85%+ | Easy |
| Text processing | 72%+ | Medium |
| System admin | 68%+ | Hard |
| Scripting | 55%+ | Very hard |

### Common Errors
- **Syntax errors** (30%): Wrong flags, command format
- **Logic errors** (25%): Incorrect approach to problem
- **Incomplete solutions** (20%): Partial implementation
- **Piping errors** (15%): Chain operations incorrectly
- **Permission errors** (10%): Incorrect permission handling

### Strengths
- Real-world terminal environment
- Tests practical system administration
- Measures practical shell scripting capability
- Clear pass/fail metrics
- Valuable for DevOps and system automation

### Limitations
- Limited to command-line (not GUI applications)
- Simulated environment may differ from real systems
- Task difficulty can vary significantly
- Some tasks have multiple valid solutions
- Smaller community relative to other benchmarks

### Recommendations for Use
- Primary metric for terminal/shell capability
- Essential for DevOps and system automation assessment
- Use for understanding scripting limitations
- Important for infrastructure automation
- Pair with general reasoning benchmarks

---

## tau2-Bench

### Description
tau2-Bench is a benchmark of multi-step reasoning tasks where models must chain multiple reasoning steps, integrate information, and solve complex problems requiring 5-20 intermediate steps. It measures planning and multi-turn reasoning.

### Benchmark Design
- **Task count**: 2,000+ multi-step tasks
- **Step range**: 5-20 logical steps per task
- **Task types**:
  - Mathematical reasoning chains
  - Logic puzzles with multiple constraints
  - Planning and scheduling
  - Information synthesis across domains
  - Debugging and problem-solving
- **Intermediate step tracking**: Can evaluate reasoning at each step
- **Difficulty calibration**: From medium to very difficult

### Task Characteristics
| Type | Steps | Difficulty |
|------|-------|-----------|
| Mathematical chains | 5-8 | Medium-Hard |
| Logic puzzles | 8-12 | Hard |
| Planning | 10-15 | Very Hard |
| Synthesis | 12-20 | Very Hard |

### Scoring & Methodology
- **Format**: Task description → multi-step reasoning required
- **Evaluation**: Process + answer correctness
- **Metrics**:
  - Overall success rate
  - Intermediate step accuracy
  - Reasoning quality assessment
- **Chain evaluation**: Each step can be scored independently

### Current Performance (March 2026)
| Model | Overall | Avg Steps Correct | Category |
|-------|---------|---|---|
| GPT-5 | ~77%+ | 85% | Frontier reasoning |
| Claude Opus 4.5 | ~73% | 81% | Advanced reasoning |
| Gemini 3.1 Pro | ~70% | 78% | Advanced reasoning |

### Performance by Step Count
| Steps | Success Rate | Complexity |
|-------|---|---|
| 5 steps | 88%+ | Easy |
| 8 steps | 80%+ | Medium |
| 12 steps | 70%+ | Hard |
| 15+ steps | 55%+ | Very hard |

### Reasoning Quality
- **Complete chains**: ~77% (all steps correct)
- **Partial chains**: ~12% (some steps correct)
- **Failed chains**: ~11% (incomplete/incorrect)

### Strengths
- Tests genuine multi-step reasoning
- Intermediate step tracking enables analysis
- Measures planning and problem decomposition
- Large test set (2,000+ tasks)
- Clear difficulty progression

### Limitations
- Smaller scale than comprehensive benchmarks
- Still newer benchmark (evolving methodology)
- Step definition can be ambiguous
- Evaluation requires careful step decomposition
- Limited adoption relative to other benchmarks

### Recommendations for Use
- Important for multi-step reasoning assessment
- Use intermediate step analysis for diagnostics
- Valuable for planning and complex reasoning
- Track long-chain capability development
- Useful for agentic systems requiring planning

---

## FieldWorkArena

### Description
FieldWorkArena is a benchmark of 100+ long-horizon tasks in a simulated environment, requiring sustained planning, tool use, and environmental interaction over 50-200 steps. It represents frontier autonomous capability.

### Benchmark Design
- **Environment**: Simulated workplace/field scenarios
- **Task count**: 100+ long-horizon tasks
- **Horizon**: 50-200 steps per task
- **Task types**:
  - Research tasks (locate information, synthesize findings)
  - Project planning (organize complex work)
  - Resource management (allocate tools and resources)
  - Problem-solving (debugging, troubleshooting)
- **Tool availability**: Various tools and information sources
- **State tracking**: Rich environmental state to track

### Task Scope Examples
- Research paper: Literature review, synthesis (100+ steps)
- Project management: Plan team project (150+ steps)
- System debugging: Diagnose complex issue (80+ steps)

### Scoring & Methodology
- **Format**: Long-horizon task in simulated environment
- **Evaluation**: Goal achievement and efficiency
- **Metrics**:
  - Task completion (did model achieve goal?)
  - Efficiency (steps taken vs. optimal)
  - Plan quality (was approach reasonable?)
- **Intermediate: Succ tracking of progress

### Current Performance (March 2026)
| Model | Completion | Efficiency | Category |
|-------|-----------|-----------|----------|
| Claude Opus 4.5 | ~42% | ~68% optimal | Advanced agent |
| GPT-5 | ~40% | ~65% optimal | Advanced agent |
| Frontier models | 35-42% | 60-70% | Frontier |

### Task Difficulty Performance
| Horizon | Completion | Challenge |
|---------|-----------|-----------|
| 50-75 steps | 60%+ | Manageable |
| 100-150 steps | 40%+ | Significant |
| 150-200 steps | 25%+ | Frontier |

### Failure Modes
- **Goal drift** (35%): Losing sight of original goal
- **Resource misallocation** (25%): Inefficient resource use
- **Context limits** (20%): Context window exhaustion
- **Plan failures** (15%): Sub-optimal planning
- **Tool misuse** (5%): Incorrect tool application

### Strengths
- Long-horizon tasks test sustained capability
- Rich environment with realistic complexity
- Measurable efficiency and quality metrics
- Tests planning at frontier difficulty
- Represents practical autonomous systems

### Limitations
- Simulated environment (not real-world)
- Small test set (100+ tasks)
- Difficulty to separate planning vs. execution capability
- Context window often a limiting factor
- Evaluation complexity

### Recommendations for Use
- Use for long-horizon agent capability
- Important for autonomous system assessment
- Analyze goal drift and efficiency patterns
- Useful for identifying context window limitations
- Essential for frontier agent evaluation

---

## AgentClinic

### Description
AgentClinic is a benchmark of 500+ medical diagnostic tasks requiring multi-step diagnostic reasoning, symptom analysis, differential diagnosis, and treatment planning. It represents specialized agentic capability in medical domain.

### Benchmark Design
- **Domain**: Medical diagnosis and treatment planning
- **Task count**: 500+ patient cases
- **Case types**:
  - Symptom interpretation (identify disease from symptoms)
  - Diagnostic planning (order appropriate tests)
  - Differential diagnosis (narrow possibilities)
  - Treatment planning (recommend treatment)
  - Reasoning justification (explain reasoning)
- **Complexity**: Single condition to multi-condition diagnosis
- **Realism**: Based on actual medical cases (de-identified)

### Diagnostic Task Stages
| Stage | Complexity | Focus |
|-------|-----------|-------|
| Symptom analysis | Low-Medium | Identify relevant symptoms |
| Differential diagnosis | Medium | Generate diagnostic hypotheses |
| Test planning | Medium | Order appropriate tests |
| Final diagnosis | High | Determine correct diagnosis |
| Treatment | High | Plan appropriate treatment |

### Scoring & Methodology
- **Format**: Patient case description + medical history
- **Evaluation**: Diagnostic accuracy + plan quality
- **Metrics**:
  - Diagnosis correctness
  - Differential diagnosis quality
  - Test selection appropriateness
  - Treatment plan quality
  - Overall medical reasoning quality
- **Clinical grading**: By medical professionals

### Current Performance (March 2026)
| Model | Accuracy | Reasoning | Category |
|-------|----------|-----------|----------|
| Claude Opus 4.5 | ~89% | Excellent | Advanced medical |
| GPT-5 | ~86% | Excellent | Advanced medical |
| Medical-specific | 85-88% | Very Good | Specialized |

### Diagnostic Accuracy by Condition Type
| Type | Frontier Score | Difficulty |
|------|---|---|
| Single condition | 94%+ | Easy |
| Multi-condition | 85%+ | Medium |
| Rare disease | 73%+ | Hard |
| Complex case | 68%+ | Very hard |

### Reasoning Quality
- **Complete differential** (89%): Considers multiple diagnoses
- **Appropriate tests** (87%): Orders relevant tests
- **Clinical reasoning** (85%): Sound medical logic
- **Treatment planning** (86%): Appropriate interventions

### Strengths
- Specialized domain testing
- Real-world medical cases
- Multi-step diagnostic reasoning
- Professional evaluation criteria
- Important for medical AI applications

### Limitations
- Limited to medical domain
- Smaller test set (500 cases)
- De-identification may remove clinical nuance
- Evaluation requires medical expertise
- Specialized benchmark (limited general applicability)

### Recommendations for Use
- Essential for medical AI systems
- Specialized capability assessment
- Important for clinical decision support
- Use for understanding medical reasoning limitations
- Valuable for regulated medical applications

---

## Agentic Benchmark Comparison

| Benchmark | Domain | Scale | Type | Best For |
|-----------|--------|-------|------|----------|
| WebArena | Web | 812 | Real environment | Web automation |
| GAIA | General | 466 | Real-world tasks | General agents |
| Terminal-Bench | CLI | 500+ | Real environment | DevOps |
| tau2-Bench | Reasoning | 2,000+ | Multi-step | Planning/reasoning |
| FieldWorkArena | General | 100+ | Long-horizon | Autonomous agents |
| AgentClinic | Medical | 500+ | Specialized | Medical diagnosis |

---

## Integrated Agentic Evaluation Strategy

### For General-Purpose Agents
1. GAIA (primary - real-world tasks)
2. tau2-Bench (reasoning capability)
3. WebArena (environmental interaction)

### For Web Automation
1. WebArena (primary - web interaction)
2. GAIA (reasoning and planning)
3. Custom web-specific tasks

### For Long-Horizon Agents
1. FieldWorkArena (primary - sustained capability)
2. tau2-Bench (step-by-step reasoning)
3. GAIA (goal-oriented reasoning)

### For Specialized Agents
1. Domain-specific benchmarks (AgentClinic for medical)
2. Terminal-Bench for DevOps/CLI
3. GAIA for general capability

---

## Performance Trends & Key Observations (March 2026)

### Capability Distribution
- **Easy tasks** (GAIA easy, short horizon): 90%+
- **Medium tasks** (WebArena medium, GAIA medium): 60-75%
- **Hard tasks** (long horizon, complex reasoning): 35-45%
- **Frontier**: Long-horizon planning (25-42%)

### Common Challenges
- **Planning limitations**: Multi-step planning difficult beyond 15 steps
- **Context constraints**: Long contexts exhaust window
- **Error recovery**: Recovering from mistakes challenging
- **Goal tracking**: Sustaining focus on original goal
- **Tool usage**: Complex tool chains cause failures

### Agent Specialization
- General agents (GAIA ~88%+) outperform specialized on breadth
- Specialized agents (AgentClinic 89%, medical focused) excel in domain
- WebArena shows limited web-specific capability (35%)
- Terminal-Bench shows limited shell expertise (68%)

### Emerging Challenges
- Long-horizon tasks remain frontier (42% best)
- Goal drift increases with task horizon
- Context window becoming limiting factor
- Multi-tool coordination challenging
- Error recovery and replanning underdeveloped

---

## References

**Official Repositories**:
- WebArena: https://github.com/web-arena-x/webarena
- GAIA: https://huggingface.co/datasets/gaia-benchmark/GAIA
- Terminal-Bench: https://github.com/mehrad31415/TerminalBench
- tau2-Bench: https://github.com/reasoning-machines/tau2-bench

**Key Papers**:
- WebArena: Zhou et al., "WebArena: A Realistic Web Environment for Building Autonomous Agents"
- GAIA: Ruan et al., "GAIA: A Benchmark for Real-World AI Assistants"
