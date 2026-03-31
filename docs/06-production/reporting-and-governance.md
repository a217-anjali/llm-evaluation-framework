# Reporting and Governance

**Status:** Production Guide
**Date:** March 31, 2026
**Version:** 1.0

## Overview

Evaluation results drive critical business decisions and must be documented, communicated, and governed properly. This guide covers reporting for different audiences, compliance documentation, version control for evaluations, and governance processes.

## Part 1: Reporting for Different Audiences

### Audience-Specific Reports

Different stakeholders need different information:

```python
# reporting.py
"""
Generate audience-specific evaluation reports.
"""

from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime
import json

@dataclass
class ReportAudience:
    """Definition of report audience."""

    name: str
    role: str  # 'technical', 'product', 'executive', 'compliance'
    technical_depth: str  # 'deep', 'moderate', 'shallow'
    decision_focus: str  # What decision this audience makes

# Engineering/Technical Report

class EngineeringReport:
    """Deep technical report for engineering teams."""

    @staticmethod
    def generate(eval_results: Dict, config: Dict = None) -> str:
        """Generate detailed technical report."""

        report = []
        report.append("=" * 100)
        report.append("EVALUATION TECHNICAL REPORT")
        report.append("=" * 100)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Evaluation Framework: llm_eval_framework v2")

        # 1. Test Coverage
        report.append("\n1. TEST COVERAGE AND METHODOLOGY")
        report.append("-" * 100)
        report.append(f"Total test cases: {eval_results['test_case_count']}")
        report.append(f"Test case distribution:")
        report.append(f"  - Easy: {eval_results['easy_count']} ({eval_results['easy_pct']:.1%})")
        report.append(f"  - Medium: {eval_results['medium_count']} ({eval_results['medium_pct']:.1%})")
        report.append(f"  - Hard: {eval_results['hard_count']} ({eval_results['hard_pct']:.1%})")

        report.append(f"\nEvaluation dimensions:")
        for dim_name, dim_weight in eval_results['dimensions'].items():
            report.append(f"  - {dim_name}: {dim_weight:.1%} weight")

        # 2. Detailed Results by Model
        report.append("\n2. PER-MODEL DETAILED RESULTS")
        report.append("-" * 100)

        for model_name, results in eval_results['models'].items():
            report.append(f"\n{model_name}")
            report.append(f"  Overall Score: {results['overall_score']:.2f}/100")
            report.append(f"  95% CI: [{results['ci_lower']:.2f}, {results['ci_upper']:.2f}]")

            for dim_name, dim_results in results['dimensions'].items():
                report.append(f"\n  {dim_name}: {dim_results['score']:.1f}")
                report.append(f"    Errors: {len(dim_results['errors'])}")
                if dim_results['errors']:
                    for error in dim_results['errors'][:5]:  # Show top 5
                        report.append(f"      - {error}")

        # 3. Statistical Analysis
        report.append("\n3. STATISTICAL SIGNIFICANCE TESTING")
        report.append("-" * 100)

        for comparison, results in eval_results['significance_tests'].items():
            report.append(f"\n{comparison}")
            report.append(f"  p-value: {results['p_value']:.4f}")
            report.append(f"  Cohen's d: {results['cohens_d']:.3f} ({results['effect_size']})")
            report.append(f"  Significant: {'Yes' if results['significant'] else 'No'}")

        # 4. Edge Cases and Failures
        report.append("\n4. ERROR ANALYSIS")
        report.append("-" * 100)

        if eval_results.get('failure_cases'):
            report.append(f"Failed test cases: {len(eval_results['failure_cases'])}")
            for case in eval_results['failure_cases'][:10]:  # Show top 10
                report.append(f"\n  Test Case: {case['id']}")
                report.append(f"  Error: {case['error']}")
                report.append(f"  Context: {case['context']}")

        # 5. Regression Analysis
        report.append("\n5. REGRESSION FROM BASELINE")
        report.append("-" * 100)

        if eval_results.get('baseline'):
            for model, baseline in eval_results['baseline'].items():
                current = eval_results['models'][model]['overall_score']
                regression = baseline - current
                report.append(f"\n{model}")
                report.append(f"  Baseline: {baseline:.2f}")
                report.append(f"  Current: {current:.2f}")
                report.append(f"  Change: {regression:+.2f} {'(regression)' if regression > 0 else '(improvement)'}")

        report.append("\n" + "=" * 100)
        return "\n".join(report)

# Product/Business Report

class ProductReport:
    """High-level report for product teams."""

    @staticmethod
    def generate(eval_results: Dict) -> str:
        """Generate business-focused report."""

        report = []
        report.append("EVALUATION SUMMARY - PRODUCT PERSPECTIVE")
        report.append("=" * 80)
        report.append(f"Date: {datetime.now().strftime('%B %d, %Y')}")

        # Key question: Is the model ready?
        passing_models = [m for m, r in eval_results['models'].items()
                         if r['overall_score'] >= 80]

        report.append(f"\n✓ READY FOR PRODUCTION: {', '.join(passing_models) if passing_models else 'None'}")

        # Performance characteristics
        report.append("\nPERFORMANCE CHARACTERISTICS")
        report.append("-" * 80)

        best_model = max(eval_results['models'].items(),
                        key=lambda x: x[1]['overall_score'])
        report.append(f"\nBest performing model: {best_model[0]}")
        report.append(f"  Overall quality: {best_model[1]['overall_score']:.0f}/100")
        report.append(f"  Ready for production: {'Yes' if best_model[1]['overall_score'] >= 80 else 'No'}")
        report.append(f"  Cost efficiency: {'High' if best_model[1]['cost_per_query'] < 0.01 else 'Moderate'}")

        # Business impact
        report.append("\nBUSINESS IMPACT")
        report.append("-" * 80)

        report.append("\nQuality Impact:")
        report.append(f"  Models meeting >85% accuracy: {len([m for m, r in eval_results['models'].items() if r['overall_score'] > 85])}")
        report.append(f"  Expected customer satisfaction: Moderate")

        report.append("\nCost Impact (assuming 100k monthly queries):")
        for model, results in eval_results['models'].items():
            monthly_cost = results.get('cost_per_query', 0) * 100000
            report.append(f"  {model}: ${monthly_cost:,.0f}/month")

        # Recommendation
        report.append("\nRECOMMENDATION")
        report.append("-" * 80)

        if best_model[1]['overall_score'] >= 80:
            report.append(f"\nDeploy {best_model[0]} to production.")
            report.append(f"Expected quality: {best_model[1]['overall_score']:.0f}/100")
            report.append(f"Estimated monthly cost: ${best_model[1].get('cost_per_query', 0) * 100000:,.0f}")
        else:
            report.append("\nNo model meets production threshold (80/100).")
            report.append("Recommend: Further model tuning or evaluation refinement.")

        report.append("\n" + "=" * 80)
        return "\n".join(report)

# Executive Report

class ExecutiveReport:
    """High-level report for leadership."""

    @staticmethod
    def generate(eval_results: Dict, business_context: Dict = None) -> str:
        """Generate executive summary."""

        report = []
        report.append("EXECUTIVE SUMMARY - LLM EVALUATION")
        report.append("=" * 70)

        # Status
        passing_count = len([m for m, r in eval_results['models'].items()
                           if r['overall_score'] >= 80])

        if passing_count > 0:
            report.append(f"\nSTATUS: ✓ READY FOR DEPLOYMENT")
        else:
            report.append(f"\nSTATUS: ✗ NOT READY - Further work needed")

        # Quick metrics
        report.append("\nKEY METRICS")
        report.append("-" * 70)

        best_model = max(eval_results['models'].items(),
                        key=lambda x: x[1]['overall_score'])

        report.append(f"Best model: {best_model[0]}")
        report.append(f"Quality score: {best_model[1]['overall_score']:.0f}/100")
        report.append(f"Estimated accuracy: {best_model[1].get('accuracy_pct', 85):.0f}%")

        # Business impact
        report.append("\nBUSINESS IMPACT")
        report.append("-" * 70)

        monthly_volume = business_context.get('monthly_volume', 100000) if business_context else 100000
        monthly_cost = best_model[1].get('cost_per_query', 0) * monthly_volume
        annual_cost = monthly_cost * 12

        report.append(f"Expected monthly cost: ${monthly_cost:,.0f}")
        report.append(f"Expected annual cost: ${annual_cost:,.0f}")

        # Timeline
        if best_model[1]['overall_score'] >= 80:
            report.append("\nNEXT STEPS")
            report.append("-" * 70)
            report.append("1. Deploy to staging environment (Week 1)")
            report.append("2. Run production validation (Week 2)")
            report.append("3. Gradual rollout to production (Week 3-4)")
            report.append("4. Monitor performance metrics")

        report.append("\n" + "=" * 70)
        return "\n".join(report)

# Compliance Report

class ComplianceReport:
    """Documentation for regulatory compliance."""

    @staticmethod
    def generate(eval_results: Dict, compliance_requirements: Dict = None) -> str:
        """Generate compliance documentation."""

        report = []
        report.append("COMPLIANCE AND GOVERNANCE REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Framework Version: llm_eval_framework v2.0")

        # Evaluation Methodology
        report.append("\n1. EVALUATION METHODOLOGY")
        report.append("-" * 80)
        report.append("Domain: Customer support LLM responses")
        report.append("Evaluation Approach: Multi-dimensional rubric with 4 dimensions")
        report.append("Sample Size: 50 test cases")
        report.append("Quality Control: Double-blind scoring on 10% of cases")

        # Models Evaluated
        report.append("\n2. MODELS EVALUATED")
        report.append("-" * 80)

        for model_name, results in eval_results['models'].items():
            report.append(f"\n{model_name}")
            report.append(f"  Provider: Model Provider")
            report.append(f"  Version: v1.0")
            report.append(f"  Evaluation Date: {datetime.now().strftime('%Y-%m-%d')}")
            report.append(f"  Overall Score: {results['overall_score']:.2f}/100")
            report.append(f"  Safety Score: {results.get('safety_score', 'Not evaluated')}")

        # Bias and Fairness Assessment
        report.append("\n3. BIAS AND FAIRNESS ASSESSMENT")
        report.append("-" * 80)
        report.append("Demographic parity: Not systematically evaluated in this round")
        report.append("Performance across subgroups: Limited data available")
        report.append("Recommendation: Conduct expanded fairness evaluation before production")

        # Limitations
        report.append("\n4. LIMITATIONS AND CAVEATS")
        report.append("-" * 80)
        report.append("- Evaluation based on curated test cases (may not reflect all real-world scenarios)")
        report.append("- Limited evaluation of edge cases and adversarial inputs")
        report.append("- No evaluation of response to harmful requests")
        report.append("- Performance may vary with prompt engineering")

        # Audit Trail
        report.append("\n5. AUDIT TRAIL")
        report.append("-" * 80)
        report.append(f"Evaluation Framework: {eval_results.get('framework_version', 'v2.0')}")
        report.append(f"Evaluation Date: {eval_results.get('eval_date', 'Not recorded')}")
        report.append(f"Evaluator: {eval_results.get('evaluator', 'Automated')}")
        report.append(f"Data Retention: 7 years (compliance requirement)")

        # Recommendations for Production
        report.append("\n6. RECOMMENDATIONS FOR PRODUCTION DEPLOYMENT")
        report.append("-" * 80)
        report.append("1. Maintain audit log of all LLM responses")
        report.append("2. Implement human review for sensitive queries")
        report.append("3. Monitor for drift in model performance")
        report.append("4. Conduct annual re-evaluation")
        report.append("5. Implement incident reporting for model failures")

        report.append("\n" + "=" * 80)
        report.append("\nReport Approved By: [Name and Title]")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")

        return "\n".join(report)
```

