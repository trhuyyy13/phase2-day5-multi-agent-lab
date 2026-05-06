"""Command-line entrypoint for the lab starter."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.benchmark import (
    run_benchmark,
    run_multi_agent_workflow,
    run_single_agent_baseline,
)
from multi_agent_research_lab.evaluation.report import render_markdown_report
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging
from multi_agent_research_lab.services.llm_client import create_llm_client

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline placeholder."""

    _init()
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    llm = create_llm_client()
    system_prompt = "You are a helpful research assistant."
    user_prompt = f"Research query: {query}\nWrite a concise summary."
    response = llm.complete(system_prompt, user_prompt)
    state.final_answer = response.content
    state.record_llm_usage(response.input_tokens, response.output_tokens, response.cost_usd)
    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    console.print(result.model_dump_json(indent=2))


@app.command("benchmark")
def benchmark(
    query: Annotated[
        str,
        typer.Option("--query", "-q", help="Research query"),
    ] = "Research GraphRAG state-of-the-art and write a 500-word summary",
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Markdown report path"),
    ] = Path("reports/benchmark_report.md"),
) -> None:
    """Run baseline and multi-agent workflow, then write a benchmark report."""

    _init()
    output.parent.mkdir(parents=True, exist_ok=True)
    _, baseline_metrics = run_benchmark(
        "single-agent baseline",
        query,
        run_single_agent_baseline,
    )
    _, multi_agent_metrics = run_benchmark(
        "multi-agent workflow",
        query,
        run_multi_agent_workflow,
    )
    report = render_markdown_report([baseline_metrics, multi_agent_metrics])
    output.write_text(report, encoding="utf-8")
    console.print(
        Panel.fit(
            f"Wrote {output}\n"
            f"Baseline: {baseline_metrics.latency_seconds:.4f}s, "
            f"${baseline_metrics.estimated_cost_usd or 0:.6f}\n"
            f"Multi-agent: {multi_agent_metrics.latency_seconds:.4f}s, "
            f"${multi_agent_metrics.estimated_cost_usd or 0:.6f}",
            title="Benchmark",
        )
    )


if __name__ == "__main__":
    app()
