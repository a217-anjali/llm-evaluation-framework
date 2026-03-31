# Lab 01: Running Your First Benchmark Suite

**Difficulty:** Green (Beginner)
**Time Estimate:** 45 minutes
**Tools:** lm-evaluation-harness, HuggingFace, Python

## Objectives

By the end of this lab, you will:
- Install and configure the lm-evaluation-harness framework
- Download and run MMLU-Pro and IFEval benchmarks on an open-weight model
- Parse and interpret benchmark results
- Compare evaluation metrics across two different models
- Create a results summary table

## Prerequisites

- Python 3.11 or higher
- 16GB RAM minimum (32GB recommended)
- GPU recommended (NVIDIA with CUDA 12.1 or higher)
- HuggingFace account with API token
- ~5GB free disk space for models
- pip and git installed

## Equipment & Environment Setup

### 1.1 Create Workspace

```bash
mkdir -p ~/llm-eval-lab && cd ~/llm-eval-lab
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 1.2 Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install lm-eval==0.4.2
pip install transformers==4.39.0
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install accelerate==0.28.0
pip install datasets==2.18.0
pip install peft==0.9.0
pip install tqdm pandas numpy scikit-learn
```

Verify installation:
```bash
lm_eval --version
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}')"
```

### 1.3 Configure HuggingFace Credentials

```bash
huggingface-cli login
# Enter your HuggingFace token when prompted
# Get token at: https://huggingface.co/settings/tokens
```

## Step-by-Step Instructions

### Step 1: Understand Available Benchmarks (5 minutes)

Create a reference script to explore available tasks:

**File: `explore_tasks.py`**
```python
#!/usr/bin/env python3
"""
Explore available tasks in lm-evaluation-harness
"""

import json
from lm_eval.tasks import get_task_dict

# Get all available tasks
try:
    tasks = get_task_dict()

    print(f"\nTotal available tasks: {len(tasks)}\n")

    # Filter for our target benchmarks
    target_benchmarks = ['mmlu_pro', 'ifeval']

    for benchmark in target_benchmarks:
        matching = [t for t in tasks.keys() if benchmark in t.lower()]
        print(f"\n{benchmark.upper()} variants:")
        for task in matching[:5]:  # Show first 5
            print(f"  - {task}")

    # Show task structure for MMLU-Pro
    if 'mmlu_pro' in tasks:
        mmlu_task = tasks['mmlu_pro']
        print(f"\nMMLA-Pro Task Details:")
        print(f"  - Type: {type(mmlu_task)}")
        print(f"  - Available attributes: {dir(mmlu_task)}")

except Exception as e:
    print(f"Error exploring tasks: {e}")
```

Run it:
```bash
python explore_tasks.py
```

Expected output:
```
Total available tasks: 200+

MMLU_PRO variants:
  - mmlu_pro
  - mmlu_pro_history
  - mmlu_pro_physics
  ...

IFEVAL variants:
  - ifeval
```

### Step 2: Download and Prepare Models (10 minutes)

We'll use two models for comparison. Qwen3.5-0.8B is small but capable; Phi-3-3.8B is slightly larger.

