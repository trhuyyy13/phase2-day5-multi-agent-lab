"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import create_llm_client


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""

        llm = create_llm_client()
        system_prompt = "You are a clear technical writer."
        user_prompt = (
            f"Query: {state.request.query}\n"
            f"Research notes:\n{state.research_notes or ''}\n"
            f"Analysis notes:\n{state.analysis_notes or ''}\n"
            "Write a concise answer with brief source references in parentheses."
        )
        response = llm.complete(system_prompt, user_prompt)
        state.final_answer = response.content
        usage = state.record_llm_usage(
            response.input_tokens,
            response.output_tokens,
            response.cost_usd,
        )
        state.agent_results.append(
            AgentResult(agent=AgentName.WRITER, content=response.content, metadata=usage)
        )
        state.add_trace_event("agent", {"name": self.name, **usage})
        return state
