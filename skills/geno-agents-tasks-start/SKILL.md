---
name: geno-agents-tasks-start
description: >-
  Pick up a task from the current workspace's geno-notes project scope,
  plan if needed, and start executing. Workspace-only — global-scope tasks
  are out of scope for v0.1.
  Installed by geno-tools as the /gt-tasks-start slash command.
license: MIT
metadata:
  author: 42euge
  version: "0.3.0"
observability:
  success_signal: "task marked done via geno-notes with milestone journal entry summarizing what was accomplished"
  failure_signals:
    - "no project scope found and user aborts initialization"
    - "task execution blocked and user cannot resolve blocker"
    - "geno-notes CLI errors prevent task state transitions"
  knowledge_reads:
    - "geno-notes project-scope task list (active + backlog)"
    - "CLAUDE.md / project instructions for project context"
    - "task details via geno-notes show"
  knowledge_writes:
    - "geno-notes journal entries (milestone, finding, bug, decision)"
    - "plan file at geno-notes path/plans/<task-id>.md (medium/large tasks)"
    - "task status transitions (backlog -> active -> done)"
---

# Start Task

Pick up a task from this workspace's `geno-notes` project scope (discovered automatically by `geno-notes path --project`) and start working on it.

**Workspace-only.** This skill does not read from or write to the global geno-notes scope. If the user wants to start a task that lives globally, they should either `geno-notes promote <task> --to project` first, or invoke it manually outside this skill.

Uses the `geno-notes` CLI (`~/.local/bin/geno-notes` or on PATH).

## Input

The user optionally provides a task description or number as `$ARGUMENTS`. If empty, show the task list and ask which one to start.

## Workflow

### 0. Confirm we can proceed

Immediately check that a project scope exists:

```bash
geno-notes path --project 2>/dev/null
```

If the command exits non-zero (no project scope found in cwd or ancestors):

1. **Ask the user upfront** using `AskUserQuestion` with these options:
   - **Initialize here** — run `geno-notes init --project` in the current directory.
   - **Proceed without prompts** — auto-run `geno-notes init --project` here and don't stop for a confirmation on future gaps this session.
   - **Abort** — they want to handle it outside this skill.

2. Only once a project scope exists, continue to step 1.

If the user has already chosen "Proceed without prompts" earlier in the session, skip the `AskUserQuestion` and just run `geno-notes init --project` silently.

### 1. Load context

```bash
geno-notes list --project --status active --json    # current active tasks
geno-notes list --project --status backlog --json   # candidates to start
```

Also read any `CLAUDE.md` or project instructions for project context.

### 2. Select the task

- If `$ARGUMENTS` is provided, pass it to `geno-notes show <pattern> --project` to confirm a unique match. If the CLI exits non-zero with multiple candidates, show them and ask the user to disambiguate.
- If no arguments, use `AskUserQuestion`. Show up to 4 options — Active tasks first, then Backlog. Label = task title; description = `[<status>] <id>`. Include an "Other" option so the user can specify a task outside the top 4.
- If the task is already in Active, skip to step 3.
- If the task is in Backlog, run:
  ```bash
  geno-notes start <task-id-or-pattern> --project
  ```

### 3. Understand the task

```bash
geno-notes show <task-id> --project   # frontmatter + body + journal refs
```

Assess complexity:

- **Small task** (single-file change, config tweak, quick addition): skip step 4; go to step 5.
- **Medium/large task** (multi-file, research needed, design decisions): proceed to step 4.

### 4. Plan (for medium/large tasks)

Use `EnterPlanMode`. Explore the codebase, design an approach, resolve open questions with the user.

Save the plan to `$(geno-notes path --project)/plans/<task-id>.md` (same id as the task file). Structure:

```markdown
# Plan: <task title>

## Goal
<What does "done" look like?>

## Approach
<Numbered steps>
```

Once the user approves, call `ExitPlanMode`.

### 5. Execute

- Work through the task (or the plan steps).
- At meaningful progress points, log a timestamped entry linked to the task:
  ```bash
  geno-notes note "<what just happened>" --task <task-id> --project --kind milestone
  ```
  Use `--kind finding` for discovered facts, `--kind bug` for problems hit, `--kind decision` for design calls. Default `note` is fine for routine updates. Log milestones, not every small step.
- If you hit a blocker, stop and ask the user.

### 6. Complete

```bash
geno-notes note "<summary of what was done>" --task <task-id> --project --kind milestone
geno-notes done <task-id> --project
```

Then tell the user what was accomplished and suggest what to start next:

```bash
geno-notes list --project --status backlog
```

## Completion

When this skill finishes, emit a trace:

```bash
geno-trace emit \
  --skill geno-agents-tasks-start \
  --status <success|failure|abandoned> \
  --tool-calls <approximate count> \
  --errors <count of tool/command errors>
```

- `success` = task marked done via `geno-notes done` with a summary milestone logged
- `failure` = task could not be completed due to unresolved blocker, missing project scope (user aborted), or repeated CLI errors
- `abandoned` = user stopped early
