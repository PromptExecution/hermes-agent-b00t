"""
Autotask tool — first-class task queue management for Hermes.
Allows the agent to list, pick, complete, add, and nudge tasks in the alpha node task queue.

When autotask mode is enabled (B00T_AUTOTASK=1), the agent automatically picks from the queue
at conversation start and executes tasks autonomously.
"""

import json
import os
import subprocess
from typing import Optional

TASK_QUEUE_DIR = os.environ.get(
    "B00T_TASK_QUEUE",
    os.path.expanduser("~/.local/share/b00t/task-queue"),
)
PENDING = os.path.join(TASK_QUEUE_DIR, "pending")
ACTIVE = os.path.join(TASK_QUEUE_DIR, "active")
DONE = os.path.join(TASK_QUEUE_DIR, "done")

AUTOTASK_SCHEMA = {
    "name": "autotask",
    "description": "Manage the alpha node task queue. List pending/active/done tasks, pick the highest priority task, mark tasks complete, add new tasks from bravo nodes, or nudge the epoch progression.",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["list", "pick", "done", "add", "nudge", "status"],
                "description": "Action to perform on the task queue"
            },
            "task_id": {
                "type": "string",
                "description": "Task ID (for 'done' action)"
            },
            "title": {
                "type": "string",
                "description": "Task title (for 'add' action)"
            },
            "body": {
                "type": "string",
                "description": "Task description (for 'add' action)"
            },
            "source": {
                "type": "string",
                "description": "Source of the task (for 'add' action, default: hermes-agent)"
            },
            "priority": {
                "type": "integer",
                "description": "Priority 0-4 (for 'add' action, default: 2)"
            },
            "tags": {
                "type": "string",
                "description": "Comma-separated tags (for 'add' action)"
            }
        },
        "required": ["action"]
    }
}


def _ensure_dirs():
    for d in [PENDING, ACTIVE, DONE]:
        os.makedirs(d, exist_ok=True)


def _read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _list_tasks(directory):
    tasks = []
    if not os.path.isdir(directory):
        return tasks
    for fname in sorted(os.listdir(directory)):
        if fname.endswith(".json"):
            path = os.path.join(directory, fname)
            task = _read_json(path)
            if task:
                tasks.append(task)
    return tasks


