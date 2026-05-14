---
name: task-queue-manager
description: "Alpha node task queue — persistent local queue of work items, GitHub issue backlog integration, priority-based picking, and bravo node idea submission."
version: 1.0.0
author: b00t alpha node
license: MIT
metadata:
  hermes:
    tags: [task-queue, backlog, alpha, bravo, epoch]
    related_skills: [a2a-protocol, governance-gates]
---

# Task Queue Manager

## Overview

The alpha node manages a persistent task queue that drives autonomous epoch progression. Tasks come from three sources:

1. **Bravo nodes** — submit ideas by writing JSON to the pending queue
2. **GitHub issues** — pulled hourly into backlog, promoted to queue
3. **Alpha planner** — self-generated test and implementation tasks

## Queue Directory

```
~/.local/share/b00t/task-queue/
├── pending/       ← Tasks waiting for processing
├── active/        ← Tasks currently being worked
└── done/          ← Completed tasks (historical)
```

## Task Format

```json
{
  "id": "epoch-6a-47fd1191",
  "source": "alpha-planner",
  "type": "test",
  "title": "Cycle 2: Test + harden A2A SDK",
  "body": "Run full A2A test suite (84 tests)...",
  "priority": 1,
  "created_at": "2026-05-06T22:10:00Z",
  "tags": ["a2a", "test"],
  "epoch": "6a",
  "github_issue": null
}
```

## Commands

```bash
# List queue status
b00t-task list

# Add a task
b00t-task add "Title" "Description" [source] [tags] [priority]

# Pick highest priority task
b00t-task pick

# Mark task as done
b00t-task done <task-id>

# See ideas from bravo nodes
b00t-task ideas

# Promote a GitHub issue to the queue
b00t-task promote <issue-number>
```

## Cron Schedule

| Cron | Interval | Purpose |
|------|----------|---------|
| epoch-progression | Every 10 min | Pick + execute next task |
| github-backlog-pull | Every hour | Sync tagged issues into backlog |
| governance-heartbeat | Every 15 min | Check hook store |

## Bravo Node Submission

To submit an idea from a bravo node:

```bash
# Write a task file directly to the pending queue
cat > ~/.local/share/b00t/task-queue/pending/idea-$(date +%s).json << 'EOF'
{
  "id": "idea-1746489600",
  "source": "bravo-node-3",
  "type": "idea",
  "title": "Add A2A WebSocket transport",
  "body": "In addition to HTTP, add WebSocket support for real-time agent communication...",
  "priority": 3,
  "tags": ["a2a", "enhancement"]
}
EOF
```

The alpha node will pick it up on the next epoch progression tick.
