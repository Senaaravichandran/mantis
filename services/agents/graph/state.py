"""MANTISState — shared state object passed between all MANTIS agents."""

from typing import Annotated, Any, Sequence
from pydantic import BaseModel, Field
from datetime import datetime
import operator


class MANTISState(BaseModel):
    """Shared state object passed between all MANTIS agents in the LangGraph."""

    # Trigger context
    trigger_type: str  # "sensor_anomaly" | "scheduled" | "manual" | "document_upload"
    trigger_asset_id: str | None = None
    trigger_sensor_data: dict[str, Any] | None = None

    # Agent outputs (accumulated as graph runs)
    anomaly_detected: bool = False
    anomaly_details: dict[str, Any] = Field(default_factory=dict)
    risk_score: float | None = None  # 0.0 - 100.0
    risk_confidence: float | None = None
    root_cause_analysis: str | None = None
    recommended_actions: list[str] = Field(default_factory=list)

    # Work order data
    work_order_draft: dict[str, Any] | None = None
    work_order_approved: bool = False
    work_order_id: str | None = None

    # Report data
    report_content: str | None = None
    report_type: str | None = None

    # Contractor data
    contractor_matches: list[dict[str, Any]] = Field(default_factory=list)
    rfq_draft: dict[str, Any] | None = None

    # Compliance data
    compliance_status: dict[str, Any] | None = None
    upcoming_deadlines: list[dict[str, Any]] = Field(default_factory=list)

    # Routing and control
    next_agent: str | None = None
    completed_agents: list[str] = Field(default_factory=list)
    escalation_required: bool = False
    human_review_required: bool = False

    # Conversation / reasoning log
    messages: list[dict[str, Any]] = Field(default_factory=list)
    thought_chain: list[str] = Field(default_factory=list)  # Audit trail

    # Metadata
    run_id: str = ""
    started_at: datetime = Field(default_factory=datetime.utcnow)
    municipality_id: str = ""

    model_config = {"arbitrary_types_allowed": True}
