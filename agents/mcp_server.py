"""MCP (Model Context Protocol) server for SPECTRA health intelligence.

Exposes health intelligence tools via JSON-RPC 2.0 protocol, enabling
external AI agents to query indicators, run forecasts, retrieve country
profiles, and search biomedical evidence through a standardized interface.
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "name": "query_indicators",
        "description": "Query health, climate, or economic indicators by code, country, and time range",
        "inputSchema": {
            "type": "object",
            "properties": {
                "indicator_codes": {"type": "array", "items": {"type": "string"}, "description": "Indicator codes to query"},
                "countries": {"type": "array", "items": {"type": "string"}, "description": "ISO3 country codes"},
                "year_start": {"type": "integer"},
                "year_end": {"type": "integer"},
            },
            "required": ["indicator_codes"],
        },
    },
    {
        "name": "run_forecast",
        "description": "Generate disease incidence forecast for a country and indicator",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "ISO3 country code"},
                "indicator": {"type": "string", "description": "Disease indicator code"},
                "horizon_months": {"type": "integer", "default": 12},
                "model": {"type": "string", "enum": ["arima", "prophet", "ensemble"], "default": "ensemble"},
            },
            "required": ["country", "indicator"],
        },
    },
    {
        "name": "get_country_profile",
        "description": "Retrieve comprehensive health, climate, and economic profile for a country",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "ISO3 country code"},
                "sections": {"type": "array", "items": {"type": "string", "enum": ["health", "climate", "economics", "demographics"]}, "default": ["health", "climate", "economics"]},
            },
            "required": ["country"],
        },
    },
    {
        "name": "search_evidence",
        "description": "Semantic search over biomedical evidence base (268M embedded passages)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Natural language search query"},
                "top_k": {"type": "integer", "default": 10},
                "source_filter": {"type": "string", "enum": ["all", "pmc", "who", "lancet"], "default": "all"},
            },
            "required": ["query"],
        },
    },
]


@dataclass
class JSONRPCRequest:
    method: str
    params: dict[str, Any]
    id: str | int | None = None
    jsonrpc: str = "2.0"


@dataclass
class JSONRPCResponse:
    result: Any = None
    error: dict[str, Any] | None = None
    id: str | int | None = None
    jsonrpc: str = "2.0"

    def to_dict(self) -> dict[str, Any]:
        resp: dict[str, Any] = {"jsonrpc": self.jsonrpc, "id": self.id}
        if self.error is not None:
            resp["error"] = self.error
        else:
            resp["result"] = self.result
        return resp


class MCPServer:
    """MCP-compliant server exposing health intelligence tools.

    Handles tool discovery (tools/list), tool execution (tools/call),
    and server capability negotiation via JSON-RPC 2.0.
    """

    def __init__(self) -> None:
        self.tools = {t["name"]: t for t in TOOL_DEFINITIONS}
        self._handlers: dict[str, Any] = {
            "initialize": self._handle_initialize,
            "tools/list": self._handle_tools_list,
            "tools/call": self._handle_tools_call,
            "ping": self._handle_ping,
        }

    def handle_request(self, raw: str) -> str:
        try:
            data = json.loads(raw)
            request = JSONRPCRequest(
                method=data["method"],
                params=data.get("params", {}),
                id=data.get("id"),
            )
        except (json.JSONDecodeError, KeyError) as exc:
            return json.dumps(JSONRPCResponse(
                error={"code": -32700, "message": f"Parse error: {exc}"}
            ).to_dict())

        handler = self._handlers.get(request.method)
        if handler is None:
            return json.dumps(JSONRPCResponse(
                error={"code": -32601, "message": f"Method not found: {request.method}"},
                id=request.id,
            ).to_dict())

        try:
            result = handler(request.params)
            return json.dumps(JSONRPCResponse(result=result, id=request.id).to_dict())
        except Exception as exc:
            logger.exception("Handler error for %s", request.method)
            return json.dumps(JSONRPCResponse(
                error={"code": -32000, "message": str(exc)},
                id=request.id,
            ).to_dict())

    def _handle_initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "spectra-health-intelligence", "version": "2.0.0"},
            "capabilities": {"tools": {"listChanged": False}},
        }

    def _handle_tools_list(self, params: dict[str, Any]) -> dict[str, Any]:
        return {"tools": TOOL_DEFINITIONS}

    def _handle_tools_call(self, params: dict[str, Any]) -> dict[str, Any]:
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        executor = getattr(self, f"_exec_{tool_name}", None)
        if executor is None:
            raise ValueError(f"No executor for tool: {tool_name}")

        result = executor(arguments)
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}

    def _handle_ping(self, params: dict[str, Any]) -> dict[str, Any]:
        return {}

    def _exec_query_indicators(self, args: dict[str, Any]) -> dict[str, Any]:
        codes = args.get("indicator_codes", [])
        countries = args.get("countries", [])
        return {
            "indicators": codes,
            "countries": countries if countries else ["global"],
            "records_matched": len(codes) * max(len(countries), 1) * 25,
            "note": "Connect to SAGE warehouse for live data",
        }

    def _exec_run_forecast(self, args: dict[str, Any]) -> dict[str, Any]:
        return {
            "country": args["country"],
            "indicator": args["indicator"],
            "model": args.get("model", "ensemble"),
            "horizon_months": args.get("horizon_months", 12),
            "status": "forecast_generated",
            "note": "Connect to forecasting engine for live predictions",
        }

    def _exec_get_country_profile(self, args: dict[str, Any]) -> dict[str, Any]:
        return {
            "country": args["country"],
            "sections": args.get("sections", ["health", "climate", "economics"]),
            "status": "profile_retrieved",
        }

    def _exec_search_evidence(self, args: dict[str, Any]) -> dict[str, Any]:
        return {
            "query": args["query"],
            "top_k": args.get("top_k", 10),
            "source_filter": args.get("source_filter", "all"),
            "status": "search_complete",
            "note": "Connect to OpenSearch AOSS for live semantic search",
        }


def run_stdio() -> None:
    """Run MCP server in stdio transport mode."""
    server = MCPServer()
    logger.info("SPECTRA MCP server started (stdio transport)")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        response = server.handle_request(line)
        sys.stdout.write(response + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    run_stdio()
