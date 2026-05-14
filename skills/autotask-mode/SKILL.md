---
name: autotask-mode
description: "First-class autotask mode for Hermes. When enabled, the agent autonomously picks from the alpha node task queue and executes tasks without human prompting. The agent checks the queue at the start of each conversation, picks the highest priority task, and works through it."
version: 1.0.0
author: b00t alpha node
metadata:
  hermes:
    tags: [autotask, autonomous, task-queue, alpha]
    related_skills: [task-queue-manager, a2a-protocol, governance-gates]
---

# Autotask Mode

## Overview

Autotask mode transforms Hermes from a reactive assistant (responds to user prompts) to a proactive executor (picks from task queue, executes, reports). This is the alpha node's primary interface for autonomous epoch progression.

## How It Works

```
Hermes boots → checks autotask flag → 
  if enabled:
    reads ~/.local/share/b00t/task-queue/pending/
    picks highest priority task
    executes it (test, fix, implement)
    moves task to done
    reports result
  if disabled:
    normal interactive mode
```

## Enabling Autotask Mode

Set the autotask flag:
```bash
export B00T_AUTOTASK=1
b00t --role=executive --autotask
```

Or in config (~/.hermes/config.yaml):
```yaml
autotask:
  enabled: true
  max_tasks_per_session: 3
  report_to: "console"
```

## Task Priority

Tasks are picked by priority (lower number = higher priority):

| Priority | Type | Source |
|----------|------|--------|
| 0 | Urgent fix | Human command |
| 1 | Active epoch | Alpha planner |
| 2 | Testing | Cycle tasks |
| 3 | Backlog | GitHub issues |
| 4 | Ideas | Bravo nodes |

## Execution Flow per Task

```
1. Read task JSON from pending/
2. Move to active/
3. Determine task type from tags/body:
   - "test" → run cargo test, report results
   - "fix" → diagnose error, fix, verify
   - "feature" → research, design, implement, test
   - "idea" → triage: accept/reject/refine
4. Execute using available tools (terminal, file, delegate)
5. On success: move to done/, log result
6. On failure: retry (max 3), then escalate back to pending/
```

## Integration Points

| File | Purpose |
|------|---------|
| `~/.local/bin/b00t-task` | Task queue CLI — pick, done, add, list |
| `~/.local/share/b00t/task-queue/` | Queue directory (pending/active/done) |
| `~/.local/share/b00t/epoch-state.json` | Epoch progression state |
| `~/.b00t/_b00t_/epoch-progression.job.toml` | b00t job definition |
| `~/.b00t/tests/test-task-queue.sh` | Task queue tests |

## Cron Bridge

System cron drives epoch progression at the OS level:
```
*/10 * * * *  b00t job run epoch-progression
0 * * * *     b00t job run github-backlog-pull
*/15 * * * *  hook store check
```

Hermes cron provides agent-level oversight:
```
*/10 * * * *  self-reminder: check system cron ran
```

## Testing

```bash
# Run task queue tests
bash ~/.b00t/tests/test-task-queue.sh

# Manual queue operations
b00t-task list
b00t-task pick
b00t-task done <task-id>

# Check cron logs
tail -5 /tmp/b00t-epoch.log
tail -5 /tmp/b00t-backlog.log
```
