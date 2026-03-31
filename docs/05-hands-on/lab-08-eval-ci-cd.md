# Lab 08: Integrating Evals into CI/CD

**Difficulty:** Yellow (Intermediate)
**Duration:** 60 minutes
**Tools:** GitHub Actions, pytest, DeepEval, Python
**Prerequisites:** Lab 01-03, familiarity with Git and GitHub

## Overview

This lab teaches you to integrate LLM evaluations into GitHub Actions CI/CD pipelines with automated quality gates, cost budgets, and Slack notifications. You will create pytest-based test files using DeepEval framework, configure GitHub Actions workflows, set pass/fail thresholds, track evaluation costs, and receive notifications when quality drops below acceptable levels.

## Learning Objectives

By the end of this lab, you will:

1. **Write pytest tests** using DeepEval for LLM evaluation
2. **Configure GitHub Actions workflows** for automated evaluation
3. **Implement quality gates** with pass/fail thresholds
4. **Track evaluation costs** per model and deployment
5. **Send Slack notifications** for quality regressions
6. **Integrate regression detection** for model comparisons

## Part 1: Setup and Installation

Create the project structure:

```python
# setup.py
"""
Setup for CI/CD evaluation integration.
"""

import subprocess
import sys

def install_dependencies():
    """Install required packages."""

    packages = [
        "pytest==7.4.0",
        "pytest-asyncio==0.21.1",
        "deepeval==0.20.0",
        "openai==1.3.0",
        "anthropic==0.7.0",
        "python-dotenv==1.0.0",
        "requests==2.31.0"
    ]

    for package in packages:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    print("All dependencies installed.")

def create_project_structure():
    """Create project structure for CI/CD integration."""

    import os

    dirs = [
        "tests/evals",
        "tests/fixtures",
        "config",
        ".github/workflows"
    ]

    for d in dirs:
        os.makedirs(d, exist_ok=True)
        print(f"Created directory: {d}")

if __name__ == "__main__":
    create_project_structure()
    print("\nProject structure created. Run 'install_dependencies()' to install packages.")
```

## Part 2: Create DeepEval Test Suite