**File: `download_models.py`**
```python
#!/usr/bin/env python3
"""
Download and verify models for evaluation
"""

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

def download_and_verify_model(model_id, cache_dir="./model_cache"):
    """
    Download model and tokenizer, verify they work
    """
    print(f"\n{'='*60}")
    print(f"Loading: {model_id}")
    print(f"{'='*60}")

    try:
        # Download tokenizer
        print(f"Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_id,
            cache_dir=cache_dir,
            trust_remote_code=True
        )
        print(f"✓ Tokenizer loaded: {len(tokenizer)} tokens")

        # Download model (in fp16 to save memory)
        print(f"Downloading model (may take 2-5 minutes)...")
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            cache_dir=cache_dir,
            torch_dtype=torch.float16,
            device_map="auto" if torch.cuda.is_available() else "cpu",
            trust_remote_code=True
        )
        print(f"✓ Model loaded successfully")
        print(f"  - Parameters: {sum(p.numel() for p in model.parameters()) / 1e9:.2f}B")
        print(f"  - Device: {next(model.parameters()).device}")

        # Test inference
        print(f"Testing inference...")
        test_input = "The capital of France is"
        inputs = tokenizer(test_input, return_tensors="pt").to(model.device)
        with torch.no_grad():
            output = model.generate(**inputs, max_new_tokens=10)
        result = tokenizer.decode(output[0], skip_special_tokens=True)
        print(f"  Test prompt: '{test_input}'")
        print(f"  Output: '{result}'")
        print(f"✓ Inference test passed")

        return True

    except Exception as e:
        print(f"✗ Error loading {model_id}: {e}")
        return False

if __name__ == "__main__":
    models = [
        "Qwen/Qwen2.5-0.5B-Instruct",
        "microsoft/phi-3-mini-4k-instruct"
    ]

    results = {}
    for model_id in models:
        results[model_id] = download_and_verify_model(model_id)

    print(f"\n{'='*60}")
    print("Summary:")
    print(f"{'='*60}")
    for model_id, success in results.items():
        status = "✓ Ready" if success else "✗ Failed"
        print(f"{model_id}: {status}")
```

Run it:
```bash
python download_models.py
```

### Step 3: Run MMLU-Pro Benchmark (12 minutes)

**File: `run_mmlu_benchmark.py`**
```python
#!/usr/bin/env python3
"""
Run MMLU-Pro evaluation on specified models
"""

import subprocess
import json
import os
from datetime import datetime

def run_mmlu_eval(model_id, num_fewshot=5, limit=100):
    """
    Run MMLU-Pro evaluation using lm-eval

    Args:
        model_id: HuggingFace model identifier
        num_fewshot: Number of few-shot examples
        limit: Number of examples to evaluate (use subset for speed)
    """

    print(f"\n{'='*70}")
    print(f"Running MMLU-Pro on {model_id}")
    print(f"{'='*70}")
    print(f"Few-shot: {num_fewshot}")
    print(f"Sample size: {limit}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Build lm_eval command
    cmd = [
        "lm_eval",
        "--model", "hf",
        "--model_args", f"pretrained={model_id},dtype=float16",
        "--tasks", "mmlu_pro",
        "--num_fewshot", str(num_fewshot),
        "--limit", str(limit),
        "--batch_size", "auto",
        "--output_path", f"./results/{model_id.replace('/', '_')}_mmlu",
        "--log_samples",
        "--seed", "42"
    ]

    # Create output directory
    os.makedirs("./results", exist_ok=True)

    print(f"\nCommand: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)

        if result.returncode == 0:
            print(f"\n✓ MMLU-Pro evaluation completed successfully")
            return True
        else:
            print(f"\n✗ Evaluation failed with return code: {result.returncode}")
            return False

    except Exception as e:
        print(f"✗ Error running evaluation: {e}")
        return False

def run_mmlu_with_accelerate(model_id, num_fewshot=5, limit=100):
    """
    Alternative: Run with explicit device settings for better memory management
    """

    print(f"\n{'='*70}")
    print(f"Running MMLU-Pro with Accelerate: {model_id}")
    print(f"{'='*70}")

    cmd = [
        "lm_eval",
        "--model", "hf",
        "--model_args", f"pretrained={model_id},dtype=float16,device_map=auto",
        "--tasks", "mmlu_pro",
        "--num_fewshot", str(num_fewshot),
        "--batch_size", "2",  # Smaller batch for memory management
        "--limit", str(limit),
        "--output_path", f"./results/{model_id.replace('/', '_')}_mmlu_accelerate",
        "--log_samples",
        "--seed", "42"
    ]

    os.makedirs("./results", exist_ok=True)

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    # Models to evaluate
    models = [
        "Qwen/Qwen2.5-0.5B-Instruct",
        "microsoft/phi-3-mini-4k-instruct"
    ]

    print("="*70)
    print("MMLU-Pro Benchmark Runner")
    print("="*70)

    results = {}
    for model_id in models:
        # Use smaller limit (100) for quicker evaluation in lab
        success = run_mmlu_eval(model_id, num_fewshot=5, limit=100)
        results[model_id] = success

    print(f"\n{'='*70}")
    print("Evaluation Summary:")
    print(f"{'='*70}")
    for model, success in results.items():
        status = "✓ Complete" if success else "✗ Failed"
        print(f"{model}: {status}")
```

