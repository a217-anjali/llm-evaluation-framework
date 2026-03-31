# Eval-Driven Model Selection

**Status:** Production Guide
**Date:** March 31, 2026
**Version:** 1.0

## Overview

This guide presents a systematic framework for selecting LLM models for production deployments using evaluation data. Rather than relying on benchmarks alone, this approach combines domain-specific evaluation results with business requirements to make evidence-based model selection decisions.

## Part 1: Requirements Matrix Definition

### Step 1: Define Multi-Dimensional Requirements

Create a requirements matrix with all relevant dimensions:

```python
# requirements_matrix.py
"""
Define comprehensive requirements matrix for model selection.
"""

from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

class Requirement:
    """Represents a single requirement dimension."""

    def __init__(self, name: str, constraint_type: str, threshold: float,
                 weight: float = 1.0, criticality: str = "required"):
        self.name = name
        self.constraint_type = constraint_type  # 'min', 'max', 'range'
        self.threshold = threshold
        self.weight = weight
        self.criticality = criticality  # 'required', 'important', 'nice_to_have'

    def is_met(self, value: float) -> bool:
        """Check if requirement is met."""
        if self.constraint_type == 'min':
            return value >= self.threshold
        elif self.constraint_type == 'max':
            return value <= self.threshold
        return False

class RequirementsMatrix:
    """Define requirements for model selection."""

    def __init__(self, use_case: str):
        self.use_case = use_case
        self.requirements = {}

    def add_requirement(self, requirement: Requirement):
        """Add a requirement to the matrix."""
        self.requirements[requirement.name] = requirement

    def create_customer_support(self):
        """Requirements for customer support chatbot."""

        self.add_requirement(Requirement(
            name="accuracy",
            constraint_type="min",
            threshold=85.0,
            weight=0.35,
            criticality="required"
        ))

        self.add_requirement(Requirement(
            name="latency_p95",
            constraint_type="max",
            threshold=3000,  # 3 seconds
            weight=0.25,
            criticality="required"
        ))

        self.add_requirement(Requirement(
            name="cost_per_query",
            constraint_type="max",
            threshold=0.01,  # $0.01
            weight=0.25,
            criticality="important"
        ))

        self.add_requirement(Requirement(
            name="context_window",
            constraint_type="min",
            threshold=32000,  # 32K tokens
            weight=0.10,
            criticality="important"
        ))

        self.add_requirement(Requirement(
            name="safety",
            constraint_type="min",
            threshold=0.95,  # 95% safe responses
            weight=0.05,
            criticality="required"
        ))

        return self.requirements

    def create_batch_processing(self):
        """Requirements for batch document processing."""

        self.add_requirement(Requirement(
            name="accuracy",
            constraint_type="min",
            threshold=88.0,
            weight=0.40,
            criticality="required"
        ))

        self.add_requirement(Requirement(
            name="cost_per_query",
            constraint_type="max",
            threshold=0.05,  # $0.05 per document
            weight=0.35,
            criticality="required"
        ))

        self.add_requirement(Requirement(
            name="latency_p95",
            constraint_type="max",
            threshold=60000,  # 60 seconds, batch is not real-time
            weight=0.10,
            criticality="important"
        ))

        self.add_requirement(Requirement(
            name="context_window",
            constraint_type="min",
            threshold=100000,  # 100K tokens for long documents
            weight=0.15,
            criticality="required"
        ))

        return self.requirements

    def create_real_time_classification(self):
        """Requirements for real-time classification."""

        self.add_requirement(Requirement(
            name="latency_p95",
            constraint_type="max",
            threshold=200,  # 200ms
            weight=0.40,
            criticality="required"
        ))

        self.add_requirement(Requirement(
            name="accuracy",
            constraint_type="min",
            threshold=80.0,
            weight=0.35,
            criticality="required"
        ))

        self.add_requirement(Requirement(
            name="cost_per_query",
            constraint_type="max",
            threshold=0.001,  # $0.001 due to high volume
            weight=0.20,
            criticality="important"
        ))

        self.add_requirement(Requirement(
            name="availability",
            constraint_type="min",
            threshold=0.999,  # 99.9% uptime
            weight=0.05,
            criticality="required"
        ))

        return self.requirements

    def evaluate_candidate(self, model_metrics: Dict) -> Dict:
        """Evaluate if candidate meets all requirements."""

        evaluation = {
            'model': model_metrics.get('name'),
            'meets_required': True,
            'details': {}
        }

        for req_name, requirement in self.requirements.items():
            value = model_metrics.get(req_name)

            if value is None:
                evaluation['details'][req_name] = {
                    'status': 'unknown',
                    'value': None,
                    'requirement': requirement.threshold,
                    'met': None
                }
                continue

            is_met = requirement.is_met(value)
            evaluation['details'][req_name] = {
                'status': 'met' if is_met else 'failed',
                'value': value,
                'requirement': requirement.threshold,
                'met': is_met
            }

            if not is_met and requirement.criticality == "required":
                evaluation['meets_required'] = False

        return evaluation
```

