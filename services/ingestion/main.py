"""MANTIS Ingestion Service — starts all data connectors."""

import asyncio
import os
import sys
import logging

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from mantis_shared.logging import setup_logging

from .connectors.simulator import SensorSimulator
from .connectors.weather_connector import WeatherConnector
from .connectors.usgs_connector import USGSConnector

logger = setup_logging("mantis-ingestion")


async def main():
    logger.info("MANTIS Ingestion Service starting")

    kafka_producer = None
    try:
        from aiokafka import AIOKafkaProducer
        kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        kafka_producer = AIOKafkaProducer(bootstrap_servers=kafka_servers)
        await kafka_producer.start()
        logger.info("Kafka producer connected")
    except Exception as e:
        logger.warning(f"Kafka not available ({e}), running connectors in log-only mode")

    # Initialize connectors
    connectors = [
        SensorSimulator(kafka_producer=kafka_producer, anomaly_probability=0.03),
        WeatherConnector(kafka_producer=kafka_producer),
        USGSConnector(kafka_producer=kafka_producer),
    ]

    # Start all connectors concurrently
    tasks = [asyncio.create_task(c.start()) for c in connectors]
    logger.info(f"Started {len(connectors)} connectors")

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Shutting down connectors")
        for c in connectors:
            await c.stop()
        if kafka_producer:
            await kafka_producer.stop()


if __name__ == "__main__":
    asyncio.run(main())

# Initialize ingestion pipeline routes
