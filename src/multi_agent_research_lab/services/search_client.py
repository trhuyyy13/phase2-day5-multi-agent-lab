"""Search client abstraction for ResearcherAgent."""

from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic search client skeleton."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query."""

        max_results = max(1, min(max_results, 10))
        return [
            SourceDocument(
                title=f"Mock source {idx + 1} for: {query}",
                url=None,
                snippet=f"This is a mock snippet for '{query}'.",
                metadata={"rank": idx + 1, "source": "mock"},
            )
            for idx in range(max_results)
        ]