### Step 2: Define Business Requirements

Beyond technical metrics, define business constraints:

```python
class BusinessRequirements:
    """Business constraints for model selection."""

    def __init__(self):
        self.max_monthly_budget = 100000  # $100k/month
        self.max_vendor_count = 3  # Avoid too many vendors
        self.min_vendor_stability = 3  # Companies in business for 3+ years
        self.required_sla = 0.999  # 99.9% uptime
        self.data_residency = "US"  # Must be US-hosted
        self.compliance = ["SOC2", "HIPAA"]  # Required certifications

    def evaluate(self, model_profile: Dict) -> Dict:
        """Check business requirements."""

        checks = {
            'monthly_cost': model_profile.get('monthly_cost', 0) <= self.max_monthly_budget,
            'vendor_stability': model_profile.get('vendor_years', 0) >= self.min_vendor_stability,
            'availability_sla': model_profile.get('sla', 0) >= self.required_sla,
            'data_residency': model_profile.get('region', '') == self.data_residency,
            'compliance': all(c in model_profile.get('certifications', [])
                            for c in self.compliance)
        }

        return {
            'all_met': all(checks.values()),
            'details': checks
        }
```

## Part 2: Multi-Stage Evaluation Process

### Stage 1: Screening

Filter candidates that meet minimum requirements:

```python
class ScreeningStage:
    """Initial screening phase."""

    @staticmethod
    def screen_candidates(candidates: List[Dict],
                         requirements: RequirementsMatrix) -> List[Dict]:
        """
        Screening: Filter candidates meeting basic requirements.

        Eliminates candidates that fail required constraints.
        """

        passed_screening = []

        for candidate in candidates:
            evaluation = requirements.evaluate_candidate(candidate)

            if evaluation['meets_required']:
                # Candidate passed screening
                passed_screening.append({
                    'model': candidate.get('name'),
                    'reason_for_screening': 'Passed',
                    'metrics': candidate
                })
            else:
                # Document why it failed
                failures = [req for req, details in evaluation['details'].items()
                           if not details['met']]
                print(f"Screening failed for {candidate.get('name')}: {failures}")

        return passed_screening
```

### Stage 2: Shortlist

Rank remaining candidates and create shortlist:

```python
class ShortlistStage:
    """Shortlist top candidates for detailed evaluation."""

    @staticmethod
    def rank_candidates(candidates: List[Dict],
                       requirements: RequirementsMatrix) -> List[Dict]:
        """
        Rank candidates by weighted requirements.

        Computes aggregate score across all requirements.
        """

        scores = []

        for candidate in candidates:
            evaluation = requirements.evaluate_candidate(candidate)
            weighted_score = 0
            total_weight = 0

            for req_name, requirement in requirements.requirements.items():
                if req_name in evaluation['details']:
                    detail = evaluation['details'][req_name]
                    value = detail['value']
                    threshold = detail['requirement']

                    if value is not None:
                        # Normalize value to 0-1 scale
                        if requirement.constraint_type == 'min':
                            # Higher is better
                            norm_value = min(1.0, value / threshold)
                        else:
                            # Lower is better
                            norm_value = min(1.0, threshold / value) if value > 0 else 0

                        weighted_score += norm_value * requirement.weight
                        total_weight += requirement.weight

            # Final score
            final_score = weighted_score / total_weight if total_weight > 0 else 0

            scores.append({
                'model': candidate.get('name'),
                'score': final_score,
                'metrics': candidate
            })

        # Sort by score descending
        scores = sorted(scores, key=lambda x: x['score'], reverse=True)

        return scores

    @staticmethod
    def create_shortlist(ranked: List[Dict], count: int = 3) -> List[Dict]:
        """Create shortlist of top N candidates."""
        return ranked[:count]
```

### Stage 3: Deep Evaluation

Conduct detailed evaluation on shortlisted models:

