import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
import os
import csv
from pathlib import Path
from llm_eval_framework.harness.config import EvalConfig, ModelConfig, MetricConfig
from llm_eval_framework.harness.runner import EvalRunner, ParallelEvalRunner
from llm_eval_framework.harness.report import EvalReport, EvalResult


class TestEvalConfigLoading(unittest.TestCase):
    """Test EvalConfig loading from YAML"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_load_basic_config(self):
        """Test loading basic YAML config"""
        yaml_content = """
name: basic_eval
description: Basic evaluation
models:
  - name: gpt-4o-mini
    provider: openai
    params:
      temperature: 0.7
metrics:
  - name: accuracy
    type: rubric
test_cases: 10
"""
        config_path = os.path.join(self.temp_dir, "config.yaml")
        with open(config_path, 'w') as f:
            f.write(yaml_content)

        config = EvalConfig.from_yaml(config_path)

        self.assertEqual(config.name, "basic_eval")
        self.assertEqual(len(config.models), 1)
        self.assertEqual(config.models[0].name, "gpt-4o-mini")
        self.assertEqual(len(config.metrics), 1)

    def test_load_full_config(self):
        """Test loading full configuration with all options"""
        yaml_content = """
name: full_eval
description: Full evaluation suite
models:
  - name: gpt-4o
    provider: openai
    params:
      temperature: 0.5
      max_tokens: 2000
  - name: claude-opus-4-6
    provider: anthropic
    params:
      temperature: 0.7
metrics:
  - name: accuracy
    type: rubric
    params:
      scale: 10
  - name: instruction_following
    type: instruction_following
test_cases: 100
parallel: true
num_workers: 4
timeout: 30
output_dir: /tmp/results
"""
        config_path = os.path.join(self.temp_dir, "config.yaml")
        with open(config_path, 'w') as f:
            f.write(yaml_content)

        config = EvalConfig.from_yaml(config_path)

        self.assertEqual(config.name, "full_eval")
        self.assertEqual(len(config.models), 2)
        self.assertEqual(len(config.metrics), 2)
        self.assertEqual(config.test_cases, 100)
        self.assertTrue(config.parallel)
        self.assertEqual(config.num_workers, 4)

    def test_config_validation(self):
        """Test config validation"""
        config = EvalConfig(
            name="test",
            models=[ModelConfig(name="gpt-4o-mini", provider="openai")],
            metrics=[MetricConfig(name="accuracy", type="rubric")],
            test_cases=10
        )

        self.assertIsNotNone(config)
        self.assertEqual(config.test_cases, 10)

    def test_missing_required_field(self):
        """Test handling of missing required fields"""
        yaml_content = """
name: incomplete
description: Missing models
metrics:
  - name: accuracy
"""
        config_path = os.path.join(self.temp_dir, "config.yaml")
        with open(config_path, 'w') as f:
            f.write(yaml_content)

        with self.assertRaises((ValueError, KeyError)):
            EvalConfig.from_yaml(config_path)


class TestEvalRunner(unittest.TestCase):
    """Test EvalRunner orchestration"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = EvalConfig(
            name="test_eval",
            models=[ModelConfig(name="test-model", provider="openai")],
            metrics=[MetricConfig(name="accuracy", type="rubric")],
            test_cases=5
        )
        self.runner = EvalRunner(self.config)

    @patch('llm_eval_framework.harness.runner.litellm.completion')
    def test_runner_initialization(self, mock_completion):
        """Test runner initialization"""
        self.assertEqual(self.runner.config.name, "test_eval")
        self.assertEqual(len(self.runner.config.models), 1)

    @patch('llm_eval_framework.harness.runner.litellm.completion')
    def test_evaluate_single_test_case(self, mock_completion):
        """Test evaluation of single test case"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        )

        test_case = {
            "prompt": "What is 2+2?",
            "expected": "4",
            "id": "test_1"
        }

        result = self.runner.evaluate_test_case(test_case, "test-model")

        self.assertIsNotNone(result)
        self.assertEqual(result["id"], "test_1")

    @patch('llm_eval_framework.harness.runner.litellm.completion')
    def test_runner_with_multiple_models(self, mock_completion):
        """Test running evaluation with multiple models"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Response"))]
        )

        config = EvalConfig(
            name="multi_model",
            models=[
                ModelConfig(name="model-1", provider="openai"),
                ModelConfig(name="model-2", provider="openai")
            ],
            metrics=[MetricConfig(name="accuracy", type="rubric")],
            test_cases=2
        )

        runner = EvalRunner(config)
        self.assertEqual(len(runner.config.models), 2)

    @patch('llm_eval_framework.harness.runner.litellm.completion')
    def test_evaluation_with_errors(self, mock_completion):
        """Test handling of evaluation errors"""
        mock_completion.side_effect = Exception("API Error")

        test_case = {"prompt": "Test", "id": "test_1"}

        with self.assertRaises(Exception):
            self.runner.evaluate_test_case(test_case, "test-model")

    @patch('llm_eval_framework.harness.runner.litellm.completion')
    def test_evaluation_timeout(self, mock_completion):
        """Test handling of evaluation timeout"""
        mock_completion.side_effect = TimeoutError("Request timeout")

        test_case = {"prompt": "Test", "id": "test_1"}

        with self.assertRaises(TimeoutError):
            self.runner.evaluate_test_case(test_case, "test-model")


