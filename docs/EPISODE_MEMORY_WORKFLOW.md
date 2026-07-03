# Episode Memory Workflow

This document defines the intended future workflow for reading project memory, writing episodes, and proposing memory updates.

This is a documentation contract only. It does not create a Lore Keeper agent, Episode Writer agent, or new production pipeline behavior.

---

# Purpose

Episode memory keeps long-running stories consistent.

Future story and episode agents must use project memory before writing and must preserve approved canon after writing.

The workflow must prevent silent lore drift, accidental contradiction of locked canon, and unreviewed changes to core world or character files.

---

# Memory To Read Before Writing

Before writing or expanding an episode, a future episode/story agent must read project memory from:

```text
projects/<project>/memory/world/
projects/<project>/memory/characters/
projects/<project>/memory/prompts/
projects/<project>/memory/episodes/
projects/<project>/memory/pending/
```

The agent should use these sources as follows:

- `world/` for realm rules, factions, cultivation, arcs, locations, and world constraints;
- `characters/` for character canon, motivations, relationships, and forbidden changes;
- `prompts/` for visual rules, story rules, negative prompts, and style rules;
- `episodes/` for accepted summaries of completed episodes;
- `pending/` for uncertain lore notes awaiting human approval.

---

# Canon Preservation Rules

## Locked Canon

Locked canon must be preserved.

Future agents must not change locked canon without explicit human approval.

If a requested episode idea conflicts with locked canon, the agent must preserve locked canon and flag the conflict.

## Expandable Canon

Expandable canon may be extended only when the new addition does not contradict locked canon.

An addition should be treated as expandable canon only after it is accepted as part of an episode or approved directly by a human.

## Uncertain Facts

New uncertain facts must not be written directly into locked canon files.

Uncertain facts should be written as pending notes under:

```text
projects/<project>/memory/pending/
```

Pending notes are not permanent canon until reviewed and accepted.

---

# Files That Must Not Be Silently Rewritten

Future agents must not silently rewrite core approved canon files such as:

```text
world_overview.md
cultivation_system.md
lin_mo.md
lin_jian.md
story_rules.md
```

These files may contain locked canon.

Changes to them require explicit human approval and should be reviewable as a focused update.

---

# After An Episode Is Accepted

After an episode is accepted, an episode summary should be written to:

```text
projects/<project>/memory/episodes/episode_<number>_summary.md
```

The summary should record what became accepted memory.

It should not contain unapproved speculation as if it were canon.

---

# Episode Summary Template

Each accepted episode summary should include:

```markdown
# Episode <number> Summary

## Episode ID

episode_<number>

## Title

Accepted episode title.

## Accepted Events

- Event that happened on screen or was explicitly accepted.

## Character Changes

- Character state, relationship, motivation, injury, power, or reputation changes accepted by the episode.

## World/Lore Additions

- New accepted world, faction, system, location, or cultivation facts.

## New Unresolved Mysteries

- Mysteries introduced or reinforced by the episode.

## Continuity Notes

- Details that future episodes must preserve.

## Memory Update Recommendations

- Suggested updates to world, character, prompt, episode, or pending memory files.
```

---

# Proposed Memory Updates

Proposed memory updates should be separated into three groups.

## Accepted Updates

Accepted updates are facts that have been approved as canon.

They may be written to episode summaries or, with human approval, to relevant world, character, or prompt files.

## Pending Review

Pending review contains useful but uncertain additions.

These should go to:

```text
projects/<project>/memory/pending/
```

Pending review is the right place for uncertain motives, possible conspiracy details, future reveals, and candidate lore that is not yet locked.

## Rejected / Do Not Use

Rejected ideas should be clearly marked as not canon.

They must not be reused by future agents unless a human explicitly reverses the decision.

---

# Example: The Origin System

Episode 1 introduces:

- public humiliation;
- The Origin System awakening;
- Lin Jian forcing Lin Mo into a public confrontation;
- Lin Jian stepping back for the first time after Lin Mo counters through system analysis.

After Episode 1 is accepted, its accepted summary should be written to:

```text
projects/ImmortalAcademy/memory/episodes/episode_001_summary.md
```

Accepted episode facts can be recorded in the episode summary.

Any uncertain detail about the framing conspiracy should go to:

```text
projects/ImmortalAcademy/memory/pending/
```

The uncertain framing detail must not be written directly into locked canon files such as:

```text
projects/ImmortalAcademy/memory/world/world_overview.md
projects/ImmortalAcademy/memory/characters/lin_mo.md
projects/ImmortalAcademy/memory/characters/lin_jian.md
projects/ImmortalAcademy/memory/prompts/story_rules.md
```

---

# Future Implementation Notes

A future Lore Keeper or Memory Curator agent may automate this workflow later.

That future agent must:

- extract facts only from accepted episodes;
- separate accepted updates from pending review and rejected ideas;
- never overwrite locked canon without human approval;
- produce reviewable diffs or proposed updates;
- preserve file identifiers so humans can trace where each memory update came from.

A future Episode Writer agent may also use this workflow, but it must not become responsible for silently mutating canon files.

Episode writing and canon mutation should remain separate responsibilities unless explicitly redesigned later.
