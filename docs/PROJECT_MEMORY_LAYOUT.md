# Project Memory Layout

This document defines the preferred project memory layout for ImmortalStudio projects.

It documents the current Foundation behavior after approved creative memory canon was connected to runtime memory loading.

This is a documentation contract. It does not change the production pipeline.

---

# Purpose

Project memory stores approved world, character, episode, prompt, and continuity knowledge for a single project.

The goal is to keep creative canon stable across episodes while still allowing the story to grow under human control.

---

# Preferred Layout

New project memory and approved creative canon should be stored under:

```text
projects/<project>/memory/
```

Preferred structure:

```text
projects/<project>/memory/
  world/
  characters/
  prompts/
  episodes/
  pending/
```

Use this layout for new canon, future accepted episode summaries, style rules, and pending lore notes.

---

# Supported Legacy Layout

The current runtime still supports the older project memory folders:

```text
projects/<project>/world/
projects/<project>/characters/
projects/<project>/prompts/
projects/<project>/episodes/
```

These folders remain supported for compatibility with existing projects and earlier Foundation work.

They are not the preferred location for new approved creative canon.

---

# Approved Creative Canon

Approved creative canon should be stored under:

```text
projects/<project>/memory/...
```

The runtime memory loader reads approved canon from:

```text
projects/<project>/memory/world/
projects/<project>/memory/characters/
projects/<project>/memory/prompts/
```

Legacy folders are still read, but new canon should be placed in the preferred `memory/` layout so its source is explicit and easy to review.

---

# Memory Categories

## world

Use `memory/world/` for:

- realm canon;
- factions;
- cultivation systems;
- story arcs;
- locations;
- world rules;
- timeline rules;
- forbidden world contradictions.

## characters

Use `memory/characters/` for:

- character canon;
- motivations;
- relationships;
- personality rules;
- starting conditions;
- combat identity;
- forbidden character changes.

## prompts

Use `memory/prompts/` for:

- visual rules;
- story rules;
- negative prompts;
- style rules;
- tone rules;
- prompt constraints for future agents.

## episodes

Use `memory/episodes/` for accepted summaries of completed episodes.

Episode memory should record what became canon after an episode was approved.

Do not store uncertain drafts here.

## pending

Use `memory/pending/` for uncertain lore notes awaiting human approval.

Pending notes may contain possible future reveals, unresolved theories, or candidate continuity updates.

Pending notes are not locked canon until explicitly approved.

---

# Locked Canon And Expandable Canon

## Locked Canon

Locked canon must not be changed without explicit human approval.

Examples:

- project title;
- main character identity;
- core world rules;
- fixed backstory facts;
- forbidden changes;
- approved system rules.

When locked canon conflicts with a generated idea, locked canon wins.

## Expandable Canon

Expandable canon may be extended if the addition does not contradict locked canon.

Examples:

- new accepted episode summaries;
- additional visual references;
- extra relationship details;
- newly approved world notes;
- later arc notes approved by a human.

Expandable canon should still be written carefully and should preserve previous accepted memory.

## Uncertain Additions

Uncertain additions should go to:

```text
projects/<project>/memory/pending/
```

Use pending notes when an idea is useful but not yet approved as permanent canon.

Do not silently promote pending notes into locked canon.

---

# Example: The Origin System

The Origin System uses the preferred memory layout:

```text
projects/ImmortalAcademy/memory/world/world_overview.md
projects/ImmortalAcademy/memory/world/cultivation_system.md
projects/ImmortalAcademy/memory/characters/lin_mo.md
projects/ImmortalAcademy/memory/prompts/story_rules.md
```

These files are approved creative canon.

They should be treated as stronger creative guidance than empty or legacy placeholder files.

---

# Runtime Notes

Foundation runtime memory loading currently combines:

- legacy project memory folders;
- approved `memory/` canon folders.

The combined memory is exposed to pipeline agents through `memory_context` excerpts and summary metadata.

Empty files may be counted in summary fields, but they should not produce excerpts.

File identifiers should remain visible in excerpts so agents can reference where memory came from.
