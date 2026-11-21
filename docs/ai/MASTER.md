# GARNET — Single Source of Operational Truth

**Control system:** GDCS v1.0 | **Recorded:** 2026-11-21 | **Input baseline:** GARNET_Codex_GDCS_Integrated_v1.zip (complete)

## Where we are
- Local Django and browser baselines are recorded in the change log. Production verification remains open.
- Current application: Django monolith with server-side templates and static CSS/JS.
- Future frontend/backend technology is NOT decided. Preserve platform-neutral behavior, data and URL contracts.
- Current task: **none** — select a backlog item.
- Latest design task: **GNT-009** — shared header and footer refinement, verified locally.

## Control authority
- `state.json` and `tasks.json` are **canonical for task status**; this file is a succinct human-readable snapshot.
- `ARCHITECTURE.md`, `MODULE_REGISTRY.md`, `PROJECT_MAP.md`: factual/context references.
- `DECISIONS.md`: durable architecture decisions; proposals are not automatically adopted.
- `CHANGE_LOG.md`: changes with actual evidence; never declare unexecuted checks passed.
- Run `python tools/gdcs.py status` to see live task state, `python tools/gdcs.py context` to generate minimal task context.

## Session restart protocol (no dependence on long chats)
1. Upload the current project/source snapshot **without secrets** plus `docs/ai/` and `tools/gdcs.py` as needed; or work from a shared versioned repository.
2. Read `MASTER.md` and `state.json` first.
3. Read only `ACTIVE_TASK.md`, task-specific module entries, and source files actually required.
4. Finish each task with evidence + update state, decisions, change log and actual project files.
5. Never assume files/chat automatically sync across sessions. Re-upload changed files or use versioned repository.

## Security boundary
The two supplied GDCS ZIPs passed the file inventory review. Historical archive and upstream history checks are tracked in GNT-005.
