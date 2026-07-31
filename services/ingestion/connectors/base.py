"""Abstract base class for all data connectors."""

from abc import ABC, abstractmethod
from typing import Any
import logging

logger = logging.getLogger("mantis.ingestion")


class BaseConnector(ABC):
    """Base class for all MANTIS data connectors."""

    name: str = "base"
    poll_interval_seconds: int = 60

    def __init__(self, kafka_producer=None):
        self.kafka_producer = kafka_producer
        self.running = False

    @abstractmethod
    async def poll(self) -> list[dict[str, Any]]:
        """Poll for new data. Returns a list of events."""
        ...

    async def publish(self, topic: str, events: list[dict[str, Any]]):
        """Publish events to Kafka."""
        if self.kafka_producer:
            import json
            for event in events:
                await self.kafka_producer.send_and_wait(
                    topic,
                    json.dumps(event, default=str).encode("utf-8"),
                )
        else:
            logger.info(f"[{self.name}] Would publish {len(events)} events to {topic}")

    async def start(self):
        """Start the polling loop."""
        import asyncio
        self.running = True
        logger.info(f"[{self.name}] Connector started (interval: {self.poll_interval_seconds}s)")
        while self.running:
            try:
                events = await self.poll()
                if events:
                    await self.publish(f"mantis.{self.name}", events)
                    logger.info(f"[{self.name}] Published {len(events)} events")
            except Exception as e:
                logger.error(f"[{self.name}] Poll error: {e}")
            await asyncio.sleep(self.poll_interval_seconds)

    async def stop(self):
        """Stop the polling loop."""
        self.running = False
        logger.info(f"[{self.name}] Connector stopped")
