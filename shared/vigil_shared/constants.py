"""MANTIS shared constants and enumerations."""

from enum import StrEnum


class AssetType(StrEnum):
    BRIDGE = "bridge"
    WATER_MAIN = "water_main"
    ROAD = "road"
    POWER_LINE = "power_line"
    TUNNEL = "tunnel"
    PUMP_STATION = "pump_station"
    CULVERT = "culvert"
    RETENTION_BASIN = "retention_basin"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class WorkOrderStatus(StrEnum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class AgentType(StrEnum):
    SENTINEL = "sentinel"
    ANALYST = "analyst"
    PLANNER = "planner"
    REPORTER = "reporter"
    CONTRACTOR = "contractor"
    REGULATOR = "regulator"


class TriggerType(StrEnum):
    SENSOR_ANOMALY = "sensor_anomaly"
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    DOCUMENT_UPLOAD = "document_upload"


class SensorType(StrEnum):
    VIBRATION = "vibration"
    PRESSURE = "pressure"
    STRAIN = "strain"
    FLOW = "flow"
    TEMPERATURE = "temperature"
    DISPLACEMENT = "displacement"
    WATER_LEVEL = "water_level"
    CORROSION = "corrosion"
    HUMIDITY = "humidity"
    TILT = "tilt"


# Kafka Topics
KAFKA_TOPICS = {
    "sensor_raw": "mantis.sensors.raw",
    "sensor_processed": "mantis.sensors.processed",
    "alerts": "mantis.alerts",
    "agent_tasks": "mantis.agents.tasks",
    "agent_results": "mantis.agents.results",
    "weather": "mantis.weather",
    "satellite": "mantis.satellite",
}
