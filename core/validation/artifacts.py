"""Validation of pipeline output artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from core.validation.json_schema import JsonSchemaValidator, ValidationIssue, ValidationResult
from core.validation.schemas import SCHEMAS


@dataclass(frozen=True)
class ArtifactContract:
    """Maps a pipeline stage to the JSON artifact it must produce."""

    stage_id: str
    schema_name: str
    relative_path: Path


class DefaultArtifactValidator:
    """Validate known first-pipeline JSON outputs after each stage."""

    CONTRACTS: dict[str, ArtifactContract] = {
        "story_architect": ArtifactContract("story_architect", "episode_plan", Path("episode_plan.json")),
        "prompt_engineer": ArtifactContract("prompt_engineer", "scene_prompts", Path("scene_prompts.json")),
        "image_director": ArtifactContract("image_director", "image_manifest", Path("images") / "image_manifest.json"),
        "voice_director": ArtifactContract("voice_director", "voice_manifest", Path("voice") / "voice_manifest.json"),
        "video_editor": ArtifactContract("video_editor", "video_manifest", Path("video") / "video_manifest.json"),
        "analytics": ArtifactContract("analytics", "episode_report", Path("episode_report.json")),
        "publisher": ArtifactContract("publisher", "metadata", Path("final") / "metadata.json"),
    }

    def __init__(self, validator: JsonSchemaValidator | None = None) -> None:
        self.validator = validator or JsonSchemaValidator()

    def validate_stage(self, stage_id: str, output_directory: Path) -> ValidationResult:
        """Validate the configured JSON artifact for a completed stage."""

        contract = self.CONTRACTS.get(stage_id)
        if contract is None:
            return ValidationResult(
                success=True,
                schema_name="not_applicable",
                artifact_path="",
                skipped=True,
            )

        artifact_path = output_directory / contract.relative_path
        if not artifact_path.is_file():
            return ValidationResult(
                success=False,
                schema_name=contract.schema_name,
                artifact_path=artifact_path.as_posix(),
                issues=[ValidationIssue("$", "Expected stage output artifact is missing.")],
            )

        try:
            with artifact_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            return ValidationResult(
                success=False,
                schema_name=contract.schema_name,
                artifact_path=artifact_path.as_posix(),
                issues=[ValidationIssue("$", f"Invalid JSON: {exc}")],
            )

        schema = SCHEMAS[contract.schema_name]
        return self.validator.validate(
            data=data,
            schema=schema,
            schema_name=contract.schema_name,
            artifact_path=artifact_path.as_posix(),
        )
