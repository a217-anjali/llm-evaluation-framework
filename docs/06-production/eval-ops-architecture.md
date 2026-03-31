# EvalOps Architecture

**Status:** Production Guide
**Date:** March 31, 2026
**Version:** 1.0

## Overview

EvalOps is the operational infrastructure for running evaluations at scale. This guide presents a reference architecture for building production-grade evaluation systems, from data collection through result visualization and decision-making.

## Part 1: Reference Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PRODUCTION SYSTEM                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  User Request → LLM Model → Output → (Sample: Y/N)                         │
│                                │                                            │
│                                ├→ If sampled:                              │
│                                │   ├ Store in Eval Queue                  │
│                                │   └ (ground truth label added later)      │
│                                │                                            │
│                                └→ Serve to user                            │
│                                                                              │
└──────────────────────────┬───────────────────────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
        ▼                                     ▼
    ┌────────────────┐            ┌───────────────────┐
    │  Eval Queue    │            │  Ground Truth      │
    │ (Sampled data) │            │ (Manual labels)    │
    └────────┬───────┘            └─────────┬─────────┘
             │                               │
             └───────────────┬───────────────┘
                             │
                    ┌────────▼────────┐
                    │  Scorer Service │
                    │  (Automated)    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    ┌────────┐          ┌────────┐          ┌────────┐
    │Quality │          │  Cost  │          │Latency │
    │Scorer  │          │Tracker │          │Monitor │
    └────┬───┘          └───┬────┘          └───┬────┘
         │                  │                    │
         └──────────────────┼────────────────────┘
                            │
                   ┌────────▼────────┐
                   │  Result Store   │
                   │  (PostgreSQL)   │
                   └────────┬────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
    ┌────────┐         ┌────────┐         ┌────────┐
    │Analysis│         │Alerts  │         │Reports │
    │Engine  │         │System  │         │        │
    └────┬───┘         └───┬────┘         └───┬────┘
         │                 │                   │
         └─────────────────┼───────────────────┘
                           │
                  ┌────────▼────────┐
                  │   Dashboard     │
                  │   & Monitoring  │
                  └─────────────────┘
```

### Component Details

#### 1. Evaluation Queue

Stores requests sampled from production for later evaluation.

```python
class EvaluationQueue:
    """Queue for production traffic to be evaluated."""

    def __init__(self, db_connection, max_queue_size=100000):
        self.db = db_connection
        self.max_queue_size = max_queue_size

    def enqueue_request(self, request: Dict):
        """Add production request to evaluation queue."""

        eval_item = {
            'request_id': request['id'],
            'timestamp': datetime.now().isoformat(),
            'model': request['model'],
            'input': request['input'],
            'output': request['output'],
            'ground_truth': None,  # Filled in later
            'score': None,
            'scorer_version': None,
            'status': 'pending'
        }

        self.db.insert('evaluation_queue', eval_item)

    def get_pending_items(self, limit=1000) -> List[Dict]:
        """Get items awaiting ground truth or scoring."""

        return self.db.query(
            "SELECT * FROM evaluation_queue WHERE status='pending' LIMIT ?",
            (limit,)
        )

    def mark_ground_truth_added(self, request_id: str, ground_truth: str):
        """Mark ground truth has been added (by human or automatic)."""

        self.db.update(
            'evaluation_queue',
            {'request_id': request_id},
            {'ground_truth': ground_truth, 'status': 'ready_for_scoring'}
        )

    def mark_scored(self, request_id: str, score: float, scorer_version: str):
        """Mark item as scored."""

        self.db.update(
            'evaluation_queue',
            {'request_id': request_id},
            {
                'score': score,
                'scorer_version': scorer_version,
                'status': 'complete',
                'scored_at': datetime.now().isoformat()
            }
        )