## Part 2: Model Cards and Evaluation Cards

### Model Card Template

```python
# model_card.py
"""
Model Card: Comprehensive model documentation.
Based on: https://arxiv.org/abs/1810.03993
"""

class ModelCard:
    """Create comprehensive model card."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.card = {}

    def add_model_details(self, details: Dict):
        """Add model information."""
        self.card['model_details'] = {
            'model_name': self.model_name,
            'model_version': details.get('version', 'unknown'),
            'model_type': 'Large Language Model',
            'architecture': details.get('architecture'),
            'parameters': details.get('parameters'),
            'training_data': details.get('training_data'),
            'release_date': details.get('release_date'),
            'developers': details.get('developers', [])
        }

    def add_intended_use(self, use_cases: List[str], out_of_scope: List[str]):
        """Add intended use information."""
        self.card['intended_use'] = {
            'primary_use_cases': use_cases,
            'out_of_scope_uses': out_of_scope,
            'users': ['Customer support teams', 'Developers'],
            'use_restrictions': 'Model must not be used for harassment or illegal activities'
        }

    def add_factors(self, factors: Dict):
        """Add relevant factors affecting performance."""
        self.card['factors'] = {
            'relevant_factors': factors.get('relevant', []),
            'evaluation_factors': factors.get('evaluation', []),
            'disparate_impact_factors': factors.get('disparity', [])
        }

    def add_metrics(self, metrics: Dict):
        """Add evaluation metrics."""
        self.card['evaluation_metrics'] = {
            'accuracy': metrics.get('accuracy'),
            'accuracy_ci': metrics.get('accuracy_ci'),
            'fairness_metrics': metrics.get('fairness', {}),
            'latency_p95': metrics.get('latency_p95'),
            'cost_per_query': metrics.get('cost')
        }

    def add_ethical_considerations(self, considerations: List[str]):
        """Add ethical considerations."""
        self.card['ethical_considerations'] = {
            'potential_risks': considerations,
            'mitigation_strategies': [
                'Implement human review for sensitive queries',
                'Monitor for harmful outputs',
                'Regular performance audits'
            ],
            'data_privacy': 'User inputs are processed but not stored for training'
        }

    def add_limitations(self, limitations: List[str]):
        """Add known limitations."""
        self.card['limitations'] = {
            'scope_limitations': limitations,
            'performance_degradation': [
                'Performance drops on out-of-domain queries',
                'Limited reasoning on complex multi-step problems'
            ],
            'known_issues': []
        }

    def add_recommendations(self, recommendations: Dict):
        """Add recommendations for use."""
        self.card['recommendations'] = {
            'human_oversight': recommendations.get('human_oversight', True),
            'affected_groups': recommendations.get('affected_groups', []),
            'monitoring_requirements': recommendations.get('monitoring', []),
            'update_strategy': 'Quarterly evaluation and potential model updates'
        }

    def generate_markdown(self) -> str:
        """Generate markdown version of model card."""

        md = []
        md.append(f"# Model Card: {self.model_name}")

        if 'model_details' in self.card:
            md.append("\n## Model Details")
            for key, value in self.card['model_details'].items():
                md.append(f"- **{key}**: {value}")

        if 'intended_use' in self.card:
            md.append("\n## Intended Use")
            md.append(f"**Primary use cases:**")
            for uc in self.card['intended_use']['primary_use_cases']:
                md.append(f"- {uc}")

        if 'ethical_considerations' in self.card:
            md.append("\n## Ethical Considerations")
            md.append(f"**Potential Risks:**")
            for risk in self.card['ethical_considerations']['potential_risks']:
                md.append(f"- {risk}")

        return "\n".join(md)
```

