---
name: geno-agents-supercharge
description: >-
  Run an extended autonomous work session with structured cycles of
  planning, implementation, and evaluation. Works in any workspace —
  discovers tasks from geno-notes, TODOs, or user-specified goals.
disable-model-invocation: true
argument-hint: "[duration] [scope]  e.g. 'go!', '4h auth-refactor', '12h all'"
license: MIT
metadata:
  author: 42euge
  version: "0.2.0"
observability:
  success_signal: "all planned cycles completed (or early-stopped because tasks are healthy) with checkpoints and session log written"
  failure_signals:
    - "cycle agent crashes repeatedly and no checkpoint is written"
    - "same action fails 3+ times without forward progress"
    - "git push or Kaggle API errors block all remaining work"
  knowledge_reads:
    - "task notebooks and reviews in tasks/"
    - "CLAUDE.md for architecture rules"
    - "~/.geno/supercharge/state.json (cross-session memory)"
    - "previous cycle checkpoints"
  knowledge_writes:
    - "session log at geno-agents/supercharge/sessions/<timestamp>/session.md"
    - "cycle checkpoints at geno-agents/supercharge/sessions/<timestamp>/checkpoints/"
    - "~/.geno/supercharge/state.json (updated cross-session memory)"
    - "task reviews in tasks/<task>/review/"
---

# Supercharge — Long-Running Autonomous Agent Loop

Run an extended autonomous work session with structured cycles of planning, implementation, and evaluation. Works in any workspace — discovers tasks from geno-notes, scans for TODOs, or accepts user-specified goals. Based on Anthropic's harness design patterns for long-running apps.

## Input

`$ARGUMENTS` — Optional directives. Examples:
- `go!` — Start with defaults (8 hours, all discovered tasks)
- `4h auth-refactor` — 4 hours focused on one area
- `12h all` — Maximum duration across everything

If no arguments, ask the user for duration and scope.

## Configuration

### Duration Dial

Map the requested duration to cycle counts. Each cycle is ~30 minutes of wall time:

| Duration | Cycles | Use case |
|----------|--------|----------|
| 1h       | 2      | Quick pass on one task |
| 2h       | 4      | Focused work on 1-2 tasks |
| 4h       | 8      | Medium run across several tasks |
| 8h       | 16     | Full run across all tasks |
| 12h      | 24     | Maximum — deep iteration on everything |

### Storage

