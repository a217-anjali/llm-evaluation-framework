"""LLM Evaluation Framework: Comprehensive toolkit for evaluating Large Language Models.

This package provides:
- Judge-based evaluation (rubric, pairwise, constitutional)
- Metric-based scoring (faithfulness, instruction following, safety)
- Evaluation harness with configuration and reporting
- Contamination detection
- Model selection based on Pareto optimality
- Statistical utilities and visualization
"""

__version__ = "0.1.0"
__author__ = "LLM Eval Team"

from llm_eval_framework.judges import (
    BaseJudge,
    RubricJudge,
    PairwiseJudge,
    MultiJudgePanel,
    ConstitutionalJudge,
)
from llm_eval_framework.metrics import (
    FaithfulnessScorer,
    InstructionFollowingScorer,
    CalibrationMetrics,
    CodeExecutionScorer,
    SafetyScorer,
)
from llm_eval_framework.harness import (
    EvalConfig,
    EvalRunner,
    EvalReport,
    ParallelEvalRunner,
)
from llm_eval_framework.contamination import ContaminationDetector
from llm_eval_framework.selection import ParetoSelector

__all__ = [
    "BaseJudge",
    "RubricJudge",
    "PairwiseJudge",
    "MultiJudgePanel",
    "ConstitutionalJudge",
    "FaithfulnessScorer",
    "InstructionFollowingScorer",
    "CalibrationMetrics",
    "CodeExecutionScorer",
    "SafetyScorer",
    "EvalConfig",
    "EvalRunner",
    "EvalReport",
    "ParallelEvalRunner",
    "ContaminationDetector",
    "ParetoSelector",
]
