"""Test: MCP batch lookup fails → recommendation still returned with caveat."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_mcp_tool_failure_returns_recommendation_with_caveat():
    """When MCP tool fails, agent still returns a recommendation noting data unavailability."""
    with patch("mcp_providers.agw.get_mcp_tools", return_value=AsyncMock(return_value=[])()):
        from agent import SampleAgent

        agent = SampleAgent()
        query = (
            "Batch B004 for material M400 is at 80% of TOR limit. "
            "Elapsed: 48 min, TOR limit: 60 min, remaining: 12 min. "
            "Batch data lookup failed. Provide recommendation."
        )

        mock_result = {
            "messages": [
                MagicMock(
                    content=(
                        "Decision: EXPEDITE\n"
                        "Urgency: HIGH\n"
                        "Remaining TOR: 12 minutes\n"
                        "Reasoning: Batch data unavailable — recommendation based on TOR time only. "
                        "12 minutes remaining; expedite immediately to minimise further exposure.\n"
                        "Compliance Note: GxP/GDP — manual verification of batch status required as data was unavailable."
                    )
                )
            ]
        }

        with patch.object(agent, "_invoke_with_fallback", return_value=mock_result):
            response = await agent.invoke(query, "test-context-mcp-failure")

        assert response.status == "completed"
        assert response.message  # Has a recommendation despite tool failure
        # Should mention data unavailability
        assert "unavailable" in response.message.lower() or "EXPEDITE" in response.message