### Evaluation Card Template

```python
class EvaluationCard:
    """Create evaluation card documenting assessment."""

    def __init__(self, model_name: str, eval_date: str):
        self.model_name = model_name
        self.eval_date = eval_date
        self.card = {}

    def add_evaluation_info(self, info: Dict):
        """Add evaluation information."""
        self.card['evaluation_info'] = {
            'model_evaluated': self.model_name,
            'evaluation_date': self.eval_date,
            'evaluation_framework': 'llm_eval_framework v2',
            'evaluators': info.get('evaluators', []),
            'methodology': 'Multi-dimensional rubric with human validation'
        }

    def add_test_suite(self, test_suite: Dict):
        """Add test suite information."""
        self.card['test_suite'] = {
            'total_cases': test_suite.get('total'),
            'easy_cases': test_suite.get('easy'),
            'medium_cases': test_suite.get('medium'),
            'hard_cases': test_suite.get('hard'),
            'domains': test_suite.get('domains', []),
            'coverage': test_suite.get('coverage')
        }

    def add_results(self, results: Dict):
        """Add evaluation results."""
        self.card['results'] = {
            'overall_score': results.get('overall_score'),
            'dimensions': results.get('dimensions', {}),
            'confidence_interval': results.get('ci'),
            'pass_rate': results.get('pass_rate'),
            'production_ready': results.get('overall_score', 0) >= 80
        }

    def add_findings(self, findings: Dict):
        """Add key findings."""
        self.card['findings'] = {
            'strengths': findings.get('strengths', []),
            'weaknesses': findings.get('weaknesses', []),
            'edge_cases': findings.get('edge_cases', []),
            'recommendations': findings.get('recommendations', [])
        }

    def generate_markdown(self) -> str:
        """Generate markdown version."""

        md = []
        md.append(f"# Evaluation Card: {self.model_name}")
        md.append(f"**Evaluation Date:** {self.eval_date}")

        if 'results' in self.card:
            md.append("\n## Results")
            md.append(f"**Overall Score:** {self.card['results']['overall_score']:.1f}/100")
            md.append(f"**Production Ready:** {'✓ Yes' if self.card['results']['production_ready'] else '✗ No'}")

        if 'findings' in self.card:
            md.append("\n## Key Findings")
            md.append("\n**Strengths:**")
            for strength in self.card['findings']['strengths']:
                md.append(f"- {strength}")

            md.append("\n**Weaknesses:**")
            for weakness in self.card['findings']['weaknesses']:
                md.append(f"- {weakness}")

        return "\n".join(md)
```

