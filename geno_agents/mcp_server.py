"""MCP server for geno-agents coordination layer.

Exposes agent registry tools: list_agents, who, update_agent, register_agent.
Run with: python -m geno_agents.mcp_server
"""

from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import asdict
from typing import Any

from .registry import (
    Agent,
    find_by_capability,
    find_by_role,
    get,
    heartbeat,
    list_agents,
    register,
    update,
)


def _write_response(response: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()


def _success(id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": id, "result": result}


def _error(id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": id, "error": {"code": code, "message": message}}


TOOLS = [
    {
        "name": "list_agents",
        "description": "List all registered agents with their roles, capabilities, current task, and resource usage.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "include_stale": {
                    "type": "boolean",
                    "description": "Include agents not seen in 10+ minutes (default false)",
                    "default": False,
                },
            },
        },
    },
    {
        "name": "who",
        "description": "Find agents by role or capability. Use before messaging to find the right agent.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search term — matches against role names and capability tags",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "update_agent",
        "description": "Update this agent's card — set current task, resource usage, or status.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "Session ID (optional, auto-detected if omitted)",
                },
                "working_on": {
                    "type": "string",
                    "description": "What you're currently working on (empty string to clear)",
                },
                "using": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Resources currently in use, e.g. ['browser', 'kaggle-api'] (empty array to clear)",
                },
                "status": {
                    "type": "string",
                    "enum": ["available", "busy"],
                    "description": "Current availability status",
                },
            },
        },
    },
    {
        "name": "register_agent",
        "description": "Register this agent in the network with a role and capabilities.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "role": {
                    "type": "string",
                    "description": "Agent role name, e.g. 'benchmark-agent'",
                },
                "description": {
                    "type": "string",
                    "description": "What this agent does",
                },
                "capabilities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Capability tags for discovery, e.g. ['kaggle', 'benchmarks']",
                },
                "session_id": {
                    "type": "string",
                    "description": "Session ID (optional, auto-detected if omitted)",
                },
                "project": {
                    "type": "string",
                    "description": "Project directory name",
                },
            },
            "required": ["role"],
        },
    },
]


def _detect_session_id() -> str | None:
    import os
    return os.environ.get("CLAUDE_SESSION_ID")


def handle_tool_call(name: str, arguments: dict[str, Any]) -> str:
    if name == "list_agents":
        include_stale = arguments.get("include_stale", False)
        agents = list_agents(include_stale=include_stale)
        return json.dumps([asdict(a) for a in agents], indent=2)

    elif name == "who":
        query = arguments["query"]
        by_role = find_by_role(query)
        by_cap = find_by_capability(query)
        seen = set()
        results = []
        for a in by_role + by_cap:
            if a.session_id not in seen:
                seen.add(a.session_id)
                results.append(asdict(a))
        return json.dumps(results, indent=2)

    elif name == "update_agent":
        sid = arguments.get("session_id") or _detect_session_id()
        if not sid:
            return json.dumps({"error": "Could not detect session ID"})
        fields = {}
        if "working_on" in arguments:
            fields["working_on"] = arguments["working_on"]
        if "using" in arguments:
            fields["using"] = arguments["using"]
        if "status" in arguments:
            fields["status"] = arguments["status"]
        if not fields:
            return json.dumps({"error": "No fields to update"})
        if update(sid, **fields):
            return json.dumps({"updated": True, "session_id": sid})
        return json.dumps({"error": "Agent not registered. Register first."})

    elif name == "register_agent":
        sid = arguments.get("session_id") or _detect_session_id()
        if not sid:
            return json.dumps({"error": "Could not detect session ID"})
        agent = Agent(
            session_id=sid,
            role=arguments["role"],
            description=arguments.get("description", ""),
            capabilities=arguments.get("capabilities", []),
            project=arguments.get("project", ""),
        )
        register(agent)
        return json.dumps({"registered": True, "session_id": sid, "role": agent.role})

    return json.dumps({"error": f"Unknown tool: {name}"})


def handle_request(request: dict[str, Any]) -> None:
    req_id = request.get("id")
    method = request.get("method", "")

    if method == "initialize":
        _write_response(_success(req_id, {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "geno-agents", "version": "0.1.0"},
            "capabilities": {"tools": {}},
        }))

    elif method == "notifications/initialized":
        pass  # no response needed

    elif method == "tools/list":
        _write_response(_success(req_id, {"tools": TOOLS}))

    elif method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        try:
            result_text = handle_tool_call(tool_name, arguments)
            _write_response(_success(req_id, {
                "content": [{"type": "text", "text": result_text}],
            }))
        except Exception as e:
            _write_response(_error(req_id, -32000, str(e)))

    elif method == "ping":
        _write_response(_success(req_id, {}))

    else:
        if req_id is not None:
            _write_response(_error(req_id, -32601, f"Method not found: {method}"))


async def main() -> None:
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        line = await reader.readline()
        if not line:
            break
        try:
            request = json.loads(line.decode())
            handle_request(request)
        except json.JSONDecodeError:
            continue


if __name__ == "__main__":
    asyncio.run(main())
