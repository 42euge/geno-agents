# geno-agents

Agent coordination layer — registration, discovery, and presence for multi-agent systems. Provides a CLI, MCP server, and coding agent skills for managing agent identity, finding peers by role or capability, and coordinating shared resource usage.

## Skills

| Skill | Sub-skillset | Slash command |
|-------|-------------|---------------|
| geno-agents | — | — (umbrella) |
| geno-agents-supercharge | — | /geno-agents-supercharge |
| geno-agents-tasks-start | — | /geno-agents-tasks-start |

## Repo structure

```
geno-agents/
├── GENO.md              # agent instructions (this file)
├── SKILL.md             # umbrella skill manifest
├── genotools.yaml       # geno-tools manifest
├── pyproject.toml       # Python package
├── package.json         # npm metadata
├── .geno-agents         # agent identity file for this repo
├── geno_agents/         # Python package
│   ├── cli.py           #   click CLI (register, update, ls, who, whois, prune)
│   ├── registry.py      #   agent registry (JSON at ~/.geno/agents/registry.json)
│   ├── mcp_server.py    #   MCP server (JSON-RPC over stdio)
│   └── __main__.py      #   entry point (routes to CLI or MCP server)
├── skills/              # skill definitions
│   ├── geno-agents/     #   umbrella skill
│   ├── geno-agents-supercharge/  # autonomous agent loop
│   └── geno-agents-tasks-start/  # task execution from geno-notes
└── docs/                # documentation site
```

## Architecture

### Registry

Agent state is stored as JSON at `~/.geno/agents/registry.json`. Each entry is keyed by session ID and contains: role, description, capabilities, status, working_on, using, project, and timestamps.

### CLI

Entry point: `geno_agents.cli:main` (click). Subcommands: `register`, `unregister`, `update`, `heartbeat`, `ls`, `who`, `who-are`, `whois`, `prune`.

### MCP server

`geno_agents.mcp_server` exposes five tools over JSON-RPC stdio: `list_agents`, `who`, `whois`, `update_agent`, `register_agent`.

### `.geno-agents` file

Projects declare agent identity via a `.geno-agents` YAML file at the repo root. Fields: `role` (required), `description`, `capabilities`. The auto-registration hook reads this on session start.

## Conventions

- The CLI is installed by `geno-tools install geno-agents` and exposed on PATH.
- Agent data lives at `~/.geno/agents/` — never committed.
- Agents are identified by session ID and expire after 10 minutes without a heartbeat.
- The `who-are` command excludes the calling session; `ls` includes all agents.

### Prefix aliasing

Source code and documentation use the canonical `geno-` prefix (e.g., `geno-agents`, `/geno-agents-supercharge`). Short `/gt-` aliases (e.g., `/gt-supercharge`, `/gt-agents`) are configured per-install by `geno-tools` and are not defined in this repo. When adding new skills or commands, always use the canonical `geno-agents` prefix; the installer handles alias generation.

### Adding a new skill

To add a new skill to the geno-agents skillset:

1. Create a directory under `skills/<skill-name>/` with a `SKILL.md` file containing YAML front-matter (`name`, `description`, `allowed-tools`, `license`, `metadata`) and usage instructions.
2. Register the skill in the `Skills` table in this file (`GENO.md`).
3. Add the skill to the `Available skills` table in the umbrella `SKILL.md`.
4. If the skill needs new CLI subcommands, add them in `geno_agents/cli.py`.
5. If the skill needs new MCP tools, add them in `geno_agents/mcp_server.py` and list them in the `allowed-tools` front-matter field.
6. Update `genotools.yaml` with the new skill entry so `geno-tools install` picks it up.
