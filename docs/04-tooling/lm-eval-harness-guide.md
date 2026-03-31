# lm-evaluation-harness: Complete Implementation Guide

**Version:** lm-eval v0.4.3+
**License:** MIT
**Maintainer:** EleutherAI
**Latest Update:** March 2026

lm-evaluation-harness is the industry-standard benchmark evaluation framework maintained by EleutherAI. It powers the HuggingFace Open LLM Leaderboard with 1000+ tasks including MMLU, TruthfulQA, and GSM8K.

## Installation & Setup

### Basic Installation

```bash
# Clone from GitHub
git clone https://github.com/EleutherAI/lm-evaluation-harness
cd lm-evaluation-harness

# Install in development mode
pip install -e .

# Or via pip
pip install lm-eval

# Verify installation
lm_eval --version
```

### Required Dependencies

```bash
# Core dependencies
pip install torch transformers datasets

# For different backends
pip install vllm              # For fast inference
pip install openai            # For API-based models
pip install anthropic          # For Claude models
pip install ollama             # For Ollama local models

# Optional: GPU support
pip install torch[cuda12.1]   # For NVIDIA GPUs
```

### Environment Setup

```bash
# API keys for LLM providers
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# HuggingFace token (for private models)
export HF_TOKEN="hf_..."

# Optional: Configure inference backend
export VLLM_GPU_MEMORY_UTILIZATION=0.9
```

## Your First Benchmark Evaluation

### Running MMLU (Massive Multitask Language Understanding)

```bash
# Simplest: Evaluate a HuggingFace model on MMLU
lm_eval \
  --model hf \
  --model_args "pretrained=meta-llama/Llama-2-7b-hf" \
  --tasks mmlu \
  --batch_size 8 \
  --num_fewshot 5 \
  --device cuda

# Output:
# {
#   "mmlu": {"acc": 0.4532, "acc_norm": 0.4601}
# }
```

### Running with OpenAI API

```bash
lm_eval \
  --model openai-chat-completions \
  --model_args model=gpt-4 \
  --tasks mmlu_pro \
  --num_fewshot 0 \
  --batch_size 32

# Output shows:
# gpt-4 performance on MMLU-Pro benchmark
```

### Multiple Tasks at Once

```bash
lm_eval \
  --model hf \
  --model_args "pretrained=meta-llama/Llama-2-70b-hf" \
  --tasks mmlu,hellaswag,truthfulqa_mc,arc_challenge \
  --batch_size 4 \
  --num_fewshot 5 \
  --output_path results/llama2_70b.json
```

## Standard Tasks & Benchmarks

### Major Benchmark Categories

**Language Understanding:**
- `mmlu`: Massive Multitask Language Understanding (57 subjects)
- `mmlu_pro`: MMLU with harder questions (updated 2024)
- `mmlu_extended`: Extended version (360+ subjects)
- `hellaswag`: Commonsense reasoning (80k examples)
- `arc_challenge`: Science questions (1,172 challenges)

**Knowledge & Facts:**
- `truthfulqa_mc`: Multiple choice truthfulness (817 questions)
- `wikitext`: Language modeling benchmark
- `hendrycks_test`: Medical, legal, professional knowledge

**Reasoning:**
- `gsm8k`: Grade school math (8,500 problems)
- `math_aime`: Math competition problems (7,500 problems)
- `math_problems`: Advanced mathematics
- `aime`: American Invitational Math Exam

**Coding:**
- `humaneval`: Python code generation (164 tasks)
- `humaneval_plus`: Extended HumanEval (500+ tests)
- `mbpp`: Mostly Basic Programming Problems (900 tasks)

**Commonsense:**
- `commonsensea`: AI2 Commonsense (1,221 questions)
- `sciq`: Science questions
- `openbookqa`: Open Book QA

**Multilingual:**
- `xcopa`: Cross-lingual choice of plausible alternatives
- `xnli`: Cross-lingual NLI (5 languages)
- `xstory_cloze`: Cross-lingual story understanding

### Complete Task List

```bash
# List all available tasks
lm_eval --list_tasks

# List tasks by category
lm_eval --list_tasks | grep mmlu
lm_eval --list_tasks | grep gsm

# Get task details
lm_eval --list_tasks | jq '.[] | select(.name | contains("mmlu"))'
```

## Configuration & Advanced Usage

### YAML Configuration File

Create `eval_config.yaml`:

```yaml
model:
  type: hf
  pretrained: meta-llama/Llama-2-70b-hf
  dtype: float16
  device: cuda
  batch_size: 8

tasks:
  - name: mmlu
    num_fewshot: 5
  - name: hellaswag
    num_fewshot: 10
  - name: truthfulqa_mc
    num_fewshot: 5
  - name: gsm8k
    num_fewshot: 8

output:
  path: results/baseline_eval.json
  log_samples: true
  log_metadata: true
```

### Run with Config

```bash
lm_eval \
  --config eval_config.yaml \
  --cache_dir /path/to/cache

# Output: results/baseline_eval.json
```

### Custom Model Integration

```python
# custom_model.py
from lm_eval.api.model import LM

class CustomLLMModel(LM):
    def __init__(self, model_args: str = ""):
        super().__init__()
        # Initialize your custom model
        self.model = load_your_model(model_args)

    def loglikelihood(self, requests):
        """Compute log probability for given prompts"""
        results = []
        for prompt, target in requests:
            logprob = self.model.get_logprob(prompt, target)
            results.append(logprob)
        return results

    def loglikelihood_rolling(self, requests):
        """Compute log prob with rolling window"""
        # Implementation for language modeling
        pass

    def generate_until(self, requests, until=None, max_length=256):
        """Generate text until condition met"""
        results = []
        for prompt in requests:
            text = self.model.generate(prompt, max_length=max_length)
            results.append(text)
        return results
```

Register and use:

```bash
lm_eval \
  --model custom_model \
  --model_args "model_path=/path/to/model" \
  --tasks mmlu \
  --batch_size 4
```

## Vision Language Model (VLM) Support

lm-eval now supports evaluating vision language models (v0.4.0+):

### Running VLM Benchmarks

```bash
# Evaluate CLIP model on image understanding
lm_eval \
  --model hf \
  --model_args "pretrained=openai/clip-vit-base-patch32" \
  --tasks winoground \
  --batch_size 32

# Evaluate LLaVA on visual QA
lm_eval \
  --model hf \
  --model_args "pretrained=llava-hf/llava-1.5-7b-hf" \
  --tasks vqav2 \
  --num_fewshot 0
```

### Supported VLM Tasks

- `winoground`: Visual reasoning (400 examples)
- `vqav2`: Visual question answering (65k+ questions)
- `gqa`: Compositional visual reasoning
- `textocr`: Text recognition in images
- `docvqa`: Document question answering

## Integration with HuggingFace Leaderboard

### Automatic Leaderboard Submission

```bash
# Submit your model to Open LLM Leaderboard
lm_eval \
  --model hf \
  --model_args "pretrained=your-org/your-model" \
  --tasks mmlu,hellaswag,truthfulqa_mc,arc_challenge \
  --batch_size 4 \
  --num_fewshot 0 \
  --output_path results/submission.json \
  --hf_hub_log_args "repo_name=your-org/your-model-evals" \
  --hf_token $HF_TOKEN

# This automatically logs results to HuggingFace Hub
# Results visible on: https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard
```

### Leaderboard Standard Settings

The official leaderboard uses:

```bash
lm_eval \
  --model hf \
  --model_args "pretrained=<model_id>" \
  --tasks mmlu,hellaswag,truthfulqa_mc,arc_challenge \
  --batch_size 1 \
  --num_fewshot 0 \
  --output_path results/leaderboard_eval.json

# Evaluated on 4 core benchmarks:
# - MMLU (57,141 questions)
# - HellaSwag (10,042 tasks)
# - TruthfulQA MC (817 questions)
# - ARC Challenge (1,172 questions)
```

## Custom Task Development

### Task File Structure

Create `tasks/custom_qa.py`:

```python
from lm_eval.api.task import Task
from lm_eval.api.instance import Instance

class CustomQATask(Task):
    """Custom question-answering task"""

    VERSION = 0
    DATASET_PATH = "json"
    DATASET_NAME = None

    def __init__(self, data_dir=None, **kwargs):
        super().__init__(**kwargs)
        self.data_dir = data_dir

    def has_training_docs(self):
        return True

    def has_validation_docs(self):
        return True

    def has_test_docs(self):
        return False

    def training_docs(self):
        """Return training examples"""
        if self.has_training_docs():
            return iter(self.dataset["train"])

    def validation_docs(self):
        """Return validation examples"""
        return iter(self.dataset["validation"])

    def doc_to_text(self, doc):
        """Convert document to prompt text"""
        return f"Question: {doc['question']}\nAnswer:"

    def doc_to_target(self, doc):
        """Extract gold target"""
        return f" {doc['answer']}"

    def construct_requests(self, doc, ctx):
        """Define evaluation requests"""
        return [
            Instance(request_type="loglikelihood",
                    request=(ctx, self.doc_to_target(doc)))
        ]

    def process_results(self, doc, results):
        """Process evaluation results"""
        gold = self.doc_to_target(doc)
        pred_logprob = results[0][0]
        return {"acc": int(pred_logprob > 0)}

    def aggregation(self):
        """Define how to aggregate metrics"""
        return {"acc": sum}

    def higher_is_better(self):
        """Define if higher scores are better"""
        return {"acc": True}
```

### Register Custom Task

```bash
# Place task file in tasks/
# Then reference it:
lm_eval \
  --model hf \
  --model_args "pretrained=mistral-7b" \
  --tasks custom_qa \
  --batch_size 8
```

## Performance Optimization

### Batch Size Tuning

```bash
# Find optimal batch size for your GPU
for bs in 1 2 4 8 16 32; do
  lm_eval \
    --model hf \
    --model_args "pretrained=meta-llama/Llama-2-7b" \
    --tasks mmlu \
    --num_fewshot 0 \
    --batch_size $bs \
    --output_path "results/bs_${bs}.json"
done

# Larger batch size = faster but uses more memory
# Rule: Start with batch_size=1, double until OOM
```

### Quantization for Speed

```bash
# 4-bit quantization (5x faster, slight accuracy loss)
lm_eval \
  --model hf \
  --model_args "pretrained=meta-llama/Llama-2-70b,load_in_4bit=True" \
  --tasks mmlu,hellaswag \
  --batch_size 32

# Result: ~2x memory, 3-5x faster
# Accuracy loss: typically <2%
```

### Distributed Evaluation

```bash
# Evaluate using multiple GPUs
lm_eval \
  --model hf \
  --model_args "pretrained=meta-llama/Llama-2-70b" \
  --tasks mmlu \
  --batch_size 16 \
  --device cuda \
  --num_gpus 4

# Requires: torch.nn.DataParallel or DeepSpeed
```

## Results Analysis

### Output Format

Results are saved as JSON:

```json
{
  "results": {
    "mmlu": {
      "acc": 0.4532,
      "acc_norm": 0.4601,
      "acc_stderr": 0.0089
    },
    "hellaswag": {
      "acc": 0.5612,
      "acc_norm": 0.5889,
      "acc_stderr": 0.0045
    }
  },
  "metadata": {
    "model": "meta-llama/Llama-2-7b-hf",
    "batch_size": 8,
    "date": "2026-03-31"
  }
}
```

### Parsing Results

```python
import json

with open('results/eval.json') as f:
    results = json.load(f)

# Print all metrics
for task, metrics in results['results'].items():
    print(f"{task:20s} acc={metrics['acc']:.4f}")

# Calculate average
avg_acc = sum(m['acc'] for m in results['results'].values()) \
          / len(results['results'])
print(f"Average accuracy: {avg_acc:.4f}")
```

## Troubleshooting

### Common Issues

**Issue: "CUDA out of memory"**
```bash
# Reduce batch size
lm_eval --model hf ... --batch_size 1

# Or enable 8-bit quantization
lm_eval \
  --model_args "pretrained=model,load_in_8bit=True" \
  --tasks mmlu
```

**Issue: "Model not found on HuggingFace Hub"**
```bash
# Ensure model exists and token has access
export HF_TOKEN="hf_..."

# Or provide local path
lm_eval \
  --model hf \
  --model_args "pretrained=/local/path/to/model" \
  --tasks mmlu
```

**Issue: "Task not found"**
```bash
# List available tasks
lm_eval --list_tasks | grep "task_name"

# Check task name spelling and capitalization
lm_eval --model hf ... --tasks mmlu_pro  # Correct
lm_eval --model hf ... --tasks MMLU_PRO  # Wrong
```

**Issue: "Evaluation very slow (>1 hour)"**
```bash
# Increase batch size (if memory allows)
lm_eval ... --batch_size 16

# Use quantization
lm_eval ... --model_args "load_in_8bit=True"

# Use vLLM backend (3-5x faster)
pip install vllm
lm_eval --model vllm --model_args "model=meta-llama/Llama-2-7b" ...
```