```python
# tests/evals/test_model_quality.py
"""
Pytest-based evaluation tests using DeepEval.
Integrates with GitHub Actions for automated quality gates.
"""

import os
import pytest
from typing import List
import json
from deepeval import evaluate
from deepeval.metrics import Faithfulness, Relevance, Coherence, AnswerRelevancy
from deepeval.test_case import LLMTestCase

# Configuration
PASS_THRESHOLD = 0.75  # 75% pass rate required
PRODUCTION_THRESHOLD = 0.85  # 85% for production deployment
COST_BUDGET_PER_EVAL = 0.05  # $0.05 per evaluation max
COST_BUDGET_TOTAL = 25.00  # $25 total budget per run

class ModelQualityGates:
    """Define quality gates for different models."""

    gates = {
        "gpt-4o": {
            "accuracy_threshold": 0.85,
            "latency_threshold": 5.0,  # seconds
            "cost_per_1k_tokens": 0.015
        },
        "claude-sonnet-4.6": {
            "accuracy_threshold": 0.88,
            "latency_threshold": 4.0,
            "cost_per_1k_tokens": 0.012
        },
        "gemini-3-flash": {
            "accuracy_threshold": 0.80,
            "latency_threshold": 3.0,
            "cost_per_1k_tokens": 0.008
        }
    }

@pytest.fixture
def test_cases() -> List[LLMTestCase]:
    """Load test cases for evaluation."""

    return [
        LLMTestCase(
            input="What is the capital of France?",
            expected_output="Paris",
            actual_output="Paris is the capital of France"
        ),
        LLMTestCase(
            input="Explain quantum entanglement in simple terms",
            expected_output="Quantum entanglement is when two particles are connected such that the state of one instantly affects the other",
            actual_output="Quantum entanglement occurs when particles become correlated in such a way that measuring one instantly determines the state of the other, regardless of distance"
        ),
        LLMTestCase(
            input="What are the benefits of machine learning?",
            expected_output="Benefits include automation, improved accuracy, handling large datasets, and pattern recognition",
            actual_output="Machine learning enables systems to: 1) Automate repetitive tasks, 2) Improve accuracy through data-driven insights, 3) Process massive datasets, 4) Discover hidden patterns, 5) Adapt to new information"
        ),
        LLMTestCase(
            input="Describe the water cycle",
            expected_output="Evaporation, condensation, and precipitation",
            actual_output="The water cycle consists of evaporation (water from Earth's surface turning into vapor), condensation (vapor turning into clouds), and precipitation (water falling as rain or snow)"
        ),
        LLMTestCase(
            input="What is photosynthesis?",
            expected_output="Process where plants convert sunlight into chemical energy",
            actual_output="Photosynthesis is the process by which plants, algae, and some bacteria convert light energy into chemical energy stored in glucose, using carbon dioxide and water"
        )
    ]

class TestModelAccuracy:
    """Test model accuracy against quality gates."""

    @pytest.mark.parametrize("model_name", ["gpt-4o", "claude-sonnet-4.6", "gemini-3-flash"])
    def test_accuracy_threshold(self, model_name: str, test_cases: List[LLMTestCase]):
        """Test that model accuracy meets threshold."""

        gate = ModelQualityGates.gates[model_name]
        threshold = gate["accuracy_threshold"]

        # Simulate model accuracy (in production, evaluate real model)
        if model_name == "gpt-4o":
            accuracy = 0.87
        elif model_name == "claude-sonnet-4.6":
            accuracy = 0.90
        else:
            accuracy = 0.82

        assert accuracy >= threshold, \
            f"{model_name} accuracy {accuracy:.2%} below threshold {threshold:.2%}"

        # Record metric for CI/CD
        pytest.results = getattr(pytest, 'results', {})
        pytest.results[f"{model_name}_accuracy"] = accuracy

    def test_faithfulness_score(self, test_cases: List[LLMTestCase]):
        """Test response faithfulness to source material."""

        faithfulness = Faithfulness()
        score = faithfulness.measure(test_cases[0])

        assert score > 0.7, f"Faithfulness score {score:.2f} below threshold 0.7"

    def test_relevance_score(self, test_cases: List[LLMTestCase]):
        """Test response relevance to question."""

        relevance = Relevance()
        score = relevance.measure(test_cases[0])

        assert score > 0.75, f"Relevance score {score:.2f} below threshold 0.75"

    def test_coherence_score(self, test_cases: List[LLMTestCase]):
        """Test response coherence."""

        coherence = Coherence()
        score = coherence.measure(test_cases[0])

        assert score > 0.80, f"Coherence score {score:.2f} below threshold 0.80"

class TestModelPerformance:
    """Test model performance metrics."""

    @pytest.mark.parametrize("model_name", ["gpt-4o", "claude-sonnet-4.6"])
    def test_pass_rate(self, model_name: str):
        """Test that model passes minimum number of cases."""

        # Simulate pass rate (in production, count actual passes)
        if model_name == "gpt-4o":
            pass_rate = 0.92
        else:
            pass_rate = 0.95

        required_pass_rate = PASS_THRESHOLD
        assert pass_rate >= required_pass_rate, \
            f"{model_name} pass rate {pass_rate:.1%} below {required_pass_rate:.1%}"

    @pytest.mark.parametrize("model_name", ["gpt-4o", "claude-sonnet-4.6"])
    def test_latency_requirement(self, model_name: str):
        """Test that model responds within latency requirement."""

        gate = ModelQualityGates.gates[model_name]
        max_latency = gate["latency_threshold"]

        # Simulate latency measurement (in production, measure actual)
        if model_name == "gpt-4o":
            latency = 2.5
        else:
            latency = 1.8

        assert latency <= max_latency, \
            f"{model_name} latency {latency:.2f}s exceeds {max_latency}s"

    def test_cost_per_evaluation(self):
        """Test that evaluation cost stays within budget."""

        # Simulate cost calculation
        input_tokens = 150
        output_tokens = 200
        cost_per_1k_input = 0.003
        cost_per_1k_output = 0.006

        cost = (input_tokens / 1000 * cost_per_1k_input +
               output_tokens / 1000 * cost_per_1k_output)

        assert cost <= COST_BUDGET_PER_EVAL, \
            f"Cost ${cost:.4f} exceeds budget ${COST_BUDGET_PER_EVAL}"

class TestRegressionDetection:
    """Test for model quality regression."""

    def test_no_regression_from_baseline(self):
        """
        Test that current model performance doesn't regress significantly
        from last deployment baseline.

        Requires: baseline_results.json from previous deployment
        """

        baseline_file = "baseline_results.json"

        # Load baseline (if exists)
        try:
            with open(baseline_file, 'r') as f:
                baseline = json.load(f)
        except FileNotFoundError:
            pytest.skip("No baseline results found; creating first baseline")
            return

        current_accuracy = 0.87  # Simulate current eval result
        baseline_accuracy = baseline.get("accuracy", 0.88)

        regression_threshold = 0.05  # 5% degradation threshold
        assert current_accuracy >= (baseline_accuracy - regression_threshold), \
            f"Regression detected: {baseline_accuracy:.2%} -> {current_accuracy:.2%}"

    def test_improvement_over_previous_model(self):
        """Test that new model version improves over previous."""

        previous_version_accuracy = 0.85
        current_version_accuracy = 0.87

        improvement = current_version_accuracy - previous_version_accuracy
        assert improvement >= 0, \
            f"New version {current_version_accuracy:.2%} worse than previous {previous_version_accuracy:.2%}"

class TestCostTracking:
    """Track evaluation costs across models."""

    @pytest.fixture(autouse=True)
    def cost_tracker(self):
        """Initialize cost tracking."""

        self.cost_breakdown = {
            "gpt-4o": 0.0,
            "claude-sonnet-4.6": 0.0,
            "gemini-3-flash": 0.0
        }

    def test_total_cost_within_budget(self):
        """Test that total evaluation cost stays within budget."""

        # Simulate costs
        costs = {
            "gpt-4o": 8.50,
            "claude-sonnet-4.6": 7.20,
            "gemini-3-flash": 3.15
        }

        total_cost = sum(costs.values())

        assert total_cost <= COST_BUDGET_TOTAL, \
            f"Total cost ${total_cost:.2f} exceeds budget ${COST_BUDGET_TOTAL}"

        # Log cost breakdown
        print("\nCost Breakdown:")
        for model, cost in costs.items():
            print(f"  {model}: ${cost:.2f}")
        print(f"  Total: ${total_cost:.2f} / ${COST_BUDGET_TOTAL}")

def pytest_configure(config):
    """Configure pytest with custom markers."""

    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "quality_gate: mark test as quality gate check"
    )
    config.addinivalue_line(
        "markers", "cost: mark test as cost tracking"
    )

def pytest_runtest_logreport(report):
    """Custom logging for test results."""

    if report.when == "call":
        if report.outcome == "passed":
            print(f"✓ {report.nodeid}")
        elif report.outcome == "failed":
            print(f"✗ {report.nodeid}")
```

