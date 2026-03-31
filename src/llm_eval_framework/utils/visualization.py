"""Visualization utilities for evaluation results."""

from typing import Optional


def plot_radar_chart(
    scores: dict[str, float],
    title: str = "Model Evaluation Radar",
    output_path: Optional[str] = None,
) -> str:
    """Generate a radar chart for multi-dimensional scores.

    Args:
        scores: Dict of dimension -> score
        title: Chart title
        output_path: Optional path to save PNG

    Returns:
        HTML string for the chart (for notebook display)
    """
    try:
        import plotly.graph_objects as go

        categories = list(scores.keys())
        values = list(scores.values()) + [scores[categories[0]]]  # Close the loop

        fig = go.Figure(
            data=go.Scatterpolar(
                r=values,
                theta=categories + [categories[0]],
                fill='toself',
                name='Score',
            )
        )

        fig.update_layout(
            title=title,
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        )

        if output_path:
            fig.write_html(output_path)

        return fig.to_html(include_plotlyjs='cdn')

    except ImportError:
        return "<p>Install plotly to view charts: pip install plotly</p>"


def plot_pareto_frontier(
    models: list[dict],
    x_metric: str,
    y_metric: str,
    output_path: Optional[str] = None,
) -> str:
    """Generate a Pareto frontier plot.

    Args:
        models: List of model dicts with metrics
        x_metric: Metric name for x-axis
        y_metric: Metric name for y-axis
        output_path: Optional path to save PNG

    Returns:
        HTML string for the chart
    """
    try:
        import plotly.graph_objects as go

        x_values = [m.get(x_metric, 0) for m in models]
        y_values = [m.get(y_metric, 0) for m in models]
        names = [m.get("name", f"Model {i}") for i, m in enumerate(models)]

        fig = go.Figure(
            data=go.Scatter(
                x=x_values,
                y=y_values,
                mode='markers+text',
                text=names,
                textposition='top center',
                marker=dict(size=10, color=y_values, colorscale='Viridis'),
            )
        )

        fig.update_layout(
            title=f"Pareto Frontier: {x_metric} vs {y_metric}",
            xaxis_title=x_metric,
            yaxis_title=y_metric,
        )

        if output_path:
            fig.write_html(output_path)

        return fig.to_html(include_plotlyjs='cdn')

    except ImportError:
        return "<p>Install plotly to view charts: pip install plotly</p>"


def plot_confidence_intervals(
    intervals: dict[str, dict],
    output_path: Optional[str] = None,
) -> str:
    """Generate a confidence interval comparison chart.

    Args:
        intervals: Dict of name -> {point_estimate, ci_lower, ci_upper}
        output_path: Optional path to save PNG

    Returns:
        HTML string for the chart
    """
    try:
        import plotly.graph_objects as go

        names = list(intervals.keys())
        point_estimates = [intervals[n]["point_estimate"] for n in names]
        ci_lowers = [intervals[n]["ci_lower"] for n in names]
        ci_uppers = [intervals[n]["ci_upper"] for n in names]

        errors = [
            [point_estimates[i] - ci_lowers[i] for i in range(len(names))],
            [ci_uppers[i] - point_estimates[i] for i in range(len(names))],
        ]

        fig = go.Figure(
            data=go.Scatter(
                x=point_estimates,
                y=names,
                mode='markers',
                marker=dict(size=10),
                error_x=dict(
                    type='data',
                    symmetric=False,
                    array=errors[1],
                    arrayminus=errors[0],
                ),
            )
        )

        fig.update_layout(
            title="Confidence Intervals",
            xaxis_title="Score",
            yaxis_title="Model",
        )

        if output_path:
            fig.write_html(output_path)

        return fig.to_html(include_plotlyjs='cdn')

    except ImportError:
        return "<p>Install plotly to view charts: pip install plotly</p>"


def plot_score_distribution(
    scores: list[float],
    title: str = "Score Distribution",
    output_path: Optional[str] = None,
) -> str:
    """Generate a score distribution histogram.

    Args:
        scores: List of scores
        title: Chart title
        output_path: Optional path to save PNG

    Returns:
        HTML string for the chart
    """
    try:
        import plotly.graph_objects as go

        fig = go.Figure(
            data=go.Histogram(
                x=scores,
                nbinsx=30,
                name='Score',
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="Score",
            yaxis_title="Frequency",
        )

        if output_path:
            fig.write_html(output_path)

        return fig.to_html(include_plotlyjs='cdn')

    except ImportError:
        return "<p>Install plotly to view charts: pip install plotly</p>"


def plot_heatmap(
    data: list[list[float]],
    row_labels: list[str],
    col_labels: list[str],
    title: str = "Heatmap",
    output_path: Optional[str] = None,
) -> str:
    """Generate a heatmap visualization.

    Args:
        data: 2D list of values
        row_labels: Labels for rows
        col_labels: Labels for columns
        title: Chart title
        output_path: Optional path to save PNG

    Returns:
        HTML string for the chart
    """
    try:
        import plotly.graph_objects as go

        fig = go.Figure(
            data=go.Heatmap(
                z=data,
                x=col_labels,
                y=row_labels,
                colorscale='Viridis',
            )
        )

        fig.update_layout(title=title)

        if output_path:
            fig.write_html(output_path)

        return fig.to_html(include_plotlyjs='cdn')

    except ImportError:
        return "<p>Install plotly to view charts: pip install plotly</p>"
