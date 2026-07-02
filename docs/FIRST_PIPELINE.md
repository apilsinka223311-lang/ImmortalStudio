⚠ This document defines the canonical execution order of ImmortalStudio.

All agents, scripts and workflows must follow this specification.

If implementation differs from this document, the implementation must be updated or this document must be revised.

This file is the single source of truth for the production pipeline.

# FIRST PIPELINE
Version: 1.0

---

# Purpose

This document describes the minimum production pipeline of ImmortalStudio.

The goal is to transform a simple user idea into a complete short animated episode.

This is NOT the final production pipeline.

This is the first working vertical slice.

If this pipeline works from start to finish, ImmortalStudio becomes a functioning AI production system.

---

# Production Contracts

The first pipeline communicates through explicit file contracts.

Canonical schema documentation lives in:

- `docs/schemas/episode_plan.md`
- `docs/schemas/episode_script.md`
- `docs/schemas/scene_prompt.md`
- `docs/schemas/character.md`
- `docs/schemas/world.md`
- `docs/schemas/metadata.md`

Agents must produce and consume files according to these contracts.

In v1, some artifacts may remain human-readable Markdown, but their content must stay structured enough to be converted into JSON without guessing.

No agent should rely on hidden context when a required field belongs in a schema.

---

# Input

User provides:

- Project
- World
- Idea
- Episode Goal
- Duration
- Language
- Target Platform

Example:

Project:
Immortal Academy

Idea:
A new disciple enters the academy and accidentally awakens an ancient sword.

Episode length:
60 seconds

Language:
English

Platform:
YouTube Shorts

---

# Global Pipeline

User

↓

Studio Director

↓

Story Architect

↓

Script Writer

↓

Prompt Engineer

↓

Image Director

↓

Voice Director

↓

Video Editor

↓

Analytics

↓

Publisher

↓

Finished Episode

---

# STEP 1
Studio Director

Purpose:

Receive user request.

Validate project.

Load project configuration.

Load world memory.

Load character memory.

Load style configuration.

Create production task.

Output:

production_task.json

---

# STEP 2
Story Architect

Purpose:

Expand the idea into a complete episode plan.

Produces:

- Synopsis
- Story Structure
- Scene List
- Emotional Curve

Output:

episode_plan.json

Schema:

docs/schemas/episode_plan.md

---

# STEP 3
Script Writer

Purpose:

Convert episode plan into screenplay.

Produces:

- Narration
- Dialogues
- Scene descriptions
- Camera notes

Output:

episode_script.md

Schema:

docs/schemas/episode_script.md

---

# STEP 4
Prompt Engineer

Purpose:

Generate prompts for every scene.

Produces:

- Image Prompt
- Animation Prompt
- Voice Prompt
- Music Prompt

Output:

scene_prompts.json

Schema:

docs/schemas/scene_prompt.md

---

# STEP 5
Image Director

Purpose:

Generate every illustration.

Input:

scene_prompts.json

Output:

images/

scene_001.png

scene_002.png

scene_003.png

...

---

# STEP 6
Voice Director

Purpose:

Generate narration and voices.

Produces:

Narrator

Character voices

Sound effects references

Output:

voice/

narration.wav

character_01.wav

character_02.wav

...

---

# STEP 7
Video Editor

Purpose:

Combine:

Images

Voice

Music

Transitions

Camera Motion

Subtitles

Output:

episode.mp4

---

# STEP 8
Analytics

Purpose:

Collect metadata.

Calculate:

Generation time

Models used

Prompt versions

Token usage

Estimated cost

Output:

episode_report.json

Final metadata must also be written as:

metadata.json

Schema:

docs/schemas/metadata.md

---

# STEP 9
Publisher

Purpose:

Move all generated files into final project folder.

Create final structure.

Archive temporary files.

---

# Output Structure

Episode/

│

├── episode.mp4

├── script.md

├── prompts.json

├── report.json

├── images/

├── voice/

├── subtitles/

└── metadata.json

---

# Error Handling

If one agent fails:

Stop pipeline.

Save current state.

Generate error log.

Allow resume from failed step.

Never restart completed steps.

---

# Memory Usage

Before execution every agent receives:

Project

World

Characters

Style Guide

Previous Episodes

Global Rules

Current Task

Every agent returns structured output only.

World and character memory must follow:

- docs/schemas/world.md
- docs/schemas/character.md

---

# Minimal Version (v1)

The first working version MUST support:

✓ One project

✓ One episode

✓ One narrator

✓ Static images

✓ Simple voice

✓ Simple subtitles

✓ Final MP4

No automatic uploads.

No scheduling.

No multi-language support.

No parallel generation.

---

# Future Versions

v2

Multiple projects

Persistent memory

Character consistency

Better prompts

Animation improvements

v3

Multiple AI providers

Parallel generation

Automatic publishing

Voice cloning

Advanced analytics

Episode scheduling

---

# Success Criteria

Pipeline is considered operational when:

User enters one idea.

↓

The system automatically executes every stage.

↓

A complete episode folder is generated.

↓

Episode can be watched without manual editing.

This is the minimum definition of a working ImmortalStudio.
