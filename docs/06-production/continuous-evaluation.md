# Continuous Evaluation in Production

**Status:** Production Guide
**Date:** March 31, 2026
**Version:** 1.0

## Overview

Pre-deployment evaluations provide confidence that a model meets requirements before launch. However, production behavior diverges from lab testing due to real-world complexity, shifting data distributions, and unexpected edge cases. This guide covers monitoring model performance in production with continuous evaluation, drift detection, and quality regression alerting.

## Part 1: Why Pre-Deployment Evals Are Insufficient

### The Pre-Deployment Gap

Even with thorough evaluation, production reveals new issues:

```
Lab Evaluation                  Production Reality
─────────────────────────────────────────────────
Curated test cases      →       Real-world variety
Controlled distribution →       Shifting distributions
Single snapshot          →       Time-varying performance
Offline metrics          →       User satisfaction
Artificial latency       →       Real network conditions
Batch processing         →       Interactive requests
```

### Real Examples of Drift

**Example 1: Seasonal Shift**
- Model trained on summer customer support data
- December holiday spike arrives with different question types
- Performance drops from 87% to 79% on holiday queries

**Example 2: Domain Shift**
- Support chatbot trained on account/billing questions
- Company launches new product line
- Model accuracy on new product questions is only 65%

**Example 3: Data Quality Issues**
- Model evaluated with clean data
- Production data contains formatting variations
- Handling of special characters degrades performance

## Part 2: Production Monitoring Architecture

### Core Components

```python
# production_monitoring.py
"""
Production evaluation monitoring system.
"""

from dataclasses import dataclass
from typing import Dict, List
from datetime import datetime
import json

@dataclass
class MonitoringMetric:
    """A single monitored metric."""

    name: str
    description: str
    metric_type: str  # 'quality', 'cost', 'latency', 'safety'
    threshold_warning: float
    threshold_critical: float
    window_minutes: int = 60

@dataclass
class DriftDetector:
    """Detect distribution shift in production."""

    name: str
    detector_type: str  # 'ks_test', 'js_divergence', 'psi'
    baseline_distribution: Dict
    threshold: float = 0.05

class ProductionMonitoringSystem:
    """Complete production monitoring."""

    def __init__(self):
        self.metrics = {}
        self.drift_detectors = {}
        self.alert_handlers = []

    def register_metric(self, metric: MonitoringMetric):
        """Register a metric to monitor."""
        self.metrics[metric.name] = metric

    def register_drift_detector(self, detector: DriftDetector):
        """Register a drift detector."""
        self.drift_detectors[detector.name] = detector

    def sample_production_traffic(self, traffic: List[Dict],
                                 sample_rate: float = 0.01) -> List[Dict]:
        """
        Sample production traffic for evaluation.

        Sample rates:
        - 1% (1-10k QPS): Good for quality checks
        - 0.1% (10-100k QPS): Standard rate
        - 0.01% (>100k QPS): For high-volume services
        """

        import random
        sampled = [req for req in traffic if random.random() < sample_rate]
        return sampled

    def evaluate_sample(self, sample: List[Dict]) -> Dict:
        """Evaluate sampled production traffic."""

        results = {
            'timestamp': datetime.now().isoformat(),
            'sample_size': len(sample),
            'metrics': {}
        }

        # Evaluate accuracy on sample
        correct = sum(1 for req in sample if req.get('correct'))
        accuracy = correct / len(sample) if sample else 0
        results['metrics']['accuracy'] = accuracy

        # Measure latencies
        latencies = [req.get('latency_ms') for req in sample if 'latency_ms' in req]
        if latencies:
            results['metrics']['latency_p50'] = sorted(latencies)[len(latencies)//2]
            results['metrics']['latency_p95'] = sorted(latencies)[int(len(latencies)*0.95)]
            results['metrics']['latency_p99'] = sorted(latencies)[int(len(latencies)*0.99)]

        return results

    def detect_drift(self, current_sample: Dict) -> List[Dict]:
        """Detect distribution drift in production."""

        drifts = []

        for detector_name, detector in self.drift_detectors.items():
            # Perform statistical test
            p_value = self._run_statistical_test(detector, current_sample)

            if p_value < detector.threshold:
                drifts.append({
                    'detector': detector_name,
                    'p_value': p_value,
                    'drift_detected': True,
                    'severity': 'high' if p_value < 0.01 else 'medium'
                })

        return drifts

    def check_quality_regression(self, current_metrics: Dict,
                                 baseline: Dict,
                                 threshold: float = 0.05) -> Dict:
        """
        Check for quality degradation vs baseline.

        threshold: Maximum acceptable degradation (e.g., 0.05 = 5%)
        """

        regression = {
            'detected': False,
            'metrics': {}
        }

        for metric_name, current_value in current_metrics.items():
            if metric_name not in baseline:
                continue

            baseline_value = baseline[metric_name]
            degradation = (baseline_value - current_value) / baseline_value

            if degradation > threshold:
                regression['detected'] = True
                regression['metrics'][metric_name] = {
                    'baseline': baseline_value,
                    'current': current_value,
                    'degradation': degradation,
                    'severity': 'critical' if degradation > 0.10 else 'warning'
                }

        return regression

    def _run_statistical_test(self, detector: DriftDetector,
                            sample: Dict) -> float:
        """Run statistical test for drift detection."""

        from scipy import stats

        if detector.detector_type == 'ks_test':
            # Kolmogorov-Smirnov test
            _, p_value = stats.ks_2samp(
                detector.baseline_distribution.get('values', []),
                sample.get('values', [])
            )
        else:
            # Default: return high p-value (no drift)
            p_value = 0.5

        return p_value
```

