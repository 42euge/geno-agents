# geno-agents

Agent coordination layer — registration, discovery, and presence for multi-agent systems.

Provides a CLI, MCP server, and coding agent skills for managing agent identity, discovering peers by role or capability, and coordinating shared resource usage across concurrent agent sessions.

## Install

```bash
geno-tools install geno-agents
```

Or from an agent session:

```
/geno-tools install geno-agents
```

## Features

- **Agent registry** — register with a role, description, and capability tags
- **Discovery** — find agents by role (`whois browser`) or list all (`ls`)
- **Presence** — heartbeat-based liveness with automatic stale detection
- **Resource coordination** — declare shared resources in use to avoid conflicts
- **MCP server** — native tool integration for supported coding agents
- **`.geno-agents` file** — declare agent identity per-repo for auto-registration

## CLI commands

| Command | Description |
|---------|-------------|
| `geno-agents register <role>` | Register with a role |
| `geno-agents ls` | List all agents |
| `geno-agents who` | Show your agent card |
| `geno-agents who-are` | List other agents |
| `geno-agents whois <query>` | Find by role or capability |
| `geno-agents update` | Update card (--working-on, --using, --status) |
| `geno-agents heartbeat` | Send a presence heartbeat |
| `geno-agents prune` | Remove stale agents |

## Documentation

[https://42euge.github.io/geno-agents](https://42euge.github.io/geno-agents)

## License

MIT
