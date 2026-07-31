"""Document chunking and Qdrant vector indexing for RAG."""

import hashlib
from typing import Any
from uuid import uuid4

from ..llm.embeddings import EmbeddingClient


class DocumentIndexer:
    """Indexes documents into Qdrant for RAG retrieval."""

    def __init__(self, embedding_client: EmbeddingClient | None = None, qdrant_host: str = "localhost", qdrant_port: int = 6333):
        self.embedding_client = embedding_client or EmbeddingClient()
        self.qdrant_url = f"http://{qdrant_host}:{qdrant_port}"
        self.collection = "mantis_documents"

    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
        """Split text into overlapping chunks for embedding."""
        if len(text) <= chunk_size:
            return [text]
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            if chunk.strip():
                chunks.append(chunk)
            start += chunk_size - overlap
        return chunks

    async def index_document(
        self, title: str, content: str, doc_type: str, metadata: dict[str, Any] | None = None
    ) -> list[str]:
        """Index a document by chunking and storing embeddings in Qdrant."""
        import httpx

        chunks = self.chunk_text(content)
        point_ids = []

        for i, chunk in enumerate(chunks):
            embedding = await self.embedding_client.embed_text(chunk)
            point_id = hashlib.md5(f"{title}:{i}".encode()).hexdigest()

            payload = {
                "content": chunk,
                "title": title,
                "doc_type": doc_type,
                "chunk_index": i,
                "total_chunks": len(chunks),
                **(metadata or {}),
            }

            try:
                async with httpx.AsyncClient() as client:
                    await client.put(
                        f"{self.qdrant_url}/collections/{self.collection}/points",
                        json={
                            "points": [
                                {"id": point_id, "vector": embedding, "payload": payload}
                            ]
                        },
                        timeout=30.0,
                    )
                point_ids.append(point_id)
            except Exception:
                pass

        return point_ids
