# .geno-agents file spec

A `.geno-agents` file at the root of a repo declares the agent identity for that project. When an agent session starts in this directory, the auto-registration hook reads it and registers accordingly.

## Format

```yaml
role: dev-agent
description: Feature development and code review
capabilities:
  - coding
  - testing
  - review
```

## Fields

| Field | Required | Description |
|-------|----------|-------------|
| role | yes | Agent identity name |
| description | no | What this agent does (1 line) |
| capabilities | no | Capability tags for discovery |