## Part 3: Version Control for Evaluations

### Evaluation Versioning System

```python
class EvaluationVersionControl:
    """Version control for evaluations (similar to Git)."""

    def __init__(self, db_connection):
        self.db = db_connection
        self.current_version = None

    def create_evaluation_version(self, eval_name: str, eval_config: Dict,
                                test_cases: List[Dict],
                                results: Dict) -> str:
        """Create a new evaluation version."""

        version_id = f"{eval_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        record = {
            'version_id': version_id,
            'eval_name': eval_name,
            'created_date': datetime.now().isoformat(),
            'config': json.dumps(eval_config),
            'test_cases': json.dumps(test_cases),
            'results': json.dumps(results),
            'status': 'completed'
        }

        self.db.insert('evaluation_versions', record)
        self.current_version = version_id

        return version_id

    def compare_versions(self, version1: str, version2: str) -> Dict:
        """Compare two evaluation versions."""

        v1 = self.db.query(
            "SELECT * FROM evaluation_versions WHERE version_id = ?",
            (version1,)
        )[0]

        v2 = self.db.query(
            "SELECT * FROM evaluation_versions WHERE version_id = ?",
            (version2,)
        )[0]

        config1 = json.loads(v1['config'])
        config2 = json.loads(v2['config'])

        results1 = json.loads(v1['results'])
        results2 = json.loads(v2['results'])

        return {
            'version1': version1,
            'version2': version2,
            'config_changes': self._diff(config1, config2),
            'test_case_changes': f"{len(json.loads(v1['test_cases']))} vs {len(json.loads(v2['test_cases']))}",
            'score_change': results1.get('overall_score') - results2.get('overall_score')
        }

    def rollback_to_version(self, version_id: str) -> bool:
        """Rollback evaluation results to previous version."""

        version = self.db.query(
            "SELECT * FROM evaluation_versions WHERE version_id = ?",
            (version_id,)
        )[0]

        if not version:
            return False

        self.current_version = version_id
        return True

    def get_version_history(self, eval_name: str) -> List[Dict]:
        """Get version history for evaluation."""

        return self.db.query(
            "SELECT version_id, created_date, status FROM evaluation_versions WHERE eval_name = ? ORDER BY created_date DESC",
            (eval_name,)
        )

    def _diff(self, d1: Dict, d2: Dict) -> Dict:
        """Compute differences between dicts."""

        diff = {}
        for key in set(list(d1.keys()) + list(d2.keys())):
            if d1.get(key) != d2.get(key):
                diff[key] = {'old': d1.get(key), 'new': d2.get(key)}

        return diff
```

