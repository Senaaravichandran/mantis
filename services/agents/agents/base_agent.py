"""Abstract base class for all MANTIS agents."""

import os
from abc import ABC, abstractmethod
from pathlib import Path

from ..graph.state import MANTISState
from ..llm.provider import OllamaProvider
from ..memory.working_memory import WorkingMemory


class BaseMantisAgent(ABC):
    """Base class providing common functionality for all MANTIS agents."""

    name: str = "base"
    description: str = "Base MANTIS agent"

    def __init__(self, llm: OllamaProvider | None = None, db_session=None):
        self.llm = llm or OllamaProvider()
        self.db_session = db_session
        self.working_memory = WorkingMemory()
        self._system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load the agent's system prompt from the prompts directory."""
        prompt_path = Path(__file__).parent.parent / "llm" / "prompts" / f"{self.name}.md"
        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")
        return f"You are {self.name}, a MANTIS infrastructure monitoring agent."

    async def _invoke_llm(self, prompt: str, use_fast: bool = False) -> str:
        """Invoke the LLM with the agent's system prompt."""
        return await self.llm.generate(
            prompt=prompt,
            system_prompt=self._system_prompt,
            use_fast_model=use_fast,
        )

    def _add_thought(self, state: MANTISState, thought: str) -> MANTISState:
        """Add a thought to the agent's reasoning chain."""
        state.thought_chain.append(f"[{self.name.upper()}] {thought}")
        return state

    @abstractmethod
    async def run(self, state: MANTISState) -> MANTISState:
        """Execute the agent's logic and update the shared state."""
        ...
