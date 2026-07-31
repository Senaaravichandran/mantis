"""RAG retrieval with MMR reranking from Qdrant."""

from typing import Any

from ..llm.embeddings import EmbeddingClient
from ..tools.vector_search import VectorSearchTool


class RAGRetriever:
    """Retrieves relevant documents for agent context using RAG."""

    def __init__(
        self,
        embedding_client: EmbeddingClient | None = None,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
    ):
        self.embedding_client = embedding_client or EmbeddingClient()
        self.search_tool = VectorSearchTool(host=qdrant_host, port=qdrant_port)

    async def retrieve(
        self,
        query: str,
        doc_type: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Retrieve relevant documents for a query.

        Uses semantic search via Qdrant with optional document type filtering.
        """
        query_embedding = await self.embedding_client.embed_text(query)
        results = await self.search_tool.search_documents(
            query_vector=query_embedding,
            limit=top_k,
            doc_type=doc_type,
        )
        return results

    async def retrieve_for_asset(
        self, asset_id: str, query: str, top_k: int = 3
    ) -> list[dict[str, Any]]:
        """Retrieve documents relevant to a specific asset."""
        enriched_query = f"Asset {asset_id}: {query}"
        return await self.retrieve(enriched_query, top_k=top_k)

    async def retrieve_standards(
        self, asset_type: str, issue_description: str, top_k: int = 3
    ) -> list[dict[str, Any]]:
        """Retrieve relevant regulatory standards."""
        standard_map = {
            "bridge": "fhwa",
            "water_main": "awwa",
            "road": "fhwa",
            "tunnel": "fhwa",
        }
        standard_type = standard_map.get(asset_type, "general")
        query = f"{standard_type} standard: {issue_description}"
        return await self.retrieve(query, doc_type=f"{standard_type}_standard", top_k=top_k)

    def format_context(self, documents: list[dict[str, Any]]) -> str:
        """Format retrieved documents into a context string for the LLM."""
        if not documents:
            return "No relevant documents found in the knowledge base."

        context_parts = []
        for i, doc in enumerate(documents, 1):
            title = doc.get("title", "Untitled")
            content = doc.get("content", "")
            score = doc.get("score", 0)
            context_parts.append(
                f"[Document {i}] ({title}, relevance: {score:.2f})\n{content}"
            )
        return "\n\n".join(context_parts)
