"""Unit tests for the multi-agent orchestrator."""
import asyncio
import pytest
from agents.orchestrator import (
    AgentOrchestrator, DataFusionAgent, AnalyticsAgent, ReportAgent,
    AgentStatus, ToolRegistry,
)


class TestToolRegistry:
    def test_register_and_list(self):
        registry = ToolRegistry()
        registry.register("test_tool", "A test tool", {"required": []}, lambda: "ok")
        tools = registry.list_tools()
        assert len(tools) == 1
        assert tools[0]["name"] == "test_tool"

    def test_get_missing_tool_raises(self):
        registry = ToolRegistry()
        with pytest.raises(KeyError, match="Tool not found"):
            registry.get("nonexistent")

    def test_execute_validates_required_params(self):
        registry = ToolRegistry()
        registry.register("need_param", "Needs a param", {"required": ["x"]}, lambda x: x)
        with pytest.raises(ValueError, match="Missing required"):
            asyncio.get_event_loop().run_until_complete(registry.execute("need_param"))

    def test_execute_calls_handler(self):
        registry = ToolRegistry()
        registry.register("add", "Add numbers", {"required": ["a", "b"]}, lambda a, b: a + b)
        result = asyncio.get_event_loop().run_until_complete(registry.execute("add", a=2, b=3))
        assert result == 5


class TestDataFusionAgent:
    def setup_method(self):
        self.agent = DataFusionAgent()

    def test_initial_status_is_idle(self):
        assert self.agent.status == AgentStatus.IDLE

    def test_has_required_tools(self):
        tool_names = [t["name"] for t in self.agent.tools.list_tools()]
        assert "discover_sources" in tool_names
        assert "resolve_schema" in tool_names
        assert "fuse_datasets" in tool_names

    def test_execute_health_domain(self):
        result = asyncio.get_event_loop().run_until_complete(
            self.agent.execute({"domain": "health", "description": "Test fusion"})
        )
        assert result["status"] == "success"
        assert result["records"] > 0
        assert self.agent.status == AgentStatus.COMPLETED

    def test_execute_unknown_domain(self):
        result = asyncio.get_event_loop().run_until_complete(
            self.agent.execute({"domain": "unknown"})
        )
        assert result["status"] == "success"
        assert result["records"] == 0


class TestAnalyticsAgent:
    def test_execute_trend_analysis(self):
        agent = AnalyticsAgent()
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute({"dataset": {"records": 1000}, "analysis_type": "trend"})
        )
        assert result["status"] == "success"
        assert result["validation"]["valid"] is True

    def test_execute_default_analysis(self):
        agent = AnalyticsAgent()
        result = asyncio.get_event_loop().run_until_complete(agent.execute({}))
        assert result["status"] == "success"


class TestReportAgent:
    def test_generate_executive_report(self):
        agent = ReportAgent()
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute({"analysis_results": {}, "audience": "executive"})
        )
        assert result["status"] == "success"
        assert result["report"]["audience"] == "executive"

    def test_generate_technical_report(self):
        agent = ReportAgent()
        result = asyncio.get_event_loop().run_until_complete(
            agent.execute({"analysis_results": {}, "audience": "technical"})
        )
        assert result["report"]["audience"] == "technical"


class TestAgentOrchestrator:
    def test_default_agents_registered(self):
        orch = AgentOrchestrator()
        assert "DataFusionAgent" in orch.agents
        assert "AnalyticsAgent" in orch.agents
        assert "ReportAgent" in orch.agents

    def test_get_statuses(self):
        orch = AgentOrchestrator()
        statuses = orch.get_statuses()
        assert all(s == "idle" for s in statuses.values())

    def test_list_tools(self):
        orch = AgentOrchestrator()
        tools = orch.list_tools()
        assert len(tools) == 3

    def test_execute_workflow(self):
        orch = AgentOrchestrator()
        result = asyncio.get_event_loop().run_until_complete(
            orch.execute_workflow({"domain": "health", "analyses": ["trend", "anomaly"], "audience": "executive"})
        )
        assert result["status"] == "completed"
        assert len(result["steps"]) == 3
        assert result["elapsed_seconds"] > 0