Run the benchmark:
```bash
python run_mmlu_benchmark.py
```

This will take 15-20 minutes depending on GPU. The output will be saved to `./results/` directory.

### Step 4: Run IFEval Benchmark (12 minutes)

**File: `run_ifeval_benchmark.py`**
```python
#!/usr/bin/env python3
"""
Run IFEval (Instruction Following Eval) on models
"""

import subprocess
import os
from datetime import datetime

def run_ifeval(model_id, limit=100):
    """
    Run IFEval evaluation

    Args:
        model_id: HuggingFace model identifier
        limit: Number of examples to evaluate
    """

    print(f"\n{'='*70}")
    print(f"Running IFEval on {model_id}")
    print(f"{'='*70}")
    print(f"Sample size: {limit}")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    cmd = [
        "lm_eval",
        "--model", "hf",
        "--model_args", f"pretrained={model_id},dtype=float16,device_map=auto",
        "--tasks", "ifeval",
        "--batch_size", "4",
        "--limit", str(limit),
        "--output_path", f"./results/{model_id.replace('/', '_')}_ifeval",
        "--log_samples",
        "--seed", "42"
    ]

    os.makedirs("./results", exist_ok=True)

    print(f"\nCommand: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(cmd, capture_output=False, text=True)

        if result.returncode == 0:
            print(f"\n✓ IFEval evaluation completed")
            return True
        else:
            print(f"\n✗ Evaluation failed")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    models = [
        "Qwen/Qwen2.5-0.5B-Instruct",
        "microsoft/phi-3-mini-4k-instruct"
    ]

    print("="*70)
    print("IFEval Benchmark Runner")
    print("="*70)

    for model_id in models:
        run_ifeval(model_id, limit=100)
```

Run it:
```bash
python run_ifeval_benchmark.py
```

### Step 5: Parse and Analyze Results (5 minutes)

**File: `parse_results.py`**
```python
#!/usr/bin/env python3
"""
Parse evaluation results and create comparison table
"""

import json
import os
from pathlib import Path
import pandas as pd

def load_results(results_dir="./results"):
    """
    Load all evaluation results from JSON files
    """
    results = {}

    for result_file in Path(results_dir).glob("*/results.json"):
        try:
            with open(result_file) as f:
                data = json.load(f)
                model_name = result_file.parent.name
                results[model_name] = data
        except Exception as e:
            print(f"Error loading {result_file}: {e}")

    return results

def extract_metrics(results):
    """
    Extract key metrics from evaluation results
    """
    metrics_table = []

    for model_key, result_data in results.items():
        # Parse model name and task from key
        parts = model_key.split('_')

        # Extract results
        if 'results' in result_data:
            task_results = result_data['results']

            for task_name, metrics in task_results.items():
                row = {
                    'Model': model_key.replace('_', '/'),
                    'Task': task_name,
                    'Accuracy': metrics.get('acc', metrics.get('accuracy', None)),
                    'Num Examples': result_data.get('n_docs', 'N/A'),
                }

                # Add task-specific metrics
                if 'f1' in metrics:
                    row['F1'] = metrics['f1']
                if 'macro_f1' in metrics:
                    row['Macro F1'] = metrics['macro_f1']

                metrics_table.append(row)

    return pd.DataFrame(metrics_table)

def create_comparison_table(results_df):
    """
    Create formatted comparison table
    """
    print("\n" + "="*80)
    print("EVALUATION RESULTS SUMMARY")
    print("="*80 + "\n")

    # Group by task
    for task in results_df['Task'].unique():
        task_df = results_df[results_df['Task'] == task]
        print(f"\n{task.upper()}")
        print("-" * 60)

        # Select columns to display
        display_cols = ['Model', 'Accuracy', 'Num Examples']
        if 'F1' in task_df.columns:
            display_cols.append('F1')

        display_df = task_df[display_cols].copy()
        display_df['Accuracy'] = display_df['Accuracy'].apply(
            lambda x: f"{x*100:.2f}%" if isinstance(x, float) else x
        )

        print(display_df.to_string(index=False))

    return results_df

def save_results_to_csv(results_df, filename="evaluation_summary.csv"):
    """
    Save results to CSV
    """
    results_df.to_csv(filename, index=False)
    print(f"\n✓ Results saved to {filename}")
    return filename

if __name__ == "__main__":
    print("Parsing evaluation results...\n")

    # Load results
    results = load_results("./results")

    if not results:
        print("No results found. Run evaluations first:")
        print("  python run_mmlu_benchmark.py")
        print("  python run_ifeval_benchmark.py")
    else:
        # Extract metrics
        metrics_df = extract_metrics(results)

        # Display comparison
        create_comparison_table(metrics_df)

        # Save to CSV
        save_results_to_csv(metrics_df)

        # Show detailed statistics
        print("\n" + "="*80)
        print("DETAILED STATISTICS")
        print("="*80)
        print(metrics_df.describe().to_string())
```

