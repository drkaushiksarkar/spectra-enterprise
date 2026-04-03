"""SPECTRA multi-agent orchestration and MCP server.

This package provides the agentic AI layer for the SPECTRA health
intelligence platform, including:

- Multi-agent orchestration with specialized tool-calling agents
- MCP (Model Context Protocol) server for external AI integration
- Tool registry with automatic schema generation
"""

from agents.orchestrator import AgentOrchestrator, DataFusionAgent, AnalyticsAgent, ReportAgent
from agents.mcp_server import MCPServer
from agents.tools import tool, list_tools, execute_tool

__all__ = [
    "AgentOrchestrator",
    "DataFusionAgent",
    "AnalyticsAgent",
    "ReportAgent",
    "MCPServer",
    "tool",
    "list_tools",
    "execute_tool",
]
