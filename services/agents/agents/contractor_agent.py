"""Contractor Agent — RFQ and bid management."""

from ..graph.state import MANTISState
from ..tools.contractor_tools import search_contractors, draft_rfq
from .base_agent import BaseMantisAgent


class ContractorAgent(BaseMantisAgent):
    """Searches contractor registry, drafts RFQs, and evaluates bids."""

    name = "contractor"
    description = "RFQ and bid management agent"

    async def run(self, state: MANTISState) -> MANTISState:
        self._add_thought(state, "Searching for qualified contractors")

        work_order = state.work_order_draft or {}
        specialty = work_order.get("recommended_specialty", "general")

        # Search for contractors
        contractors = await search_contractors(
            specialty=specialty,
            db_session=self.db_session,
        )

        self._add_thought(state, f"Found {len(contractors)} qualified contractors for '{specialty}'")
        state.contractor_matches = contractors

        # Draft RFQ
        if contractors and work_order:
            rfq = await draft_rfq(work_order, contractors)
            state.rfq_draft = rfq
            self._add_thought(state, f"RFQ drafted: {rfq.get('rfq_id', 'N/A')}")

            # LLM evaluation of contractor fit
            prompt = (
                f"Evaluate these contractors for this infrastructure work:\n\n"
                f"Work Order: {work_order.get('title', 'N/A')}\n"
                f"Estimated Cost: ${work_order.get('estimated_cost', 0):,.0f}\n"
                f"Specialty Required: {specialty}\n\n"
                f"Available Contractors:\n"
            )
            for c in contractors:
                prompt += f"- {c.get('name', 'Unknown')}: {c.get('specialty', 'N/A')}, Rating: {c.get('rating', 'N/A')}\n"
            prompt += "\nRecommend the best contractor and explain why."

            evaluation = await self._invoke_llm(prompt, use_fast=True)
            self._add_thought(state, f"Contractor evaluation: {evaluation[:200]}...")

        state.next_agent = "regulator"
        state.completed_agents.append(self.name)
        return state