## Part 4: Governance and Compliance

### EU AI Act Compliance

```python
class AIActCompliance:
    """Documentation for EU AI Act compliance."""

    @staticmethod
    def generate_risk_assessment() -> str:
        """Generate EU AI Act risk assessment."""

        report = []
        report.append("EU AI ACT RISK ASSESSMENT")
        report.append("=" * 80)

        # Risk Classification
        report.append("\n1. RISK CLASSIFICATION")
        report.append("-" * 80)
        report.append("Risk Level: Medium")
        report.append("Justification: LLM used for customer support (affects consumer decisions)")

        # High-Risk Requirement: Documentation
        report.append("\n2. DOCUMENTATION REQUIREMENTS")
        report.append("-" * 80)
        report.append("✓ Training data documentation")
        report.append("✓ Model card and evaluation card")
        report.append("✓ Quality management system")
        report.append("✓ Human oversight procedures")

        # Transparency
        report.append("\n3. TRANSPARENCY REQUIREMENTS")
        report.append("-" * 80)
        report.append("- Users informed that they're interacting with AI")
        report.append("- Capabilities and limitations disclosed")
        report.append("- Decision logic documented")

        # Human Oversight
        report.append("\n4. HUMAN OVERSIGHT")
        report.append("-" * 80)
        report.append("- High-confidence decisions: Automated")
        report.append("- Medium-confidence (60-85%): Human review available")
        report.append("- Low-confidence (<60%): Escalate to human")

        return "\n".join(report)
```

