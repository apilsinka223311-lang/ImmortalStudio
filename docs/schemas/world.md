# World Schema

Version: 1.0

---

# Purpose

Defines the persistent memory contract for world facts, locations, rules and timeline constraints inside one ImmortalStudio project.

World records prevent episodes from contradicting lore and provide shared context for all production agents.

---

# Produced by

Studio Director, Story Architect, Lore-focused future agents or approved human worldbuilding updates.

---

# Consumed by

Studio Director, Story Architect, Script Writer, Prompt Engineer, Image Director, Voice Director, Video Editor, Analytics and future QA agents.

---

# Input

- Project concept
- Approved lore documents
- Previous episode memory
- Character records
- Style guide
- Human-approved worldbuilding changes

---

# Output

A world memory record, usually stored under a project-specific world memory location.

In v1, the repository may store this information as Markdown, but the canonical contract is JSON-compatible.

---

# Required fields

- `schema_version`: Contract version. Must be `"1.0"` for this schema.
- `project_id`
- `world_id`
- `name`
- `description`
- `genre`
- `tone`
- `rules`
- `locations`
- `factions`
- `timeline`
- `visual_identity`
- `continuity_rules`
- `last_updated`

Each rule must contain:

- `rule_id`
- `category`
- `description`
- `strictness`

Each location must contain:

- `location_id`
- `name`
- `description`
- `visual_traits`
- `allowed_scene_types`

Each timeline entry must contain:

- `event_id`
- `time_reference`
- `description`
- `episode_id`

---

# Optional fields

- `cultivation_system`
- `magic_system`
- `technology_level`
- `languages`
- `cultures`
- `maps`
- `important_objects`
- `forbidden_elements`
- `open_mysteries`
- `production_notes`
- `revision`

---

# Validation rules

- `world_id` must be unique within the project.
- `location_id`, `rule_id`, `faction_id` and `event_id` values must be stable.
- Story, script and prompt outputs must not contradict strict world rules.
- New locations must be marked as planned until approved into world memory.
- Timeline entries must not conflict with previous episode events.
- Visual identity must be specific enough to guide prompt generation.
- World records must not contain provider-specific model settings.
- Important lore facts must be stored here or in linked project memory, not only inside prompts.

---

# JSON example

```json
{
  "schema_version": "1.0",
  "project_id": "immortal_academy",
  "world_id": "immortal_academy_world",
  "name": "Immortal Academy",
  "description": "A mountain academy where young disciples learn cultivation, discipline and the cost of spiritual power.",
  "genre": "fantasy cultivation drama",
  "tone": "mysterious, cinematic, character-driven",
  "rules": [
    {
      "rule_id": "rule_spiritual_pressure",
      "category": "cultivation",
      "description": "Spiritual pressure reveals a disciple's current control, not their ultimate destiny.",
      "strictness": "strict"
    }
  ],
  "locations": [
    {
      "location_id": "academy_main_gate",
      "name": "Academy Main Gate",
      "description": "An ancient stone gate overlooking misty mountain paths.",
      "visual_traits": ["tall stone pillars", "mist", "golden academy emblem", "mountain dawn"],
      "allowed_scene_types": ["arrival", "departure", "ceremony"]
    },
    {
      "location_id": "training_hall",
      "name": "Training Hall",
      "description": "A large hall where disciples test spiritual control under elder supervision.",
      "visual_traits": ["polished stone floor", "circular test platform", "hanging banners"],
      "allowed_scene_types": ["trial", "conflict", "reveal"]
    }
  ],
  "factions": [
    {
      "faction_id": "academy_elders",
      "name": "Academy Elders",
      "description": "Senior cultivators responsible for protecting the academy's secrets."
    }
  ],
  "timeline": [
    {
      "event_id": "event_sword_sleeping",
      "time_reference": "before series",
      "description": "An ancient sword was sealed beneath the training hall.",
      "episode_id": null
    }
  ],
  "visual_identity": {
    "style_id": "immortal_academy_style_v1",
    "palette": ["deep blue", "jade green", "warm gold", "mist white"],
    "lighting": "cinematic fantasy lighting with soft atmospheric depth",
    "camera_language": "stable cinematic shots, clear emotional framing"
  },
  "continuity_rules": [
    "The academy should feel ancient and disciplined, not modern.",
    "Cultivation power must have visible cost or limitation.",
    "Major lore reveals require memory updates."
  ],
  "last_updated": "2026-07-01"
}
```

---

# Example workflow

1. Studio Director loads the world record during task creation.
2. Story Architect plans scenes using approved rules and locations.
3. Script Writer uses world tone and timeline constraints.
4. Prompt Engineer uses location and visual identity data.
5. QA validates that generated episode outputs do not contradict strict rules.
6. Approved new lore updates the world record after production.

---

# Future extensions

- Dedicated lore database.
- Timeline conflict validator.
- Map and location graph support.
- Multi-world and crossover support.
- Rule strictness scoring.
- Automated memory update proposals after each episode.