## Part 3: Continuous Evaluation Patterns

### Pattern 1: Shadow Evaluation

Deploy new model alongside production model, compare results:

```python
class ShadowEvaluation:
    """Run new model in shadow mode for comparison."""

    def __init__(self, production_model: str, shadow_model: str):
        self.production_model = production_model
        self.shadow_model = shadow_model
        self.results = []

    def process_request(self, request: Dict) -> Dict:
        """
        Process request through both models.

        Only production model's response served to user.
        Shadow model results logged for comparison.
        """

        # Production model (serves user)
        prod_response = self._call_model(self.production_model, request)

        # Shadow model (logged only)
        shadow_response = self._call_model(self.shadow_model, request)

        # Compare
        comparison = {
            'request_id': request.get('id'),
            'timestamp': datetime.now().isoformat(),
            'production': {
                'response': prod_response['text'],
                'latency_ms': prod_response['latency_ms'],
                'cost': prod_response['cost']
            },
            'shadow': {
                'response': shadow_response['text'],
                'latency_ms': shadow_response['latency_ms'],
                'cost': shadow_response['cost']
            },
            'difference': self._compare_responses(
                prod_response['text'],
                shadow_response['text']
            )
        }

        self.results.append(comparison)

        # Return only production response to user
        return prod_response

    def generate_report(self, sample_size: int = None) -> Dict:
        """Generate comparison report."""

        results = self.results if sample_size is None else self.results[-sample_size:]

        identical = sum(1 for r in results if r['difference']['identical'])
        improved = sum(1 for r in results if r['difference']['shadow_better'])
        degraded = sum(1 for r in results if r['difference']['prod_better'])

        return {
            'total_requests': len(results),
            'identical_responses': identical,
            'shadow_better': improved,
            'production_better': degraded,
            'shadow_avg_latency_ms': sum(r['shadow']['latency_ms'] for r in results) / len(results),
            'production_avg_latency_ms': sum(r['production']['latency_ms'] for r in results) / len(results),
            'cost_difference': sum(r['shadow']['cost'] - r['production']['cost'] for r in results)
        }

    def _call_model(self, model: str, request: Dict) -> Dict:
        """Call model (simulated)."""
        return {
            'text': f'Response from {model}',
            'latency_ms': 100,
            'cost': 0.001
        }

    def _compare_responses(self, response1: str, response2: str) -> Dict:
        """Compare two responses."""
        return {
            'identical': response1 == response2,
            'shadow_better': len(response2) > len(response1),
            'prod_better': len(response1) > len(response2),
            'similarity': 0.95  # Compute actual similarity in production
        }
```

### Pattern 2: A/B Testing

Route percentage of traffic to new model, compare metrics:

```python
class ABTestingEvaluation:
    """A/B test new model against production."""

    def __init__(self, control_model: str, treatment_model: str,
                 treatment_percentage: float = 0.10):
        self.control_model = control_model
        self.treatment_model = treatment_model
        self.treatment_percentage = treatment_percentage
        self.results = {'control': [], 'treatment': []}

    def route_request(self, request: Dict) -> str:
        """Route request to control or treatment."""

        import random
        if random.random() < self.treatment_percentage:
            return self.treatment_model
        return self.control_model

    def record_result(self, request_id: str, model: str,
                     success: bool, latency_ms: float,
                     cost: float, user_satisfaction: float = None):
        """Record result from model."""

        group = 'treatment' if model == self.treatment_model else 'control'

        self.results[group].append({
            'request_id': request_id,
            'success': success,
            'latency_ms': latency_ms,
            'cost': cost,
            'user_satisfaction': user_satisfaction
        })

    def compute_metrics(self) -> Dict:
        """Compute comparison metrics."""

        from scipy import stats

        control_success = [r['success'] for r in self.results['control']]
        treatment_success = [r['treatment']['success'] for r in self.results['treatment']]

        # Chi-square test for success rate
        control_success_count = sum(control_success)
        treatment_success_count = sum(treatment_success)

        chi2, p_value = stats.chi2_contingency(
            [[control_success_count, len(control_success) - control_success_count],
             [treatment_success_count, len(treatment_success) - treatment_success_count]]
        )[:2]

        return {
            'control': {
                'n': len(self.results['control']),
                'success_rate': control_success_count / len(control_success),
                'avg_latency_ms': sum(r['latency_ms'] for r in self.results['control']) / len(self.results['control']),
                'avg_cost': sum(r['cost'] for r in self.results['control']) / len(self.results['control'])
            },
            'treatment': {
                'n': len(self.results['treatment']),
                'success_rate': treatment_success_count / len(treatment_success),
                'avg_latency_ms': sum(r['latency_ms'] for r in self.results['treatment']) / len(self.results['treatment']),
                'avg_cost': sum(r['cost'] for r in self.results['treatment']) / len(self.results['treatment'])
            },
            'statistical_significance': {
                'chi2': chi2,
                'p_value': p_value,
                'significant': p_value < 0.05
            }
        }
```

### Pattern 3: Canary Deployments

Gradually roll out new model:

```python
class CanaryDeployment:
    """Gradual rollout with automatic rollback."""

    def __init__(self, stable_model: str, canary_model: str):
        self.stable_model = stable_model
        self.canary_model = canary_model
        self.traffic_split = 0.01  # Start with 1%
        self.max_traffic_split = 1.0  # 100%
        self.rollback_triggered = False

    def increase_traffic(self):
        """Increase canary traffic if metrics pass."""

        if self.traffic_split < self.max_traffic_split:
            self.traffic_split = min(self.max_traffic_split, self.traffic_split * 2)

    def check_health(self, canary_metrics: Dict, stable_metrics: Dict) -> bool:
        """Check if canary is healthy relative to stable."""

        # Must be within 5% on accuracy
        if canary_metrics['accuracy'] < stable_metrics['accuracy'] * 0.95:
            return False

        # Error rate must be <2x
        if canary_metrics['error_rate'] > stable_metrics['error_rate'] * 2:
            return False

        # Cost must be reasonable
        if canary_metrics['cost_per_query'] > stable_metrics['cost_per_query'] * 1.5:
            return False

        return True

    def route_request(self, request: Dict) -> str:
        """Route request to canary or stable."""

        import random
        if self.rollback_triggered:
            return self.stable_model

        if random.random() < self.traffic_split:
            return self.canary_model
        return self.stable_model

    def maybe_rollback(self, canary_metrics: Dict, stable_metrics: Dict):
        """Rollback if canary fails health checks."""

        if not self.check_health(canary_metrics, stable_metrics):
            self.rollback_triggered = True
            print(f"Rolling back {self.canary_model}, reverting to {self.stable_model}")
```

## Part 4: Sampling Strategies

### Stratified Sampling

Sample across different request types to ensure coverage:

```python
class StratifiedSampler:
    """Sample production traffic with stratification."""

    def __init__(self, strata: Dict[str, float]):
        """
        strata: {stratum_name: sample_rate}
        Example: {'high_value': 0.10, 'normal': 0.01, 'low_value': 0.001}
        """
        self.strata = strata

    def should_sample(self, request: Dict) -> bool:
        """Determine if request should be sampled."""

        import random

        # Classify request into stratum
        stratum = self._classify(request)
        sample_rate = self.strata.get(stratum, 0.0)

        return random.random() < sample_rate

    def _classify(self, request: Dict) -> str:
        """Classify request into stratum."""

        # Example: classify by request value
        value = request.get('estimated_value', 0)

        if value > 1000:
            return 'high_value'
        elif value > 100:
            return 'normal'
        else:
            return 'low_value'
```

## Part 5: Alerting on Quality Regression

### Alert Configuration