```python
class DeepEvaluationStage:
    """Detailed evaluation of shortlisted candidates."""

    @staticmethod
    def run_domain_eval(model: str, test_cases: List[Dict]) -> Dict:
        """Run domain-specific evaluation on shortlisted model."""

        # Simulated evaluation (in production, run actual eval)
        accuracy = 0.87
        completeness = 0.85
        latency_p95 = 2800  # ms

        return {
            'model': model,
            'accuracy': accuracy,
            'completeness': completeness,
            'latency_p95': latency_p95,
            'error_cases': [],  # Detailed error analysis
            'edge_cases': []  # Edge cases found
        }

    @staticmethod
    def run_production_simulation(model: str, traffic_pattern: Dict) -> Dict:
        """Simulate production load to test behavior."""

        return {
            'model': model,
            'throughput_sustained': 1000,  # QPS
            'error_rate': 0.001,  # 0.1%
            'cost_at_scale': 15000,  # Monthly cost at expected volume
            'p99_latency': 5000  # ms
        }

    @staticmethod
    def conduct_security_audit(model: str) -> Dict:
        """Security and safety assessment."""

        return {
            'model': model,
            'injection_resistance': True,
            'jailbreak_resistance': 0.98,
            'pii_handling': 'compliant',
            'safety_score': 0.96,
            'audit_notes': []
        }

    @staticmethod
    def create_deep_eval_report(shortlisted: List[Dict]) -> str:
        """Create comprehensive deep evaluation report."""

        report = []
        report.append("=" * 100)
        report.append("DEEP EVALUATION REPORT - SHORTLISTED MODELS")
        report.append("=" * 100)

        for model_info in shortlisted:
            model = model_info['model']
            report.append(f"\n{model}")
            report.append("-" * 100)

            # Run evaluations
            domain_eval = DeepEvaluationStage.run_domain_eval(model, [])
            prod_sim = DeepEvaluationStage.run_production_simulation(model, {})
            security = DeepEvaluationStage.conduct_security_audit(model)

            report.append(f"Domain-Specific Accuracy: {domain_eval['accuracy']:.1%}")
            report.append(f"Production P99 Latency: {prod_sim['p99_latency']}ms")
            report.append(f"Estimated Monthly Cost at Scale: ${prod_sim['cost_at_scale']:,.0f}")
            report.append(f"Safety Score: {security['safety_score']:.1%}")

        return "\n".join(report)
```

### Stage 4: Production Pilot

Deploy finalist to production with monitoring:

```python
class ProductionPilotStage:
    """Deploy selected model to production for validation."""

    @staticmethod
    def setup_canary_deployment(model: str, traffic_percentage: float = 0.10) -> Dict:
        """
        Deploy model as canary with small traffic percentage.

        Allows real-world validation before full rollout.
        """

        deployment = {
            'model': model,
            'traffic_percentage': traffic_percentage,
            'monitoring_metrics': [
                'accuracy',
                'latency_p50',
                'latency_p95',
                'latency_p99',
                'error_rate',
                'cost_per_query',
                'user_satisfaction'
            ],
            'success_criteria': {
                'accuracy': 0.85,  # Must meet 85% accuracy
                'error_rate': 0.02,  # <2% errors
                'latency_p95': 3000,  # <3 seconds p95
                'cost_per_query': 0.010  # <$0.01
            },
            'duration_hours': 24,  # Monitor for 24 hours
            'rollback_trigger': 'automated on any critical failure'
        }

        return deployment

    @staticmethod
    def monitor_pilot(metrics: Dict) -> Dict:
        """Monitor pilot performance."""

        evaluation = {
            'passed': True,
            'details': {}
        }

        thresholds = {
            'accuracy': ('>=', 0.85),
            'error_rate': ('<=', 0.02),
            'latency_p95': ('<=', 3000)
        }

        for metric, (op, threshold) in thresholds.items():
            value = metrics.get(metric)
            if value is not None:
                if op == '>=':
                    passed = value >= threshold
                else:
                    passed = value <= threshold

                evaluation['details'][metric] = {
                    'value': value,
                    'threshold': threshold,
                    'passed': passed
                }

                if not passed:
                    evaluation['passed'] = False

        return evaluation
```

## Part 3: Case Study - Customer Support Chatbot

### Scenario

SelectCorp wants to deploy an LLM-powered customer support chatbot with these requirements:

- Serve 100,000 messages/month
- Maximum $8,000/month budget
- <3 second response latency (p95)
- 85%+ accuracy on support interactions
- Must be available 24/7 (99.9% uptime)

### Candidates

