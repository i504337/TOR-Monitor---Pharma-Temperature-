"""Test: batch with 25% TOR remaining → EXPEDITE recommendation."""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_expedite_recommendation():
    """Agent recommends EXPEDITE when 25% TOR time remains."""
    with patch("mcp_providers.agw.get_mcp_tools", return_value=AsyncMock(return_value=[])()):
        from agent import SampleAgent

        agent = SampleAgent()
        query = (
            "Batch B001 for material M100 has reached 75% of its TOR limit. "
            "Elapsed: 45 min, TOR limit: 60 min, remaining: 15 min. "
            "Provide an EXPEDITE or HOLD recommendation."
        )

        mock_result = {
            "messages": [
                MagicMock(
                    content=(
                        "Decision: EXPEDITE\n"
                        "Urgency: HIGH\n"
                        "Remaining TOR: 15 minutes\n"
                        "Reasoning: Batch has limited TOR remaining but can still be safely moved to the line.\n"
                        "Compliance Note: GxP/GDP — expedite to minimise further TOR consumption."
                    )
                )
            ]
        }

        with patch.object(agent, "_invoke_with_fallback", return_value=mock_result):
            response = await agent.invoke(query, "test-context-expedite")

        assert response.status == "completed"
        assert "EXPEDITE" in response.message