## Part 3: GitHub Actions Workflow

Create the GitHub Actions configuration:

```yaml
# .github/workflows/eval-ci-cd.yml
name: LLM Evaluation CI/CD

on:
  push:
    branches: [main, develop]
    paths:
      - 'src/**'
      - 'tests/**'
      - '.github/workflows/eval-ci-cd.yml'
  pull_request:
    branches: [main, develop]
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'

env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  GOOGLE_API_KEY: ${{ secrets.GOOGLE_API_KEY }}
  SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

jobs:
  evaluate:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11']
      fail-fast: false

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0  # Full history for regression detection

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: 'pip'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-json-report

    - name: Run evaluation tests
      id: eval_tests
      run: |
        pytest tests/evals/ \
          --cov=src \
          --cov-report=html \
          --json-report --json-report-file=eval-report.json \
          -v \
          --tb=short
      continue-on-error: true

    - name: Parse evaluation results
      id: parse_results
      run: |
        python scripts/parse_eval_results.py eval-report.json

    - name: Check quality gates
      id: quality_gates
      run: |
        python scripts/check_quality_gates.py \
          --baseline baseline_results.json \
          --current eval-report.json \
          --threshold 0.75
      continue-on-error: true

    - name: Track costs
      id: cost_tracking
      run: |
        python scripts/track_evaluation_costs.py eval-report.json

    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
        flags: evaluation
        name: eval-coverage

    - name: Generate evaluation report
      if: always()
      run: |
        python scripts/generate_eval_report.py \
          --eval-results eval-report.json \
          --cost-summary cost_summary.json \
          --output eval_report.md

    - name: Comment PR with results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v7
      with:
        script: |
          const fs = require('fs');
          const report = fs.readFileSync('eval_report.md', 'utf8');
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: report
          });

    - name: Update baseline on success
      if: success() && github.ref == 'refs/heads/main'
      run: |
        cp eval-report.json baseline_results.json
        git config user.name "GitHub Actions"
        git config user.email "actions@github.com"
        git add baseline_results.json
        git commit -m "Update evaluation baseline" || true
        git push origin main || true

    - name: Send Slack notification on failure
      if: failure()
      uses: slackapi/slack-github-action@v1.24.0
      with:
        webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
        payload: |
          {
            "text": "⚠️ LLM Evaluation CI/CD Failed",
            "blocks": [
              {
                "type": "header",
                "text": {
                  "type": "plain_text",
                  "text": "Evaluation Quality Gate Failure"
                }
              },
              {
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "*Repository*: ${{ github.repository }}\n*Branch*: ${{ github.ref }}\n*Commit*: ${{ github.sha }}\n*Actor*: ${{ github.actor }}"
                }
              },
              {
                "type": "section",
                "text": {
                  "type": "mrkdwn",
                  "text": "*Details*:\n${{ steps.parse_results.outputs.failure_reason }}"
                }
              },
              {
                "type": "actions",
                "elements": [
                  {
                    "type": "button",
                    "text": {
                      "type": "plain_text",
                      "text": "View Workflow"
                    },
                    "url": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
                  }
                ]
              }
            ]
          }

    - name: Send Slack notification on success
      if: success() && github.ref == 'refs/heads/main'
      uses: slackapi/slack-github-action@v1.24.0
      with:
        webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
        payload: |
          {
            "text": "✅ LLM Evaluation Passed",
            "blocks": [
              {
                "type": "header",
                "text": {
                  "type": "plain_text",
                  "text": "Evaluation Quality Gates Passed"
                }
              },
              {
                "type": "section",
                "fields": [
                  {
                    "type": "mrkdwn",
                    "text": "*Models Evaluated*:\n3 models"
                  },
                  {
                    "type": "mrkdwn",
                    "text": "*Pass Rate*:\n92%"
                  },
                  {
                    "type": "mrkdwn",
                    "text": "*Total Cost*:\n$18.85"
                  },
                  {
                    "type": "mrkdwn",
                    "text": "*Budget*:\n$25.00"
                  }
                ]
              }
            ]
          }

  deployment-gate:
    needs: evaluate
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v4

    - name: Check production readiness
      run: |
        python scripts/check_production_readiness.py \
          --eval-results baseline_results.json \
          --threshold 0.85

    - name: Trigger deployment if ready
      if: success()
      run: |
        echo "Production deployment approved - all quality gates passed"
        # Trigger deployment to staging/production
```

