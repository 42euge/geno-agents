"""Agent registry — register, discover, and manage agent roles.

Stores agent registrations at ~/.geno/agents/registry.json.
Each agent has a session_id, role, description, capabilities, and status.
"""

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

REGISTRY_DIR = Path.home() / ".geno" / "agents"
REGISTRY_FILE = REGISTRY_DIR / "registry.json"

# Agents not seen for this many seconds are considered stale
STALE_THRESHOLD = 600  # 10 minutes


@dataclass
class Agent:
    session_id: str
    role: str
    description: str = ""
    capabilities: list[str] = field(default_factory=list)
    status: str = "available"  # available, busy, offline
    last_seen: float = field(default_factory=time.time)
    registered_at: float = field(default_factory=time.time)


def _load() -> dict[str, dict]:
    if REGISTRY_FILE.exists():
        with open(REGISTRY_FILE) as f:
            return json.load(f)
    return {}


def _save(data: dict[str, dict]) -> None:
    REGISTRY_DIR.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def register(agent: Agent) -> None:
    """Register an agent or update its registration."""
    data = _load()
    data[agent.session_id] = asdict(agent)
    _save(data)


def unregister(session_id: str) -> bool:
    """Remove an agent from the registry. Returns True if it existed."""
    data = _load()
    if session_id in data:
        del data[session_id]
        _save(data)
        return True
    return False


def heartbeat(session_id: str, status: str | None = None) -> bool:
    """Update last_seen timestamp. Optionally update status. Returns False if not registered."""
    data = _load()
    if session_id not in data:
        return False
    data[session_id]["last_seen"] = time.time()
    if status:
        data[session_id]["status"] = status
    _save(data)
    return True


def get(session_id: str) -> Agent | None:
    """Get a single agent by session ID (supports partial match)."""
    data = _load()
    # Exact match first
    if session_id in data:
        return Agent(**data[session_id])
    # Partial match
    matches = [k for k in data if k.startswith(session_id)]
    if len(matches) == 1:
        return Agent(**data[matches[0]])
    return None


def list_agents(include_stale: bool = False) -> list[Agent]:
    """List all registered agents, sorted by last_seen (most recent first)."""
    data = _load()
    now = time.time()
    agents = []
    for entry in data.values():
        agent = Agent(**entry)
        if not include_stale and (now - agent.last_seen) > STALE_THRESHOLD:
            agent.status = "stale"
        agents.append(agent)
    agents.sort(key=lambda a: a.last_seen, reverse=True)
    return agents


def find_by_role(role: str) -> list[Agent]:
    """Find agents by role (substring match)."""
    return [a for a in list_agents() if role.lower() in a.role.lower()]


def find_by_capability(capability: str) -> list[Agent]:
    """Find agents that have a matching capability."""
    return [
        a for a in list_agents()
        if any(capability.lower() in c.lower() for c in a.capabilities)
    ]


def prune_stale() -> int:
    """Remove agents that haven't been seen recently. Returns count removed."""
    data = _load()
    now = time.time()
    stale = [k for k, v in data.items() if (now - v.get("last_seen", 0)) > STALE_THRESHOLD]
    for k in stale:
        del data[k]
    if stale:
        _save(data)
    return len(stale)