```python
class QualityAlertSystem:
    """Alert on quality degradation."""

    def __init__(self):
        self.thresholds = {
            'accuracy_drop': 0.05,  # 5% drop
            'latency_increase': 1000,  # 1000ms
            'error_rate_rise': 0.02,  # 2% error rate
            'cost_spike': 1.5  # 1.5x cost increase
        }
        self.alert_channels = []

    def register_alert_channel(self, channel: str, config: Dict):
        """Register alert destination (Slack, PagerDuty, etc)."""
        self.alert_channels.append({
            'channel': channel,
            'config': config
        })

    def check_and_alert(self, current_metrics: Dict,
                       baseline_metrics: Dict,
                       model: str):
        """Check metrics and send alerts if needed."""

        alerts = []

        # Check accuracy drop
        accuracy_drop = baseline_metrics['accuracy'] - current_metrics['accuracy']
        if accuracy_drop > self.thresholds['accuracy_drop']:
            alerts.append({
                'type': 'accuracy_regression',
                'severity': 'critical',
                'message': f"{model} accuracy dropped {accuracy_drop:.1%}",
                'baseline': baseline_metrics['accuracy'],
                'current': current_metrics['accuracy']
            })

        # Check latency increase
        latency_increase = current_metrics['latency_p95'] - baseline_metrics['latency_p95']
        if latency_increase > self.thresholds['latency_increase']:
            alerts.append({
                'type': 'latency_degradation',
                'severity': 'warning',
                'message': f"{model} p95 latency increased {latency_increase:.0f}ms",
                'baseline': baseline_metrics['latency_p95'],
                'current': current_metrics['latency_p95']
            })

        # Send alerts
        for alert in alerts:
            self._send_alert(alert)

    def _send_alert(self, alert: Dict):
        """Send alert to all configured channels."""

        for channel_info in self.alert_channels:
            if channel_info['channel'] == 'slack':
                self._send_slack_alert(alert, channel_info['config'])
            elif channel_info['channel'] == 'pagerduty':
                self._send_pagerduty_alert(alert, channel_info['config'])

    def _send_slack_alert(self, alert: Dict, config: Dict):
        """Send alert to Slack."""

        severity_emoji = {
            'critical': ':rotating_light:',
            'warning': ':warning:',
            'info': ':information_source:'
        }

        message = f"""
{severity_emoji.get(alert['severity'], '')} *{alert['type'].upper()}*

{alert['message']}

Baseline: {alert['baseline']}
Current: {alert['current']}
"""

        # In production, send via Slack webhook
        print(f"Slack alert: {message}")
```

## Part 6: Continuous Evaluation Dashboard

```python
class ContinuousEvalDashboard:
    """Dashboard for monitoring production evaluation metrics."""

    @staticmethod
    def create_dashboard_data() -> Dict:
        """Generate data for monitoring dashboard."""

        return {
            'current_metrics': {
                'model': 'claude-sonnet-4.6',
                'accuracy': 0.897,
                'latency_p95_ms': 2850,
                'error_rate': 0.011,
                'cost_per_query': 0.0067,
                'sample_size': 1250  # Last hour
            },
            'baseline_metrics': {
                'accuracy': 0.910,
                'latency_p95_ms': 2650,
                'error_rate': 0.008,
                'cost_per_query': 0.0065
            },
            'drift_detection': {
                'detected_drifts': 0,
                'warning_drifts': 1,
                'last_check': '2026-03-31T14:30:00Z'
            },
            'active_tests': {
                'shadow_eval': {
                    'status': 'running',
                    'new_model': 'gpt-4o-mini',
                    'requests_compared': 5230
                },
                'ab_test': {
                    'status': 'running',
                    'treatment_model': 'gemini-3-flash',
                    'treatment_traffic': 0.10,
                    'control_accuracy': 0.891,
                    'treatment_accuracy': 0.876,
                    'p_value': 0.042  # Statistically significant difference
                }
            },
            'recent_alerts': [
                {
                    'timestamp': '2026-03-31T14:15:00Z',
                    'type': 'accuracy_regression',
                    'severity': 'warning',
                    'message': 'Accuracy down 1.3% from baseline'
                }
            ]
        }
```

## Summary

Continuous evaluation ensures:

1. **Early drift detection:** Catch performance changes within hours, not days
2. **Gradual rollout validation:** Reduce risk of new model deployments
3. **Comparative metrics:** Objective data for model comparisons
4. **User impact tracking:** Monitor real-world satisfaction alongside metrics
5. **Automated responses:** Automatic rollback on critical failures

## Key Metrics to Monitor

- **Quality:** Accuracy, F1, user satisfaction
- **Latency:** P50, P95, P99 latencies
- **Cost:** Per-query and monthly costs
- **Safety:** Error rate, safety violations
- **Availability:** Uptime, error rates
- **Distribution shift:** KS test, JS divergence

## Monitoring Cadence

| Check | Frequency | Action |
|-------|-----------|--------|
| Real-time alerts | Continuous | Auto-rollback if critical |
| Hourly metrics | Hourly | Warning alerts |
| Daily deep eval | Daily | Manual review |
| Weekly analysis | Weekly | Trend analysis |
| Monthly review | Monthly | Model evaluation decision |

## Next Steps

1. Implement sampling strategy for your traffic volume
2. Set up continuous evaluation in production
3. Configure alert thresholds based on business needs
4. Train team on interpreting drift signals
5. Establish runbooks for common alerts
6. Quarterly review of continuous eval effectiveness