### Quarterly Review Cadence

```python
class QuarterlyEvaluationCycle:
    """Establish and track quarterly evaluation cycle."""

    def __init__(self, current_quarter: str):
        self.quarter = current_quarter  # e.g., "Q2-2026"
        self.timeline = self._define_timeline()

    def _define_timeline(self) -> Dict:
        """Define quarterly evaluation timeline."""

        return {
            'week_1': {
                'milestone': 'Data Collection',
                'tasks': [
                    'Collect production traffic sample',
                    'Gather ground truth labels',
                    'Document any model changes'
                ]
            },
            'week_2': {
                'milestone': 'Evaluation Execution',
                'tasks': [
                    'Run automated scoring',
                    'Conduct statistical analysis',
                    'Compare against baseline'
                ]
            },
            'week_3': {
                'milestone': 'Review and Analysis',
                'tasks': [
                    'Technical deep dive (engineering)',
                    'Business impact analysis (product)',
                    'Compliance review (legal)'
                ]
            },
            'week_4': {
                'milestone': 'Decision and Action',
                'tasks': [
                    'Make model selection decision',
                    'Plan any optimization work',
                    'Document decisions and rationale'
                ]
            }
        }

    def generate_quarterly_report(self, eval_results: Dict) -> str:
        """Generate quarterly evaluation report."""

        report = []
        report.append(f"QUARTERLY EVALUATION REPORT - {self.quarter}")
        report.append("=" * 80)

        report.append("\nEVALUATION TIMELINE")
        report.append("-" * 80)
        for week, info in self.timeline.items():
            report.append(f"{week}: {info['milestone']}")

        report.append("\nKEY DECISIONS")
        report.append("-" * 80)
        report.append("1. Model Selection: [Model name and justification]")
        report.append("2. Quality Threshold: [Minimum acceptable score]")
        report.append("3. Cost Budget: [Monthly/annual budget]")
        report.append("4. SLA Commitments: [Performance guarantees]")

        report.append("\nIMPLEMENTATION PLAN")
        report.append("-" * 80)
        report.append("- Timeline: [When to deploy]")
        report.append("- Rollout strategy: [Canary/gradual/all-at-once]")
        report.append("- Monitoring plan: [What to track]")
        report.append("- Rollback criteria: [When to revert]")

        report.append("\nNEXT QUARTER GOALS")
        report.append("-" * 80)
        report.append("- Improve accuracy by [X%]")
        report.append("- Reduce cost by [Y%]")
        report.append("- Expand to [new domain]")

        return "\n".join(report)
```

