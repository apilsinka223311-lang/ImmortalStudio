# Scene Prompt Schema

Version: 1.0

---

# Purpose

Defines the contract for `scene_prompts.json`, the structured prompt package used to generate visual, animation, voice and music assets for each scene.

Prompts must preserve story, character, world and style continuity while staying provider-independent.

---

# Produced by

Prompt Engineer.

---

# Consumed by

Image Director, Voice Director, Video Editor, Analytics and future Animation and Music agents.

---

# Input

- `episode_script.md`
- `episode_plan.json`
- Character schema records
- World schema records
- Style guide
- Provider routing configuration when available

---

# Output

`scene_prompts.json`

---

# Required fields

- `schema_version`: Contract version. Must be `"1.0"` for this schema.
- `pipeline_version`
- `project_id`
- `episode_id`
- `source_script_id`
- `language`
- `prompt_style_version`
- `scenes`
- `validation_status`

Each scene prompt must contain:

- `scene_id`: Must match the script scene.
- `order`
- `image_prompt`: Provider-independent visual generation prompt.
- `animation_prompt`: Motion and camera guidance.
- `voice_prompt`: Narration and dialogue voice guidance.
- `music_prompt`: Music direction for the scene.
- `negative_prompt`: Things to avoid.
- `character_references`: Characters and required visual traits.
- `world_references`: Locations, props and world rules.
- `output_targets`: Expected asset paths or logical targets.

---

# Optional fields

- `provider_hints`
- `aspect_ratio`
- `resolution`
- `seed`
- `style_reference_ids`
- `shot_type`
- `camera_motion`
- `lighting`
- `mood`
- `subtitle_text`
- `quality_notes`
- `revision`

---

# Validation rules

- Every `scene_id` must exist in `episode_script.md`.
- Prompts must not contradict Character or World schema records.
- `image_prompt` must include required characters, location, mood and visual style.
- `negative_prompt` must include continuity risks relevant to the scene.
- `provider_hints` must be optional; the core prompt must remain provider-independent.
- `output_targets` must not point outside the current project output structure.
- Seeds are optional in v1 but must be stored when used.
- Scene prompt order must match the script order.

---

# JSON example

```json
{
  "schema_version": "1.0",
  "pipeline_version": "1.0",
  "project_id": "immortal_academy",
  "episode_id": "ia_s01_e001",
  "source_script_id": "ia_s01_e001",
  "language": "English",
  "prompt_style_version": "immortal_academy_style_v1",
  "scenes": [
    {
      "scene_id": "scene_001",
      "order": 1,
      "image_prompt": "Cinematic anime-inspired fantasy academy gate at dawn, nervous young disciple entering for the first time, senior students watching from stone steps, consistent Immortal Academy visual style, clear facial expression, dramatic but readable composition.",
      "animation_prompt": "Slow forward camera move from wide gate view into the disciple's nervous close-up. Keep motion subtle and stable.",
      "voice_prompt": "Narrator voice, curious and gentle, with a cinematic pace.",
      "music_prompt": "Soft mysterious academy theme with light strings and distant bells.",
      "negative_prompt": "Do not change protagonist face, clothing colors, academy architecture, or visual style. Avoid chaotic motion and modern objects.",
      "character_references": [
        {
          "character_id": "protagonist",
          "required_traits": ["nervous expression", "new disciple robes", "youthful silhouette"]
        }
      ],
      "world_references": [
        {
          "location_id": "academy_main_gate",
          "required_traits": ["ancient stone gate", "cultivation academy", "dawn atmosphere"]
        }
      ],
      "output_targets": {
        "image": "images/scene_001.png",
        "voice": "voice/scene_001_narration.wav"
      },
      "aspect_ratio": "9:16",
      "mood": "uncertainty"
    }
  ],
  "validation_status": "draft"
}
```

---

# Example workflow

1. Prompt Engineer reads the script scene by scene.
2. Prompt Engineer loads Character, World and Style memory.
3. Prompt Engineer creates `scene_prompts.json`.
4. Image Director generates images from `image_prompt`.
5. Voice Director generates audio from `voice_prompt` and script lines.
6. Analytics records prompt versions, provider hints and seeds.

---

# Future extensions

- Provider-specific prompt adapters.
- Automatic prompt linting.
- Reference image binding.
- Per-shot prompt splitting.
- Prompt performance analytics.
- Multi-model fallback routing.
