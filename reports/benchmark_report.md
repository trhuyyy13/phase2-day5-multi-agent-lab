# Benchmark Report

## Summary

This report compares the single-agent baseline with the multi-agent workflow using the same query set. Local runs use deterministic mock LLM/search clients when API keys are absent, so latency and quality are useful for regression checks rather than production claims. Cost is computed from provider usage when available, otherwise from local token estimates and the lab pricing table.

| Run | Latency (s) | Cost (USD) | Quality | Notes |
|---|---:|---:|---:|---|
| single-agent baseline | 0.000033 | 0.000044 | 4.0 | routes=0, sources=0, agents=0, input_tokens=35, output_tokens=65 |
| multi-agent workflow | 0.000058 | 0.000336 | 10.0 | routes=4, sources=5, agents=4, input_tokens=858, output_tokens=345 |

## Findings

- Highest quality score: `multi-agent workflow` (10.0/10).
- Fastest run: `single-agent baseline` (0.000033s).
- Lowest estimated cost: `single-agent baseline` ($0.000044).
- Multi-agent runs should be preferred when source collection, analysis, and final writing need separate traceable steps.
- Single-agent runs remain useful as a low-latency baseline and fallback path.

## Failure Modes

- Mock search provides synthetic sources; production evaluation should connect a real search provider and verify citation URLs.
- Quality scoring is heuristic in this repo; important submissions should add human review or model-graded rubric checks.
- Mock-mode token counts are character-based estimates, so production cost reporting should use provider usage metadata.
- More agents add orchestration overhead, so the workflow enforces max iterations and records route history for debugging.
