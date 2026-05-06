"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

import os
from contextlib import suppress
from dataclasses import dataclass
from importlib import import_module
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from multi_agent_research_lab.core.config import get_settings

OpenAI: Any = None
with suppress(Exception):
    OpenAI = import_module("openai").OpenAI

_DEFAULT_PRICING_PER_1K_TOKENS = {
    "gpt-4o-mini": (0.00015, 0.00060),
    "gpt-4o": (0.00500, 0.01500),
}
_FALLBACK_PRICING_PER_1K_TOKENS = (0.00015, 0.00060)


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client interface."""

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion."""

        raise NotImplementedError("Subclasses must implement LLMClient.complete")


class OpenAIClient(LLMClient):
    """OpenAI-backed LLM client using the OpenAI SDK."""

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        self.model = model or settings.openai_model
        self.timeout_seconds = settings.timeout_seconds
        api_key = _get_openai_api_key(settings.openai_api_key)
        if OpenAI is None:
            raise RuntimeError("openai package not installed")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        self.client = OpenAI(api_key=api_key, timeout=self.timeout_seconds)

    @retry(wait=wait_exponential(multiplier=1, min=1, max=8), stop=stop_after_attempt(3))
    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content or ""
        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else None
        output_tokens = usage.completion_tokens if usage else None
        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=estimate_cost_usd(self.model, input_tokens, output_tokens),
        )


class MockLLMClient(LLMClient):
    """Deterministic mock LLM client for local runs without API keys."""

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        prompt = user_prompt.lower()
        query = _extract_field(user_prompt, "Query") or _extract_field(
            user_prompt,
            "Research query",
        )
        if "5-7 bullet points" in prompt:
            content = "\n".join(
                [
                    (
                        f"- Define the problem scope for '{query}' and capture the main "
                        "concepts (mock source 1)."
                    ),
                    (
                        "- Compare implementation options by complexity, observability, "
                        "and failure isolation (mock source 2)."
                    ),
                    (
                        "- Track evidence quality separately from generated prose so weak "
                        "claims stay visible (mock source 3)."
                    ),
                    (
                        "- Prefer explicit handoff state between agents to make debugging "
                        "and evaluation repeatable (mock source 4)."
                    ),
                    (
                        "- Use max-iteration and timeout guardrails to prevent runaway "
                        "orchestration (mock source 5)."
                    ),
                ]
            )
        elif "produce: key claims" in prompt:
            content = (
                "Key claims:\n"
                "- Multi-agent workflows help when research, critique, and writing need "
                "distinct context windows.\n"
                "- The trade-off is higher orchestration latency and more moving parts.\n\n"
                "Evidence strength:\n"
                "- Moderate in local mock mode; source coverage is simulated for "
                "repeatable tests.\n\n"
                "Open questions:\n"
                "- Replace mock search with a provider-backed client before production use."
            )
        elif "3 bullet checks" in prompt:
            content = "\n".join(
                [
                    "- Clarity: answer is structured and readable.",
                    "- Evidence: cites local mock sources; production runs should use real URLs.",
                    "- Missing risks: benchmark quality still needs human or model-graded review.",
                ]
            )
        else:
            content = (
                f"Summary for '{query}': a single-agent baseline can answer directly, but it mixes "
                "research, analysis, and writing in one prompt. Use it as a latency and simplicity "
                "baseline against the multi-agent workflow."
            )
        input_tokens = estimate_tokens(system_prompt) + estimate_tokens(user_prompt)
        output_tokens = estimate_tokens(content)
        return LLMResponse(
            content=content,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=estimate_cost_usd(get_settings().openai_model, input_tokens, output_tokens),
        )


def estimate_tokens(text: str) -> int:
    """Estimate token count for local/mock runs without provider usage metadata."""

    if not text:
        return 0
    return max(1, round(len(text) / 4))


def estimate_cost_usd(
    model: str,
    input_tokens: int | None,
    output_tokens: int | None,
) -> float | None:
    """Estimate USD cost from token usage using the lab's pricing table."""

    if input_tokens is None or output_tokens is None:
        return None
    input_rate, output_rate = _DEFAULT_PRICING_PER_1K_TOKENS.get(
        model,
        _FALLBACK_PRICING_PER_1K_TOKENS,
    )
    return (input_tokens / 1000 * input_rate) + (output_tokens / 1000 * output_rate)


def _extract_field(text: str, field: str) -> str:
    prefix = f"{field}:"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return ""


def create_llm_client() -> LLMClient:
    """Return OpenAIClient if key present, else a mock client."""
    settings = get_settings()
    api_key = _get_openai_api_key(settings.openai_api_key)
    if api_key:
        return OpenAIClient()
    return MockLLMClient()


def _get_openai_api_key(settings_api_key: str | None) -> str | None:
    if "OPENAI_API_KEY" in os.environ:
        return os.environ["OPENAI_API_KEY"]
    return settings_api_key