Run the parser:
```bash
python parse_results.py
```

### Step 6: Create Detailed Comparison Report (3 minutes)

**File: `generate_report.py`**
```python
#!/usr/bin/env python3
"""
Generate comprehensive evaluation report
"""

import json
from pathlib import Path
import pandas as pd
from datetime import datetime

def generate_html_report(results_dir="./results", output_file="evaluation_report.html"):
    """
    Generate an HTML report with results and visualizations
    """

    # Collect all metrics
    all_results = {}
    for result_file in Path(results_dir).glob("*/results.json"):
        try:
            with open(result_file) as f:
                data = json.load(f)
                all_results[result_file.parent.name] = data
        except Exception as e:
            print(f"Error loading {result_file}: {e}")

    # Build HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>LLM Evaluation Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }}
            h1, h2 {{
                color: #333;
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                background-color: white;
                margin: 20px 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }}
            th {{
                background-color: #007bff;
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .metric {{
                font-weight: bold;
                color: #007bff;
            }}
            .timestamp {{
                color: #666;
                font-size: 0.9em;
            }}
        </style>
    </head>
    <body>
        <h1>LLM Evaluation Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <h2>Overview</h2>
        <p>This report summarizes the evaluation of different language models on standard benchmarks.</p>

        <h2>Results by Model and Task</h2>
        <table>
            <tr>
                <th>Model</th>
                <th>Task</th>
                <th>Accuracy</th>
                <th>Samples Evaluated</th>
            </tr>
    """

    # Add rows
    for model_key, result_data in all_results.items():
        if 'results' in result_data:
            for task_name, metrics in result_data['results'].items():
                accuracy = metrics.get('acc', metrics.get('accuracy', 0))
                num_samples = result_data.get('n_docs', 'N/A')

                accuracy_str = f"{accuracy*100:.2f}%" if isinstance(accuracy, float) else str(accuracy)

                html_content += f"""
                <tr>
                    <td>{model_key}</td>
                    <td>{task_name}</td>
                    <td class="metric">{accuracy_str}</td>
                    <td>{num_samples}</td>
                </tr>
                """

    html_content += """
        </table>

        <h2>Interpretation Guide</h2>
        <ul>
            <li><strong>Accuracy (MMLU-Pro):</strong> Percentage of questions answered correctly in a multiple-choice format</li>
            <li><strong>Instruction Following (IFEval):</strong> Percentage of instructions correctly followed by the model</li>
            <li>Higher scores indicate better performance on these benchmarks</li>
        </ul>

        <h2>Key Observations</h2>
        <ul>
            <li>Compare which models perform best on reasoning tasks (MMLU-Pro)</li>
            <li>Compare instruction-following capabilities across models</li>
            <li>Consider model size vs. performance trade-off</li>
        </ul>
    </body>
    </html>
    """

    # Write HTML file
    with open(output_file, 'w') as f:
        f.write(html_content)

    print(f"✓ HTML report generated: {output_file}")
    print(f"  Open in browser: file://{Path(output_file).absolute()}")

if __name__ == "__main__":
    generate_html_report()
```

