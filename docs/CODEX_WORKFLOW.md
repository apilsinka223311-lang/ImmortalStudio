# Codex Workflow

ImmortalStudio uses a repository-based workflow for controlled Codex development.

The goal is to make future work predictable, reviewable and safe without relying on browser automation, copy-paste loops or external UI control.

---

# One-Task-Per-Run Rule

Each Codex run must complete at most one unchecked task from:

```text
docs/TASK_QUEUE.md
```

Codex must not continue to the next task automatically.

---

# Standard Run Procedure

1. Read `docs/TASK_QUEUE.md`.
2. Identify the first unchecked item in the Active Task Queue.
3. Read the relevant architecture, schema and implementation files.
4. Implement only the active task.
5. Run relevant smoke tests.
6. Remove temporary production artifacts.
7. Update `docs/TASK_QUEUE.md`.
8. Write a Russian report under `reports/codex/`.
9. Stop and wait for the next explicit instruction.

---

# Implementation Boundaries

Codex must preserve:

- Existing public folder names.
- The Studio Director, PipelineManager and AgentRegistry architecture.
- Agent separation by responsibility.
- Project isolation under `projects/`.
- Provider-independent local contracts unless a task explicitly allows external APIs.

---

# Smoke Test Expectations

Every implementation task should include or update a smoke test when practical.

Smoke tests must verify:

- The new stage can be discovered through the registry.
- The expected output artifact is created.
- `production_task.json` is updated correctly.
- The next missing agent is handled gracefully.
- Temporary production artifacts are removed after the test.

---

# Report Requirement

Every completed task must produce one Russian report in:

```text
reports/codex/
```

Use the report format documented in:

```text
reports/codex/README.md
```

The report is part of the repository history and should be clear enough for a human reviewer to understand what changed without reading every diff.
