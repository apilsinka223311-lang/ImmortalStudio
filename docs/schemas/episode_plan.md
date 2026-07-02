# Episode Plan Schema

Version: 1.0

---

# Purpose

Defines the contract for `episode_plan.json`, the first structured creative plan for one episode in the first production pipeline.

The episode plan turns a user idea, project memory, world memory, character memory and style rules into a scene-level plan that later agents can execute without inventing missing story facts.

---

# Produced by

Story Architect.

---

# Consumed by

Script Writer, Prompt Engineer, Analytics and future QA agents.

---

# Input

- `production_task.json`
- World schema records
- Character schema records
- Project style guide
- Previous episode summaries when available
- Global project rules

---

# Output

`episode_plan.json`

The output must be structured JSON. Human-readable notes are allowed only inside explicit string fields.

---

# Required fields

- `schema_version`: Contract version. Must be `"1.0"` for this schema.
- `pipeline_version`: Pipeline version that produced the plan.
- `project_id`: Stable project identifier.
- `episode_id`: Stable episode identifier.
- `title`: Working episode title.
- `language`: Primary language for the episode.
- `target_platform`: Intended platform, for example `YouTube Shorts`.
- `target_duration_seconds`: Planned total duration in seconds.
- `episode_goal`: The production goal supplied by the user or Studio Director.
- `logline`: One-sentence summary.
- `synopsis`: Short summary of the complete episode.
- `story_structure`: Object containing `setup`, `conflict`, `turning_point` and `resolution`.
- `emotional_curve`: Ordered list of emotional beats.
- `scenes`: Ordered list of scene plan objects.
- `continuity_notes`: Facts that must remain consistent with memory.
- `validation_status`: Current validation state.

Each scene object must contain:

- `scene_id`: Stable scene identifier, for example `scene_001`.
- `order`: Integer scene order starting at 1.
- `purpose`: Why the scene exists.
- `summary`: What happens in the scene.
- `location_id`: Existing or planned world location identifier.
- `character_ids`: Character identifiers appearing in the scene.
- `estimated_duration_seconds`: Planned scene duration.
- `emotional_beat`: Primary emotional function of the scene.
- `story_function`: Role in the episode structure.

---

# Optional fields

- `season_id`
- `series_id`
- `genre`
- `tone`
- `audience`
- `content_rating`
- `visual_style_id`
- `music_direction`
- `risk_notes`
- `open_questions`
- `revision`
- `source_references`
- `provider_notes`

---

# Validation rules

- `scene_id` values must be unique within the episode.
- Scene `order` values must be sequential and must match list order.
- Sum of `estimated_duration_seconds` should be within 10 percent of `target_duration_seconds`.
- Every `character_ids` value must reference a Character schema record or be marked as a planned new character.
- Every `location_id` must reference a World schema location or be marked as a planned new location.
- `story_structure` must contain a complete beginning, middle and ending.
- `continuity_notes` must not contradict world rules or character memory.
- No scene may exist without a clear `purpose`.
- The plan must not include provider-specific prompt syntax.

---

# JSON example

```json
{
  "schema_version": "1.0",
  "pipeline_version": "1.0",
  "project_id": "immortal_academy",
  "episode_id": "ia_s01_e001",
  "title": "The Sleeping Sword",
  "language": "English",
  "target_platform": "YouTube Shorts",
  "target_duration_seconds": 60,
  "episode_goal": "Introduce a new disciple and awaken an ancient sword.",
  "logline": "A nervous new disciple accidentally awakens a forgotten sword during his first trial.",
  "synopsis": "A new disciple enters Immortal Academy, fails a simple test, and unexpectedly draws power from an ancient sword hidden beneath the training hall.",
  "story_structure": {
    "setup": "The disciple arrives at the academy and feels out of place.",
    "conflict": "He fails the basic spiritual pressure test in front of other students.",
    "turning_point": "The floor cracks and an ancient sword answers his fear.",
    "resolution": "The academy elders realize the disciple may be tied to an old prophecy."
  },
  "emotional_curve": [
    "uncertainty",
    "embarrassment",
    "fear",
    "awe",
    "mystery"
  ],
  "scenes": [
    {
      "scene_id": "scene_001",
      "order": 1,
      "purpose": "Introduce the academy and the protagonist's insecurity.",
      "summary": "The new disciple walks through the academy gate while senior students watch.",
      "location_id": "academy_main_gate",
      "character_ids": ["protagonist"],
      "estimated_duration_seconds": 12,
      "emotional_beat": "uncertainty",
      "story_function": "setup"
    },
    {
      "scene_id": "scene_002",
      "order": 2,
      "purpose": "Create public failure and trigger the hidden power.",
      "summary": "The disciple fails the test, but the ancient sword awakens below the hall.",
      "location_id": "training_hall",
      "character_ids": ["protagonist", "elder_mentor"],
      "estimated_duration_seconds": 32,
      "emotional_beat": "awe",
      "story_function": "turning_point"
    },
    {
      "scene_id": "scene_003",
      "order": 3,
      "purpose": "End with mystery and future story momentum.",
      "summary": "The elders recognize the sword and exchange a worried look.",
      "location_id": "training_hall",
      "character_ids": ["protagonist", "elder_mentor"],
      "estimated_duration_seconds": 16,
      "emotional_beat": "mystery",
      "story_function": "resolution"
    }
  ],
  "continuity_notes": [
    "The sword must be treated as ancient and rare.",
    "The protagonist is inexperienced, not secretly confident."
  ],
  "validation_status": "draft"
}
```

---

# Example workflow

1. Studio Director creates `production_task.json`.
2. Story Architect loads world and character memory.
3. Story Architect creates `episode_plan.json`.
4. Script Writer validates required fields before writing the screenplay.
5. Analytics stores the plan version for later production reports.

---

# Future extensions

- Formal JSON Schema file generation.
- Automatic duration balancing.
- Lore validation against world timelines.
- Multi-language episode planning.
- A/B testing variants for hooks and endings.
- Risk scoring for continuity, pacing and production cost.
