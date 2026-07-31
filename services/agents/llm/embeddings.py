"""BGE-M3 embedding client via Ollama."""

from .provider import OllamaProvider


class EmbeddingClient:
    """Generate text embeddings using BGE-M3 via Ollama."""

    def __init__(self, provider: OllamaProvider | None = None):
        self.provider = provider or OllamaProvider()

    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        return await self.provider.get_embeddings(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        results = []
        for text in texts:
            embedding = await self.provider.get_embeddings(text)
            results.append(embedding)
        return results

    async def embed_document(self, title: str, content: str) -> list[float]:
        """Generate embedding for a document (title + content combined)."""
        combined = f"{title}\n\n{content}"
        if len(combined) > 8000:
            combined = combined[:8000]
        return await self.provider.get_embeddings(combined)
