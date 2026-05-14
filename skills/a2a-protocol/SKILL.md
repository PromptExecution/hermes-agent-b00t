---
name: a2a-protocol
description: "Agent-to-Agent (A2A) protocol v1.0 — Rust SDK for agent card discovery, task lifecycle, skill registry, HTTP transport, cross-hive communication, reputation tracking, and agent travel between hives."
version: 1.0.0
author: b00t alpha node
license: MIT
metadata:
  hermes:
    tags: [a2a, agent-to-agent, interoperability, protocol]
    related_skills: [governance-gates, task-queue-manager]
---

# A2A Protocol — Agent-to-Agent Communication

## Overview

This skill enables Hermes to communicate with other agents using the A2A protocol (v1.0, Linux Foundation standard). A2A complements MCP: MCP provides agent-to-tool communication, A2A provides agent-to-agent collaboration.

## Architecture

The A2A implementation lives in `b00t-c0re-a2a` crate at `~/.b00t/b00t-c0re-a2a/`.

```
Agent Card (discovery)
  → SkillRegistry (what can I do?)
  → Task (work unit sent between agents)
  → HTTP Transport (how agents reach each other)
  → HiveRegistry (who else is out there?)
  → Reputation (how trustworthy is this agent?)
  → Travel (can I relocate to another hive?)
```

## Key Concepts

### Agent Card
Every agent publishes an A2A Agent Card — a discovery document describing who they are, what skills they offer, and how to reach them:

```json
{
  "name": "RustCoder",
  "description": "Systems programming specialist",
  "url": "stdio://local/b00t/crew/RustCoder",
  "skills": [{
    "id": "rust-compile",
    "name": "Compile Rust project",
    "input_schema": { "type": "object", "properties": {...} }
  }],
  "reputation": { "score": 3.2, "missions_completed": 12, ... }
}
```

### Task Lifecycle
Tasks progress through states: `Submitted → Working → InputRequired → Completed/Failed/Canceled`

### HTTP Transport
Agents communicate over HTTP: `POST /task` to send work, `GET /task/{id}/status` to check progress, `GET /.well-known/agent-cards` for discovery.

### Cross-Hive
Agents can travel between hives. A `TravelManifest` documents the relocation, freezes the agent's cake balance on the source hive, and reconciles on return.

## Commands

```bash
# List registered A2A skills
b00t crew roster --a2a

# Send a task to a local agent
b00t task send RustCoder rust-compile '{"target": "debug"}'

# Discover remote hives
b00t hive discover http://hive-beta:8081

# Travel to another hive
b00t crew travel @RustCoder --to hive-beta --duration 30m

# Check reputation
b00t crew reputation RustCoder
```

## Integration Points

| File | Purpose |
|------|---------|
| `~/.b00t/b00t-c0re-a2a/src/agent_card.rs` | AgentCard, Skill, Reputation types |
| `~/.b00t/b00t-c0re-a2a/src/task.rs` | Task lifecycle |
| `~/.b00t/b00t-c0re-a2a/src/skill_registry.rs` | Skill registration and dispatch |
| `~/.b00t/b00t-c0re-a2a/src/http_transport.rs` | HTTP server/client |
| `~/.b00t/b00t-c0re-a2a/src/hive.rs` | Cross-hive registry |
| `~/.b00t/b00t-c0re-a2a/src/travel.rs` | Agent travel |
| `~/.b00t/b00t-c0re-a2a/src/heartbeat.rs` | Hive heartbeat |
| `~/.b00t/b00t-c0re-a2a/tests/` | 84+ tests |