```

#### 2. Scorer Service

Runs scoring logic on queued items.

```python
class ScorerService:
    """Service for running automated scorers."""

    def __init__(self, scorers: Dict):
        self.scorers = scorers  # {scorer_name: scorer_function}
        self.results = []

    def score_item(self, item: Dict, scorer_name: str) -> Dict:
        """Score a single evaluation item."""

        if scorer_name not in self.scorers:
            raise ValueError(f"Unknown scorer: {scorer_name}")

        scorer_fn = self.scorers[scorer_name]

        # Run scorer
        score = scorer_fn(
            input_text=item['input'],
            output_text=item['output'],
            ground_truth=item['ground_truth']
        )

        result = {
            'request_id': item['request_id'],
            'scorer': scorer_name,
            'score': score,
            'timestamp': datetime.now().isoformat()
        }

        self.results.append(result)
        return result

    def batch_score(self, items: List[Dict], scorer_name: str) -> List[Dict]:
        """Score multiple items."""

        results = []
        for item in items:
            result = self.score_item(item, scorer_name)
            results.append(result)

        return results

    def register_scorer(self, name: str, scorer_fn):
        """Register a new scorer function."""

        self.scorers[name] = scorer_fn

    def get_available_scorers(self) -> List[str]:
        """List available scorers."""

        return list(self.scorers.keys())
```

#### 3. Result Store

Persistent storage for evaluation results.

```python
class ResultStore:
    """Store and query evaluation results."""

    def __init__(self, db_connection):
        self.db = db_connection

    def store_result(self, result: Dict):
        """Store evaluation result."""

        record = {
            'request_id': result['request_id'],
            'model': result['model'],
            'prompt': result['prompt'],
            'response': result['response'],
            'ground_truth': result['ground_truth'],
            'score': result['score'],
            'scorer_version': result.get('scorer_version'),
            'latency_ms': result.get('latency_ms'),
            'cost_usd': result.get('cost_usd'),
            'timestamp': result.get('timestamp', datetime.now().isoformat()),
            'tags': result.get('tags', {})
        }

        self.db.insert('evaluation_results', record)

    def query_results(self, filters: Dict = None, start_date: str = None,
                     end_date: str = None, limit: int = 10000) -> List[Dict]:
        """Query results with filtering."""

        query = "SELECT * FROM evaluation_results WHERE 1=1"
        params = []

        if filters:
            if 'model' in filters:
                query += " AND model = ?"
                params.append(filters['model'])
            if 'scorer' in filters:
                query += " AND scorer_version LIKE ?"
                params.append(f"%{filters['scorer']}%")

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)

        query += f" LIMIT {limit}"

        return self.db.query(query, tuple(params))

    def compute_model_metrics(self, model: str,
                            start_date: str = None,
                            end_date: str = None) -> Dict:
        """Compute aggregated metrics for a model."""

        results = self.query_results(
            filters={'model': model},
            start_date=start_date,
            end_date=end_date
        )

        if not results:
            return {}

        scores = [r['score'] for r in results if r['score'] is not None]
        latencies = [r['latency_ms'] for r in results if r['latency_ms'] is not None]
        costs = [r['cost_usd'] for r in results if r['cost_usd'] is not None]

        return {
            'model': model,
            'sample_count': len(results),
            'accuracy': sum(scores) / len(scores) if scores else None,
            'accuracy_std': np.std(scores) if len(scores) > 1 else 0,
            'latency_mean_ms': sum(latencies) / len(latencies) if latencies else None,
            'latency_p95_ms': np.percentile(latencies, 95) if latencies else None,
            'cost_mean_usd': sum(costs) / len(costs) if costs else None,
            'date_range': {
                'start': start_date,
                'end': end_date
            }
        }
