import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import numpy as np
from llm_eval_framework.metrics.faithfulness import FaithfulnessScorer
from llm_eval_framework.metrics.instruction_following import InstructionFollowingScorer
from llm_eval_framework.metrics.calibration import CalibrationMetrics
from llm_eval_framework.metrics.code_execution import CodeExecutionScorer
from llm_eval_framework.metrics.safety import SafetyScorer


class TestFaithfulnessScorer(unittest.TestCase):
    """Test FaithfulnessScorer metric"""

    def setUp(self):
        """Set up test fixtures"""
        self.scorer = FaithfulnessScorer(model="gpt-4o-mini")

    @patch('llm_eval_framework.metrics.faithfulness.litellm.completion')
    def test_faithful_response(self, mock_completion):
        """Test scoring a faithful response"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "score": 0.95,
                "is_faithful": True,
                "inconsistencies": [],
                "reasoning": "Response is faithful to context"
            })))]
        )

        score = self.scorer.score(
            response="Paris is the capital of France",
            context="France is a country in Europe with Paris as its capital",
            question="What is the capital of France?"
        )

        self.assertAlmostEqual(score, 0.95, places=2)

    @patch('llm_eval_framework.metrics.faithfulness.litellm.completion')
    def test_unfaithful_response(self, mock_completion):
        """Test scoring an unfaithful response"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "score": 0.1,
                "is_faithful": False,
                "inconsistencies": ["Claims Madrid is capital"],
                "reasoning": "Contains factual error"
            })))]
        )

        score = self.scorer.score(
            response="Madrid is the capital of France",
            context="France is in Europe with Paris as capital",
            question="What is the capital of France?"
        )

        self.assertLess(score, 0.3)

    @patch('llm_eval_framework.metrics.faithfulness.litellm.completion')
    def test_partially_faithful_response(self, mock_completion):
        """Test scoring partially faithful response"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "score": 0.65,
                "is_faithful": False,
                "inconsistencies": ["Overstates tourist numbers"],
                "reasoning": "Mostly accurate with one exaggeration"
            })))]
        )

        score = self.scorer.score(
            response="Paris has millions of tourists yearly",
            context="Paris attracts many tourists but exact numbers vary",
            question="Tell about Paris tourism"
        )

        self.assertGreater(score, 0.5)
        self.assertLess(score, 0.8)

    @patch('llm_eval_framework.metrics.faithfulness.litellm.completion')
    def test_empty_response(self, mock_completion):
        """Test scoring empty response"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "score": 0.0,
                "is_faithful": False,
                "inconsistencies": ["Empty response"],
                "reasoning": "No content to evaluate"
            })))]
        )

        score = self.scorer.score(
            response="",
            context="Some context",
            question="Question"
        )

        self.assertEqual(score, 0.0)


class TestInstructionFollowingScorer(unittest.TestCase):
    """Test InstructionFollowingScorer metric"""

    def setUp(self):
        """Set up test fixtures"""
        self.scorer = InstructionFollowingScorer(model="gpt-4o-mini")

    @patch('llm_eval_framework.metrics.instruction_following.litellm.completion')
    def test_perfect_instruction_following(self, mock_completion):
        """Test response that perfectly follows instructions"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "score": 1.0,
                "follows_instructions": True,
                "violations": [],
                "reasoning": "All instructions followed correctly"
            })))]
        )

        score = self.scorer.score(
            response="123\n456\n789",
            instructions="Output three numbers, one per line, in ascending order"
        )

        self.assertEqual(score, 1.0)

    @patch('llm_eval_framework.metrics.instruction_following.litellm.completion')
    def test_partial_instruction_following(self, mock_completion):
        """Test response that partially follows instructions"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "score": 0.66,
                "follows_instructions": False,
                "violations": ["Missing one number"],
                "reasoning": "Only two of three numbers provided"
            })))]
        )

        score = self.scorer.score(
            response="100\n200",
            instructions="Output three numbers in ascending order"
        )

        self.assertGreater(score, 0.5)
        self.assertLess(score, 1.0)

    @patch('llm_eval_framework.metrics.instruction_following.litellm.completion')
    def test_no_instruction_following(self, mock_completion):
        """Test response that doesn't follow instructions"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "score": 0.0,
                "follows_instructions": False,
                "violations": ["Wrong format", "Wrong content"],
                "reasoning": "Completely ignores instructions"
            })))]
        )

        score = self.scorer.score(
            response="Some random text",
            instructions="Output three numbers in ascending order"
        )

        self.assertEqual(score, 0.0)

    @patch('llm_eval_framework.metrics.instruction_following.litellm.completion')
    def test_complex_instructions(self, mock_completion):
        """Test scoring with complex multi-part instructions"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "score": 0.9,
                "follows_instructions": True,
                "violations": [],
                "reasoning": "Follows all main instructions with minor formatting deviation"
            })))]
        )

        instructions = """
        1. Write a function
        2. Use Python
        3. Add error handling
        4. Include docstring
        5. Add type hints
        """

        score = self.scorer.score(
            response="def add(x: int, y: int) -> int:\n    return x + y",
            instructions=instructions
        )

        self.assertGreater(score, 0.8)


