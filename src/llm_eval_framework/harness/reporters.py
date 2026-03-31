"""Evaluation report generation and analysis."""

import json
import statistics
from pathlib import Path
from typing import Any, Optional

import numpy as np


class EvalReport:
    """Generates and exports evaluation reports."""

    def __init__(self, results: list[dict], config_name: str = "evaluation"):
        """Initialize the report.

        Args:
            results: List of evaluation results from EvalRunner
            config_name: Name of the evaluation configuration
        """
        self.results = results
        self.config_name = config_name

    def compute_summary_statistics(self) -> dict:
        """Compute summary statistics across all results.

        Returns:
            Dict with aggregated statistics
        """
        if not self.results:
            return {}

        summary = {
            "num_examples": len(self.results),
            "judges": {},
            "metrics": {},
        }

        # Aggregate judge scores
        judge_names = set()
        for result in self.results:
            judge_names.update(result.get("judges", {}).keys())

        for judge_name in judge_names:
            scores = []
            for result in self.results:
                if judge_name in result.get("judges", {}):
                    judge_result = result["judges"][judge_name]
                    if "score" in judge_result:
                        scores.append(judge_result["score"])

            if scores:
                summary["judges"][judge_name] = {
                    "mean": float(statistics.mean(scores)),
                    "stdev": float(statistics.stdev(scores)) if len(scores) > 1 else 0.0,
                    "min": float(min(scores)),
                    "max": float(max(scores)),
                    "median": float(statistics.median(scores)),
                }

        # Aggregate metric scores
        metric_names = set()
        for result in self.results:
            metric_names.update(result.get("metrics", {}).keys())

        for metric_name in metric_names:
            scores = []
            for result in self.results:
                if metric_name in result.get("metrics", {}):
                    metric_result = result["metrics"][metric_name]
                    if "overall_score" in metric_result:
                        scores.append(metric_result["overall_score"])

            if scores:
                summary["metrics"][metric_name] = {
                    "mean": float(statistics.mean(scores)),
                    "stdev": float(statistics.stdev(scores)) if len(scores) > 1 else 0.0,
                    "min": float(min(scores)),
                    "max": float(max(scores)),
                    "median": float(statistics.median(scores)),
                }

        return summary

    def to_json(self, output_path: str) -> None:
        """Export report to JSON.

        Args:
            output_path: Path to write JSON file
        """
        report = {
            "config_name": self.config_name,
            "summary": self.compute_summary_statistics(),
            "results": self.results,
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

    def to_csv(self, output_path: str) -> None:
        """Export report to CSV.

        Args:
            output_path: Path to write CSV file
        """
        import csv

        if not self.results:
            return

        # Flatten nested structures
        flattened = []
        for result in self.results:
            flat_result = {"example_id": result.get("example_id", "")}

            for judge_name, judge_result in result.get("judges", {}).items():
                flat_result[f"judge_{judge_name}"] = judge_result.get("score", "")

            for metric_name, metric_result in result.get("metrics", {}).items():
                flat_result[f"metric_{metric_name}"] = metric_result.get("overall_score", "")

            flattened.append(flat_result)

        if not flattened:
            return

        keys = set()
        for flat in flattened:
            keys.update(flat.keys())

        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=sorted(list(keys)))
            writer.writeheader()
            writer.writerows(flattened)

    def to_html(self, output_path: str) -> None:
        """Export report to HTML.

        Args:
            output_path: Path to write HTML file
        """
        summary = self.compute_summary_statistics()

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Evaluation Report - {self.config_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background-color: #007bff; color: white; }}
        tr:hover {{ background-color: #f5f5f5; }}
        .stat {{ color: #28a745; font-weight: bold; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }}
        .summary-card {{ background: #f9f9f9; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }}
        .summary-card h3 {{ margin-top: 0; color: #007bff; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Evaluation Report: {self.config_name}</h1>
        <p>Total examples evaluated: <span class="stat">{summary.get('num_examples', 0)}</span></p>

        <h2>Judge Performance</h2>
        <div class="summary-grid">
"""

        for judge_name, judge_stats in summary.get("judges", {}).items():
            html_content += f"""
            <div class="summary-card">
                <h3>{judge_name}</h3>
                <p>Mean Score: <span class="stat">{judge_stats['mean']:.3f}</span></p>
                <p>Median: {judge_stats['median']:.3f}</p>
                <p>Range: [{judge_stats['min']:.3f}, {judge_stats['max']:.3f}]</p>
            </div>
"""

        html_content += """
        </div>

        <h2>Metric Performance</h2>
        <div class="summary-grid">
"""

        for metric_name, metric_stats in summary.get("metrics", {}).items():
            html_content += f"""
            <div class="summary-card">
                <h3>{metric_name}</h3>
                <p>Mean Score: <span class="stat">{metric_stats['mean']:.3f}</span></p>
                <p>Median: {metric_stats['median']:.3f}</p>
                <p>Range: [{metric_stats['min']:.3f}, {metric_stats['max']:.3f}]</p>
            </div>
"""

        html_content += """
        </div>
    </div>
</body>
</html>"""

        with open(output_path, 'w') as f:
            f.write(html_content)

    def generate_comparison_table(self, metric_name: str) -> dict:
        """Generate a comparison table for a specific metric across examples.

        Args:
            metric_name: Name of the metric to compare

        Returns:
            Dict with comparison data
        """
        comparison = {
            "metric": metric_name,
            "examples": [],
        }

        for result in self.results:
            if metric_name in result.get("metrics", {}):
                example_data = {
                    "example_id": result.get("example_id"),
                    "score": result["metrics"][metric_name].get("overall_score"),
                    "details": result["metrics"][metric_name],
                }
                comparison["examples"].append(example_data)

        return comparison

    def __repr__(self) -> str:
        """String representation."""
        return f"EvalReport(config={self.config_name}, results={len(self.results)})"
