import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from typing import Dict, List, Any
from llm_eval_framework.judges.base import BaseJudge, JudgeOutput
from llm_eval_framework.judges.rubric import RubricJudge, RubricDimension
from llm_eval_framework.judges.pairwise import PairwiseJudge
from llm_eval_framework.judges.panel import MultiJudgePanel, VotingStrategy
from llm_eval_framework.judges.constitutional import ConstitutionalAIJudge, Principle


class TestBaseJudge(unittest.TestCase):
    """Test BaseJudge abstract class functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_llm = Mock()
        self.sample_output = JudgeOutput(
            score=8.5,
            reasoning="Response is accurate and complete",
            raw_response="Score: 8.5/10\nReasoning: Response is accurate"
        )

    def test_judge_output_creation(self):
        """Test JudgeOutput dataclass initialization"""
        output = JudgeOutput(
            score=7.0,
            reasoning="Good response",
            raw_response="Raw text"
        )
        self.assertEqual(output.score, 7.0)
        self.assertEqual(output.reasoning, "Good response")
        self.assertEqual(output.raw_response, "Raw text")

    def test_judge_output_with_metadata(self):
        """Test JudgeOutput with additional metadata"""
        output = JudgeOutput(
            score=8.0,
            reasoning="Excellent",
            raw_response="Response",
            metadata={"model": "gpt-4", "tokens": 150}
        )
        self.assertIsNotNone(output.metadata)
        self.assertEqual(output.metadata["model"], "gpt-4")


class TestRubricJudge(unittest.TestCase):
    """Test RubricJudge with dimension-based scoring"""

    def setUp(self):
        """Set up test fixtures"""
        self.dimensions = [
            RubricDimension(name="accuracy", weight=0.4, scale=10),
            RubricDimension(name="relevance", weight=0.3, scale=10),
            RubricDimension(name="clarity", weight=0.3, scale=10)
        ]
        self.judge = RubricJudge(
            model="gpt-4o-mini",
            dimensions=self.dimensions,
            temperature=0.7
        )

    @patch('llm_eval_framework.judges.rubric.litellm.completion')
    def test_rubric_judge_evaluate(self, mock_completion):
        """Test basic rubric evaluation"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "accuracy": 8,
                "relevance": 7,
                "clarity": 9,
                "reasoning": "Well-structured response"
            })))]
        )

        result = self.judge.evaluate(
            prompt="Explain machine learning",
            response="Machine learning is a subset of AI...",
            reference="ML reference text"
        )

        self.assertIsNotNone(result)
        self.assertGreater(result.score, 0)
        self.assertIsNotNone(result.reasoning)

    @patch('llm_eval_framework.judges.rubric.litellm.completion')
    def test_rubric_weighted_scoring(self, mock_completion):
        """Test weighted dimension scoring"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "accuracy": 10,
                "relevance": 10,
                "clarity": 10,
                "reasoning": "Perfect response"
            })))]
        )

        result = self.judge.evaluate(
            prompt="Test",
            response="Response"
        )

        self.assertEqual(result.score, 10.0)

    @patch('llm_eval_framework.judges.rubric.litellm.completion')
    def test_rubric_with_partial_scores(self, mock_completion):
        """Test rubric with mixed dimension scores"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "accuracy": 6,
                "relevance": 8,
                "clarity": 7,
                "reasoning": "Mixed quality"
            })))]
        )

        result = self.judge.evaluate(
            prompt="Test",
            response="Response"
        )

        expected_score = (6 * 0.4 + 8 * 0.3 + 7 * 0.3)
        self.assertAlmostEqual(result.score, expected_score, places=1)

    @patch('llm_eval_framework.judges.rubric.litellm.completion')
    def test_invalid_json_handling(self, mock_completion):
        """Test handling of invalid JSON response"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content="Not valid JSON"))]
        )

        with self.assertRaises(ValueError):
            self.judge.evaluate(
                prompt="Test",
                response="Response"
            )


class TestPairwiseJudge(unittest.TestCase):
    """Test PairwiseJudge for comparative evaluation"""

    def setUp(self):
        """Set up test fixtures"""
        self.judge = PairwiseJudge(
            model="gpt-4o-mini",
            temperature=0.7
        )

    @patch('llm_eval_framework.judges.pairwise.litellm.completion')
    def test_pairwise_comparison_a_wins(self, mock_completion):
        """Test pairwise comparison where A wins"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "winner": "A",
                "confidence": 0.85,
                "reasoning": "A is more accurate"
            })))]
        )

        result = self.judge.evaluate(
            prompt="Which response is better?",
            response_a="Response A with good content",
            response_b="Response B with poor content"
        )

        self.assertEqual(result.score, 1.0)
        self.assertIn("A", result.reasoning)

    @patch('llm_eval_framework.judges.pairwise.litellm.completion')
    def test_pairwise_comparison_b_wins(self, mock_completion):
        """Test pairwise comparison where B wins"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "winner": "B",
                "confidence": 0.92,
                "reasoning": "B is superior"
            })))]
        )

        result = self.judge.evaluate(
            prompt="Compare responses",
            response_a="Mediocre",
            response_b="Excellent response"
        )

        self.assertEqual(result.score, 0.0)

    @patch('llm_eval_framework.judges.pairwise.litellm.completion')
    def test_pairwise_comparison_tie(self, mock_completion):
        """Test pairwise comparison resulting in tie"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "winner": "TIE",
                "confidence": 0.50,
                "reasoning": "Both responses are similar"
            })))]
        )

        result = self.judge.evaluate(
            prompt="Compare",
            response_a="Response",
            response_b="Response"
        )

        self.assertEqual(result.score, 0.5)

    @patch('llm_eval_framework.judges.pairwise.litellm.completion')
    def test_position_bias_detection(self, mock_completion):
        """Test position bias detection with reversed positions"""
        # First call: A first, B second
        mock_completion.side_effect = [
            MagicMock(choices=[MagicMock(message=MagicMock(content=json.dumps({
                "winner": "A",
                "confidence": 0.8,
                "reasoning": "A is better"
            })))]),
            # Second call: B first, A second
            MagicMock(choices=[MagicMock(message=MagicMock(content=json.dumps({
                "winner": "B",
                "confidence": 0.8,
                "reasoning": "B is better"
            })))])
        ]

        result1 = self.judge.evaluate(
            prompt="Compare",
            response_a="Strong response",
            response_b="Weak response"
        )

        result2 = self.judge.evaluate(
            prompt="Compare",
            response_a="Weak response",
            response_b="Strong response"
        )

        self.assertNotEqual(result1.score, result2.score)