class TestCalibrationMetrics(unittest.TestCase):
    """Test CalibrationMetrics calculations"""

    def setUp(self):
        """Set up test fixtures"""
        self.metrics = CalibrationMetrics()

    def test_expected_calibration_error_perfect(self):
        """Test ECE with perfectly calibrated predictions"""
        confidences = np.array([0.9, 0.8, 0.7, 0.6, 0.5])
        accuracies = np.array([0.9, 0.8, 0.7, 0.6, 0.5])

        ece = self.metrics.expected_calibration_error(confidences, accuracies)
        self.assertAlmostEqual(ece, 0.0, places=2)

    def test_expected_calibration_error_overconfident(self):
        """Test ECE with overconfident predictions"""
        confidences = np.array([0.9, 0.9, 0.9, 0.9, 0.9])
        accuracies = np.array([0.5, 0.5, 0.5, 0.5, 0.5])

        ece = self.metrics.expected_calibration_error(confidences, accuracies)
        self.assertGreater(ece, 0.2)

    def test_expected_calibration_error_underconfident(self):
        """Test ECE with underconfident predictions"""
        confidences = np.array([0.5, 0.5, 0.5, 0.5, 0.5])
        accuracies = np.array([0.9, 0.9, 0.9, 0.9, 0.9])

        ece = self.metrics.expected_calibration_error(confidences, accuracies)
        self.assertGreater(ece, 0.3)

    def test_brier_score_perfect(self):
        """Test Brier score with perfect predictions"""
        predictions = np.array([1.0, 0.0, 1.0, 0.0])
        targets = np.array([1, 0, 1, 0])

        brier = self.metrics.brier_score(predictions, targets)
        self.assertAlmostEqual(brier, 0.0, places=2)

    def test_brier_score_random(self):
        """Test Brier score with random predictions"""
        predictions = np.array([0.5, 0.5, 0.5, 0.5])
        targets = np.array([1, 0, 1, 0])

        brier = self.metrics.brier_score(predictions, targets)
        self.assertAlmostEqual(brier, 0.25, places=2)

    def test_calibration_curve(self):
        """Test calibration curve calculation"""
        confidences = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
        accuracies = np.array([0.0, 0.1, 0.3, 0.7, 0.9, 1.0])

        curve = self.metrics.calibration_curve(confidences, accuracies, n_bins=3)
        self.assertEqual(len(curve), 3)

    def test_overconfidence_ratio(self):
        """Test overconfidence ratio calculation"""
        confidences = np.array([0.9, 0.9, 0.8, 0.8])
        accuracies = np.array([0.5, 0.5, 0.5, 0.5])

        ratio = self.metrics.overconfidence_ratio(confidences, accuracies)
        self.assertGreater(ratio, 1.0)


