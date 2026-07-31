"""Reporter Agent — report and notification generation."""

from ..graph.state import MANTISState
from ..tools.document_tools import generate_report
from ..tools.notification_tools import send_email, send_slack_notification
from .base_agent import BaseMantisAgent


class ReporterAgent(BaseMantisAgent):
    """Generates human-readable reports and sends notifications.

    Converts agent reasoning into plain English for different audiences.
    """

    name = "reporter"
    description = "Report and alert generation agent"

    async def run(self, state: MANTISState) -> MANTISState:
        self._add_thought(state, "Generating reports and notifications")

        # Determine report type based on pipeline state
        if state.work_order_draft:
            report_type = "work_order_report"
        elif state.risk_score and state.risk_score >= 60:
            report_type = "anomaly_summary"
        else:
            report_type = "anomaly_summary"

        # Generate report content via LLM
        prompt = (
            f"Generate a clear, professional infrastructure report:\n\n"
            f"Report Type: {report_type}\n"
            f"Anomaly Detected: {state.anomaly_detected}\n"
            f"Risk Score: {state.risk_score}/100\n"
            f"Root Cause: {(state.root_cause_analysis or 'N/A')[:300]}\n"
            f"Recommended Actions: {state.recommended_actions}\n"
        )

        if state.work_order_draft:
            prompt += (
                f"\nWork Order:\n"
                f"- Title: {state.work_order_draft.get('title', 'N/A')}\n"
                f"- Priority: {state.work_order_draft.get('priority', 'N/A')}\n"
                f"- Est. Cost: ${state.work_order_draft.get('estimated_cost', 0):,.0f}\n"
                f"- Timeline: {state.work_order_draft.get('timeline', 'N/A')}\n"
            )

        prompt += "\nWrite the report in clear, non-technical language suitable for city officials."

        report_content = await self._invoke_llm(prompt)
        self._add_thought(state, f"Report generated ({len(report_content)} chars)")

        # Generate structured report document
        report = await generate_report(
            report_type=report_type,
            title=f"MANTIS Alert Report - Risk Score {state.risk_score}",
            content={
                "summary": report_content,
                "risk_assessment": state.root_cause_analysis or "",
                "actions": state.recommended_actions,
                "work_order": state.work_order_draft,
            },
            municipality_id=state.municipality_id,
        )

        state.report_content = report_content
        state.report_type = report_type

        # Send notifications
        severity = "critical" if (state.risk_score or 0) >= 70 else "warning"
        await send_slack_notification(
            channel="#mantis-alerts",
            message=f"MANTIS Alert: Risk score {state.risk_score}/100 detected",
            severity=severity,
        )
        self._add_thought(state, f"Notifications sent (severity: {severity})")

        # Route based on pipeline state
        if state.work_order_approved:
            state.next_agent = "contractor"
        elif state.risk_score and state.risk_score >= 70:
            state.next_agent = "regulator"
        else:
            state.next_agent = None

        state.completed_agents.append(self.name)
        return state
