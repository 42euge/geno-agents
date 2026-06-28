---
name: geno-agents
description: >-
  Agent coordination — register as an agent, see who's online, update status.
  Also includes autonomous agent loops (supercharge).
  Use when user says /geno-agents, wants to register this session, check who's online,
  update what they're working on, or /geno-agents-supercharge.
allowed-tools: "Bash(geno-agents *) mcp__geno-agents__list_agents mcp__geno-agents__who mcp__geno-agents__whois mcp__geno-agents__update_agent mcp__geno-agents__register_agent"
argument-hint: "[who|whois|ls|register|update|status] [args...]"
license: MIT
metadata:
  author: 42euge
  version: "0.1.0"
---

# geno-agents — Agent Coordination

Umbrella skill for the geno-agents skillset. Routes to sub-skills based on arguments.

## Available skills

| Skill | Slash command | Description |
|-------|--------------|-------------|
| geno-agents | /geno-agents | Agent coordination — status, register, update, who, whois |
| geno-agents-supercharge | /geno-agents-supercharge | Long-running autonomous agent loop |
| geno-agents-tasks-start | /geno-agents-tasks-start | Pick up and execute a task from geno-notes |