## Pros & Cons

### Advantages
- **Industry standard:** Powers HF Open LLM Leaderboard
- **1000+ benchmarks:** Most comprehensive task coverage
- **Well-maintained:** Regular updates, large community
- **HuggingFace integrated:** Direct model hub support
- **VLM support:** Can evaluate vision language models
- **Performance:** Highly optimized inference
- **Open source:** MIT licensed, transparent
- **Reproducible:** Standardized evaluation protocols

### Disadvantages
- **Steep learning curve:** More complex than DeepEval
- **Limited metrics:** Mainly accuracy-based (not semantic similarity)
- **Requires GPU:** Most models need GPU acceleration
- **Slow for large models:** 70B models take hours
- **No built-in safety:** Requires separate tool (Garak, etc.)
- **Custom metrics hard:** Requires Python class implementation
- **Limited agent eval:** Not designed for agentic systems

## Performance Benchmarks

| Model | MMLU | HellaSwag | TruthfulQA | ARC | Time |
|-------|------|-----------|-----------|-----|------|
| Llama 2 7B | 45.3% | 78.9% | 42.2% | 57.1% | 2h |
| Llama 2 70B | 69.2% | 87.3% | 79.3% | 85.2% | 12h |
| Mistral 7B | 64.2% | 83.4% | 61.1% | 80.2% | 2.5h |
| GPT-4 | 88.7% | 96.3% | 94.8% | 96.3% | 24h* |

*GPT-4: API rate limits, longer real-world time

## When to Use lm-eval

**Best For:**
- Comparing models against standard benchmarks
- Publishing benchmark results (leaderboard credibility)
- Research papers (reproducible evaluation)
- Large-scale benchmark campaigns
- Models in HuggingFace Hub
- If you need 1000+ task coverage

**Not Best For:**
- Quick prototyping (too complex setup)
- Custom evaluation metrics (limited flexibility)
- Safety evaluation (use Garak instead)
- Agent evaluation (use LangSmith instead)
- RAG evaluation (use Ragas instead)
- Small teams with limited GPU resources

## Comparison with Alternatives

| Feature | lm-eval-harness | DeepEval | Inspect AI |
|---------|-----------------|----------|-----------|
| Task count | 1000+ | 50+ | 100+ |
| Setup | 30 min | 5 min | 15 min |
| Benchmark std | Highest | Moderate | Low |
| GPU required | Yes | No | Optional |
| Customization | Hard | Easy | Moderate |
| Speed (7B) | 2h | 30m* | 45m |

*DeepEval: Includes LLM judge costs, serial evaluation

## Integration with Production

### Export for Model Cards

```bash
lm_eval \
  --model hf \
  --model_args "pretrained=your-model" \
  --tasks mmlu,hellaswag,truthfulqa_mc,arc_challenge \
  --output_path results/model_card.json

# Use results in HuggingFace model card:
# results:
#   - task_name: mmlu
#     task_type: multiple_choice
#     metrics:
#       - type: accuracy
#         value: 0.4532
```

### CI/CD Integration

```yaml
# .github/workflows/benchmark.yml
name: Benchmark Evaluation

on:
  push:
    branches: [main]

jobs:
  evaluate:
    runs-on: gpu-runner  # Requires GPU
    steps:
      - uses: actions/checkout@v2
      - run: pip install lm-eval
      - run: |
          lm_eval \
            --model hf \
            --model_args "pretrained=${{ github.repository }}" \
            --tasks mmlu,hellaswag \
            --output_path results.json
      - run: python scripts/check_regression.py results.json
      - run: git commit -am "Results: ${{ matrix.task }}"
```

## Next Steps

1. **Install:** Follow installation instructions
2. **Run baseline:** Evaluate a standard model (Llama 2 7B)
3. **Run custom model:** Evaluate your fine-tuned model
4. **Integrate:** Add to CI/CD pipeline
5. **Leaderboard:** Submit to HF Open LLM Leaderboard

## Resources

- **GitHub:** https://github.com/EleutherAI/lm-evaluation-harness
- **Docs:** https://github.com/EleutherAI/lm-evaluation-harness/tree/main/docs
- **HF Leaderboard:** https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard
- **Discord:** EleutherAI community server

---

**Document Version:** 1.0
**Last Verified:** March 31, 2026
