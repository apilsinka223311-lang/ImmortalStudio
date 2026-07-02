# Character Schema

Version: 1.0

---

# Purpose

Defines the persistent memory contract for a character in an ImmortalStudio project.

Character records preserve identity, appearance, personality, relationships and voice continuity across episodes.

---

# Produced by

Character memory may be created by Studio Director, Story Architect or a future Character Agent. Updates must be validated by the agent responsible for character continuity.

---

# Consumed by

Studio Director, Story Architect, Script Writer, Prompt Engineer, Image Director, Voice Director, Video Editor, Analytics and future QA agents.

---

# Input

- Project concept
- World schema records
- Previous episode memory
- Approved character descriptions
- Visual references
- Voice references

---

# Output

A character memory record, usually stored under a project-specific character memory location.

In v1, the repository may store this information as Markdown, but the canonical contract is JSON-compatible.

---

# Required fields

- `schema_version`: Contract version. Must be `"1.0"` for this schema.
- `project_id`
- `character_id`: Stable unique identifier.
- `name`
- `role`: Narrative role, for example `protagonist`, `mentor`, `rival` or `villain`.
- `status`: Current continuity status.
- `description`: Short human-readable character summary.
- `personality`
- `appearance`
- `voice_profile`
- `relationships`
- `continuity_rules`
- `first_appearance`
- `last_updated`

`appearance` must contain:

- `age_range`
- `silhouette`
- `face`
- `hair`
- `clothing`
- `colors`
- `distinguishing_features`

`voice_profile` must contain:

- `voice_id`
- `language`
- `tone`
- `pace`
- `emotional_range`

---

# Optional fields

- `aliases`
- `faction_id`
- `location_id`
- `abilities`
- `weaknesses`
- `motivation`
- `backstory`
- `arc_summary`
- `visual_reference_ids`
- `voice_reference_ids`
- `forbidden_changes`
- `production_notes`
- `revision`

---

# Validation rules

- `character_id` must be unique within the project.
- A recurring character must not change face, silhouette, main clothing identity or voice without explicit approval.
- `voice_id` must remain stable for recurring characters.
- Relationships must reference existing Character schema records or be marked as planned.
- Character abilities must not contradict World schema rules.
- `continuity_rules` must include any facts that future agents are not allowed to improvise.
- Visual descriptions should be specific enough for prompt generation.
- No provider-specific model settings belong in the character record.

---

# JSON example

```json
{
  "schema_version": "1.0",
  "project_id": "immortal_academy",
  "character_id": "protagonist",
  "name": "Lin Kai",
  "role": "protagonist",
  "status": "active",
  "description": "A nervous new disciple whose hidden connection to an ancient sword slowly reshapes his destiny.",
  "personality": {
    "core_traits": ["anxious", "observant", "kind", "stubborn under pressure"],
    "speech_style": "Polite, hesitant, increasingly direct when protecting others.",
    "default_emotions": ["uncertainty", "curiosity", "determination"]
  },
  "appearance": {
    "age_range": "late teens",
    "silhouette": "slim young disciple with slightly tense posture",
    "face": "soft youthful face, wide attentive eyes",
    "hair": "dark messy hair tied loosely",
    "clothing": "simple new disciple robes",
    "colors": ["deep blue", "white", "muted silver"],
    "distinguishing_features": ["small jade wrist charm", "slightly oversized robe sleeves"]
  },
  "voice_profile": {
    "voice_id": "voice_likai_v1",
    "language": "English",
    "tone": "young, gentle, uncertain but sincere",
    "pace": "medium",
    "emotional_range": ["nervous", "awed", "determined"]
  },
  "relationships": [
    {
      "character_id": "elder_mentor",
      "relationship_type": "mentor",
      "current_state": "The elder is cautious but curious about Lin Kai."
    }
  ],
  "continuity_rules": [
    "Lin Kai is inexperienced at the start of the series.",
    "The jade wrist charm must remain visible in close shots.",
    "His voice must not sound arrogant in early episodes."
  ],
  "first_appearance": "ia_s01_e001",
  "last_updated": "2026-07-01"
}
```

---

# Example workflow

1. Studio Director loads character records before starting an episode.
2. Story Architect uses character motivation and continuity rules while planning.
3. Script Writer writes dialogue consistent with personality and speech style.
4. Prompt Engineer uses appearance and forbidden changes in scene prompts.
5. Voice Director uses `voice_profile` to preserve voice consistency.
6. After production, approved changes update the character record.

---

# Future extensions

- Character arc timeline.
- Visual embedding or reference image registry.
- Voice model compatibility matrix.
- Automated contradiction detection.
- Relationship graph generation.
- Per-season character state snapshots.
