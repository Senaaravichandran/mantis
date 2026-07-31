"""Qdrant vector search tools for document RAG."""

from typing import Any
import httpx


class VectorSearchTool:
    """Semantic search over MANTIS's document corpus using Qdrant."""

    def __init__(self, host: str = "localhost", port: int = 6333, collection: str = "mantis_documents"):
        self.base_url = f"http://{host}:{port}"
        self.collection = collection

    async def search_documents(
        self,
        query_vector: list[float],
        limit: int = 5,
        doc_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search for relevant documents using vector similarity."""
        filter_condition = None
        if doc_type:
            filter_condition = {
                "must": [{"key": "doc_type", "match": {"value": doc_type}}]
            }

        payload = {
            "vector": query_vector,
            "limit": limit,
            "with_payload": True,
        }
        if filter_condition:
            payload["filter"] = filter_condition

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/collections/{self.collection}/points/search",
                    json=payload,
                    timeout=30.0,
                )
                if response.status_code == 200:
                    results = response.json().get("result", [])
                    return [
                        {
                            "id": r["id"],
                            "score": r["score"],
                            "content": r.get("payload", {}).get("content", ""),
                            "title": r.get("payload", {}).get("title", ""),
                            "doc_type": r.get("payload", {}).get("doc_type", ""),
                        }
                        for r in results
                    ]
        except Exception:
            pass
        return []

    async def search_standards(
        self, query_vector: list[float], standard_type: str = "fhwa", limit: int = 3
    ) -> list[dict[str, Any]]:
        """Search regulatory standards (FHWA, AWWA, etc.)."""
        return await self.search_documents(
            query_vector, limit=limit, doc_type=f"{standard_type}_standard"
        )