## Part 4: Supporting Scripts

Create helper scripts:

```python
# scripts/parse_eval_results.py
"""
Parse pytest JSON report and extract evaluation metrics.
"""

import json
import sys
from typing import Dict

def parse_pytest_report(json_file: str) -> Dict:
    """Parse pytest JSON report."""

    with open(json_file, 'r') as f:
        report = json.load(f)

    summary = {
        'total': report['summary']['total'],
        'passed': report['summary'].get('passed', 0),
        'failed': report['summary'].get('failed', 0),
        'errors': report['summary'].get('error', 0),
        'pass_rate': report['summary'].get('passed', 0) / report['summary']['total']
    }

    return summary

def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_eval_results.py <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]
    results = parse_pytest_report(json_file)

    print(f"Pass Rate: {results['pass_rate']:.1%}")
    print(f"Passed: {results['passed']}/{results['total']}")

    # Set GitHub Actions outputs
    with open(os.environ.get('GITHUB_OUTPUT', ''), 'a') as f:
        f.write(f"pass_rate={results['pass_rate']:.2%}\n")
        f.write(f"passed={results['passed']}\n")
        f.write(f"failed={results['failed']}\n")

if __name__ == "__main__":
    main()
```

```python
# scripts/check_quality_gates.py
"""
Check model quality against defined gates.
"""

import json
import sys
import argparse

def check_gates(current_results: Dict, baseline: Dict, threshold: float) -> bool:
    """Verify quality gates are met."""

    current_pass_rate = current_results.get('pass_rate', 0)
    baseline_pass_rate = baseline.get('pass_rate', threshold)

    print(f"Current Pass Rate: {current_pass_rate:.1%}")
    print(f"Baseline Pass Rate: {baseline_pass_rate:.1%}")
    print(f"Required Threshold: {threshold:.1%}")

    if current_pass_rate >= threshold:
        print("✓ Quality gate PASSED")
        return True
    else:
        print("✗ Quality gate FAILED")
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--current', required=True)
    parser.add_argument('--baseline')
    parser.add_argument('--threshold', type=float, default=0.75)
    args = parser.parse_args()

    # Load results
    with open(args.current) as f:
        current = json.load(f)

    baseline = {}
    if args.baseline:
        try:
            with open(args.baseline) as f:
                baseline = json.load(f)
        except FileNotFoundError:
            pass

    # Check gates
    passed = check_gates(current, baseline, args.threshold)
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
```

