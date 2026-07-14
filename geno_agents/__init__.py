"""geno-agents — agent coordination + execution/tracking layer.

Two halves that share ~/.geno/agents/:
  - registry: peer discovery (who's online, roles, capabilities) → registry.json
  - runner:   execution/tracking of launched processes            → <id>.json
"""

__version__ = "0.3.0"

from .runner import (
    read_status,
    write_status,
    list_agents as list_runs,
    wait_for_agent,
    run_agent,
    run_agent_pty,
)

__all__ = [
    "read_status",
    "write_status",
    "list_runs",
    "wait_for_agent",
    "run_agent",
    "run_agent_pty",
    "__version__",
]
