"""Test: batch with 5% TOR remaining and high quantity → HOLD recommendation."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_hold_recommendation():
    """Agent recommends HOLD when < 15 minutes remain and quantity is high."""
    with patch("mcp_providers.agw.get_mcp_tools", return_value=AsyncMock(return_value=[])()):
        from agent import SampleAgent

        agent = SampleAgent()
        query = (
            "Batch B002 for material M200 has reached 95% of its TOR limit. "
            "Elapsed: 57 min, TOR limit: 60 min, remaining: 3 min. "
            "Batch quantity: 500 units, production line can consume 50 units before TOR expires. "
            "Provide an EXPEDITE or HOLD recommendation."
        )

        mock_result = {
            "messages": [
                MagicMock(
                    content=(
                        "Decision: HOLD\n"
                        "Urgency: HIGH\n"
                        "Remaining TOR: 3 minutes\n"
                        "Reasoning: Insufficient TOR time to process 500 units; only 50 can be consumed. "
                        "Hold and initiate quality review for partial use or controlled disposal.\n"
                        "Compliance Note: GxP/GDP — batch must not enter manufacturing if TOR will be exceeded during processing."
                    )
                )
            ]
        }

        with patch.object(agent, "_invoke_with_fallback", return_value=mock_result):
            response = await agent.invoke(query, "test-context-hold")

        assert response.status == "completed"
        assert "HOLD" in response.message