```python
candidates = [
    {
        'name': 'GPT-4o',
        'accuracy': 0.89,
        'latency_p95': 2500,
        'cost_per_query': 0.0085,
        'monthly_cost': 850,  # 100k queries * $0.0085
        'sla': 0.9999,
        'safety': 0.98
    },
    {
        'name': 'Claude-Sonnet-4.6',
        'accuracy': 0.91,
        'latency_p95': 3200,
        'cost_per_query': 0.0068,
        'monthly_cost': 680,
        'sla': 0.999,
        'safety': 0.99
    },
    {
        'name': 'Gemini-3-Flash',
        'accuracy': 0.85,
        'latency_p95': 1800,
        'cost_per_query': 0.0012,
        'monthly_cost': 120,
        'sla': 0.999,
        'safety': 0.94
    },
    {
        'name': 'Qwen-3.5-9B (self-hosted)',
        'accuracy': 0.76,
        'latency_p95': 1200,
        'cost_per_query': 0.0003,
        'monthly_cost': 30,  # Mostly infrastructure
        'sla': 0.95,
        'safety': 0.85
    }
]
```

### Selection Process

**Stage 1: Screening**
- GPT-4o: PASS (meets accuracy, latency, budget)
- Claude-Sonnet-4.6: PASS (meets all requirements)
- Gemini-3-Flash: PASS (very low cost)
- Qwen-3.5-9B: FAIL (accuracy 76% < 85% requirement)

**Stage 2: Shortlist**
Rank by weighted score:
1. Claude-Sonnet-4.6 (0.92 score)
2. GPT-4o (0.89 score)
3. Gemini-3-Flash (0.82 score)

**Stage 3: Deep Evaluation**
- Claude-Sonnet-4.6: Domain eval 91% accuracy, real-world simulation shows excellent performance on customer queries, safety score 99%
- GPT-4o: Similar performance but higher cost
- Gemini-3-Flash: Good speed but slightly lower accuracy (85%)

**Stage 4: Production Pilot**
Deploy Claude-Sonnet-4.6 as canary with 10% traffic for 24 hours.

**Result:** Claude-Sonnet-4.6 selected for production deployment.

## Part 4: When to Use Frontier vs Open-Weight Models

### Frontier Models (GPT-4, Claude, Gemini)

**Use when:**
- Accuracy is critical (>85% required)
- Complex reasoning needed
- Supporting novel use cases
- Safety/compliance essential
- Can justify cost

**Examples:**
- Customer support complex escalations
- Legal document analysis
- Medical diagnostic support
- Financial analysis

**Budget:** $5k-100k+/month depending on scale

### Open-Weight Models (Llama, Qwen, Mistral)

**Use when:**
- Cost is primary constraint
- Accuracy requirements are moderate (70-80%)
- High volume, low margin use cases
- Can self-host or use cheap inference
- Privacy-critical (on-premise deployment)

**Examples:**
- Content filtering/moderation
- Spam detection
- Simple classification
- Internal tools

**Budget:** $500-5k/month

### Hybrid Approach

Deploy multiple models strategically:

```python
class HybridModelStrategy:
    """Use different models for different request types."""

    @staticmethod
    def route_request(request: Dict) -> str:
        """Route to appropriate model."""

        complexity = request.get('complexity')

        if complexity == 'high':
            # Complex queries → frontier model (GPT-4o)
            return 'gpt-4o'
        elif complexity == 'medium':
            # Standard queries → efficient model (Claude-Sonnet)
            return 'claude-sonnet-4.6'
        else:
            # Simple queries → lightweight model (Gemini Flash)
            return 'gemini-3-flash'

    @staticmethod
    def estimate_monthly_cost(request_distribution: Dict,
                            unit_costs: Dict) -> float:
        """Estimate monthly cost with routing strategy."""

        total_monthly_cost = 0
        total_requests = sum(request_distribution.values())

        for complexity, count in request_distribution.items():
            percentage = count / total_monthly_cost
            if complexity == 'high':
                cost = unit_costs['gpt-4o']
            elif complexity == 'medium':
                cost = unit_costs['claude-sonnet']
            else:
                cost = unit_costs['gemini-flash']

            total_monthly_cost += count * cost

        return total_monthly_cost
```

## Summary

Systematic model selection ensures:

1. **Technical fit:** Models meet performance requirements
2. **Cost optimization:** Balanced budget and quality
3. **Risk mitigation:** Validated before full production
4. **Scalability:** Considerations for growth
5. **Flexibility:** Easy to switch if new models appear

## Key Decision Points

- **Accuracy vs Cost:** Determine acceptable trade-off for your domain
- **Latency requirements:** Eliminates entire classes of models (e.g., 200ms → no batch models)
- **Scale:** Cost becomes critical factor at high volume
- **Safety/Compliance:** Non-negotiable for regulated industries
- **Vendor stability:** Consider long-term availability and support

## Next Steps

1. Define requirements matrix for your use case
2. Create candidate list with key metrics
3. Run screening and shortlist stages
4. Conduct deep evaluation on finalists
5. Deploy selected model as canary
6. Monitor production metrics
7. Quarterly review and potential model updates
