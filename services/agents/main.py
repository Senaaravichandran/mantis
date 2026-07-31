"""MANTIS Agent Service — Kafka consumer that triggers LangGraph agent runs."""

import asyncio
import json
import os
import sys
from uuid import uuid4
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from mantis_shared.logging import setup_logging
from mantis_shared.config import get_settings

from .graph.supervisor import build_mantis_graph
from .graph.state import MANTISState
from .llm.provider import OllamaProvider

logger = setup_logging("mantis-agents")
settings = get_settings()


async def process_agent_task(task: dict):
    """Process a single agent task from Kafka."""
    run_id = str(uuid4())
    logger.info(f"Starting agent run {run_id}", extra={"run_id": run_id})

    llm = OllamaProvider()

    initial_state = MANTISState(
        trigger_type=task.get("trigger_type", "manual"),
        trigger_asset_id=task.get("asset_id"),
        trigger_sensor_data=task.get("sensor_data"),
        run_id=run_id,
        municipality_id=task.get("municipality_id", ""),
    )

    graph = build_mantis_graph(llm=llm)

    try:
        final_state = await graph.ainvoke(initial_state)
        logger.info(
            f"Agent run {run_id} completed. Agents: {final_state.completed_agents}",
            extra={"run_id": run_id},
        )
        return final_state
    except Exception as e:
        logger.error(f"Agent run {run_id} failed: {e}", extra={"run_id": run_id})
        raise


async def start_kafka_consumer():
    """Start consuming agent tasks from Kafka."""
    try:
        from aiokafka import AIOKafkaConsumer

        consumer = AIOKafkaConsumer(
            "mantis.agents.tasks",
            bootstrap_servers=settings.kafka_bootstrap_servers,
            group_id="mantis-agents",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        )

        await consumer.start()
        logger.info("Agent Kafka consumer started")

        try:
            async for msg in consumer:
                task = msg.value
                logger.info(f"Received agent task: {task.get('trigger_type', 'unknown')}")
                try:
                    await process_agent_task(task)
                except Exception as e:
                    logger.error(f"Task processing failed: {e}")
        finally:
            await consumer.stop()
    except ImportError:
        logger.warning("aiokafka not available — running in standalone mode")
        logger.info("Agent service ready. Use API to trigger agent runs.")
        # Keep alive
        while True:
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(start_kafka_consumer())

# Agent core setup