- **Session log:** `geno-agents/supercharge/sessions/<timestamp>/session.md` — running log of what happened
- **Checkpoints:** `geno-agents/supercharge/sessions/<timestamp>/checkpoints/` — state snapshots between cycles
- **Artifacts:** `geno-agents/supercharge/sessions/<timestamp>/artifacts/` — generated files, analysis, etc.
- **Global state:** `~/.geno/supercharge/state.json` — cross-session memory (what worked, what didn't)

## Architecture

Three specialized agent roles cycle through work:

### Planner (runs at start and every 4 cycles)
- Reads current task state via `geno-notes list --project --json`
- Reads CLAUDE.md / CLAUDE.local.md for project conventions
- Checks `git status` and recent history for in-flight work
- Reviews any existing plans and previous checkpoint findings
- Prioritizes tasks from the backlog and writes a sprint plan to `checkpoints/sprint_<n>.md`
- Considers: which tasks are blocked? which are highest priority? which have failing tests? what does the user care about most?

### Implementer (runs most cycles)
- Picks up tasks from the sprint plan
- Does the actual work: code changes, file edits, running commands, fixing tests
- After each meaningful change, commits to git with a descriptive message
- Logs progress via `geno-notes note "<cycle N: summary of what was done>"`
- Writes a brief handoff note to `checkpoints/impl_<cycle>.md`

### Evaluator (runs every 2-3 cycles)
- Checks: do tests pass? does the build succeed? does `git diff` look right?
- Reviews whether acceptance criteria from the sprint plan are met
- Runs any project-specific validation (linters, type checks, integration tests)
- Compares current state against the sprint plan goals
- Writes evaluation to `checkpoints/eval_<cycle>.md`
- Feeds findings back into the next planner cycle

## Cycle Structure

Each cycle follows this pattern:

```
1. READ checkpoint from previous cycle
2. DECIDE role for this cycle (planner/implementer/evaluator)
3. EXECUTE the role's work
4. WRITE checkpoint with:
   - What was done
   - Current state of each task
   - What to do next
   - Any blockers or surprises
5. LOG to session.md
6. LOG milestone to geno-notes via `geno-notes note`
```

### Role Rotation

Default rotation pattern per 4-cycle sprint:
1. **Plan** — assess state, set priorities
2. **Implement** — work on highest priority item
3. **Implement** — continue or move to next item
4. **Evaluate** — check results, review, adjust

### Context Management

To handle long runs without context degradation:
- Each cycle runs as a **separate Agent** with a fresh context
- The checkpoint file is the handoff document — it must contain everything the next agent needs
- The session log is append-only and provides full history
- If a cycle's agent runs into context limits, it writes a checkpoint and the next cycle picks up

## Task Discovery

Tasks are discovered in priority order:

1. **geno-notes project scope** — `geno-notes list --project --status backlog --json` for backlog tasks; `geno-notes list --project --status in-progress --json` for in-flight work
2. **User-specified goals** — if the user provided a scope in `$ARGUMENTS`, treat it as the primary objective
3. **Code scanning** — search for `TODO`, `FIXME`, `HACK`, `XXX` comments in the codebase as supplementary work items
4. **Git state** — check for uncommitted changes, unfinished merges, or stale branches that need attention
5. **Ask the user** — if none of the above yields actionable work, ask what to focus on

## Execution

### Startup

1. Parse duration and scope from `$ARGUMENTS`
2. Create session directory: `geno-agents/supercharge/sessions/<YYYYMMDD-HHMM>/`
3. Read current state:
   - Discover tasks via geno-notes (`geno-notes list --project --json`)
   - Check `git status` and `git log --oneline -10` for recent activity
   - Scan for TODOs/FIXMEs if no geno-notes tasks exist
   - Read CLAUDE.md for project conventions and constraints
4. Write initial checkpoint with full state assessment
5. Write session header to `session.md`
6. Log session start via `geno-notes note "supercharge session started: <duration>, <scope>"`

### Main Loop

For each cycle (1 to N):
1. Read the latest checkpoint
2. Determine the role based on rotation + needs (e.g., if tests are failing, prioritize fixing them)
3. Launch an Agent with the role's instructions and the checkpoint content
4. The agent does its work and writes the next checkpoint
5. Append cycle summary to session.md
6. If the agent reports "all tasks are complete and no more work needed", stop early

### Shutdown

After all cycles or early stop:
1. Write final summary to `session.md`
2. Write final state to `~/.geno/supercharge/state.json`
3. Log completion via `geno-notes note "supercharge session complete: <summary>"`
4. Report to user what was accomplished

## Checkpoint Format

```markdown
# Checkpoint — Cycle <N>/<Total>
## Timestamp
<ISO 8601>

## Previous Cycle
<What the last cycle did, in 2-3 sentences>

## Task States
| Task | Source | Status | Key Issue | Priority |
|------|--------|--------|-----------|----------|
| fix auth middleware | geno-notes | in-progress | token refresh failing | P1 |
| add rate limiting | geno-notes | backlog | not started | P2 |
| TODO: remove deprecated API | code scan | backlog | in api/v1/routes.py:42 | P3 |

## Current Sprint Plan
<What we're working on this sprint>

## Next Action
<Specific action for the next cycle to take>

## Blockers
<Anything that's stuck>

## Lessons Learned
<What worked, what didn't — carried forward>
```

## Error Recovery

- If a cycle fails, the next cycle reads the last successful checkpoint and retries
- If the same action fails 3 times, skip it and move to the next priority
- If `git push` fails, investigate rather than retry blindly
- If tests fail after a change, revert the change and try a different approach
- If an external tool or API errors, note it and move to work that doesn't depend on it
- Never force-push or do destructive git operations

## What NOT to Do

- Don't spend multiple cycles on the same issue without trying a different approach
- Don't push broken code — run tests and verify changes make sense before committing
- Don't ignore CLAUDE.md rules — they exist for a reason
- Don't create large, sweeping changes in a single cycle — prefer small, incremental commits
- Don't skip the evaluation phase — it catches issues before they compound
- Don't modify files outside the project scope without explicit user permission

## Completion

When this skill finishes, emit a trace:

```bash
geno-trace emit \
  --skill geno-agents-supercharge \
  --status <success|failure|abandoned> \
  --tool-calls <approximate count> \
  --errors <count of tool/command errors>
```

- `success` = all planned cycles completed (or early-stopped because all tasks are healthy) with session log and final checkpoint written
- `failure` = loop terminated due to repeated cycle failures, unrecoverable errors, or no forward progress after 3 retries
- `abandoned` = user stopped early
