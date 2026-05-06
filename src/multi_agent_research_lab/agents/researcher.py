"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import create_llm_client
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""

        client = SearchClient()
        sources = client.search(state.request.query, max_results=state.request.max_sources)
        state.sources = sources
        snippets = "\n".join(f"- {doc.title}: {doc.snippet}" for doc in sources)

        llm = create_llm_client()
        system_prompt = "You are a research assistant who writes concise research notes."
        user_prompt = (
            f"Query: {state.request.query}\n"
            f"Audience: {state.request.audience}\n"
            f"Sources:\n{snippets}\n"
            "Write 5-7 bullet points of key findings with brief citations in parentheses."
        )
        response = llm.complete(system_prompt, user_prompt)
        state.research_notes = response.content
        usage = state.record_llm_usage(
            response.input_tokens,
            response.output_tokens,
            response.cost_usd,
        )
        state.agent_results.append(
            AgentResult(
                agent=AgentName.RESEARCHER,
                content=response.content,
                metadata={"sources": len(sources), **usage},
            )
        )
        state.add_trace_event("agent", {"name": self.name, "sources": len(sources), **usage})
        return state