```

#### 4. Cost Tracking

Monitor and track evaluation costs.

```python
class CostTracker:
    """Track costs of model inference and evaluation."""

    def __init__(self, db_connection, pricing_config: Dict):
        self.db = db_connection
        self.pricing = pricing_config  # {model: {input_cost_1k, output_cost_1k}}

    def record_inference(self, model: str, input_tokens: int,
                        output_tokens: int, timestamp: str = None):
        """Record model inference for cost tracking."""

        pricing = self.pricing.get(model, {})
        input_cost = (input_tokens / 1000) * pricing.get('input_cost_1k', 0)
        output_cost = (output_tokens / 1000) * pricing.get('output_cost_1k', 0)
        total_cost = input_cost + output_cost

        record = {
            'model': model,
            'timestamp': timestamp or datetime.now().isoformat(),
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost
        }

        self.db.insert('cost_tracking', record)

    def compute_daily_costs(self, date: str) -> Dict:
        """Compute daily costs by model."""

        query = """
            SELECT model, SUM(total_cost) as total_cost, COUNT(*) as request_count
            FROM cost_tracking
            WHERE DATE(timestamp) = ?
            GROUP BY model
        """

        results = self.db.query(query, (date,))

        daily_totals = {}
        for row in results:
            daily_totals[row['model']] = {
                'total_cost': row['total_cost'],
                'request_count': row['request_count'],
                'cost_per_request': row['total_cost'] / row['request_count']
            }

        return daily_totals

    def estimate_monthly_cost(self, model: str, monthly_volume: int) -> float:
        """Estimate monthly cost for a given volume."""

        pricing = self.pricing.get(model, {})
        avg_input = pricing.get('avg_input_tokens', 100)
        avg_output = pricing.get('avg_output_tokens', 200)

        cost_per_query = ((avg_input / 1000) * pricing.get('input_cost_1k', 0) +
                         (avg_output / 1000) * pricing.get('output_cost_1k', 0))

        return cost_per_query * monthly_volume
```

## Part 2: Data Flow and Versioning

### Request Lineage Tracking

```python
class RequestLineage:
    """Track complete lineage of evaluation request."""

    def __init__(self, db_connection):
        self.db = db_connection

    def create_lineage_record(self, request_id: str, request_data: Dict) -> Dict:
        """Create complete lineage record."""

        lineage = {
            'request_id': request_id,
            'timestamp': datetime.now().isoformat(),
            'model_name': request_data.get('model'),
            'model_version': request_data.get('model_version'),
            'dataset_name': request_data.get('dataset'),
            'dataset_version': request_data.get('dataset_version'),
            'prompt': request_data.get('prompt'),
            'prompt_template': request_data.get('template'),
            'response': request_data.get('response'),
            'ground_truth': None,  # Added later
            'scorer_name': None,  # Added during scoring
            'scorer_version': None,
            'score': None,
            'metadata': request_data.get('metadata', {})
        }

        self.db.insert('request_lineage', lineage)
        return lineage

    def trace_request(self, request_id: str) -> Dict:
        """Get complete lineage for a request."""

        lineage = self.db.query(
            "SELECT * FROM request_lineage WHERE request_id = ?",
            (request_id,)
        )[0]

        return {
            'request_id': request_id,
            'model': {
                'name': lineage['model_name'],
                'version': lineage['model_version']
            },
            'dataset': {
                'name': lineage['dataset_name'],
                'version': lineage['dataset_version']
            },
            'prompt': lineage['prompt'],
            'response': lineage['response'],
            'ground_truth': lineage['ground_truth'],
            'scoring': {
                'scorer': lineage['scorer_name'],
                'version': lineage['scorer_version'],
                'score': lineage['score']
            },
            'metadata': lineage['metadata']
        }