class TestMultiJudgePanel(unittest.TestCase):
    """Test MultiJudgePanel aggregation strategies"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_judges = [Mock() for _ in range(3)]

    def test_majority_voting(self):
        """Test majority voting strategy"""
        # Setup: 2 votes for A (1.0), 1 vote for B (0.0)
        for judge in self.mock_judges[:2]:
            judge.evaluate.return_value = JudgeOutput(score=1.0, reasoning="A wins")
        self.mock_judges[2].evaluate.return_value = JudgeOutput(score=0.0, reasoning="B wins")

        panel = MultiJudgePanel(
            judges=self.mock_judges,
            voting_strategy=VotingStrategy.MAJORITY
        )

        result = panel.evaluate(
            prompt="Test",
            response_a="A",
            response_b="B"
        )

        self.assertEqual(result.score, 1.0)

    def test_average_voting(self):
        """Test average voting strategy"""
        scores = [1.0, 0.5, 0.0]
        for judge, score in zip(self.mock_judges, scores):
            judge.evaluate.return_value = JudgeOutput(score=score, reasoning="")

        panel = MultiJudgePanel(
            judges=self.mock_judges,
            voting_strategy=VotingStrategy.AVERAGE
        )

        result = panel.evaluate(
            prompt="Test",
            response_a="A",
            response_b="B"
        )

        self.assertAlmostEqual(result.score, 0.5, places=2)

    def test_weighted_voting(self):
        """Test weighted voting strategy"""
        scores = [0.8, 0.6, 0.4]
        weights = [0.5, 0.3, 0.2]

        for judge, score in zip(self.mock_judges, scores):
            judge.evaluate.return_value = JudgeOutput(score=score, reasoning="")

        panel = MultiJudgePanel(
            judges=self.mock_judges,
            voting_strategy=VotingStrategy.WEIGHTED,
            weights=weights
        )

        result = panel.evaluate(
            prompt="Test",
            response_a="A",
            response_b="B"
        )

        expected = sum(s * w for s, w in zip(scores, weights))
        self.assertAlmostEqual(result.score, expected, places=2)

    def test_consensus_voting(self):
        """Test consensus voting strategy"""
        # All judges agree on score 0.9
        for judge in self.mock_judges:
            judge.evaluate.return_value = JudgeOutput(score=0.9, reasoning="Consensus")

        panel = MultiJudgePanel(
            judges=self.mock_judges,
            voting_strategy=VotingStrategy.CONSENSUS
        )

        result = panel.evaluate(
            prompt="Test",
            response_a="A",
            response_b="B"
        )

        self.assertEqual(result.score, 0.9)


class TestConstitutionalAIJudge(unittest.TestCase):
    """Test ConstitutionalAIJudge for principle-based evaluation"""

    def setUp(self):
        """Set up test fixtures"""
        self.principles = [
            Principle(
                name="harmlessness",
                description="Response should not cause harm"
            ),
            Principle(
                name="honesty",
                description="Response should be truthful"
            ),
            Principle(
                name="helpfulness",
                description="Response should be helpful"
            )
        ]
        self.judge = ConstitutionalAIJudge(
            model="gpt-4o-mini",
            principles=self.principles
        )

    @patch('llm_eval_framework.judges.constitutional.litellm.completion')
    def test_constitutional_evaluation(self, mock_completion):
        """Test constitutional AI evaluation"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "harmlessness": 1.0,
                "honesty": 0.95,
                "helpfulness": 0.9,
                "violations": [],
                "reasoning": "Response adheres to principles"
            })))]
        )

        result = self.judge.evaluate(
            prompt="Help with homework",
            response="Here's how to solve this problem..."
        )

        self.assertGreater(result.score, 0)
        self.assertIsNotNone(result.reasoning)

    @patch('llm_eval_framework.judges.constitutional.litellm.completion')
    def test_constitutional_violation_detection(self, mock_completion):
        """Test violation detection"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "harmlessness": 0.2,
                "honesty": 0.1,
                "helpfulness": 0.5,
                "violations": ["violates_harmlessness", "violates_honesty"],
                "reasoning": "Response contains harmful and false content"
            })))]
        )

        result = self.judge.evaluate(
            prompt="Dangerous request",
            response="Harmful response"
        )

        self.assertLess(result.score, 0.5)
        self.assertIn("harmful", result.reasoning.lower())

    @patch('llm_eval_framework.judges.constitutional.litellm.completion')
    def test_principle_weighted_scoring(self, mock_completion):
        """Test principle-weighted scoring"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "harmlessness": 1.0,
                "honesty": 1.0,
                "helpfulness": 0.8,
                "violations": [],
                "reasoning": "Good response"
            })))]
        )

        result = self.judge.evaluate(
            prompt="Test",
            response="Test response"
        )

        self.assertEqual(result.score, 1.0)


