from ai_agents.agents.base import AgentResult


class TestAgentResult:
    def test_default_metadata_is_none(self):
        result = AgentResult(text="hello")
        assert result.text == "hello"
        assert result.cost_usd is None
        assert result.duration_ms is None
        assert result.num_turns is None

    def test_with_all_metadata(self):
        result = AgentResult(
            text="response",
            cost_usd=0.0042,
            duration_ms=11500,
            num_turns=3,
        )
        assert result.cost_usd == 0.0042
        assert result.duration_ms == 11500
        assert result.num_turns == 3