Run it:
```bash
python generate_report.py
```

## Expected Output

After running all evaluations, you should see:

### Console Output Example:
```
======================================================================
Running MMLU-Pro on Qwen/Qwen2.5-0.5B-Instruct
======================================================================
Few-shot: 5
Sample size: 100
Start time: 2026-03-31 10:15:23

[2026-03-31 10:15:45] Loading model...
[2026-03-31 10:16:12] Generating 100 predictions...
[2026-03-31 10:28:45] Computing metrics...

======================================================================
EVALUATION RESULTS SUMMARY
======================================================================

MMLU_PRO
------------------------------------------------------------
Model                              Accuracy    Num Examples
Qwen/Qwen2.5-0.5B-Instruct         34.50%      100
microsoft/phi-3-mini-4k-instruct   42.30%      100

IFEVAL
------------------------------------------------------------
Model                              Accuracy    Num Examples
Qwen/Qwen2.5-0.5B-Instruct         65.20%      100
microsoft/phi-3-mini-4k-instruct   71.80%      100
```

### File Structure Created:
```
results/
├── Qwen_Qwen2.5-0.5B-Instruct_mmlu/
│   └── results.json
├── microsoft_phi-3-mini-4k-instruct_mmlu/
│   └── results.json
├── Qwen_Qwen2.5-0.5B-Instruct_ifeval/
│   └── results.json
└── microsoft_phi-3-mini-4k-instruct_ifeval/
    └── results.json

evaluation_summary.csv
evaluation_report.html
```

## Interpreting Your Results

### MMLU-Pro Scores
- **Below 30%:** Model struggles with knowledge recall and reasoning
- **30-45%:** Small models performing as expected; baseline capability
- **45-65%:** Solid reasoning ability
- **65%+:** Strong knowledge and reasoning (typically 7B+ parameter models)

### IFEval Scores
- **Below 50%:** Instruction understanding needs work
- **50-70%:** Decent instruction following
- **70-85%:** Good instruction adherence
- **85%+:** Excellent instruction following

### Comparing Your Two Models:
```
Metric             Qwen2.5-0.5B    Phi-3-3.8B    Advantage
─────────────────────────────────────────────────────────
MMLU-Pro           34.50%          42.30%        Phi-3
IFEval             65.20%          71.80%        Phi-3
Parameter Count    0.5B            3.8B          Phi-3
Speed              ~200 tok/s      ~80 tok/s     Qwen
```

## Troubleshooting

### Issue: "CUDA out of memory"
**Solution:**
```python
# Reduce batch size in commands
cmd = [..., "--batch_size", "1", ...]

# Or use CPU with smaller model
cmd = [..., "--model_args", "pretrained=model_id,dtype=float32", ...]
```

### Issue: "Tokenizer not found"
**Solution:**
```bash
huggingface-cli login  # Re-authenticate
pip install --upgrade transformers
```

### Issue: Slow evaluation (minutes per example)
**Causes:**
- CPU-only execution (need GPU)
- Batch size too small
- Model too large for available VRAM

**Solutions:**
```bash
# Check GPU usage
nvidia-smi

# Use smaller model
# Change from microsoft/phi-3-mini-4k-instruct to Qwen/Qwen2.5-0.5B-Instruct

# Increase batch size if you have memory
--batch_size 8
```

### Issue: "Model not found on HuggingFace"
**Solution:**
```bash
# Verify model ID exists
python -c "from transformers import AutoModel; AutoModel.from_pretrained('exact_model_id')"
```

