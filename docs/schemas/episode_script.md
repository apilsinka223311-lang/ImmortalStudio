# Episode Script Schema

Version: 1.0

---

# Purpose

Defines the contract for `episode_script.md`, the screenplay artifact produced from `episode_plan.json`.

The first pipeline stores the script as Markdown for readability, but the content must follow this schema so future tools can parse it into JSON without guessing.

---

# Produced by

Script Writer.

---

# Consumed by

Prompt Engineer, Voice Director, Video Editor, Analytics and future QA agents.

---

# Input

- `episode_plan.json`
- World schema records
- Character schema records
- Style guide
- Dialogue and tone rules

---

# Output

`episode_script.md`

The Markdown file must contain a metadata block and ordered scene sections. The canonical data model is represented by the JSON example below.

---

# Required fields

- `schema_version`: Contract version. Must be `"1.0"` for this schema.
- `pipeline_version`: Pipeline version that produced the script.
- `project_id`
- `episode_id`
- `source_episode_plan_id`
- `title`
- `language`
- `target_duration_seconds`
- `scenes`
- `validation_status`

Each scene must contain:

- `scene_id`: Must match a scene from `episode_plan.json`.
- `order`: Must match the episode plan order.
- `heading`: Short scene heading.
- `location_id`
- `estimated_duration_seconds`
- `description`: Visual and story description.
- `camera_notes`: Camera direction for the scene.
- `dialogue`: Ordered list of spoken lines.
- `narration`: Ordered list of narrator lines.
- `audio_notes`: Non-dialogue audio guidance.
- `transition_out`: How the scene moves into the next scene.

Each dialogue line must contain:

- `line_id`
- `speaker_id`
- `text`
- `emotion`
- `delivery_note`

Each narration line must contain:

- `line_id`
- `text`
- `emotion`
- `delivery_note`

---

# Optional fields

- `season_id`
- `series_id`
- `revision`
- `beat`
- `props`
- `visual_constraints`
- `subtitle_notes`
- `pronunciation_notes`
- `timing_notes`
- `content_warnings`
- `source_references`

---

# Validation rules

- Every script scene must reference an existing scene from `episode_plan.json`.
- Script scene order must match the episode plan unless a revision note explains the change.
- Dialogue speakers must reference Character schema records or the reserved speaker `narrator`.
- Dialogue and narration must be written in the declared `language`.
- Empty scenes are invalid.
- The script must preserve all `continuity_notes` from the episode plan.
- Camera notes must describe intent, not provider-specific prompt syntax.
- Estimated scene durations should remain within the episode plan duration budget.

---

# JSON example

```json
{
  "schema_version": "1.0",
  "pipeline_version": "1.0",
  "project_id": "immortal_academy",
  "episode_id": "ia_s01_e001",
  "source_episode_plan_id": "ia_s01_e001",
  "title": "The Sleeping Sword",
  "language": "English",
  "target_duration_seconds": 60,
  "scenes": [
    {
      "scene_id": "scene_001",
      "order": 1,
      "heading": "Academy Gate - Dawn",
      "location_id": "academy_main_gate",
      "estimated_duration_seconds": 12,
      "description": "The new disciple steps through the academy gate while older students pause to watch him.",
      "camera_notes": "Wide establishing shot moving into a nervous close-up.",
      "dialogue": [],
      "narration": [
        {
          "line_id": "narration_001",
          "text": "On his first morning at Immortal Academy, one disciple carried more fear than luggage.",
          "emotion": "curious",
          "delivery_note": "Soft but cinematic."
        }
      ],
      "audio_notes": "Quiet wind, distant training bells.",
      "transition_out": "Cut to the training hall doors opening."
    },
    {
      "scene_id": "scene_002",
      "order": 2,
      "heading": "Training Hall - Trial",
      "location_id": "training_hall",
      "estimated_duration_seconds": 32,
      "description": "The disciple fails the spiritual pressure test, then golden cracks spread across the floor.",
      "camera_notes": "Start with a medium shot, then push toward the cracking floor.",
      "dialogue": [
        {
          "line_id": "dialogue_001",
          "speaker_id": "elder_mentor",
          "text": "Again. Breathe before you reach.",
          "emotion": "firm",
          "delivery_note": "Controlled and patient."
        }
      ],
      "narration": [
        {
          "line_id": "narration_002",
          "text": "The hall expected silence. The sword answered instead.",
          "emotion": "awe",
          "delivery_note": "Build toward mystery."
        }
      ],
      "audio_notes": "Low rumble, rising metallic resonance.",
      "transition_out": "Bright flash into elder reaction."
    }
  ],
  "validation_status": "draft"
}
```

---

# Example workflow

1. Script Writer reads `episode_plan.json`.
2. Script Writer creates `episode_script.md` using the same `scene_id` values.
3. Prompt Engineer extracts scene descriptions, camera notes and audio notes.
4. Voice Director extracts narration and dialogue lines.
5. Video Editor uses scene order and transition notes for assembly.

---

# Future extensions

- Machine-readable screenplay export as `episode_script.json`.
- Automatic subtitle extraction.
- Dialogue timing estimates.
- Multi-language script variants.
- Pronunciation dictionaries for voice generation.
- Script linting for exposition, repetition and pacing.
