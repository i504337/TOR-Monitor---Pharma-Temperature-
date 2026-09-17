"""Test: batch with 0% remaining (already breached) → SCRAP recommendation."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_scrap_recommendation():
    """Agent recommends SCRAP when TOR has already been exceeded."""
    with patch("mcp_providers.agw.get_mcp_tools", return_value=AsyncMock(return_value=[])()):
        from agent import SampleAgent

        agent = SampleAgent()
        query = (
            "Batch B003 for material M300 has exceeded its TOR limit. "
            "Elapsed: 75 min, TOR limit: 60 min, remaining: -15 min. "
            "Provide a recommendation."
        )

        mock_result = {
            "messages": [
                MagicMock(
                    content=(
                        "Decision: SCRAP\n"
                        "Urgency: HIGH\n"
                        "Remaining TOR: -15 minutes (BREACHED)\n"
                        "Reasoning: Batch has exceeded its maximum allowable TOR exposure. "
                        "Cannot be used in manufacturing under any circumstances.\n"
                        "Compliance Note: GxP/GDP — materials exceeding TOR limits must not enter the manufacturing process. Initiate deviation report."
                    )
                )
            ]
        }

        with patch.object(agent, "_invoke_with_fallback", return_value=mock_result):
            response = await agent.invoke(query, "test-context-scrap")

        assert response.status == "completed"
        assert "SCRAP" in response.message
        # Verify EXPEDITE is NOT recommended for a breached batch
        assert "EXPEDITE" not in response.message
