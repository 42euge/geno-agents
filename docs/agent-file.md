# .geno-agents file spec

A `.geno-agents` file at the root of a repo declares the agent identity for that project. When a Claude Code session starts in this directory, the auto-registration hook reads it and registers accordingly.

## Format

```yaml
role: benchmark-agent
description: Kaggle benchmark tasks and dataset creation
capabilities:
  - kaggle
  - benchmarks
  - notebooks
```

## Fields

| Field | Required | Description |
|-------|----------|-------------|
| role | yes | Agent identity name |
| description | no | What this agent does (1 line) |
| capabilities | no | Capability tags for discovery |
