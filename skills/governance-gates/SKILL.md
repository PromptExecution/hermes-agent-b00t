---
name: governance-gates
description: "Governance gate system with Allow/Deny/Hook triple return, Eisenhower Matrix priority classification, calorie tracking per operation, and AgentTier multipliers."
version: 1.0.0
author: b00t alpha node
license: MIT
metadata:
  hermes:
    tags: [governance, gates, calories, eisenhower]
    related_skills: [a2a-protocol, task-queue-manager]
---

# Governance Gates

## Overview

Every Hermes action passes through governance gates. A gate returns one of three results:

| Result | Meaning | Action |
|--------|---------|--------|
| `Allow` | Proceed | Execute the command |
| `Deny` | Blocked | Log reason, escalate if needed |
| `Hook` | Wait | Snapshot context, register timer/event, go productive |

## Eisenhower Matrix

Gates use the Eisenhower Matrix to classify tasks by urgency and importance:

```
                    URGENT                    NOT URGENT
IMPORTANT    Allow (do now)             Hook/TimerMs (schedule)
NOT IMPORTANT Hook/Event (delegate)     Deny (eliminate)
```

## Calorie Tracking

Every command consumes calories based on the agent's tier:

| Tier | Multiplier | Example |
|------|-----------|---------|
| GAI | 100x | Strategic reasoning (GPT-4, Claude) |
| LLM | 10x | Code generation (Llama 3, Qwen) |
| SLM | 1x | Quick classification (Phi-4) |
| Algorithmic | 0.01x | Data processing (grep, awk) |

If calories hit zero, the agent is dead (☠️). Resurrection costs 50 cake.

## Cake Economy

Cake is earned retrospectively when missions complete. Scoring is multi-dimensional:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| roi | 1.0 | Return on cake investment |
| cost | 1.0 | Calorie efficiency |
| time | 0.8 | Speed of completion |
| accuracy | 0.9 | Correctness |
| utility | 0.7 | Reusability |
| risk | 0.6 | Risk level (lower = better) |

## Files

| File | Purpose |
|------|---------|
| `~/.b00t/b00t-c0re-gov/src/` | Full governance crate |
| `~/.b00t/b00t-c0re-gov/src/gates/eisenhower.rs` | Eisenhower gate |
| `~/.b00t/b00t-c0re-gov/src/scoring.rs` | ScoreCard, AgentTier, calorie tracking |
| `~/.b00t/b00t-cli/src/calorie_tracker.rs` | Per-command calorie deduction |
| `~/.b00t/b00t-cli/src/a2a_gates.rs` | Gates exposed as A2A skills |