### Issue: Different scores on re-runs
**Cause:** Randomness in sampling with temperature > 0
**Solution:**
- Scores should be similar (within 1-2%) with seed=42
- Small variations are normal with stochastic decoding

## Extension Challenges

### Challenge 1: Run on Larger Model
**Difficulty:** 10 minutes

Try evaluating a 7B parameter model:
```bash
# Replace model ID in run_mmlu_benchmark.py with:
model_id="meta-llama/Llama-2-7b-chat-hf"

# Note: Requires 16GB+ VRAM. Use 4-bit quantization if needed:
cmd = [..., "--model_args", "pretrained=meta-llama/Llama-2-7b-chat-hf,load_in_4bit=True", ...]
```

### Challenge 2: Add Custom Task
**Difficulty:** 20 minutes

Create a simple custom benchmark:

**File: `custom_task.py`**
```python
from lm_eval.base import Task

class CustomMathTask(Task):
    DATASET_PATH = "custom"
    DATASET_NAME = "math_simple"

    def has_training_docs(self):
        return False

    def has_test_docs(self):
        return True

    def test_docs(self):
        return [
            {"question": "What is 2+2?", "answer": "4"},
            {"question": "What is 5*3?", "answer": "15"},
        ]

    def doc_to_text(self, doc):
        return f"Q: {doc['question']}\nA:"

    def doc_to_target(self, doc):
        return f" {doc['answer']}"

    def process_results(self, doc, results):
        completion = results[0].strip()
        return {"acc": completion.lower() == doc['answer'].lower()}

    def aggregation(self):
        return {"acc": mean}

    def higher_is_better(self):
        return {"acc": True}

# Run with:
# lm_eval --model hf --model_args pretrained=model_id --tasks custom_task
```

### Challenge 3: Analyze per-Subject Performance
**Difficulty:** 15 minutes

**File: `analyze_by_subject.py`**
```python
#!/usr/bin/env python3
"""
Analyze MMLU-Pro performance by subject
"""

import json
from pathlib import Path
from collections import defaultdict

def analyze_by_subject(results_file):
    """
    Break down MMLU-Pro results by subject
    """
    with open(results_file) as f:
        data = json.load(f)

    subjects = defaultdict(list)

    if 'samples' in data:
        for sample in data['samples']:
            subject = sample.get('subject', 'unknown')
            correct = sample.get('target') == sample.get('completion')
            subjects[subject].append(correct)

    print(f"\nPer-Subject Breakdown:")
    print("-" * 60)

    for subject in sorted(subjects.keys()):
        results = subjects[subject]
        accuracy = sum(results) / len(results) * 100
        print(f"{subject:30s}: {accuracy:5.2f}% ({len(results)} samples)")

    return subjects

# Usage:
results_file = Path("./results").glob("*_mmlu/results.json")
for f in results_file:
    print(f"\nAnalyzing {f.parent.name}:")
    analyze_by_subject(f)
```

Run it:
```bash
python analyze_by_subject.py
```

## Lab Completion Checklist

- [ ] Successfully installed lm-evaluation-harness
- [ ] Downloaded at least 2 models without errors
- [ ] Ran MMLU-Pro evaluation on both models
- [ ] Ran IFEval evaluation on both models
- [ ] Parsed results into CSV and HTML report
- [ ] Interpreted results (which model performed better? why?)
- [ ] Identified at least one factor affecting performance
- [ ] Completed at least one extension challenge

## Summary

In this lab, you:
1. Set up the lm-evaluation-harness framework
2. Downloaded two open-weight models
3. Ran two standard benchmarks (MMLU-Pro and IFEval)
4. Parsed and analyzed results
5. Created a comparison report

Key takeaways:
- MMLU-Pro measures factual knowledge and reasoning
- IFEval measures instruction-following ability
- Model size significantly impacts both metrics
- Benchmark results are reproducible with fixed seeds
- Trade-offs exist between speed and accuracy

**Time Spent:** Approximately 45 minutes for complete evaluation and analysis
