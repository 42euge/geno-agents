"""CLI for agent coordination."""

import json
import sys
import time

import click

from geno_agents.registry import (
    Agent,
    find_by_capability,
    find_by_role,
    get,
    heartbeat,
    list_agents,
    prune_stale,
    register,
    unregister,
    update,
)


def _detect_session_id() -> str | None:
    """Try to detect the current Claude Code session ID."""
    import os
    sid = os.environ.get("CLAUDE_SESSION_ID")
    if sid:
        return sid
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "geno_msg.store", "--session-id"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return None


@click.group()
def main():
    """geno-agents — Agent coordination layer."""
    pass


@main.command()
@click.argument("role")
@click.option("--desc", "-d", default="", help="What this agent does")
@click.option("--cap", "-c", multiple=True, help="Capability tags (repeatable)")
@click.option("--project", "-p", default="", help="Project directory name")
@click.option("--session-id", default=None, help="Session ID (auto-detected if omitted)")
def register_cmd(role: str, desc: str, cap: tuple, project: str, session_id: str | None):
    """Register this agent with a role."""
    if not session_id:
        session_id = _detect_session_id()
    if not session_id:
        click.echo("Error: could not detect session ID. Pass --session-id explicitly.", err=True)
        sys.exit(1)

    agent = Agent(
        session_id=session_id,
        role=role,
        description=desc,
        capabilities=list(cap),
        project=project,
    )
    register(agent)
    click.echo(f"Registered: {role} ({session_id[:8]}...)")


@main.command("unregister")
@click.option("--session-id", default=None)
def unregister_cmd(session_id: str | None):
    """Unregister this agent."""
    if not session_id:
        session_id = _detect_session_id()
    if not session_id:
        click.echo("Error: could not detect session ID.", err=True)
        sys.exit(1)
    if unregister(session_id):
        click.echo(f"Unregistered: {session_id[:8]}...")
    else:
        click.echo("Not found in registry.", err=True)


@main.command("update")
@click.option("--working-on", "-w", default=None, help="Current task description")
@click.option("--using", "-u", multiple=True, help="Resources in use (repeatable, empty to clear)")
@click.option("--status", "-s", type=click.Choice(["available", "busy"]), default=None)
@click.option("--session-id", default=None)
def update_cmd(working_on: str | None, using: tuple, status: str | None, session_id: str | None):
    """Update this agent's card (working_on, using, status)."""
    if not session_id:
        session_id = _detect_session_id()
    if not session_id:
        click.echo("Error: could not detect session ID.", err=True)
        sys.exit(1)

    fields = {}
    if working_on is not None:
        fields["working_on"] = working_on
    if using:
        fields["using"] = [u for u in using if u]  # filter empty strings
    if status:
        fields["status"] = status

    if not fields:
        click.echo("Nothing to update.", err=True)
        sys.exit(1)

    if update(session_id, **fields):
        click.echo(f"Updated: {session_id[:8]}...")
    else:
        click.echo("Not registered. Register first.", err=True)
        sys.exit(1)


@main.command("heartbeat")
@click.option("--status", type=click.Choice(["available", "busy"]), default=None)
@click.option("--session-id", default=None)
def heartbeat_cmd(status: str | None, session_id: str | None):
    """Send a heartbeat (update last_seen)."""
    if not session_id:
        session_id = _detect_session_id()
    if not session_id:
        sys.exit(1)
    heartbeat(session_id, status)


@main.command("ls")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.option("--all", "show_all", is_flag=True, help="Include stale agents")
def ls_cmd(as_json: bool, show_all: bool):
    """List registered agents."""
    agents = list_agents(include_stale=show_all)

    if as_json:
        from dataclasses import asdict
        click.echo(json.dumps([asdict(a) for a in agents], indent=2))
        return

    if not agents:
        click.echo("No agents registered.")
        return

    now = time.time()
    for a in agents:
        age = int(now - a.last_seen)
        if age < 60:
            seen = f"{age}s ago"
        elif age < 3600:
            seen = f"{age // 60}m ago"
        else:
            seen = f"{age // 3600}h ago"

        status_icon = {"available": "🟢", "busy": "🟡", "stale": "⚪", "offline": "🔴"}.get(a.status, "❓")
        caps = f"  [{', '.join(a.capabilities)}]" if a.capabilities else ""
        proj = f"  📁 {a.project}" if a.project else ""
        task = f"  📋 {a.working_on}" if a.working_on else ""
        res = f"  🔒 {', '.join(a.using)}" if a.using else ""
        click.echo(f"  {status_icon} {a.session_id[:8]}  {a.role:<20} {seen:<10} {a.description}{caps}{proj}{task}{res}")


@main.command("who")
@click.option("--session-id", default=None)
def who_cmd(session_id: str | None):
    """Show who this agent is (my card)."""
    if not session_id:
        session_id = _detect_session_id()
    if not session_id:
        click.echo("Not registered — session ID not detected.", err=True)
        sys.exit(1)

    agent = get(session_id)
    if not agent:
        click.echo("Not registered. Run: geno-agents register <role>")
        return

    caps = ", ".join(agent.capabilities) if agent.capabilities else "none"
    click.echo(f"  Role:        {agent.role}")
    click.echo(f"  Description: {agent.description or '—'}")
    click.echo(f"  Project:     {agent.project or '—'}")
    click.echo(f"  Capabilities: [{caps}]")
    click.echo(f"  Status:      {agent.status}")
    click.echo(f"  Working on:  {agent.working_on or '—'}")
    click.echo(f"  Using:       {', '.join(agent.using) if agent.using else '—'}")
    click.echo(f"  Session:     {agent.session_id}")


@main.command("whois")
@click.argument("query")
def whois_cmd(query: str):
    """Find agents by role or capability."""
    by_role = find_by_role(query)
    by_cap = find_by_capability(query)

    seen = set()
    results = []
    for a in by_role + by_cap:
        if a.session_id not in seen:
            seen.add(a.session_id)
            results.append(a)

    if not results:
        click.echo(f"No agents matching '{query}'.")
        return

    for a in results:
        caps = f"  [{', '.join(a.capabilities)}]" if a.capabilities else ""
        task = f"  📋 {a.working_on}" if a.working_on else ""
        click.echo(f"  {a.session_id[:8]}  {a.role:<20} {a.description}{caps}{task}")


@main.command("prune")
def prune_cmd():
    """Remove stale agents from the registry."""
    count = prune_stale()
    click.echo(f"Pruned {count} stale agent(s).")
