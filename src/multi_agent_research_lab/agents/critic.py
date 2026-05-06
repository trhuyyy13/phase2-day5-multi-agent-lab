"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import create_llm_client


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""

        llm = create_llm_client()
        system_prompt = "You are a critic reviewing an answer for clarity and evidence coverage."
        user_prompt = (
            f"Answer:\n{state.final_answer or ''}\n"
            "Give 3 bullet checks: clarity, evidence, missing risks."
        )
        response = llm.complete(system_prompt, user_prompt)
        usage = state.record_llm_usage(
            response.input_tokens,
            response.output_tokens,
            response.cost_usd,
        )
        state.agent_results.append(
            AgentResult(agent=AgentName.CRITIC, content=response.content, metadata=usage)
        )
        state.add_trace_event("agent", {"name": self.name, **usage})
        return state
