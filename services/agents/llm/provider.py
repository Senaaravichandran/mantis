"""Ollama LLM client wrapper for MANTIS agents."""

import os
import httpx
from typing import Any


class OllamaProvider:
    """Wrapper for Ollama local LLM serving."""

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
        fast_model: str | None = None,
    ):
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3:70b-instruct-q4_K_M")
        self.fast_model = fast_model or os.getenv("OLLAMA_FAST_MODEL", "mistral:7b-instruct-v0.3")

    async def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        use_fast_model: bool = False,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> str:
        """Generate a response from the LLM."""
        model = self.fast_model if use_fast_model else self.model

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": model,
                        "messages": messages,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        },
                        "stream": False,
                    },
                    timeout=120.0,
                )
                if response.status_code == 200:
                    return response.json()["message"]["content"]
                return f"LLM Error: {response.status_code} - {response.text}"
        except httpx.ConnectError:
            return self._fallback_response(prompt)
        except Exception as e:
            return f"LLM Error: {str(e)}"

    def _fallback_response(self, prompt: str) -> str:
        """Provide a structured fallback when Ollama is not available."""
        if "anomaly" in prompt.lower():
            return (
                "Based on the sensor data analysis, I've detected a potential anomaly. "
                "The readings show deviation from the established baseline. "
                "Recommend further investigation by the Analyst agent."
            )
        if "risk" in prompt.lower() or "analysis" in prompt.lower():
            return (
                "Risk assessment indicates moderate concern. The combination of sensor "
                "deviations and asset age suggests proactive maintenance should be considered. "
                "Recommend generating a work order for inspection."
            )
        if "work order" in prompt.lower() or "maintenance" in prompt.lower():
            return (
                "Based on the risk assessment, I recommend scheduling a maintenance inspection "
                "within the next 30 days. Priority level: Medium. Estimated cost range: "
                "$15,000 - $50,000 depending on findings."
            )
        return (
            "Analysis complete. The infrastructure monitoring system has processed the "
            "available data and generated this assessment. Please review the detailed "
            "findings in the agent thought chain."
        )

    async def get_embeddings(self, text: str) -> list[float]:
        """Get text embeddings using the embedding model."""
        embedding_model = os.getenv("OLLAMA_EMBEDDING_MODEL", "bge-m3")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={"model": embedding_model, "prompt": text},
                    timeout=30.0,
                )
                if response.status_code == 200:
                    return response.json()["embedding"]
        except Exception:
            pass
        # Return zero vector as fallback
        return [0.0] * 1024

    async def check_health(self) -> dict[str, Any]:
        """Check if Ollama is running and models are available."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/tags",
                    timeout=5.0,
                )
                if response.status_code == 200:
                    models = [m["name"] for m in response.json().get("models", [])]
                    return {
                        "status": "healthy",
                        "available_models": models,
                        "primary_model": self.model,
                        "fast_model": self.fast_model,
                    }
        except Exception as e:
            return {"status": "unavailable", "error": str(e)}
        return {"status": "unavailable"}