```

### Version Control for Models and Datasets

```python
class VersionManagement:
    """Manage versions of models and evaluation datasets."""

    def __init__(self, db_connection):
        self.db = db_connection

    def register_model_version(self, model_name: str, version: str,
                              config: Dict, metrics: Dict = None):
        """Register a new model version."""

        record = {
            'model_name': model_name,
            'version': version,
            'registered_date': datetime.now().isoformat(),
            'config': json.dumps(config),
            'baseline_metrics': json.dumps(metrics) if metrics else None
        }

        self.db.insert('model_versions', record)

    def register_dataset_version(self, dataset_name: str, version: str,
                                record_count: int, schema: Dict = None):
        """Register a new dataset version."""

        record = {
            'dataset_name': dataset_name,
            'version': version,
            'registered_date': datetime.now().isoformat(),
            'record_count': record_count,
            'schema': json.dumps(schema) if schema else None
        }

        self.db.insert('dataset_versions', record)

    def get_model_history(self, model_name: str) -> List[Dict]:
        """Get version history for a model."""

        return self.db.query(
            "SELECT * FROM model_versions WHERE model_name = ? ORDER BY registered_date DESC",
            (model_name,)
        )

    def compare_versions(self, model_name: str, version1: str, version2: str) -> Dict:
        """Compare two model versions."""

        v1 = self.db.query(
            "SELECT * FROM model_versions WHERE model_name = ? AND version = ?",
            (model_name, version1)
        )[0]

        v2 = self.db.query(
            "SELECT * FROM model_versions WHERE model_name = ? AND version = ?",
            (model_name, version2)
        )[0]

        return {
            'model': model_name,
            'version1': version1,
            'version2': version2,
            'config_changes': self._compute_diff(v1['config'], v2['config']),
            'metric_changes': self._compute_diff(v1['baseline_metrics'], v2['baseline_metrics'])
        }

    def _compute_diff(self, config1: str, config2: str) -> Dict:
        """Compute differences between configs."""

        c1 = json.loads(config1) if config1 else {}
        c2 = json.loads(config2) if config2 else {}

        diff = {}
        for key in set(list(c1.keys()) + list(c2.keys())):
            if c1.get(key) != c2.get(key):
                diff[key] = {'old': c1.get(key), 'new': c2.get(key)}

        return diff
```

## Part 3: Scaling and Performance

### Parallel Evaluation Execution

```python
class ParallelEvaluator:
    """Run evaluations in parallel for throughput."""

    def __init__(self, num_workers: int = 8):
        self.num_workers = num_workers
        self.executor = ThreadPoolExecutor(max_workers=num_workers)

    def evaluate_batch(self, items: List[Dict], scorer_fn) -> List[Dict]:
        """Evaluate multiple items in parallel."""

        futures = []
        for item in items:
            future = self.executor.submit(scorer_fn, item)
            futures.append(future)

        results = []
        for future in as_completed(futures):
            try:
                result = future.result(timeout=30)  # 30 second timeout per item
                results.append(result)
            except Exception as e:
                print(f"Evaluation failed: {e}")

        return results

    def map_reduce_aggregation(self, results: List[Dict]) -> Dict:
        """Aggregate results using map-reduce pattern."""

        # Map: Compute per-model metrics
        model_results = {}
        for result in results:
            model = result['model']
            if model not in model_results:
                model_results[model] = []
            model_results[model].append(result)

        # Reduce: Aggregate to final metrics
        aggregated = {}
        for model, scores in model_results.items():
            aggregated[model] = {
                'mean_score': np.mean([s['score'] for s in scores]),
                'std_dev': np.std([s['score'] for s in scores]),
                'count': len(scores)
            }

        return aggregated
```

### Cost Management

```python
class CostOptimizer:
    """Optimize evaluation costs while maintaining quality."""

    @staticmethod
    def determine_sample_rate(monthly_volume: int,
                             cost_budget: float,
                             cost_per_eval: float) -> float:
        """
        Determine sampling rate given budget constraints.

        sample_rate = (budget / monthly_volume) / cost_per_eval
        """

        max_evals = cost_budget / cost_per_eval
        sample_rate = max_evals / monthly_volume

        # Cap at 100%
        return min(1.0, sample_rate)

    @staticmethod
    def prioritize_evaluations(items: List[Dict],
                              priority_rules: Dict) -> List[Dict]:
        """Prioritize which items to evaluate given cost constraints."""

        scored_items = []

        for item in items:
            priority_score = 0

            # High-value requests (from high-revenue customers)
            if item.get('customer_tier') == 'premium':
                priority_score += priority_rules.get('premium_weight', 100)

            # Uncertain predictions (model confidence < 60%)
            if item.get('confidence', 1.0) < 0.60:
                priority_score += priority_rules.get('uncertain_weight', 50)

            # Error cases
            if item.get('error'):
                priority_score += priority_rules.get('error_weight', 75)

            scored_items.append({'item': item, 'priority': priority_score})

        # Sort by priority descending
        return [x['item'] for x in sorted(scored_items, key=lambda x: x['priority'], reverse=True)]