def handle_autotool(args, **kwargs):
    action = args.get("action", "list")
    _ensure_dirs()

    if action == "list":
        pending = _list_tasks(PENDING)
        active = _list_tasks(ACTIVE)
        done = _list_tasks(DONE)

        lines = []
        lines.append(f"📋 Task Queue Status")
        lines.append(f"")
        lines.append(f"  Pending: {len(pending)}")
        for t in sorted(pending, key=lambda x: x.get("priority", 999)):
            lines.append(f"    [{t.get('priority', '?')}] {t.get('title', '?')} ({t.get('id', '?')[:16]}...)")
        lines.append(f"")
        lines.append(f"  Active: {len(active)}")
        for t in active:
            lines.append(f"    ⏳ {t.get('title', '?')}")
        lines.append(f"")
        lines.append(f"  Done (last 3): {len(done)}")
        for t in done[-3:]:
            lines.append(f"    ✅ {t.get('title', '?')}")
        return "\n".join(lines)

    elif action == "pick":
        # Find highest priority task
        best = None
        best_pri = 999
        if os.path.isdir(PENDING):
            for fname in os.listdir(PENDING):
                if not fname.endswith(".json"):
                    continue
                path = os.path.join(PENDING, fname)
                task = _read_json(path)
                if task:
                    pri = task.get("priority", 999)
                    if pri < best_pri:
                        best_pri = pri
                        best = (fname, task)

        if best is None:
            return "📭 No pending tasks in queue."

        fname, task = best
        src = os.path.join(PENDING, fname)
        dst = os.path.join(ACTIVE, fname)
        os.rename(src, dst)
        return f"📌 Picked: {task['title']} (priority {best_pri}) — {task.get('body', '')[:100]}"

    elif action == "done":
        task_id = args.get("task_id", "")
        if not task_id:
            return "❌ task_id required for 'done' action"

        # Check active first, then pending
        for directory in [ACTIVE, PENDING]:
            path = os.path.join(directory, f"{task_id}.json")
            if os.path.exists(path):
                dst = os.path.join(DONE, f"{task_id}.json")
                os.rename(path, dst)
                task = _read_json(dst)
                title = task.get("title", task_id) if task else task_id
                return f"✅ Task completed: {title}"

        # Try partial match
        for directory in [ACTIVE, PENDING]:
            if not os.path.isdir(directory):
                continue
            for fname in os.listdir(directory):
                if task_id in fname:
                    path = os.path.join(directory, fname)
                    dst = os.path.join(DONE, fname)
                    os.rename(path, dst)
                    task = _read_json(dst)
                    title = task.get("title", task_id) if task else task_id
                    return f"✅ Task completed (matched by partial ID): {title}"

        return f"❌ Task '{task_id}' not found in active or pending queue."

    elif action == "add":
        title = args.get("title", "Untitled")
        body = args.get("body", "")
        source = args.get("source", "hermes-agent")
        priority = args.get("priority", 2)
        tags = args.get("tags", "general")

        import uuid, datetime
        task_id = f"task-{int(datetime.datetime.utcnow().timestamp())}-{os.getpid()}"

        task = {
            "id": task_id,
            "source": source,
            "type": "feature",
            "title": title,
            "body": body,
            "priority": priority,
            "created_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tags": [t.strip() for t in tags.split(",")],
            "github_issue": None
        }

        path = os.path.join(PENDING, f"{task_id}.json")
        with open(path, "w") as f:
            json.dump(task, f, indent=2)

        return f"📥 Task added: {title} (priority {priority}, id: {task_id[:24]}...)"

    elif action == "nudge":
        """Nudge the epoch progression cron to run now."""
        try:
            result = subprocess.run(
                ["b00t", "job", "run", "epoch-progression"],
                cwd=os.path.expanduser("~/.b00t"),
                capture_output=True, text=True, timeout=30
            )
            output = result.stdout.strip() or result.stderr.strip() or "no output"
            return f"🔄 Epoch progression nudged:\n{output[:500]}"
        except FileNotFoundError:
            return "⚠️ b00t not found in PATH — cannot nudge epoch progression."
        except subprocess.TimeoutExpired:
            return "⏰ Epoch progression timed out after 30s."
        except Exception as e:
            return f"⚠️ Error nudging epoch: {e}"

    elif action == "status":
        pending = _list_tasks(PENDING)
        active = _list_tasks(ACTIVE)
        done = _list_tasks(DONE)
        total = len(pending) + len(active) + len(done)

        # Check cron logs
        cron_logs = ""
        for logfile in ["/tmp/b00t-epoch.log", "/tmp/b00t-backlog.log", "/tmp/b00t-hooks.log"]:
            if os.path.exists(logfile):
                try:
                    with open(logfile) as f:
                        lines = f.read().strip().split("\n")
                        last = lines[-3:] if len(lines) >= 3 else lines
                        cron_logs += f"\n  {logfile}: {len(lines)} entries, last: {last[-1][:80]}"
                except Exception:
                    cron_logs += f"\n  {logfile}: (unreadable)"

        return (
            f"📊 Alpha Node Status\n"
            f"  Task queue: {len(pending)} pending, {len(active)} active, {len(done)} done ({total} total)\n"
            f"  Cron logs:{cron_logs}\n"
            f"  Autotask mode: {'✅ ON' if os.environ.get('B00T_AUTOTASK') else '⬜ OFF'}"
        )

    return f"❌ Unknown action: {action}"


# --- Registry ---
from tools.registry import registry

registry.register(
    name="autotask",
    toolset="task",
    schema=AUTOTASK_SCHEMA,
    handler=handle_autotool,
    check_fn=lambda **kw: None,
    emoji="📋",
)
