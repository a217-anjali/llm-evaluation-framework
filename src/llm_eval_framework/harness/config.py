"""Evaluation configuration management."""

from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field, validator


class ModelConfig(BaseModel):
    """Configuration for a model to evaluate."""

    name: str = Field(..., description="Model identifier (e.g., 'gpt-4')")
    provider: str = Field(default="openai", description="Model provider")
    params: dict[str, Any] = Field(default_factory=dict, description="Model-specific parameters")


class JudgeConfig(BaseModel):
    """Configuration for a judge."""

    name: str = Field(..., description="Judge type (e.g., 'rubric', 'pairwise')")
    params: dict[str, Any] = Field(default_factory=dict, description="Judge-specific parameters")


class MetricConfig(BaseModel):
    """Configuration for a metric."""

    name: str = Field(..., description="Metric name (e.g., 'faithfulness')")
    params: dict[str, Any] = Field(default_factory=dict, description="Metric-specific parameters")


class DatasetConfig(BaseModel):
    """Configuration for evaluation dataset."""

    path: str = Field(..., description="Path to dataset file")
    format: str = Field(default="json", description="Dataset format (json, csv, etc.)")
    split: Optional[str] = Field(None, description="Dataset split to use")


class EvalConfig(BaseModel):
    """Top-level evaluation configuration."""

    name: str = Field(..., description="Evaluation run name")
    description: Optional[str] = Field(None, description="Evaluation description")

    models: list[ModelConfig] = Field(..., description="Models to evaluate")
    dataset: DatasetConfig = Field(..., description="Evaluation dataset configuration")

    judges: list[JudgeConfig] = Field(default_factory=list, description="Judges to use")
    metrics: list[MetricConfig] = Field(default_factory=list, description="Metrics to compute")

    batch_size: int = Field(default=32, description="Batch size for evaluation")
    num_workers: int = Field(default=4, description="Number of parallel workers")
    timeout: float = Field(default=30.0, description="Timeout per evaluation in seconds")

    output_dir: str = Field(default="./eval_results", description="Output directory for results")
    save_format: str = Field(default="json", description="Format for saving results")

    @validator("batch_size", "num_workers")
    def positive_values(cls, v):
        """Validate positive values."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "EvalConfig":
        """Load configuration from YAML file.

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            EvalConfig instance

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If YAML is invalid
        """
        try:
            with open(yaml_path, 'r') as f:
                data = yaml.safe_load(f)
            return cls(**data)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Config file not found: {yaml_path}") from e
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}") from e
        except Exception as e:
            raise ValueError(f"Failed to parse config: {e}") from e

    def to_yaml(self, output_path: str) -> None:
        """Save configuration to YAML file.

        Args:
            output_path: Path to save YAML file to
        """
        with open(output_path, 'w') as f:
            yaml.dump(self.dict(), f, default_flow_style=False)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation of config
        """
        return self.dict()

    def __repr__(self) -> str:
        """String representation."""
        return f"EvalConfig(name={self.name}, models={len(self.models)}, dataset={self.dataset.path})"
