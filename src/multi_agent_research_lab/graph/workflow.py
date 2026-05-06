"""LangGraph workflow skeleton."""

from multi_agent_research_lab.agents import (
    AnalystAgent,
    CriticAgent,
    ResearcherAgent,
    SupervisorAgent,
    WriterAgent,
)
from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.state import ResearchState


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def build(self) -> dict[str, BaseAgent]:
        """Create the executable agent registry."""

        # This starter uses a simple in-process loop instead of LangGraph.
        return {
            "supervisor": SupervisorAgent(),
            "researcher": ResearcherAgent(),
            "analyst": AnalystAgent(),
            "writer": WriterAgent(),
            "critic": CriticAgent(),
        }

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""

        agents = self.build()
        settings = get_settings()

        while state.iteration < settings.max_iterations:
            state = agents["supervisor"].run(state)
            if state.route_history and state.route_history[-1] == "done":
                break
            route = state.route_history[-1]
            if route not in agents:
                state.errors.append(f"Unknown route: {route}")
                break
            state = agents[route].run(state)

        if state.final_answer and "critic" in agents:
            # Optional critic pass for additional feedback.
            state = agents["critic"].run(state)
        return state
