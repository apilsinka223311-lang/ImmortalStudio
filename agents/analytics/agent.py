"""Deterministic local Analytics agent."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from core.models.production import ProductionTask
from core.pipeline.agents import AgentExecutionContext, AgentResult


class AnalyticsAgent:
    """Creates a deterministic production report without external analytics services."""

    agent_id = "analytics"
    version = "analytics_v1"

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, task: ProductionTask, context: AgentExecutionContext) -> AgentResult:
        """Create `episode_report.json` from available production artifacts."""

        task_path = context.output_directory / "production_task.json"
        plan_path = context.output_directory / "episode_plan.json"
        script_path = context.output_directory / "episode_script.md"
        prompts_path = context.output_directory / "scene_prompts.json"
        image_manifest_path = context.output_directory / "images" / "image_manifest.json"
        voice_manifest_path = context.output_directory / "voice" / "voice_manifest.json"
        video_manifest_path = context.output_directory / "video" / "video_manifest.json"
        output_path = context.output_directory / "episode_report.json"

        missing_result = self._missing_input_result(
            task_path,
            plan_path,
            script_path,
            prompts_path,
            image_manifest_path,
            voice_manifest_path,
            video_manifest_path,
        )
        if missing_result is not None:
            return missing_result

        production_task = self._load_json(task_path)
        episode_plan = self._load_json(plan_path)
        episode_script = script_path.read_text(encoding="utf-8")
        scene_prompts = self._load_json(prompts_path)
        image_manifest = self._load_json(image_manifest_path)
        voice_manifest = self._load_json(voice_manifest_path)
        video_manifest = self._load_json(video_manifest_path)

        report = self._build_report(
            task=task,
            production_task=production_task,
            episode_plan=episode_plan,
            episode_script=episode_script,
            scene_prompts=scene_prompts,
            image_manifest=image_manifest,
            voice_manifest=voice_manifest,
            video_manifest=video_manifest,
            paths={
                "production_task": task_path,
                "episode_plan": plan_path,
                "episode_script": script_path,
                "scene_prompts": prompts_path,
                "image_manifest": image_manifest_path,
                "voice_manifest": voice_manifest_path,
                "video_manifest": video_manifest_path,
            },
        )
        self._save_json(output_path, report)

        self.logger.info("Analytics created episode report: %s", output_path)
        return AgentResult(
            success=True,
            status="episode_report_created",
            message="Analytics created deterministic episode_report.json.",
            output_path=output_path,
            metadata={
                "episode_report": output_path.as_posix(),
                "scene_count": report["generation_summary"]["scene_count"],
                "pipeline_status": report["pipeline_status"],
                "analytics_status": "local_report_created",
            },
        )

    def _missing_input_result(self, *required_paths: Path) -> AgentResult | None:
        for path in required_paths:
            if not path.is_file():
                message = f"Required Analytics input is missing: {path}"
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

    def _build_report(
        self,
        task: ProductionTask,
        production_task: dict[str, Any],
        episode_plan: dict[str, Any],
        episode_script: str,
        scene_prompts: dict[str, Any],
        image_manifest: dict[str, Any],
        voice_manifest: dict[str, Any],
        video_manifest: dict[str, Any],
        paths: dict[str, Path],
    ) -> dict[str, Any]:
        prompt_scenes = scene_prompts.get("prompts") or scene_prompts.get("scenes") or []
        completed_stages = list(production_task.get("completed_stages", []))
        pending_stages = list(production_task.get("pending_stages", []))
        scene_count = len(prompt_scenes)

        return {
            "schema_version": "1.0",
            "pipeline_version": str(task.metadata.get("pipeline_version") or "1.0"),
            "project": task.project,
            "episode": task.episode,
            "task_id": task.task_id,
            "analytics_version": self.version,
            "pipeline_status": "planned_assets_ready",
            "source_artifacts": {
                name: path.as_posix() for name, path in paths.items()
            },
            "stage_summary": {
                "completed_stages": completed_stages,
                "pending_stages": pending_stages,
                "current_stage_before_analytics_completion": production_task.get("current_stage"),
                "status_before_analytics_completion": production_task.get("status"),
            },
            "generation_summary": {
                "scene_count": scene_count,
                "episode_plan_scene_count": len(episode_plan.get("scenes", [])),
                "image_plan_count": int(image_manifest.get("total_scenes") or 0),
                "voice_plan_count": int(voice_manifest.get("total_scenes") or 0),
                "video_plan_count": int(video_manifest.get("total_scenes") or 0),
                "script_character_count": len(episode_script),
                "target_duration_seconds": task.metadata.get("duration_seconds"),
                "estimated_video_duration_seconds": video_manifest.get("total_estimated_duration_seconds"),
                "real_images_generated": 0,
                "real_audio_files_generated": 0,
                "real_video_files_rendered": 0,
            },
            "artifact_status": {
                "images": image_manifest.get("image_status"),
                "voice": voice_manifest.get("audio_status"),
                "video": video_manifest.get("render_status"),
                "analytics": "report_created",
            },
            "validation_summary": self._validation_summary(
                scene_count=scene_count,
                episode_plan=episode_plan,
                image_manifest=image_manifest,
                voice_manifest=voice_manifest,
                video_manifest=video_manifest,
            ),
            "models_used": [
                {
                    "stage": "analytics",
                    "provider": "local",
                    "model": "deterministic_python",
                    "version": self.version,
                }
            ],
            "prompt_versions": {
                "scene_prompts": scene_prompts.get("prompt_style_version"),
            },
            "cost_summary": {
                "external_api_cost": 0,
                "currency": "USD",
                "notes": "No external APIs were used by the deterministic local pipeline.",
            },
            "recommendations": [
                "Implement Publisher next to package final episode artifacts.",
                "Add JSON Schema validation before replacing deterministic planners with real providers.",
                "Keep planned and generated asset statuses explicit to avoid treating placeholders as media.",
            ],
            "metadata": {
                "language": task.language,
                "platform": task.platform,
                "report_type": "deterministic_local_pipeline_report",
            },
        }

    @staticmethod
    def _validation_summary(
        scene_count: int,
        episode_plan: dict[str, Any],
        image_manifest: dict[str, Any],
        voice_manifest: dict[str, Any],
        video_manifest: dict[str, Any],
    ) -> dict[str, Any]:
        expected_counts = {
            "episode_plan": len(episode_plan.get("scenes", [])),
            "image_manifest": int(image_manifest.get("total_scenes") or 0),
            "voice_manifest": int(voice_manifest.get("total_scenes") or 0),
            "video_manifest": int(video_manifest.get("total_scenes") or 0),
            "scene_prompts": scene_count,
        }
        counts_match = len(set(expected_counts.values())) == 1
        return {
            "scene_counts_match": counts_match,
            "expected_counts": expected_counts,
            "all_assets_are_planned_only": (
                image_manifest.get("image_status") == "planned_not_generated"
                and voice_manifest.get("audio_status") == "planned_not_generated"
                and video_manifest.get("render_status") == "planned_not_rendered"
            ),
            "ready_for_publisher": counts_match,
            "warnings": [] if counts_match else ["Scene counts differ across production artifacts."],
        }

    @staticmethod
    def _save_json(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")


def create_agent() -> AnalyticsAgent:
    """Factory used by FileSystemAgentRegistry."""

    return AnalyticsAgent()
