---
name: gt-start-task
description: >-
  Pick up a task from the project's geno-notes scope, plan if needed, and
  start executing. Use when user says /gt-start-task or wants to begin work
  on the next task.
license: MIT
metadata:
  author: 42euge
  version: "0.2.0"
---

# Start Task

Pick up a task from the project's geno-notes scope and start working on it.

Uses the `geno-notes` CLI (`~/.local/bin/geno-notes` or on PATH). Scope resolves automatically: project if `./geno/geno-notes/` exists in cwd or an ancestor, otherwise global at `~/.geno/geno-notes/`. Pass `--global` or `--project` to force.

## Input

The user optionally provides a task description or number as `$ARGUMENTS`. If empty, show the task list and ask which one to start.

## Workflow

### 1. Load context

```bash
geno-notes scope                          # confirm which scope we're in
geno-notes list --status active --json    # current active tasks
geno-notes list --status backlog --json   # candidates to start
```

If no project scope exists and the user is in a project repo, prompt them: "No `./geno/geno-notes/` found here. Run `geno-notes init --project` to create one, or pass `--global` to use the global scope." Do not continue until they've chosen.

Also read any CLAUDE.md or project instructions for project context.

### 2. Select the task

- If `$ARGUMENTS` is provided, pass it to `geno-notes show <pattern>` to confirm a unique match. If the CLI exits non-zero with multiple candidates, show them to the user and ask which.
- If no arguments, use the `AskUserQuestion` tool. Show up to 4 options — Active tasks first, then Backlog tasks. Each option label is the task title; description shows `[<status>] <id>`. Include an "Other" option so the user can specify a different task.
- If the task is already in Active, skip to step 3.
- If the task is in Backlog, run:
  ```bash
  geno-notes start <task-id-or-pattern>
  ```

### 3. Understand the task

```bash
geno-notes show <task-id>   # renders task frontmatter + body + journal refs
```

Assess scope and complexity:

- **Small task** (single file change, config tweak, quick addition): proceed directly to step 5.
- **Medium/large task** (multi-file, research needed, design decisions): proceed to step 4.

### 4. Plan (for medium/large tasks)

Use the `EnterPlanMode` tool. Explore the codebase, design an approach, resolve open questions with the user.

Save the plan to `<scope-dir>/plans/<task-id>.md` (same id as the task file). Use `geno-notes path` to resolve the scope dir. The plan should follow:

```markdown
# Plan: <task title>

## Goal
<What does "done" look like?>

## Approach
<Numbered steps to complete the task>
```

Once the user approves, use `ExitPlanMode`.

### 5. Execute

- Work through the task (or the plan steps).
- At meaningful progress points, log a timestamped note linked to the task:
  ```bash
  geno-notes note "<what just happened>" --task <task-id> --kind milestone
  ```
  Use `--kind finding` for discovered facts, `--kind bug` for problems hit, `--kind decision` for design calls. Default `note` is fine for routine updates. Don't log every tiny step — just meaningful milestones.
- If you hit a blocker, stop and ask the user.

### 6. Complete

```bash
geno-notes note "<summary of what was done>" --task <task-id> --kind milestone
geno-notes done <task-id>
```

Then tell the user what was accomplished and suggest what to work on next from:

```bash
geno-notes list --status backlog
```
