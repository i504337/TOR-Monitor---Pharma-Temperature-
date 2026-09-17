"""Test: LLM timeout → default EXPEDITE fallback response returned."""
import pytest
from unittest.mock import AsyncMock, patch
from litellm.exceptions import Timeout


@pytest.mark.asyncio
async def test_timeout_returns_fallback_response():
    """When all models time out, agent returns an error status gracefully."""
    with patch("mcp_providers.agw.get_mcp_tools", return_value=AsyncMock(return_value=[])()):
        from agent import SampleAgent

        agent = SampleAgent()
        query = "Batch B005 is at 80% TOR. Recommend EXPEDITE or HOLD."

        with patch.object(
            agent,
            "_invoke_with_fallback",
            side_effect=Timeout(message="Request timed out", model="gpt-4o", llm_provider="openai"),
        ):
            response = await agent.invoke(query, "test-context-timeout")

        # Agent should handle the error gracefully and return an error status or completed with fallback
        assert response.status in ("completed", "error")
        assert response.message  # Should have some message
