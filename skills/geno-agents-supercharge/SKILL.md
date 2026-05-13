---
name: geno-agents-supercharge
description: >-
  Run an extended autonomous work session across benchmark tasks with
  structured cycles of implementation, reflection, and research.
  Use when the user says /gt-supercharge, /geno-agents-supercharge, or asks
  for a long-running autonomous run across tasks.
disable-model-invocation: true
argument-hint: "[duration] [scope]  e.g. 'go!', '4h change_blindness', '12h all'"
license: MIT
metadata:
  author: 42euge
  version: "0.1.0"
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

Run an extended autonomous work session across benchmark tasks with structured cycles of implementation, reflection, and research. Based on Anthropic's harness design patterns for long-running apps.

## Input

`$ARGUMENTS` — Optional directives. Examples:
- `go!` — Start with defaults (8 hours, all tasks)
- `4h change_blindness` — 4 hours on one task
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
- Reads current state of all tasks (notebooks, reviews, results)
- Reads CLAUDE.md and any existing reviews
- Prioritizes what to work on next
- Writes a sprint plan to `checkpoints/sprint_<n>.md`
- Considers: which tasks have errors? which lack discriminatory power? which need more items? which haven't been run yet?

### Implementer (runs most cycles)
- Picks up the sprint plan
- Does the actual work: fixes bugs, improves scoring, adds passages, refactors prompts
- After each change, updates the notebook timestamp and pushes to GitHub
- Writes a brief handoff note to `checkpoints/impl_<cycle>.md`

### Evaluator (runs every 2-3 cycles)
- Pulls latest results from Kaggle using `/gt-kaggle-benchmarks-task-review`
- If no new results, checks if a run is in progress or needs to be triggered
- Compares results against previous runs
- Writes evaluation to the task's `review/` folder
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
```

### Role Rotation

Default rotation pattern per 4-cycle sprint:
1. **Plan** — assess state, set priorities
2. **Implement** — work on highest priority item
3. **Implement** — continue or move to next item
4. **Evaluate** — pull results, review, adjust

### Context Management

To handle long runs without context degradation:
- Each cycle runs as a **separate Agent** with a fresh context
- The checkpoint file is the handoff document — it must contain everything the next agent needs
- The session log is append-only and provides full history
- If a cycle's agent runs into context limits, it writes a checkpoint and the next cycle picks up

## Execution

### Startup

1. Parse duration and scope from `$ARGUMENTS`
2. Create session directory: `geno-agents/supercharge/sessions/<YYYYMMDD-HHMM>/`
3. Read current state:
   - List all tasks in `tasks/`
   - Check which have Kaggle kernels (via `kaggle kernels list`)
   - Check which have reviews
   - Read CLAUDE.md for architecture rules
4. Write initial checkpoint with full state assessment
5. Write session header to `session.md`

### Main Loop

For each cycle (1 to N):
1. Read the latest checkpoint
2. Determine the role based on rotation + needs (e.g., if an error was found, prioritize fixing it)
3. Launch an Agent with the role's instructions and the checkpoint content
4. The agent does its work and writes the next checkpoint
5. Append cycle summary to session.md
6. If the agent reports "all tasks are in good shape and no more work needed", stop early

### Shutdown

After all cycles or early stop:
1. Write final summary to `session.md`
2. Write final state to `~/.geno/supercharge/state.json`
3. Report to user what was accomplished

## Checkpoint Format

```markdown
# Checkpoint — Cycle <N>/<Total>
## Timestamp
<ISO 8601>

## Previous Cycle
<What the last cycle did, in 2-3 sentences>

## Task States
| Task | Status | Last Run | Key Issue | Priority |
|------|--------|----------|-----------|----------|
| change_blindness | needs-rerun | 2026-03-31 04:15 UTC | scoring too strict | P1 |
| attentional_blink | not-linked | never | needs Kaggle task created | P2 |
| ... | ... | ... | ... | ... |

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
- If Kaggle API errors, note it and move to implementation work that doesn't need results
- Never force-push or do destructive git operations

## What NOT to Do

- Don't spend multiple cycles on the same issue without trying a different approach
- Don't create new tasks without using `/gt-kaggle-benchmarks-task-generate`
- Don't modify notebooks without updating the timestamp
- Don't push broken code — verify changes make sense before committing
- Don't ignore CLAUDE.md rules (self-contained notebooks, llm as list, etc.)

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
- `failure` = loop terminated due to repeated cycle failures, unrecoverable git/Kaggle errors, or no forward progress after 3 retries
- `abandoned` = user stopped early
