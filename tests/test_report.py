from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.evaluation.benchmark import run_benchmark, run_single_agent_baseline
from multi_agent_research_lab.evaluation.report import render_markdown_report


def test_report_renders_markdown() -> None:
    report = render_markdown_report(
        [
            BenchmarkMetrics(
                run_name="baseline",
                latency_seconds=1.23,
                estimated_cost_usd=0.000123,
            )
        ]
    )
    assert "Benchmark Report" in report
    assert "baseline" in report
    assert "0.000123" in report


def test_benchmark_records_cost_and_tokens(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "")
    state, metrics = run_benchmark(
        "baseline",
        "Explain multi-agent systems",
        run_single_agent_baseline,
    )
    assert state.total_input_tokens > 0
    assert state.total_output_tokens > 0
    assert metrics.estimated_cost_usd is not None
    assert metrics.estimated_cost_usd > 0
    assert "input_tokens=" in metrics.notes
