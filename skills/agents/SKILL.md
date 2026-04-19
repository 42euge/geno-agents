---
name: agents
description: >-
  Agent coordination — register as an agent, see who's online, update status.
  Also includes autonomous agent loops (supercharge).
  Use when user says /geno-agents, wants to register this session, check who's online,
  update what they're working on, or /gt-supercharge.
allowed-tools: "Bash(~/.geno/venv/bin/geno-agents *) mcp__geno-agents__list_agents mcp__geno-agents__who mcp__geno-agents__whois mcp__geno-agents__update_agent mcp__geno-agents__register_agent"
argument-hint: "[who|whois|ls|register|update|status] [args...]"
---

# geno-agents — Agent Coordination

```!
which ~/.geno/venv/bin/geno-agents >/dev/null 2>&1 || echo "⚠️ geno-agents is not installed. Run: pip install -e ~/code-purp/geno-agents"
```

You have access to geno-agents MCP tools (`list_agents`, `who`, `update_agent`, `register_agent`) and the CLI at `~/.geno/venv/bin/geno-agents`.

## Commands

Parse the user's arguments to determine the action:

### `/geno-agents` (no args) or `/geno-agents status`
Show the current agent network. Use the `list_agents` MCP tool. Display a clean summary:
- Each agent's role, project, what they're working on, resources in use, and last seen
- Highlight the current session
- Flag stale agents

### `/geno-agents who`
Show who this agent is — display the current session's agent card. Use the `who` MCP tool (no arguments needed).

### `/geno-agents who-are`
List all other agents in the network (excludes yourself). Run:
```bash
~/.geno/venv/bin/geno-agents who-are --session-id "${CLAUDE_SESSION_ID:-}"
```

### `/geno-agents whois <query>`
Find agents by role or capability. Use the `whois` MCP tool.
Example: `/geno-agents whois browser` → finds agents with browser capability.

### `/geno-agents register <role>`
Register this session as an agent with the given role. If a `.geno-agents` file exists in the current directory, read role/description/capabilities from it instead.

To register from `.geno-agents` file:
```bash
~/.geno/venv/bin/geno-agents register "$(grep '^role:' .geno-agents | sed 's/^role: *//')" \
  --desc "$(grep '^description:' .geno-agents | sed 's/^description: *//')" \
  --project "$(basename $(pwd))" \
  --session-id "${CLAUDE_SESSION_ID:-}"
```

To register with a custom role:
Use the `register_agent` MCP tool with the provided role.

After registering, confirm by showing the agent card via `list_agents`.

### `/geno-agents update`
Update this agent's card. Parse the arguments for:
- `--working-on "description"` — what you're currently doing
- `--using resource` — shared resource you're using (browser, kaggle-api, etc.)
- `--status busy|available` — availability

Use the `update_agent` MCP tool.

### `/geno-agents ls`
Alias for status — list all agents.

## Auto-Registration

On session start, the `geno-agents-register.sh` hook automatically registers this session using the `.geno-agents` file in the project root. If no file exists, it infers the role from `CLAUDE.md`.

You can check if you're registered by running `/geno-agents status`.

## `.geno-agents` File Format

Projects declare their agent identity in a `.geno-agents` file at the repo root:

```yaml
role: benchmark-agent
description: Kaggle Learning Benchmark — task creation and evaluation
capabilities:
  - kaggle
  - benchmarks
  - notebooks
```
