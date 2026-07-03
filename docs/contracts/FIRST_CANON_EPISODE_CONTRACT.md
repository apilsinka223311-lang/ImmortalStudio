# First Canon Episode Contract

This contract defines the minimum canon-driven artifact expectations for The Origin System Episode 1.

It is a small regression contract for Foundation-stage deterministic production.

It does not change the production pipeline and does not create new lore.

---

# Scope

This contract applies to the first canon-driven production sample for:

```text
Project: ImmortalAcademy
Story: The Origin System
Episode: Episode 1
```

The contract protects required canon beats so future Story Architect and Prompt Engineer changes do not accidentally remove them.

---

# Required Episode 1 Beats

Generated planning and prompt artifacts must preserve these beats:

- Lin Mo awakens during public humiliation.
- The scene is connected to Azure Sword Clan.
- Lin Jian humiliates Lin Mo as a cripple or disgrace.
- The Origin System initializes.
- Spiritual channels are artificially severed.
- A Foundation fragment is detected.
- Lin Jian's weak point is analyzed.
- Lin Mo counters for the first time.
- The system shop must not appear.
- Lin Mo must not become overpowered.

---

# Artifact Expectations

## production_task.json

`production_task.json` must contain `metadata.memory_context`.

The memory context must include approved canon references for:

- The Origin System;
- Fallen Star Realm;
- Lin Mo;
- Lin Jian;
- The Origin System has no shop.

The memory context should preserve file identifiers such as:

```text
memory/world/world_overview.md
memory/world/first_arc.md
memory/characters/lin_mo.md
memory/characters/lin_jian.md
memory/prompts/story_rules.md
```

## episode_plan.json

`episode_plan.json` must reference or include the required Episode 1 beats.

At Foundation level, a beat may appear in:

- title;
- summary;
- hook;
- logline;
- synopsis;
- scenes;
- memory references;
- continuity notes.

The plan must not describe Lin Mo as instantly overpowered.

The plan must not introduce a system shop.

## scene_prompts.json

`scene_prompts.json` must preserve canon context for downstream image, animation, voice, and music stages.

It must reference or include:

- Lin Mo;
- Lin Jian;
- Azure Sword Clan or Azure Sword Clan training courtyard;
- The Origin System;
- public humiliation or system awakening context;
- approved visual/story rules from memory context when available.

The prompt package must not introduce a system shop.

The prompt package must not describe Lin Mo as instantly overpowered.

## final/metadata.json

If the deterministic local pipeline reaches Publisher, `final/metadata.json` must exist.

It must remain a local package metadata artifact only.

It must not claim external upload or real media generation.

---

# Negative Contract Checks

Generated artifacts must not contain phrases that imply forbidden canon changes, such as:

```text
system shop appears
opens the system shop
buys from the system shop
Lin Mo becomes overpowered
Lin Mo is instantly overpowered
instant immortal lord
```

The phrase `The Origin System has no shop` is allowed because it preserves the locked system rule.

---

# Foundation-Level Notes

The current deterministic agents are simple placeholders.

This contract does not require cinematic prose or perfect story generation.

It requires that the first canon-driven production path keeps the core Episode 1 beats visible in generated artifacts through the input idea and approved runtime memory.
