"""Deterministic local Publisher agent."""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Any

from core.models.production import ProductionTask
from core.pipeline.agents import AgentExecutionContext, AgentResult


class PublisherAgent:
    """Creates a local final episode package without uploading anywhere."""

    agent_id = "publisher"
    version = "publisher_v1"

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, task: ProductionTask, context: AgentExecutionContext) -> AgentResult:
        """Create a deterministic local package and `metadata.json`."""

        required_files = {
            "production_task": context.output_directory / "production_task.json",
            "episode_plan": context.output_directory / "episode_plan.json",
            "episode_script": context.output_directory / "episode_script.md",
            "scene_prompts": context.output_directory / "scene_prompts.json",
            "episode_report": context.output_directory / "episode_report.json",
            "image_manifest": context.output_directory / "images" / "image_manifest.json",
            "voice_manifest": context.output_directory / "voice" / "voice_manifest.json",
            "video_manifest": context.output_directory / "video" / "video_manifest.json",
        }
        missing_result = self._missing_input_result(required_files.values())
        if missing_result is not None:
            return missing_result

        package_directory = context.output_directory / "final"
        package_directory.mkdir(parents=True, exist_ok=True)

        source_data = {name: self._load_json(path) for name, path in required_files.items() if path.suffix == ".json"}
        self._copy_contract_files(package_directory, required_files)
        self._copy_plan_directories(context.output_directory, package_directory)

        metadata_path = package_directory / "metadata.json"
        metadata = self._metadata_payload(
            task=task,
            context=context,
            package_directory=package_directory,
            source_data=source_data,
        )
        self._save_json(metadata_path, metadata)

        package_manifest_path = package_directory / "package_manifest.json"
        self._save_json(package_manifest_path, self._package_manifest(package_directory, metadata_path))

        self.logger.info("Publisher created local final package: %s", package_directory)
        return AgentResult(
            success=True,
            status="local_package_created",
            message="Publisher created deterministic local final package.",
            output_path=metadata_path,
            metadata={
                "package_directory": package_directory.as_posix(),
                "metadata_json": metadata_path.as_posix(),
                "package_manifest": package_manifest_path.as_posix(),
                "upload_status": "not_uploaded",
                "publisher_status": "local_package_created",
            },
        )

    def _missing_input_result(self, required_paths: Any) -> AgentResult | None:
        for path in required_paths:
            if not path.is_file():
                message = f"Required Publisher input is missing: {path}"
                self.logger.error(message)
                return AgentResult(
                    success=False,
                    status="missing_input",
                    message=message,
                    metadata={"missing_file": path.as_posix()},
                )
        return None

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _copy_contract_files(package_directory: Path, required_files: dict[str, Path]) -> None:
        file_map = {
            "episode_plan": "episode_plan.json",
            "episode_script": "episode_script.md",
            "scene_prompts": "scene_prompts.json",
            "episode_report": "episode_report.json",
            "production_task": "production_task.json",
        }
        for key, filename in file_map.items():
            shutil.copy2(required_files[key], package_directory / filename)

    @staticmethod
    def _copy_plan_directories(output_directory: Path, package_directory: Path) -> None:
        for directory_name in ("images", "voice", "video"):
            source_directory = output_directory / directory_name
            target_directory = package_directory / directory_name
            if target_directory.exists():
                shutil.rmtree(target_directory)
            shutil.copytree(source_directory, target_directory)
        (package_directory / "subtitles").mkdir(exist_ok=True)

    def _metadata_payload(
        self,
        task: ProductionTask,
        context: AgentExecutionContext,
        package_directory: Path,
        source_data: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        report = source_data["episode_report"]
        scene_prompts = source_data["scene_prompts"]
        image_manifest = source_data["image_manifest"]
        voice_manifest = source_data["voice_manifest"]
        video_manifest = source_data["video_manifest"]
        production_task = source_data["production_task"]

        return {
            "schema_version": "1.0",
            "pipeline_version": str(task.metadata.get("pipeline_version") or "1.0"),
            "project_id": str(task.metadata.get("project_id") or task.project),
            "episode_id": task.episode,
            "title": str(source_data["episode_plan"].get("title") or task.episode),
            "language": task.language,
            "target_platform": task.platform,
            "duration_seconds": task.metadata.get("duration_seconds"),
            "created_at": task.timestamp,
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
            "source_contracts": {
                "episode_plan": {"path": "episode_plan.json", "schema_version": "1.0"},
                "episode_script": {"path": "episode_script.md", "schema_version": "1.0"},
                "scene_prompts": {
                    "path": "scene_prompts.json",
                    "schema_version": str(scene_prompts.get("schema_version") or "1.0"),
                },
                "world": {"path": "project_memory/world", "schema_version": "1.0"},
                "characters": [
                    {"path": "project_memory/characters", "schema_version": "1.0"}
                ],
            },
            "agents": self._agent_summary(production_task),
            "models_used": report.get("models_used", []),
            "prompt_versions": report.get("prompt_versions", {}),
            "generation_summary": {
                **report.get("generation_summary", {}),
                "image_status": image_manifest.get("image_status"),
                "audio_status": voice_manifest.get("audio_status"),
                "render_status": video_manifest.get("render_status"),
            },
            "validation_summary": report.get("validation_summary", {}),
            "archive_policy": {
                "archive_temporary_files": False,
                "preserve_prompts": True,
                "preserve_seeds": True,
                "preserve_planning_artifacts": True,
            },
            "upload_status": "not_uploaded",
            "publisher_version": self.version,
            "package_directory": package_directory.as_posix(),
            "notes": [
                "This deterministic Publisher created a local package only.",
                "No external platform upload was attempted.",
                "No real MP4 was rendered; video artifact points to the video manifest.",
            ],
        }

    @staticmethod
    def _agent_summary(production_task: dict[str, Any]) -> list[dict[str, str]]:
        stage_results = production_task.get("metadata", {}).get("stage_results", {})
        agents: list[dict[str, str]] = []
        for stage_id in production_task.get("completed_stages", []):
            result = stage_results.get(stage_id, {})
            agents.append(
                {
                    "agent": stage_id,
                    "output": str(result.get("output_path") or ""),
                    "status": str(result.get("status") or "completed"),
                }
            )
        return agents

    @staticmethod
    def _package_manifest(package_directory: Path, metadata_path: Path) -> dict[str, Any]:
        files = sorted(
            path.relative_to(package_directory).as_posix()
            for path in package_directory.rglob("*")
            if path.is_file()
        )
        return {
            "schema_version": "1.0",
            "package_status": "local_package_created",
            "metadata": metadata_path.relative_to(package_directory).as_posix(),
            "files": files,
        }

    @staticmethod
    def _save_json(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")


def create_agent() -> PublisherAgent:
    """Factory used by FileSystemAgentRegistry."""

    return PublisherAgent()
