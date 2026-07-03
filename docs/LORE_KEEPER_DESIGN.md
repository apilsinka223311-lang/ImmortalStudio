# Lore Keeper / Memory Curator Design

This document describes a future Lore Keeper / Memory Curator agent.

It is documentation only. It does not implement the agent, change the production pipeline, or modify runtime memory loading.

---

# Purpose

The Lore Keeper / Memory Curator is responsible for reading accepted episode outputs and proposing safe project memory updates.

Its job is not to write new stories.

Its job is to protect continuity by extracting accepted facts, separating uncertain information, and preventing locked canon from being changed silently.

---

# Inputs

A future Lore Keeper should read completed and accepted episode artifacts:

```text
production_task.json
episode_plan.json
episode_script.md
scene_prompts.json
episode_report.json
final/metadata.json
```

It should also read current project memory under:

```text
projects/<project>/memory/
```

Relevant memory sections include:

```text
projects/<project>/memory/world/
projects/<project>/memory/characters/
projects/<project>/memory/prompts/
projects/<project>/memory/episodes/
projects/<project>/memory/pending/
```

Generated episode output is treated as draft until a human or approval process accepts it.

The Lore Keeper should extract facts only from accepted output.

---

# Outputs

The Lore Keeper should not silently edit canon files.

It should produce proposed memory updates separated into:

```text
accepted_updates
pending_review
rejected_or_do_not_use
```

The first implementation should output proposed Markdown updates or reviewable sections.

Later implementations may produce structured diffs, but the human review point must remain for locked canon.

---

# Memory Update Targets

## Episode Summary

Accepted episode summaries should be written to:

```text
projects/<project>/memory/episodes/episode_<number>_summary.md
```

## Pending Lore Notes

Uncertain or unapproved facts should be written to:

```text
projects/<project>/memory/pending/pending_lore_notes.md
```

## Optional Canon Files After Approval

The Lore Keeper may propose changes to:

```text
projects/<project>/memory/world/
projects/<project>/memory/characters/
projects/<project>/memory/prompts/
```

Those changes must remain proposals until approved.

Locked canon files must never be overwritten automatically.

---

# Rules

The Lore Keeper must follow these rules:

- never overwrite locked canon without explicit human approval;
- never invent lore not supported by accepted episode artifacts;
- never silently contradict `story_rules.md`;
- never move uncertain facts directly into locked canon;
- never add a system shop unless explicitly approved;
- never make Lin Mo overpowered if the Episode 1 contract says otherwise;
- never treat rejected ideas as canon;
- never hide conflicts by rewriting memory around them.

If output conflicts with locked canon, the Lore Keeper must report the conflict instead of changing memory.

---

# Episode Summary Contract

A future Lore Keeper should write episode summaries with these sections:

```markdown
# Episode <number> Summary

## Episode ID

episode_<number>

## Title

Accepted episode title.

## Accepted Events

- Events accepted as having happened in the episode.

## Character State Changes

- Character injuries, decisions, relationships, reputation changes, power changes, or emotional shifts.

## World/Lore Additions

- New accepted facts about the world, clans, factions, cultivation, locations, systems, or rules.

## Unresolved Mysteries

- Questions introduced or reinforced by the accepted episode.

## Continuity Notes

- Details future episodes must preserve.

## Memory Update Recommendations

- Suggested updates to memory files, separated into accepted updates, pending review, and rejected / do not use.
```

The summary should contain accepted facts only.

Uncertain facts should be linked or copied into pending notes instead.

---

# Review Workflow

The intended review workflow is:

1. Production pipeline generates episode artifacts.
2. Generated episode output is treated as draft.
3. Human or approval process accepts the episode.
4. Lore Keeper reads accepted episode artifacts.
5. Lore Keeper extracts facts from accepted output only.
6. Lore Keeper compares extracted facts against locked canon and current memory.
7. Lore Keeper proposes memory updates.
8. Human review approves, edits, rejects, or moves updates into pending.
9. Approved updates become canon.

This workflow prevents episode generation from silently mutating project memory.

---

# Conflict Handling

If a generated episode contradicts locked canon, the Lore Keeper should report the conflict.

It should not rewrite memory to make the contradiction disappear.

Conflict reports should include:

- the conflicting artifact;
- the extracted claim;
- the locked canon rule or file it conflicts with;
- suggested resolution options;
- whether the claim should be rejected, moved to pending review, or escalated for human approval.

---

# Example: The Origin System Episode 1

Accepted facts may include:

- Lin Mo awakened during public humiliation.
- Lin Jian forced him down publicly.
- The Origin System initialized.
- Foundation fragment was detected.
- Lin Mo countered for the first time.

Pending facts may include:

- exact truth behind the framing conspiracy;
- who ordered Lin Mo's channels to be severed;
- full origin of The Origin System.

The pending facts should not be written directly into locked canon.

They should be placed in `memory/pending/` until approved.

---

# Future Implementation Notes

The Foundation implementation should start deterministic and local.

It should not use external AI APIs.

Recommended implementation order:

1. Add a deterministic parser for accepted local artifacts.
2. Output proposed Markdown updates first.
3. Add smoke tests before automation.
4. Keep human review points for locked canon.
5. Add structured diffs only after the Markdown proposal flow is stable.

The first implementation should prefer clear, reviewable output over clever automation.

The Lore Keeper must remain a memory safety layer, not an uncontrolled canon writer.
