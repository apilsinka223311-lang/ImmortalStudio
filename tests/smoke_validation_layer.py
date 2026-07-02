"""Smoke checks for the local JSON Schema validation layer."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.validation import DefaultArtifactValidator, JsonSchemaValidator  # noqa: E402
from core.validation.schemas import SCHEMAS  # noqa: E402


def main() -> None:
    """Verify direct schema validation and artifact validation behavior."""

    validator = JsonSchemaValidator()
    valid_metadata = {
        "schema_version": "1.0",
        "pipeline_version": "1.0",
        "project_id": "ImmortalAcademy",
        "episode_id": "episode_validation_smoke",
        "title": "Validation Smoke",
        "language": "English",
        "target_platform": "YouTube Shorts",
        "duration_seconds": 60,
        "created_at": "2026-07-02T00:00:00+00:00",
        "pipeline_status": "draft",
        "artifact_paths": {
            "video": "video/video_manifest.json",
            "script": "episode_script.md",
            "prompts": "scene_prompts.json",
            "report": "episode_report.json",
            "images": "images/",
            "voice": "voice/",
            "subtitles": "subtitles/",
        },
        "source_contracts": {},
        "agents": [],
        "models_used": [],
        "prompt_versions": {},
        "generation_summary": {},
        "validation_summary": {},
        "archive_policy": {},
    }
    valid_result = validator.validate(valid_metadata, SCHEMAS["metadata"], "metadata", "metadata.json")
    assert valid_result.success is True

    invalid_metadata = dict(valid_metadata)
    invalid_metadata.pop("artifact_paths")
    invalid_result = validator.validate(invalid_metadata, SCHEMAS["metadata"], "metadata", "metadata.json")
    assert invalid_result.success is False
    assert any(issue.path == "$.artifact_paths" for issue in invalid_result.issues)

    with TemporaryDirectory() as tmp:
        output_directory = Path(tmp)
        bad_plan_path = output_directory / "episode_plan.json"
        bad_plan_path.write_text(json.dumps({"schema_version": "1.0"}), encoding="utf-8")
        artifact_result = DefaultArtifactValidator().validate_stage("story_architect", output_directory)
        assert artifact_result.success is False
        assert artifact_result.schema_name == "episode_plan"

        skipped_result = DefaultArtifactValidator().validate_stage("script_writer", output_directory)
        assert skipped_result.success is True
        assert skipped_result.skipped is True


if __name__ == "__main__":
    main()
    print("smoke_validation_layer_ok")