```python
# scripts/track_evaluation_costs.py
"""
Track evaluation costs and compare against budgets.
"""

import json
import sys

def track_costs(eval_report: str) -> Dict:
    """Extract and summarize costs from evaluation report."""

    with open(eval_report) as f:
        report = json.load(f)

    # Simulate cost extraction (in production, parse actual costs)
    costs = {
        "gpt-4o": 8.50,
        "claude-sonnet-4.6": 7.20,
        "gemini-3-flash": 3.15
    }

    total = sum(costs.values())
    budget = 25.00

    print(f"\nEvaluation Cost Summary")
    print("=" * 50)
    for model, cost in costs.items():
        percentage = (cost / total) * 100
        print(f"{model:25} ${cost:6.2f} ({percentage:5.1f}%)")
    print("-" * 50)
    print(f"{'Total':25} ${total:6.2f}")
    print(f"{'Budget':25} ${budget:6.2f}")
    print(f"{'Remaining':25} ${budget - total:6.2f}")

    # Save summary
    summary = {
        "costs": costs,
        "total": total,
        "budget": budget,
        "remaining": budget - total,
        "over_budget": total > budget
    }

    with open("cost_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    return summary

if __name__ == "__main__":
    eval_report = sys.argv[1] if len(sys.argv) > 1 else "eval-report.json"
    track_costs(eval_report)
```

## Part 5: Configuration Files

Create required configuration files:

```ini
# pytest.ini
[pytest]
testpaths = tests/evals
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    integration: Integration tests
    quality_gate: Quality gate checks
    cost: Cost tracking tests
addopts = -v --tb=short --strict-markers
```

```
# requirements.txt
pytest==7.4.0
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-json-report==1.5.0
deepeval==0.20.0
openai==1.3.0
anthropic==0.7.0
google-generativeai==0.3.0
python-dotenv==1.0.0
requests==2.31.0
pydantic==2.3.0
```

## Part 6: Manual Local Testing

Before pushing to GitHub:

```bash
# Install dependencies locally
pip install -r requirements.txt

# Run evaluations locally
pytest tests/evals/ -v --cov=src

# Test with cost tracking
pytest tests/evals/test_model_quality.py::TestCostTracking -v

# Run specific quality gate
pytest tests/evals/test_model_quality.py::TestModelAccuracy -v

# Generate HTML report
pytest tests/evals/ --cov=src --cov-report=html
# Open htmlcov/index.html

# Test GitHub Actions workflow locally (requires act)
act -j evaluate
```

## Part 7: Extension - Advanced Features

Implement regression detection and model comparisons:

```python
# .github/workflows/eval-compare-models.yml
name: Compare Models in PR

on:
  pull_request:
    paths:
      - 'src/models/**'

jobs:
  compare:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Evaluate base branch
      run: |
        git checkout ${{ github.base_ref }}
        pytest tests/evals/ --json-report --json-report-file=base-report.json
        cp base-report.json /tmp/base-report.json

    - name: Evaluate PR branch
      run: |
        git checkout ${{ github.head_ref }}
        pytest tests/evals/ --json-report --json-report-file=pr-report.json

    - name: Compare results
      run: |
        python scripts/compare_model_results.py \
          --base /tmp/base-report.json \
          --pr pr-report.json

    - name: Comment comparison on PR
      uses: actions/github-script@v7
      with:
        script: |
          const fs = require('fs');
          const comparison = fs.readFileSync('model_comparison.md', 'utf8');
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: "## Model Comparison\n" + comparison
          });
```

## Summary

In this lab, you have:

1. **Created pytest-based evaluation tests** using DeepEval
2. **Configured GitHub Actions workflows** for automated evaluation
3. **Implemented quality gates** with specific thresholds
4. **Tracked evaluation costs** against budgets
5. **Integrated Slack notifications** for failures
6. **Set up baseline tracking** for regression detection
7. **Created supporting scripts** for parsing and analysis

## Key Takeaways

- Automated evaluation in CI/CD prevents regressions before production
- Quality gates enforce minimum standards and prevent bad deployments
- Cost tracking ensures economic viability of model choices
- Notifications keep teams informed of evaluation status
- Regression detection catches unexpected quality drops
- Multiple thresholds (pass vs. production) provide gradual quality progression

## Next Steps

- Deploy this workflow to your repository
- Configure Slack webhook for notifications
- Set appropriate thresholds based on your requirements
- Use results for model selection (Lab 09) and production decisions
- Monitor costs over time to optimize model choices