class TestEvalReport(unittest.TestCase):
    """Test EvalReport generation and export"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.results = [
            EvalResult(
                test_case_id="test_1",
                model="gpt-4o-mini",
                metric="accuracy",
                score=0.95,
                details={"reasoning": "Correct"}
            ),
            EvalResult(
                test_case_id="test_2",
                model="gpt-4o-mini",
                metric="accuracy",
                score=0.85,
                details={"reasoning": "Mostly correct"}
            ),
            EvalResult(
                test_case_id="test_1",
                model="claude-sonnet-4-6",
                metric="accuracy",
                score=0.92,
                details={"reasoning": "Good"}
            )
        ]
        self.report = EvalReport(
            name="test_report",
            results=self.results,
            config=EvalConfig(
                name="test",
                models=[
                    ModelConfig(name="gpt-4o-mini", provider="openai"),
                    ModelConfig(name="claude-sonnet-4-6", provider="anthropic")
                ],
                metrics=[MetricConfig(name="accuracy", type="rubric")],
                test_cases=2
            )
        )

    def tearDown(self):
        """Clean up temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_report_creation(self):
        """Test report creation"""
        self.assertEqual(self.report.name, "test_report")
        self.assertEqual(len(self.report.results), 3)

    def test_report_aggregation_by_model(self):
        """Test aggregation of results by model"""
        aggregated = self.report.aggregate_by_model()

        self.assertIn("gpt-4o-mini", aggregated)
        self.assertIn("claude-sonnet-4-6", aggregated)

    def test_report_aggregation_by_metric(self):
        """Test aggregation of results by metric"""
        aggregated = self.report.aggregate_by_metric()

        self.assertIn("accuracy", aggregated)

    def test_export_to_json(self):
        """Test JSON export"""
        output_path = os.path.join(self.temp_dir, "report.json")
        self.report.export_json(output_path)

        self.assertTrue(os.path.exists(output_path))

        with open(output_path, 'r') as f:
            data = json.load(f)

        self.assertEqual(data["name"], "test_report")
        self.assertEqual(len(data["results"]), 3)

    def test_export_to_csv(self):
        """Test CSV export"""
        output_path = os.path.join(self.temp_dir, "report.csv")
        self.report.export_csv(output_path)

        self.assertTrue(os.path.exists(output_path))

        with open(output_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        self.assertEqual(len(rows), 3)
        self.assertIn("test_case_id", rows[0])
        self.assertIn("model", rows[0])
        self.assertIn("metric", rows[0])
        self.assertIn("score", rows[0])

    def test_export_to_markdown(self):
        """Test Markdown export"""
        output_path = os.path.join(self.temp_dir, "report.md")
        self.report.export_markdown(output_path)

        self.assertTrue(os.path.exists(output_path))

        with open(output_path, 'r') as f:
            content = f.read()

        self.assertIn("test_report", content)
        self.assertIn("gpt-4o-mini", content)
        self.assertIn("claude-sonnet-4-6", content)

    def test_report_statistics(self):
        """Test report statistics calculation"""
        stats = self.report.get_statistics()

        self.assertIn("mean_score", stats)
        self.assertIn("median_score", stats)
        self.assertIn("std_dev", stats)
        self.assertGreater(stats["mean_score"], 0.8)
        self.assertLess(stats["mean_score"], 1.0)

    def test_report_comparison(self):
        """Test model comparison in report"""
        comparison = self.report.compare_models()

        self.assertIn("gpt-4o-mini", comparison)
        self.assertIn("claude-sonnet-4-6", comparison)
        self.assertIn("mean_score", comparison["gpt-4o-mini"])


class TestParallelEvalRunner(unittest.TestCase):
    """Test ParallelEvalRunner concurrency"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = EvalConfig(
            name="parallel_eval",
            models=[
                ModelConfig(name="model-1", provider="openai"),
                ModelConfig(name="model-2", provider="openai"),
                ModelConfig(name="model-3", provider="openai")
            ],
            metrics=[MetricConfig(name="accuracy", type="rubric")],
            test_cases=10,
            parallel=True,
            num_workers=3
        )

    @patch('llm_eval_framework.harness.runner.litellm.completion')
    def test_parallel_runner_initialization(self, mock_completion):
        """Test parallel runner initialization"""
        runner = ParallelEvalRunner(self.config, num_workers=3)

        self.assertEqual(runner.num_workers, 3)
        self.assertEqual(runner.config.name, "parallel_eval")

    @patch('llm_eval_framework.harness.runner.litellm.completion')
    def test_parallel_evaluation_execution(self, mock_completion):
        """Test parallel evaluation execution"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Response"))]
        )

        runner = ParallelEvalRunner(self.config, num_workers=2)

        test_cases = [
            {"prompt": f"Question {i}", "id": f"test_{i}"}
            for i in range(5)
        ]

        self.assertGreater(len(test_cases), 0)

    @patch('llm_eval_framework.harness.runner.litellm.completion')
    def test_parallel_runner_with_single_worker(self, mock_completion):
        """Test parallel runner with single worker"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Response"))]
        )

        runner = ParallelEvalRunner(self.config, num_workers=1)

        self.assertEqual(runner.num_workers, 1)

    @patch('llm_eval_framework.harness.runner.litellm.completion')
    def test_parallel_runner_error_handling(self, mock_completion):
        """Test error handling in parallel runner"""
        mock_completion.side_effect = Exception("API Error")

        runner = ParallelEvalRunner(self.config, num_workers=2)

        with self.assertRaises(Exception):
            test_cases = [{"prompt": "Test", "id": "test_1"}]
            runner.evaluate_batch(test_cases, "model-1")

    @patch('llm_eval_framework.harness.runner.litellm.completion')
    def test_parallel_runner_result_aggregation(self, mock_completion):
        """Test result aggregation from parallel execution"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Response"))]
        )

        runner = ParallelEvalRunner(self.config, num_workers=2)

        test_cases = [
            {"prompt": "Q1", "id": "test_1"},
            {"prompt": "Q2", "id": "test_2"},
            {"prompt": "Q3", "id": "test_3"}
        ]

        self.assertEqual(len(test_cases), 3)