```

## Part 4: Monitoring and Alerting

### Dashboard Metrics

```python
class DashboardMetrics:
    """Key metrics for operations dashboard."""

    def __init__(self, result_store: ResultStore):
        self.store = result_store

    def get_dashboard_data(self, hours: int = 24) -> Dict:
        """Get all dashboard metrics."""

        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)

        models = ['gpt-4o', 'claude-sonnet-4.6', 'gemini-3-flash']

        dashboard = {
            'time_range': {
                'start': start_time.isoformat(),
                'end': end_time.isoformat()
            },
            'models': {},
            'summary': {}
        }

        for model in models:
            metrics = self.store.compute_model_metrics(
                model,
                start_date=start_time.isoformat(),
                end_date=end_time.isoformat()
            )
            dashboard['models'][model] = metrics

        # Compute summary
        all_accuracies = [m['accuracy'] for m in dashboard['models'].values()
                         if m.get('accuracy')]
        if all_accuracies:
            dashboard['summary']['best_model'] = max(
                dashboard['models'].items(),
                key=lambda x: x[1].get('accuracy', 0)
            )[0]
            dashboard['summary']['avg_accuracy'] = sum(all_accuracies) / len(all_accuracies)

        return dashboard
```

## Part 5: Architecture Diagram (Mermaid)

```
graph TD
    A["Production System<br/>(LLM Inference)"] -->|Sample Requests| B["Evaluation Queue"]
    A -->|Send Response| C["User"]

    B -->|Get Pending Items| D["Scorer Service"]
    E["Ground Truth<br/>(Manual Labels)"] -->|Add Labels| B

    D -->|Run Automated Scorers| F["Quality Scorers"]
    D -->|Track Costs| G["Cost Tracker"]
    D -->|Record Latency| H["Latency Monitor"]

    F -->|Store Results| I["Result Store<br/>(PostgreSQL)"]
    G -->|Store Results| I
    H -->|Store Results| I

    I -->|Query Metrics| J["Analysis Engine"]
    I -->|Check Thresholds| K["Alert System"]
    I -->|Visualize| L["Dashboard"]

    J -->|Detect Drift| M["Drift Detector"]
    M -->|Alert if Detected| K

    K -->|Critical Alert| N["Slack/PagerDuty"]
    L -->|Display Metrics| C

    I -->|Lineage| O["Version Control<br/>(Models/Datasets)"]
```

## Summary

A production-grade EvalOps architecture enables:

1. **Scalable evaluation:** Process thousands of requests per second
2. **Cost control:** Monitor and optimize evaluation spending
3. **Complete traceability:** Link every result to input versions
4. **Automated quality assurance:** Continuous monitoring and alerts
5. **Historical analysis:** Compare performance across model versions
6. **Decision support:** Dashboards and reports for model selection

## Implementation Checklist

- [ ] Set up evaluation queue infrastructure (Kafka/SQS)
- [ ] Build result store database (PostgreSQL recommended)
- [ ] Implement cost tracking system
- [ ] Create dashboard frontend
- [ ] Set up alert channels (Slack, PagerDuty)
- [ ] Implement drift detection
- [ ] Build version control for models and datasets
- [ ] Test scalability to production volumes
- [ ] Document runbooks for common issues
- [ ] Train operations team

## Key Technologies

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Queue | Kafka/SQS | Durability and scalability |
| Result Store | PostgreSQL | ACID compliance, powerful queries |
| Cache | Redis | Fast metric lookups |
| Dashboard | Grafana/Tableau | Rich visualization |
| Alerts | Datadog/Splunk | Comprehensive monitoring |
| Computation | Spark/Dask | Parallel processing |
| Orchestration | Airflow/Dagster | Scheduled evaluations |

## Next Steps

1. Start with minimal viable EvalOps (queue + store)
2. Add automated metrics computation
3. Integrate dashboards and alerting
4. Expand to parallel evaluation
5. Implement advanced features (drift detection, version control)
