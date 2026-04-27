# geno-agents

Agent coordination layer — registration, discovery, and presence for multi-agent systems.

## What it does

geno-agents solves the "who's here and what are they doing?" problem for multi-agent setups. When multiple coding agent sessions run concurrently, they need to:

- **Discover each other** — find which agent handles a given capability
- **Coordinate resources** — avoid conflicts on shared resources (browser, APIs)
- **Track status** — know what each agent is working on and whether it's active

## Components

| Component | Description |
|-----------|-------------|
| **CLI** | `geno-agents` command with register, ls, who, whois, update, prune |
| **MCP server** | JSON-RPC stdio server exposing registry tools natively |
| **Skills** | Slash commands for agent coordination from within agent sessions |
| **`.geno-agents` file** | Per-repo agent identity declaration for auto-registration |

## Quick links

- [Getting Started](getting-started.md) — install and first use
- [`.geno-agents` file spec](agent-file.md) — per-repo agent identity format
- [GitHub](https://github.com/42euge/geno-agents)
