# Metadata Schema

Version: 1.0

---

# Purpose

Defines the contract for `metadata.json`, the final episode metadata package created during the first pipeline.

Metadata links all generated artifacts, production settings, model usage, validation state and archive paths so the episode can be reproduced, audited and improved.

---

# Produced by

Analytics and Publisher.

---

# Consumed by

Studio Director, Analytics, Publisher, future QA agents, future scheduling systems and future improvement loops.

---

# Input

- `production_task.json`
- `episode_plan.json`
- `episode_script.md`
- `scene_prompts.json`
- Generated images
- Generated voice files
- Generated subtitles
- Final video file
- Provider usage reports
- Error logs or validation reports

---

# Output

`metadata.json`

The file belongs in the final episode folder alongside `episode.mp4`, script, prompts, report and generated assets.

---

# Required fields

- `schema_version`: Contract version. Must be `"1.0"` for this schema.
- `pipeline_version`
- `project_id`
- `episode_id`
- `title`
- `language`
- `target_platform`
- `duration_seconds`
- `created_at`
- `pipeline_status`
- `artifact_paths`
- `source_contracts`
- `agents`
- `models_used`
- `prompt_versions`
- `generation_summary`
- `validation_summary`
- `archive_policy`

`artifact_paths` must contain:

- `video`
- `script`
- `prompts`
- `report`
- `images`
- `voice`
- `subtitles`

`source_contracts` must contain:

- `episode_plan`
- `episode_script`
- `scene_prompts`
- `world`
- `characters`

---

# Optional fields

- `season_id`
- `series_id`
- `thumbnail`
- `title_candidates`
- `description`
- `tags`
- `upload_status`
- `cost_estimate`
- `token_usage`
- `seed_registry`
- `quality_score`
- `error_log`
- `revision`
- `notes`

---

# Validation rules

- Every path in `artifact_paths` must be relative to the final episode folder or project root.
- `pipeline_status` must be one of `draft`, `in_progress`, `completed`, `failed` or `archived`.
- `source_contracts` must reference the exact schema versions used to produce the episode.
- `models_used` must list provider, model name or local model identifier, purpose and version when known.
- `prompt_versions` must match the prompt package used by Prompt Engineer.
- If generation uses seeds, they must be stored in `seed_registry`.
- Failed pipelines must include `error_log`.
- Completed pipelines must include a playable `video` path.
- Metadata must not contain API keys, secrets or private credentials.

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
  "duration_seconds": 60,
  "created_at": "2026-07-01T15:00:00Z",
  "pipeline_status": "completed",
  "artifact_paths": {
    "video": "episode.mp4",
    "script": "script.md",
    "prompts": "prompts.json",
    "report": "report.json",
    "images": "images/",
    "voice": "voice/",
    "subtitles": "subtitles/"
  },
  "source_contracts": {
    "episode_plan": {
      "path": "episode_plan.json",
      "schema_version": "1.0"
    },
    "episode_script": {
      "path": "script.md",
      "schema_version": "1.0"
    },
    "scene_prompts": {
      "path": "prompts.json",
      "schema_version": "1.0"
    },
    "world": {
      "path": "world/world.md",
      "schema_version": "1.0"
    },
    "characters": [
      {
        "path": "characters/protagonist.md",
        "schema_version": "1.0"
      }
    ]
  },
  "agents": [
    {
      "agent": "Story Architect",
      "output": "episode_plan.json",
      "status": "completed"
    },
    {
      "agent": "Script Writer",
      "output": "script.md",
      "status": "completed"
    }
  ],
  "models_used": [
    {
      "purpose": "story_planning",
      "provider": "provider-agnostic",
      "model": "not_recorded",
      "version": "unknown"
    }
  ],
  "prompt_versions": {
    "scene_prompts": "immortal_academy_style_v1"
  },
  "generation_summary": {
    "images_generated": 3,
    "voice_files_generated": 2,
    "subtitles_generated": true,
    "estimated_cost": null
  },
  "validation_summary": {
    "story_valid": true,
    "visual_consistency_valid": true,
    "character_consistency_valid": true,
    "render_valid": true
  },
  "archive_policy": {
    "archive_temporary_files": true,
    "preserve_prompts": true,
    "preserve_seeds": true
  }
}
```

---

# Example workflow

1. Analytics collects model usage, prompt versions, timing and validation results.
2. Publisher moves final files into the episode folder.
3. Publisher writes `metadata.json` with stable artifact paths.
4. Future analytics and improvement systems read metadata before planning new episodes.
5. Reproduction tools use metadata to locate prompts, seeds and source contracts.

---

# Future extensions

- Automatic cost accounting.
- Audience analytics after publishing.
- Platform-specific upload metadata.
- Reproduction manifests.
- Asset checksums.
- Quality score history across revisions.
