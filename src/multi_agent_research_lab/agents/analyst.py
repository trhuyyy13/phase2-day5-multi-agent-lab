"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import create_llm_client


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""

        llm = create_llm_client()
        system_prompt = "You are an analyst who synthesizes research into structured insights."
        user_prompt = (
            f"Query: {state.request.query}\n"
            f"Research notes:\n{state.research_notes or ''}\n"
            "Produce: key claims, evidence strength, and open questions."
        )
        response = llm.complete(system_prompt, user_prompt)
        state.analysis_notes = response.content
        usage = state.record_llm_usage(
            response.input_tokens,
            response.output_tokens,
            response.cost_usd,
        )
        state.agent_results.append(
            AgentResult(agent=AgentName.ANALYST, content=response.content, metadata=usage)
        )
        state.add_trace_event("agent", {"name": self.name, **usage})
        return state
