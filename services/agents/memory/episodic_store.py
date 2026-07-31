"""Long-term agent memory backed by PostgreSQL."""

from datetime import datetime, timezone
from typing import Any


class EpisodicMemoryStore:
    """Stores and retrieves long-term agent memories.

    Memories are structured as episodes — past agent runs, decisions,
    and outcomes that inform future reasoning.
    """

    def __init__(self, db_session=None):
        self.db_session = db_session
        self._local_cache: list[dict[str, Any]] = []

    async def store_episode(
        self,
        agent_type: str,
        asset_id: str,
        episode_type: str,
        content: str,
        outcome: str | None = None,
    ):
        """Store an episode in long-term memory."""
        episode = {
            "agent_type": agent_type,
            "asset_id": asset_id,
            "episode_type": episode_type,
            "content": content,
            "outcome": outcome,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._local_cache.append(episode)

        if self.db_session:
            from sqlalchemy import text
            await self.db_session.execute(
                text("""
                    INSERT INTO agent_runs (municipality_id, agent_type, trigger_type,
                        status, thought_chain, started_at)
                    VALUES (:mid, :agent, 'memory', 'completed', :thoughts, :ts)
                """),
                {
                    "mid": "00000000-0000-0000-0000-000000000000",
                    "agent": agent_type,
                    "thoughts": f'[{{"episode": "{episode_type}", "content": "{content}"}}]',
                    "ts": datetime.now(timezone.utc),
                },
            )

    async def recall(
        self, agent_type: str, asset_id: str | None = None, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Recall past episodes relevant to the current context."""
        # Filter from local cache
        relevant = [
            ep for ep in self._local_cache
            if ep["agent_type"] == agent_type
            and (asset_id is None or ep["asset_id"] == asset_id)
        ]
        return sorted(relevant, key=lambda x: x["timestamp"], reverse=True)[:limit]
