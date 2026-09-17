"""Integration test: end-to-end agent flow with mocked LLM and MCP tools."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_end_to_end_warning_batch_flow():
    """Integration test: 80% threshold batch goes through full advisory flow."""
    # Simulate a batch at 80% of TOR limit — typical warning stage trigger
    with patch("mcp_providers.agw.get_mcp_tools", return_value=AsyncMock(return_value=[])()):
        from agent import SampleAgent

        agent = SampleAgent()
        query = (
            "Batch PHARMA-2024-001 for material API-123 has reached 80% of its TOR limit. "
            "Elapsed: 48 min, TOR limit: 60 min, remaining: 12 min. "
            "Production line has active demand. Batch quantity: 100 units. "
            "Should we expedite to the line or hold?"
        )

        # Mock end-to-end LLM response — recommendation with all required fields
        expected_recommendation = (
            "Decision: EXPEDITE\n"
            "Urgency: HIGH\n"
            "Remaining TOR: 12 minutes\n"
            "Reasoning: Production line has active demand and 12 minutes is sufficient to move the batch. "
            "Expedite immediately to prevent TOR breach.\n"
            "Compliance Note: GxP/GDP — batch remains within TOR limits; expediting is compliant with pharmaceutical handling requirements."
        )

        mock_result = {
            "messages": [MagicMock(content=expected_recommendation)]
        }

        with patch.object(agent, "_invoke_with_fallback", return_value=mock_result):
            # Test stream interface
            chunks = []
            async for chunk in agent.stream(query, "integration-test-context"):
                chunks.append(chunk)

        # Should have at least a working status and a completed status
        assert len(chunks) >= 2

        # Last chunk must be complete
        final_chunk = chunks[-1]
        assert final_chunk["is_task_complete"] is True
        assert final_chunk["require_user_input"] is False

        # Response must contain a clear decision
        content = final_chunk["content"]
        assert "EXPEDITE" in content

        # Response must include compliance information
        assert "GxP" in content or "GDP" in content or "compliance" in content.lower()
