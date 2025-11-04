# Obsidian Vault Watcher - Raw Idea

## Core concept

A lightweight Python **vault watcher** that polls your Obsidian vault on a configurable interval, detects **frontmatter property changes**, and **fires workflows** (e.g., when `assignee` flips to `agent-os`, spin up a "new agent-os ticket" workflow). It's modular: new rules + new workflows are pluggable without touching the core loop.

## Problem it solves

- **Bridges planning ↔ execution**: Notes are where you plan; agents are where work happens. This service turns specific note changes into **executable jobs**—consistently, traceably.

- **Zero vendor lock-in**: No Obsidian API required. Pure file/polling approach works anywhere your vault lives.

- **Governed automation**: CSV "database" + explicit rules give you **auditability** and easy rollback while you iterate.


## Target users

- **Power users of Obsidian** who want event-driven automation from frontmatter changes.

- **Agent-OS + Claude Code users** who want a **ticket/queue bridge** that starts in Markdown and ends in agent runs.

- **Solo devs / small teams** who favor **plain-text ops**, CSVs, and Python over SaaS glue.


## Key use cases / scenarios

- **Auto-ticketing to Agent-OS**: `assignee: agent-os` or `status: ready` → create Agent-OS ticket, link task IDs back into the note, move Kanban column to `Review`.

- **Review gate**: When `status` becomes `needs-review`, open a review task and @assign back to you.

- **Content pipeline**: `stage: scheduled` + `publish_date` in the past → fire a "publish" workflow (e.g., commit rendered artifact, post to a queue).

- **Procedures tracker**: Flip `run: start` → log a run in `runs.csv`, timestamp it, initialize checklists; flip `run: done` → close out, compute duration, write summary.


## Key features

1. **Configurable poller service**
    - Runs every _N_ seconds/minutes (env var or config file).
    - Single source of truth for **vault path** and **debug flags**.

2. **Frontmatter diff engine**
    - Parses YAML frontmatter; stores a **snapshot** per file (CSV).
    - Computes **per-property deltas** (e.g., old→new for `assignee`, `status`, `stage`).
    - Ignores non-tracked properties unless configured.

3. **Rule engine (behaviors)**
    - Declarative **rules**: _"When `assignee` changes from `""` to `"agent-os"`, run `new_agent_os_ticket`."_
    - Rules are a registry + small predicates; **easy to add** without touching main.

4. **Workflow registry**
    - `workflows.py` exposes a simple interface: `run(payload, debug=False)` per workflow.
    - Ships with **New Agent-OS Ticket** example; adding more is copy-paste-mod.

5. **CSV-backed audit trail**
    - `events.csv`: file_id, path, prop, old, new, detected_at
    - `tickets.csv`: ticket_id, note_path, status, external_ids, created_at
    - `runs.csv`: workflow_name, input_hash, started_at, finished_at, outcome
    - Dead-simple, greppable, and pandas-friendly.

6. **Global debug switch**
    - Verbose `print()` toggled **in one place** (propagated as `debug=True` into modules).
    - Each module respects the flag; no stray chatter unless you ask for it.

7. **Developer ergonomics**
    - **Function length <30 lines**, **file <200 lines** (enforced by style + comments).
    - Every file includes an `if __name__ == "__main__":` **manual test** with junior-friendly narration.

## Tech stack

- **Python 3.11+** (stdlib first mindset)
- **Common libs**: `python-frontmatter`, `pathlib`, `hashlib`, `csv`
- **CSV "DB" layout**: snapshots, events, workflows, runs, tickets
- **Project structure**: main.py, behaviors.py, workflows.py, csv_store.py, config.py, utils.py

## Acceptance criteria

- **AC1 – Poller:** Service polls at the configured interval; logs a heartbeat when `DEBUG=True`.
- **AC2 – Single source of truth:** Changing vault path in `config.py` updates all modules; no hard-coded paths elsewhere.
- **AC3 – Diffing:** When a tracked property changes, an entry appears in `events.csv` with old/new values.
- **AC4 – Rules fire:** Given rule _"assignee: '' → 'agent-os'"_, the corresponding workflow runs exactly once per change.
- **AC5 – Workflow:** The sample `new_agent_os_ticket` writes a row to `tickets.csv` and returns a success message; failures are logged to `runs.csv` with `status='error'`.
- **AC6 – Toggleable debug:** Setting `DEBUG=True` emits progress prints from **all** modules without code edits elsewhere.
- **AC7 – Code constraints:** No function >30 lines; no file >200 lines; each file has an executable `__main__` demo explaining behavior.
- **AC8 – Extensibility:** Adding a new rule/workflow requires only editing `behaviors.py` / `workflows.py` and (optionally) `config.py`; **no changes** to `main.py` needed.
