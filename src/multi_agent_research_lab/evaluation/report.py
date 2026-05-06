"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown."""

    lines = [
        "# Benchmark Report",
        "",
        "## Summary",
        "",
        "This report compares the single-agent baseline with the multi-agent workflow "
        "using the same query set. Local runs use deterministic mock LLM/search clients "
        "when API keys are absent, so latency and quality are useful for regression "
        "checks rather than production claims. Cost is computed from provider usage "
        "when available, otherwise from local token estimates and the lab pricing table.",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality | Notes |",
        "|---|---:|---:|---:|---|",
    ]
    for item in metrics:
        cost = "n/a" if item.estimated_cost_usd is None else f"{item.estimated_cost_usd:.6f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}"
        lines.append(
            f"| {item.run_name} | {item.latency_seconds:.6f} | {cost} | {quality} | {item.notes} |"
        )
    if metrics:
        best_quality = max(metrics, key=lambda item: item.quality_score or 0)
        fastest = min(metrics, key=lambda item: item.latency_seconds)
        cheapest = min(
            metrics,
            key=lambda item: item.estimated_cost_usd
            if item.estimated_cost_usd is not None
            else float("inf"),
        )
        lines.extend(
            [
                "",
                "## Findings",
                "",
                (
                    f"- Highest quality score: `{best_quality.run_name}` "
                    f"({best_quality.quality_score or 0:.1f}/10)."
                ),
                f"- Fastest run: `{fastest.run_name}` ({fastest.latency_seconds:.6f}s).",
                (
                    f"- Lowest estimated cost: `{cheapest.run_name}` "
                    f"(${cheapest.estimated_cost_usd or 0:.6f})."
                ),
                "- Multi-agent runs should be preferred when source collection, analysis, "
                "and final writing need separate traceable steps.",
                "- Single-agent runs remain useful as a low-latency baseline and fallback path.",
                "",
                "## Failure Modes",
                "",
                "- Mock search provides synthetic sources; production evaluation should "
                "connect a real search provider and verify citation URLs.",
                "- Quality scoring is heuristic in this repo; important submissions should "
                "add human review or model-graded rubric checks.",
                "- Mock-mode token counts are character-based estimates, so production cost "
                "reporting should use provider usage metadata.",
                "- More agents add orchestration overhead, so the workflow enforces max "
                "iterations and records route history for debugging.",
            ]
        )
    return "\n".join(lines) + "\n"