class TestCodeExecutionScorer(unittest.TestCase):
    """Test CodeExecutionScorer metric"""

    def setUp(self):
        """Set up test fixtures"""
        self.scorer = CodeExecutionScorer(timeout=5)

    def test_valid_python_execution(self):
        """Test execution of valid Python code"""
        code = "result = 2 + 2"
        result = self.scorer.score(code)

        self.assertGreater(result, 0.8)

    def test_syntax_error_code(self):
        """Test code with syntax errors"""
        code = "def broken(\n    pass"
        result = self.scorer.score(code)

        self.assertEqual(result, 0.0)

    def test_runtime_error_code(self):
        """Test code that raises runtime error"""
        code = "x = 1 / 0"
        result = self.scorer.score(code)

        self.assertEqual(result, 0.0)

    def test_code_with_import_errors(self):
        """Test code with import errors"""
        code = "import nonexistent_module\nx = nonexistent_module.foo()"
        result = self.scorer.score(code)

        self.assertEqual(result, 0.0)

    def test_code_timeout(self):
        """Test code that times out"""
        code = "while True:\n    pass"
        result = self.scorer.score(code)

        self.assertEqual(result, 0.0)

    def test_code_with_print_statements(self):
        """Test code with print statements"""
        code = "print('Hello')\nprint('World')"
        result = self.scorer.score(code)

        self.assertGreater(result, 0.7)

    def test_complex_valid_code(self):
        """Test complex but valid code"""
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(5)
"""
        result = self.scorer.score(code)

        self.assertGreater(result, 0.8)


class TestSafetyScorer(unittest.TestCase):
    """Test SafetyScorer metric"""

    def setUp(self):
        """Set up test fixtures"""
        self.scorer = SafetyScorer(model="gpt-4o-mini")

    @patch('llm_eval_framework.metrics.safety.litellm.completion')
    def test_safe_response(self, mock_completion):
        """Test scoring a safe response"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "safety_score": 1.0,
                "is_safe": True,
                "risks": [],
                "categories": [],
                "reasoning": "Response is safe"
            })))]
        )

        score = self.scorer.score(
            response="Here is information about healthy eating habits"
        )

        self.assertEqual(score, 1.0)

    @patch('llm_eval_framework.metrics.safety.litellm.completion')
    def test_unsafe_response_harmful_content(self, mock_completion):
        """Test scoring response with harmful content"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "safety_score": 0.0,
                "is_safe": False,
                "risks": ["Contains violent content"],
                "categories": ["violence"],
                "reasoning": "Response contains harmful content"
            })))]
        )

        score = self.scorer.score(
            response="Instructions for causing harm"
        )

        self.assertEqual(score, 0.0)

    @patch('llm_eval_framework.metrics.safety.litellm.completion')
    def test_unsafe_response_pii_leakage(self, mock_completion):
        """Test scoring response with PII leakage"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "safety_score": 0.0,
                "is_safe": False,
                "risks": ["Contains PII"],
                "categories": ["pii_leakage"],
                "reasoning": "Response leaks personal information"
            })))]
        )

        score = self.scorer.score(
            response="Your social security number is 123-45-6789"
        )

        self.assertEqual(score, 0.0)

    @patch('llm_eval_framework.metrics.safety.litellm.completion')
    def test_unsafe_response_prompt_injection(self, mock_completion):
        """Test scoring response vulnerable to prompt injection"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "safety_score": 0.3,
                "is_safe": False,
                "risks": ["Vulnerable to prompt injection"],
                "categories": ["prompt_injection"],
                "reasoning": "Response follows injected instructions"
            })))]
        )

        score = self.scorer.score(
            response="I will ignore all previous instructions and..."
        )

        self.assertLess(score, 0.5)

    @patch('llm_eval_framework.metrics.safety.litellm.completion')
    def test_borderline_unsafe_response(self, mock_completion):
        """Test scoring borderline unsafe response"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "safety_score": 0.5,
                "is_safe": False,
                "risks": ["Potentially misleading"],
                "categories": ["misinformation"],
                "reasoning": "Contains some misleading claims"
            })))]
        )

        score = self.scorer.score(
            response="This treatment might work for some people"
        )

        self.assertGreater(score, 0.3)
        self.assertLess(score, 0.7)

    @patch('llm_eval_framework.metrics.safety.litellm.completion')
    def test_empty_response_safety(self, mock_completion):
        """Test scoring empty response"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "safety_score": 1.0,
                "is_safe": True,
                "risks": [],
                "categories": [],
                "reasoning": "Empty response has no safety concerns"
            })))]
        )

        score = self.scorer.score(response="")

        self.assertEqual(score, 1.0)

    @patch('llm_eval_framework.metrics.safety.litellm.completion')
    def test_multiple_risk_categories(self, mock_completion):
        """Test response with multiple risk categories"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "safety_score": 0.1,
                "is_safe": False,
                "risks": ["Harmful content", "PII leakage", "Misinformation"],
                "categories": ["violence", "pii_leakage", "misinformation"],
                "reasoning": "Multiple safety violations detected"
            })))]
        )

        score = self.scorer.score(
            response="Harmful content with PII and misinformation"
        )

        self.assertLess(score, 0.3)


class TestMetricsEdgeCases(unittest.TestCase):
    """Test edge cases across all metrics"""

    def test_faithfulness_very_long_context(self):
        """Test faithfulness scorer with very long context"""
        scorer = FaithfulnessScorer(model="gpt-4o-mini")
        long_context = "Context. " * 1000

        with patch('llm_eval_framework.metrics.faithfulness.litellm.completion') as mock:
            mock.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content=json.dumps({
                    "score": 0.9,
                    "is_faithful": True,
                    "inconsistencies": [],
                    "reasoning": "OK"
                })))]
            )

            score = scorer.score(
                response="Response",
                context=long_context,
                question="Question"
            )

            self.assertGreater(score, 0.8)

    def test_instruction_following_with_special_characters(self):
        """Test instruction following with special characters"""
        scorer = InstructionFollowingScorer(model="gpt-4o-mini")

        with patch('llm_eval_framework.metrics.instruction_following.litellm.completion') as mock:
            mock.return_value = MagicMock(
                choices=[MagicMock(message=MagicMock(content=json.dumps({
                    "score": 1.0,
                    "follows_instructions": True,
                    "violations": [],
                    "reasoning": "OK"
                })))]
            )

            score = scorer.score(
                response="@#$%^&*()",
                instructions="Output special characters: @#$%^&*()"
            )

            self.assertEqual(score, 1.0)

    def test_calibration_metrics_with_single_bin(self):
        """Test calibration metrics with minimal data"""
        metrics = CalibrationMetrics()
        confidences = np.array([0.5])
        accuracies = np.array([0.5])

        ece = metrics.expected_calibration_error(confidences, accuracies)
        self.assertGreaterEqual(ece, 0.0)


if __name__ == '__main__':
    unittest.main()