## Part 5: Audit and Compliance Checklist

```python
class ComplianceChecklist:
    """Audit checklist for evaluation governance."""

    items = {
        'documentation': [
            ('Model cards created', False),
            ('Evaluation cards created', False),
            ('Bias/fairness assessment completed', False),
            ('Limitations documented', False),
            ('Training data sources documented', False)
        ],
        'testing': [
            ('All test cases version controlled', False),
            ('Test case coverage adequate', False),
            ('Adversarial testing conducted', False),
            ('Edge case evaluation completed', False),
            ('Regression testing performed', False)
        ],
        'governance': [
            ('Evaluation versioning system in place', False),
            ('Approval workflow defined', False),
            ('Change log maintained', False),
            ('Audit trail recorded', False),
            ('Retention policy documented', False)
        ],
        'compliance': [
            ('EU AI Act requirements met', False),
            ('Data privacy assessed', False),
            ('Fairness/bias evaluation done', False),
            ('Human oversight procedures defined', False),
            ('Incident reporting process established', False)
        ],
        'monitoring': [
            ('Production monitoring system active', False),
            ('Drift detection configured', False),
            ('Alert thresholds set', False),
            ('Performance dashboard established', False),
            ('Regular review schedule set', False)
        ]
    }

    def generate_audit_report(self) -> str:
        """Generate audit report showing compliance status."""

        report = []
        report.append("COMPLIANCE AUDIT REPORT")
        report.append("=" * 80)
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")

        for category, items in self.items.items():
            completed = sum(1 for _, status in items if status)
            total = len(items)
            percentage = (completed / total) * 100

            report.append(f"\n{category.upper()}: {completed}/{total} ({percentage:.0f}%)")
            report.append("-" * 80)

            for item, status in items:
                status_symbol = "✓" if status else "✗"
                report.append(f"  {status_symbol} {item}")

        overall_percentage = sum(1 for cat in self.items.values() for _, status in cat if status) / \
                            sum(len(cat) for cat in self.items.values()) * 100

        report.append(f"\n\nOVERALL COMPLIANCE: {overall_percentage:.0f}%")

        return "\n".join(report)
```

## Summary

Comprehensive reporting and governance ensures:

1. **Clear communication:** Each audience gets relevant information
2. **Regulatory compliance:** Documentation for audits and compliance reviews
3. **Version control:** Track evaluation history and changes
4. **Audit trails:** Accountability and traceability
5. **Institutional knowledge:** Future reference and continuous improvement

## Key Governance Documents

| Document | Frequency | Audience | Purpose |
|----------|-----------|----------|---------|
| Model Card | Annual | Technical/Compliance | Document model capabilities |
| Evaluation Card | Per eval | Engineering/Product | Document assessment results |
| Technical Report | Per eval | Engineers | Deep technical analysis |
| Executive Summary | Quarterly | Leadership | High-level decision support |
| Compliance Report | Annual | Legal/Compliance | Regulatory documentation |
| Audit Report | Quarterly | Quality/Governance | Compliance tracking |

## Next Steps

1. Create model and evaluation card templates
2. Establish evaluation versioning system
3. Define quarterly evaluation cycle
4. Build compliance checklist
5. Set up automated reporting
6. Train stakeholders on governance process
