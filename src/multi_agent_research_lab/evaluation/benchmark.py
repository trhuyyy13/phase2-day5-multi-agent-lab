"""Benchmark skeleton for single-agent vs multi-agent."""

from collections.abc import Callable
from time import perf_counter

from multi_agent_research_lab.core.schemas import BenchmarkMetrics, ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.services.llm_client import create_llm_client

Runner = Callable[[str], ResearchState]


def run_benchmark(
    run_name: str,
    query: str,
    runner: Runner,
) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return a benchmark metric object."""

    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=state.estimated_cost_usd,
        quality_score=_score_state(state),
        notes=_summarize_state(state),
    )
    return state, metrics


def run_single_agent_baseline(query: str) -> ResearchState:
    """Execute the single-agent baseline and return measured state."""

    state = ResearchState(request=ResearchQuery(query=query))
    llm = create_llm_client()
    system_prompt = "You are a helpful research assistant."
    user_prompt = f"Research query: {query}\nWrite a concise summary."
    response = llm.complete(system_prompt, user_prompt)
    state.final_answer = response.content
    usage = state.record_llm_usage(
        response.input_tokens,
        response.output_tokens,
        response.cost_usd,
    )
    state.add_trace_event("agent", {"name": "single_agent_baseline", **usage})
    return state


def run_multi_agent_workflow(query: str) -> ResearchState:
    """Execute the multi-agent workflow and return measured state."""

    state = ResearchState(request=ResearchQuery(query=query))
    return MultiAgentWorkflow().run(state)


def _score_state(state: ResearchState) -> float:
    score = 0.0
    if state.final_answer:
        score += 3.0
    if state.sources:
        score += 2.0
    if state.research_notes:
        score += 1.5
    if state.analysis_notes:
        score += 1.5
    if state.agent_results:
        score += 1.0
    if not state.errors:
        score += 1.0
    return min(score, 10.0)


def _summarize_state(state: ResearchState) -> str:
    parts = [
        f"routes={len(state.route_history)}",
        f"sources={len(state.sources)}",
        f"agents={len(state.agent_results)}",
        f"input_tokens={state.total_input_tokens}",
        f"output_tokens={state.total_output_tokens}",
    ]
    if state.errors:
        parts.append(f"errors={len(state.errors)}")
    return ", ".join(parts)