class TestEvalResultDataClass(unittest.TestCase):
    """Test EvalResult dataclass"""

    def test_eval_result_creation(self):
        """Test EvalResult creation"""
        result = EvalResult(
            test_case_id="test_1",
            model="gpt-4o-mini",
            metric="accuracy",
            score=0.95,
            details={"reasoning": "Correct"}
        )

        self.assertEqual(result.test_case_id, "test_1")
        self.assertEqual(result.model, "gpt-4o-mini")
        self.assertEqual(result.score, 0.95)

    def test_eval_result_with_error(self):
        """Test EvalResult with error information"""
        result = EvalResult(
            test_case_id="test_1",
            model="gpt-4o-mini",
            metric="accuracy",
            score=0.0,
            error="API timeout"
        )

        self.assertIsNotNone(result.error)
        self.assertEqual(result.error, "API timeout")

    def test_eval_result_serialization(self):
        """Test EvalResult serialization"""
        result = EvalResult(
            test_case_id="test_1",
            model="gpt-4o-mini",
            metric="accuracy",
            score=0.95,
            details={"reasoning": "Good"}
        )

        serialized = result.to_dict()

        self.assertEqual(serialized["test_case_id"], "test_1")
        self.assertEqual(serialized["score"], 0.95)


class TestEvalConfigModels(unittest.TestCase):
    """Test configuration model classes"""

    def test_model_config_creation(self):
        """Test ModelConfig creation"""
        config = ModelConfig(
            name="gpt-4o-mini",
            provider="openai",
            params={"temperature": 0.7, "max_tokens": 2000}
        )

        self.assertEqual(config.name, "gpt-4o-mini")
        self.assertEqual(config.provider, "openai")
        self.assertEqual(config.params["temperature"], 0.7)

    def test_metric_config_creation(self):
        """Test MetricConfig creation"""
        config = MetricConfig(
            name="accuracy",
            type="rubric",
            params={"scale": 10}
        )

        self.assertEqual(config.name, "accuracy")
        self.assertEqual(config.type, "rubric")
        self.assertEqual(config.params["scale"], 10)

    def test_eval_config_defaults(self):
        """Test EvalConfig with default values"""
        config = EvalConfig(
            name="test",
            models=[ModelConfig(name="model-1", provider="openai")],
            metrics=[MetricConfig(name="accuracy", type="rubric")],
            test_cases=10
        )

        self.assertEqual(config.parallel, False)
        self.assertEqual(config.num_workers, 1)
        self.assertGreater(config.timeout, 0)


if __name__ == '__main__':
    unittest.main()
