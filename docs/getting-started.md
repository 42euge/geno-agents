# Getting Started

## Prerequisites

- Python 3.10+
- A supported coding CLI (Claude Code, Gemini CLI, Codex, or OpenCode)
- [geno-tools](https://github.com/42euge/geno-tools) installed

## Install

```bash
geno-tools install geno-agents
```

Or from an agent session:

```
/geno-tools install geno-agents
```

This clones the repo, creates a venv, installs the CLI on PATH, and registers the skills with your coding agent.

## First use

### Check the agent network

```
/geno-agents
```

Shows all registered agents with their roles, current tasks, and resource usage.

### Register manually

```
/geno-agents register my-role
```

Or use a `.geno-agents` file at the repo root for automatic registration on session start:

```yaml
role: benchmark-agent
description: Kaggle benchmark tasks and dataset creation
capabilities:
  - kaggle
  - benchmarks
```

### Find an agent

```
/geno-agents whois browser
```

Searches by role name and capability tags.

### Update your status

```
/geno-agents update --working-on "refactoring scoring" --using browser
```

### Add the MCP server

Add to your agent's MCP configuration:

```json
{
  "geno-agents": {
    "command": "python",
    "args": ["-m", "geno_agents.mcp_server"]
  }
}
```

## CLI reference

| Command | Description |
|---------|-------------|
| `geno-agents register <role>` | Register with a role, description, and capabilities |
| `geno-agents unregister` | Remove from the registry |
| `geno-agents update` | Update card (--working-on, --using, --status) |
| `geno-agents heartbeat` | Send a presence heartbeat |
| `geno-agents ls` | List all registered agents |
| `geno-agents who` | Show your agent card |
| `geno-agents who-are` | List other agents (excludes yourself) |
| `geno-agents whois <query>` | Find by role or capability |
| `geno-agents prune` | Remove stale agents (10+ min inactive) |
