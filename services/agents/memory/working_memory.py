"""In-context working memory management for agent conversations."""

from typing import Any


class WorkingMemory:
    """Manages the agent's working memory within a single run.

    Tracks intermediate results, hypotheses, and context
    that should be available to the agent during processing
    but doesn't need to persist long-term.
    """

    def __init__(self, max_items: int = 50):
        self.max_items = max_items
        self._items: list[dict[str, Any]] = []

    def add(self, key: str, value: Any, category: str = "general"):
        """Add an item to working memory."""
        self._items.append({
            "key": key,
            "value": value,
            "category": category,
        })
        # Evict oldest items if over capacity
        if len(self._items) > self.max_items:
            self._items = self._items[-self.max_items:]

    def get(self, key: str) -> Any:
        """Retrieve an item by key."""
        for item in reversed(self._items):
            if item["key"] == key:
                return item["value"]
        return None

    def get_by_category(self, category: str) -> list[dict[str, Any]]:
        """Get all items in a category."""
        return [item for item in self._items if item["category"] == category]

    def to_context_string(self) -> str:
        """Format working memory as a context string for the LLM prompt."""
        if not self._items:
            return ""
        parts = []
        for item in self._items:
            parts.append(f"- {item['key']}: {item['value']}")
        return "Working Memory:\n" + "\n".join(parts)

    def clear(self):
        """Clear all working memory."""
        self._items.clear()