class TestJudgePromptGeneration(unittest.TestCase):
    """Test prompt template generation for judges"""

    def test_rubric_prompt_generation(self):
        """Test rubric judge prompt generation"""
        dimensions = [
            RubricDimension(name="accuracy", weight=0.5, scale=10),
            RubricDimension(name="clarity", weight=0.5, scale=10)
        ]
        judge = RubricJudge(model="gpt-4o-mini", dimensions=dimensions)

        prompt = judge.generate_prompt(
            prompt="Test question",
            response="Test response",
            reference="Test reference"
        )

        self.assertIn("accuracy", prompt.lower())
        self.assertIn("clarity", prompt.lower())
        self.assertIn("Test question", prompt)
        self.assertIn("Test response", prompt)


class TestJudgeErrorHandling(unittest.TestCase):
    """Test error handling in judges"""

    def setUp(self):
        """Set up test fixtures"""
        self.judge = RubricJudge(
            model="gpt-4o-mini",
            dimensions=[RubricDimension(name="accuracy", weight=1.0, scale=10)]
        )

    @patch('llm_eval_framework.judges.rubric.litellm.completion')
    def test_api_timeout_handling(self, mock_completion):
        """Test API timeout error handling"""
        mock_completion.side_effect = TimeoutError("API timeout")

        with self.assertRaises(TimeoutError):
            self.judge.evaluate(
                prompt="Test",
                response="Response"
            )

    @patch('llm_eval_framework.judges.rubric.litellm.completion')
    def test_api_rate_limit_handling(self, mock_completion):
        """Test API rate limit error handling"""
        mock_completion.side_effect = Exception("Rate limit exceeded")

        with self.assertRaises(Exception):
            self.judge.evaluate(
                prompt="Test",
                response="Response"
            )

    @patch('llm_eval_framework.judges.rubric.litellm.completion')
    def test_invalid_score_parsing(self, mock_completion):
        """Test handling of invalid score in response"""
        mock_completion.return_value = MagicMock(
            choices=[MagicMock(message=MagicMock(content=json.dumps({
                "accuracy": "not_a_number",
                "reasoning": "Bad score"
            })))]
        )

        with self.assertRaises((ValueError, TypeError)):
            self.judge.evaluate(
                prompt="Test",
                response="Response"
            )


if __name__ == '__main__':
    unittest.main()
