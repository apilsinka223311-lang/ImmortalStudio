# ImmortalStudio Task Queue

Project name: ImmortalStudio

---

# Current Milestone

Foundation v0.1: deterministic local production pipeline.

The current goal is to extend the first working vertical slice one agent at a time, without external AI APIs and without changing the public architecture.

---

# Current Pipeline State

```text
idea
|
v
production_task.json
|
v
episode_plan.json
|
v
episode_script.md
|
v
scene_prompts.json
|
v
images/image_manifest.json
|
v
voice/voice_manifest.json
|
v
video/video_manifest.json
|
v
episode_report.json
|
v
final/metadata.json
|
v
JSON Schema validation gates passed
|
v
Resume from existing production_task.json supported
|
v
World and character memory excerpts passed into planning/prompts
|
v
Approved creative memory canon loaded at runtime
|
v
Deterministic local pipeline completed
```

---

# Completed Tasks

- [x] Studio Director
- [x] Story Architect
- [x] Script Writer
- [x] Prompt Engineer
- [x] Image Director
- [x] Voice Director
- [x] Video Editor
- [x] Analytics
- [x] Publisher
- [x] JSON Schema validation layer

---

# Completed Manual Memory Tasks

- [x] Add approved creative memory canon for The Origin System
- [x] Connect approved creative memory canon to runtime memory loading
- [x] Document preferred project memory layout
- [x] Document episode memory workflow
- [x] Add first canon-driven episode production sample
- [x] Add first episode artifact contract
- [x] Document Lore Keeper design

---

# Active Task Queue

Codex must work on only the first unchecked task in this list.

- [x] Implement minimal deterministic Image Director
- [x] Implement minimal deterministic Voice Director
- [x] Implement minimal deterministic Video Editor
- [x] Implement minimal deterministic Analytics
- [x] Implement minimal deterministic Publisher
- [x] Add JSON Schema validation layer
- [x] Resume pipeline from existing production_task.json
- [x] Improve character/world memory usage

---

# Future Tasks

These tasks are intentionally not active until the deterministic local pipeline is stable.

- [ ] Real AI provider adapters
- [ ] Image generation integration
- [ ] Voice generation integration
- [ ] Video generation integration
- [ ] Publishing automation

---

# Rules for Codex

Codex must:

- Read this file before starting implementation work.
- Find the first unchecked task in the Active Task Queue.
- Implement only that task.
- Not skip ahead.
- Not implement future tasks early.
- Not connect external AI APIs unless the active task explicitly says so.
- Run relevant smoke tests after implementation.
- Update this file after completing the task.
- Write a Russian report to `reports/codex/<timestamp>_<task_name>.md`.
- Stop after completing one task.

Codex must not:

- Redesign the architecture without explicit instruction.
- Rename public folders.
- Move files unnecessarily.
- Leave temporary artifacts.
- Silently ignore failing tests.
- Continue to the next task automatically without explicit approval.

---

# Stop Conditions

Codex must stop after one of these conditions:

- The first unchecked task is completed, tested, documented and reported.
- Required input is missing and cannot be safely inferred.
- A smoke test fails and the failure cannot be fixed within the active task scope.
- The requested work would require implementing a later unchecked task.
- The requested work would require external APIs not explicitly allowed by the task.

---

# Reporting Rules

After completing the active task, Codex must create one report in:

```text
reports/codex/
```

Report filename format:

```text
YYYYMMDD_HHMMSS_task_name.md
```

The report must be written in Russian and follow the format defined in:

```text
reports/codex/README.md
```

---

# Safety Rules

- Repository files are the source of truth.
- Do not rely on browser automation, desktop automation, mouse control or keyboard control.
- Do not create scripts that control VS Code, browsers, mouse or keyboard.
- Do not store secrets, API keys or credentials in the repository.
- Keep generated smoke-test artifacts out of the repository.
- Prefer deterministic local implementations before real provider integrations.
- Keep each agent responsible for exactly one pipeline stage.
- Preserve existing folder names and public architecture unless explicitly instructed otherwise.
