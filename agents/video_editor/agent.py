"""Deterministic local Video Editor agent."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.models.production import ProductionTask
from core.pipeline.agents import AgentExecutionContext, AgentResult


@dataclass(frozen=True)
class VideoScenePlan:
    """Planned video assembly artifact for one scene."""

    scene_id: str
    scene_title: str
    timeline_start_seconds: int
    timeline_end_seconds: int
    estimated_duration_seconds: int
    planned_output_file: str
    plan_path: Path


class VideoEditorAgent:
    """Creates deterministic video assembly plans without rendering video."""

    agent_id = "video_editor"
    version = "video_editor_v1"

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, task: ProductionTask, context: AgentExecutionContext) -> AgentResult:
        """Create video plan JSON files from script, prompts, image plans and voice plans."""

        script_path = context.output_directory / "episode_script.md"
        prompts_path = context.output_directory / "scene_prompts.json"
        image_manifest_path = context.output_directory / "images" / "image_manifest.json"
        voice_manifest_path = context.output_directory / "voice" / "voice_manifest.json"
        video_directory = context.output_directory / "video"

        missing_result = self._missing_input_result(
            script_path,
            prompts_path,
            image_manifest_path,
            voice_manifest_path,
        )
        if missing_result is not None:
            return missing_result

        episode_script = script_path.read_text(encoding="utf-8")
        prompt_package = self._load_json(prompts_path)
        image_manifest = self._load_json(image_manifest_path)
        voice_manifest = self._load_json(voice_manifest_path)

        video_plans = self._build_video_plans(task, prompt_package, video_directory)
        video_directory.mkdir(parents=True, exist_ok=True)
        for plan in video_plans:
            self._save_json(
                plan.plan_path,
                self._video_plan_payload(
                    plan=plan,
                    prompt_package=prompt_package,
                    image_manifest=image_manifest,
                    voice_manifest=voice_manifest,
                    episode_script=episode_script,
                ),
            )

        manifest_path = video_directory / "video_manifest.json"
        manifest = self._manifest_payload(
            task=task,
            prompt_package=prompt_package,
            script_path=script_path,
            prompts_path=prompts_path,
            image_manifest_path=image_manifest_path,
            voice_manifest_path=voice_manifest_path,
            video_plans=video_plans,
        )
        self._save_json(manifest_path, manifest)

        self.logger.info("Video Editor created video manifest: %s", manifest_path)
        return AgentResult(
            success=True,
            status="video_plans_created",
            message="Video Editor created deterministic video assembly planning artifacts.",
            output_path=manifest_path,
            metadata={
                "source_episode_script": script_path.as_posix(),
                "source_scene_prompts": prompts_path.as_posix(),
                "source_image_manifest": image_manifest_path.as_posix(),
                "source_voice_manifest": voice_manifest_path.as_posix(),
                "video_manifest": manifest_path.as_posix(),
                "scene_count": len(video_plans),
                "render_status": "planned_not_rendered",
            },
        )

    def _missing_input_result(self, *required_paths: Path) -> AgentResult | None:
        for path in required_paths:
            if not path.is_file():
                message = f"Required Video Editor input is missing: {path}"
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

    def _build_video_plans(
        self,
        task: ProductionTask,
        prompt_package: dict[str, Any],
        video_directory: Path,
    ) -> list[VideoScenePlan]:
        prompts = prompt_package.get("prompts") or prompt_package.get("scenes") or []
        scene_count = max(len(prompts), 1)
        total_duration = int(task.metadata.get("duration_seconds") or 60)
        base_duration = max(total_duration // scene_count, 1)
        plans: list[VideoScenePlan] = []
        timeline_start = 0

        for index, scene_prompt in enumerate(prompts, start=1):
            scene_id = str(scene_prompt.get("scene_id") or f"scene_{index:03d}")
            scene_title = str(scene_prompt.get("scene_title") or f"Scene {index}")
            duration = base_duration
            if index == scene_count:
                duration = max(total_duration - timeline_start, 1)
            timeline_end = timeline_start + duration
            plans.append(
                VideoScenePlan(
                    scene_id=scene_id,
                    scene_title=scene_title,
                    timeline_start_seconds=timeline_start,
                    timeline_end_seconds=timeline_end,
                    estimated_duration_seconds=duration,
                    planned_output_file=f"video/{scene_id}.mp4",
                    plan_path=video_directory / f"{scene_id}.json",
                )
            )
            timeline_start = timeline_end
        return plans

    def _video_plan_payload(
        self,
        plan: VideoScenePlan,
        prompt_package: dict[str, Any],
        image_manifest: dict[str, Any],
        voice_manifest: dict[str, Any],
        episode_script: str,
    ) -> dict[str, Any]:
        scene_prompt = self._find_scene_prompt(prompt_package, plan.scene_id)
        image_scene = self._find_manifest_scene(image_manifest, plan.scene_id)
        voice_scene = self._find_manifest_scene(voice_manifest, plan.scene_id)
        image_plan = str(image_scene.get("plan_file") or f"images/{plan.scene_id}.json")
        voice_plan = str(voice_scene.get("plan_file") or f"voice/{plan.scene_id}.json")
        future_image_asset = str(
            image_scene.get("planned_output_file")
            or scene_prompt.get("output_targets", {}).get("image")
            or f"images/{plan.scene_id}.png"
        )
        future_voice_asset = str(
            voice_scene.get("planned_output_file")
            or scene_prompt.get("output_targets", {}).get("voice")
            or f"voice/{plan.scene_id}.wav"
        )

        return {
            "scene_id": plan.scene_id,
            "scene_title": plan.scene_title,
            "source_image_plan": image_plan,
            "source_voice_plan": voice_plan,
            "source_script_context": self._script_context(episode_script, plan.scene_id),
            "timeline_start_seconds": plan.timeline_start_seconds,
            "timeline_end_seconds": plan.timeline_end_seconds,
            "estimated_duration_seconds": plan.estimated_duration_seconds,
            "visual_track": {
                "image_plan_file": image_plan,
                "intended_future_image_asset": future_image_asset,
                "camera_movement": scene_prompt.get("camera_motion") or "stable cinematic push-in",
                "animation_direction": scene_prompt.get("animation_prompt") or "subtle scene motion",
                "visual_focus": self._visual_focus(scene_prompt),
            },
            "voice_track": {
                "voice_plan_file": voice_plan,
                "intended_future_audio_asset": future_voice_asset,
                "narration_dialogue_usage": scene_prompt.get("voice_prompt") or "Use planned narration and dialogue.",
                "pacing": self._pacing_for_mood(str(scene_prompt.get("mood") or "focused")),
            },
            "subtitle_track": {
                "subtitle_style": "high-contrast short-form captions",
                "approximate_subtitle_source": scene_prompt.get("subtitle_prompt") or "episode_script.md",
                "readability_notes": "Keep subtitles concise, centered safely, and readable on mobile screens.",
            },
            "music_track": {
                "mood": scene_prompt.get("mood") or "focused",
                "intensity": "restrained with clear scene support",
                "timing_notes": scene_prompt.get("music_prompt") or "Align music changes with scene transitions.",
            },
            "sfx_track": {
                "scene_sound_effects": scene_prompt.get("sound_effects_prompt") or "Use subtle scene-specific effects.",
                "timing_notes": "Place effects under dialogue and emphasize transition beats.",
            },
            "transition_in": self._transition_in(plan.timeline_start_seconds),
            "transition_out": {
                "transition_type": "cut",
                "reason": "Maintain clear pacing for short-form video.",
                "next_scene_relationship": "Continue to the next ordered scene.",
            },
            "render_status": "planned_not_rendered",
            "planned_output_file": plan.planned_output_file,
            "continuity_notes": [
                "Preserve image continuity from Image Director plans.",
                "Preserve narrator and character voice continuity from Voice Director plans.",
                "Keep subtitle style consistent across all scenes.",
            ],
            "assembly_notes": [
                "No video was rendered by this deterministic Video Editor.",
                "This file is a future video assembly plan.",
                "Do not treat planned_output_file as an existing video asset.",
            ],
            "metadata": {
                "source_scene_id": plan.scene_id,
                "prompt_style_version": prompt_package.get("prompt_style_version"),
                "aspect_ratio": scene_prompt.get("aspect_ratio", "9:16"),
                "render_target": "future_renderer",
            },
        }

    @staticmethod
    def _visual_focus(scene_prompt: dict[str, Any]) -> str:
        image_prompt = str(scene_prompt.get("image_prompt") or "")
        if not image_prompt:
            return "clear cinematic story beat"
        return image_prompt[:240]

    @staticmethod
    def _transition_in(timeline_start_seconds: int) -> dict[str, str]:
        if timeline_start_seconds == 0:
            return {
                "transition_type": "opening cut",
                "reason": "Start the episode clearly and immediately.",
                "previous_scene_relationship": "episode opening",
            }
        return {
            "transition_type": "cut",
            "reason": "Continue pacing from previous scene.",
            "previous_scene_relationship": "previous ordered scene",
        }

    @staticmethod
    def _pacing_for_mood(mood: str) -> str:
        lowered = mood.lower()
        if any(word in lowered for word in ("awe", "mystery", "uncertainty", "nervous")):
            return "slow, spacious, and suspenseful"
        if any(word in lowered for word in ("action", "fear", "urgent", "danger")):
            return "fast but readable"
        return "medium pace with clear visual beats"

    @staticmethod
    def _script_context(episode_script: str, scene_id: str) -> str:
        scene_index = episode_script.find(scene_id)
        if scene_index == -1:
            return "Scene context should be inferred from the matching scene prompt."
        snippet = episode_script[scene_index : scene_index + 500]
        return " ".join(snippet.split())

    @staticmethod
    def _find_scene_prompt(prompt_package: dict[str, Any], scene_id: str) -> dict[str, Any]:
        prompts = prompt_package.get("prompts") or prompt_package.get("scenes") or []
        for scene_prompt in prompts:
            if str(scene_prompt.get("scene_id")) == scene_id:
                return scene_prompt
        return {}

    @staticmethod
    def _find_manifest_scene(manifest: dict[str, Any], scene_id: str) -> dict[str, Any]:
        for scene in manifest.get("scenes", []):
            if str(scene.get("scene_id")) == scene_id:
                return scene
        return {}

    def _manifest_payload(
        self,
        task: ProductionTask,
        prompt_package: dict[str, Any],
        script_path: Path,
        prompts_path: Path,
        image_manifest_path: Path,
        voice_manifest_path: Path,
        video_plans: list[VideoScenePlan],
    ) -> dict[str, Any]:
        total_duration = sum(plan.estimated_duration_seconds for plan in video_plans)
        return {
            "project": prompt_package.get("project") or task.project,
            "episode": prompt_package.get("episode") or task.episode,
            "task_id": task.task_id,
            "video_editor_version": self.version,
            "source_episode_script": script_path.as_posix(),
            "source_scene_prompts": prompts_path.as_posix(),
            "source_image_manifest": image_manifest_path.as_posix(),
            "source_voice_manifest": voice_manifest_path.as_posix(),
            "total_scenes": len(video_plans),
            "total_estimated_duration_seconds": total_duration,
            "render_status": "planned_not_rendered",
            "planned_final_output_file": "video/episode.mp4",
            "scenes": [
                {
                    "scene_id": plan.scene_id,
                    "scene_title": plan.scene_title,
                    "plan_file": plan.plan_path.relative_to(script_path.parent).as_posix(),
                    "planned_output_file": plan.planned_output_file,
                    "timeline_start_seconds": plan.timeline_start_seconds,
                    "timeline_end_seconds": plan.timeline_end_seconds,
                    "render_status": "planned_not_rendered",
                }
                for plan in video_plans
            ],
            "validation_notes": [
                "Video Editor produced JSON planning artifacts only.",
                "No real video was rendered.",
                "No placeholder MP4 or MOV files were created.",
                "Each scene prompt has a corresponding video scene plan JSON file.",
            ],
            "metadata": {
                "prompt_style_version": prompt_package.get("prompt_style_version"),
                "source_scene_count": len(prompt_package.get("prompts") or prompt_package.get("scenes") or []),
                "render_target": "future_video_renderer",
            },
        }

    @staticmethod
    def _save_json(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")


def create_agent() -> VideoEditorAgent:
    """Factory used by FileSystemAgentRegistry."""

    return VideoEditorAgent()
