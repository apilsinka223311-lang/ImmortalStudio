"""Deterministic local Prompt Engineer agent."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.models.production import ProductionTask
from core.pipeline.agents import AgentExecutionContext, AgentResult


@dataclass(frozen=True)
class PromptScene:
    """Normalized data used to build one scene prompt package."""

    scene_id: str
    order: int
    title: str
    purpose: str
    location: str
    characters: list[str]
    emotion: str
    visual_focus: str
    description: str
    transition: str


class PromptEngineerAgent:
    """Creates deterministic `scene_prompts.json` from the script and episode plan."""

    agent_id = "prompt_engineer"

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, task: ProductionTask, context: AgentExecutionContext) -> AgentResult:
        """Create scene prompts for the next production departments."""

        plan_path = context.output_directory / "episode_plan.json"
        script_path = context.output_directory / "episode_script.md"
        output_path = context.output_directory / "scene_prompts.json"

        missing_result = self._missing_input_result(plan_path, script_path)
        if missing_result is not None:
            return missing_result

        episode_plan = self._load_json(plan_path)
        episode_script = script_path.read_text(encoding="utf-8")
        scenes = self._build_scenes(episode_plan)
        prompt_package = self._build_prompt_package(
            task=task,
            context=context,
            episode_plan=episode_plan,
            episode_script=episode_script,
            scenes=scenes,
            plan_path=plan_path,
            script_path=script_path,
        )
        self._save_json(output_path, prompt_package)

        self.logger.info("Prompt Engineer created scene prompts: %s", output_path)
        return AgentResult(
            success=True,
            status="scene_prompts_created",
            message="Prompt Engineer created scene_prompts.json.",
            output_path=output_path,
            metadata={
                "source_plan": plan_path.as_posix(),
                "source_script": script_path.as_posix(),
                "scene_count": len(scenes),
                "schema_version": "1.0",
            },
        )

    def _missing_input_result(self, plan_path: Path, script_path: Path) -> AgentResult | None:
        if not plan_path.is_file():
            message = f"episode_plan.json is missing: {plan_path}"
            self.logger.error(message)
            return AgentResult(
                success=False,
                status="missing_input",
                message=message,
                metadata={"missing_file": plan_path.as_posix()},
            )

        if not script_path.is_file():
            message = f"episode_script.md is missing: {script_path}"
            self.logger.error(message)
            return AgentResult(
                success=False,
                status="missing_input",
                message=message,
                metadata={"missing_file": script_path.as_posix()},
            )
        return None

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _build_scenes(self, episode_plan: dict[str, Any]) -> list[PromptScene]:
        scenes: list[PromptScene] = []
        for index, scene in enumerate(episode_plan.get("scenes", []), start=1):
            scenes.append(
                PromptScene(
                    scene_id=str(scene.get("scene_id") or f"scene_{index:03d}"),
                    order=int(scene.get("order") or index),
                    title=str(scene.get("title") or f"Scene {index}"),
                    purpose=str(scene.get("purpose") or "advance the episode"),
                    location=str(scene.get("location") or scene.get("location_id") or "primary story location"),
                    characters=[str(character) for character in scene.get("characters", scene.get("character_ids", ["protagonist"]))],
                    emotion=str(scene.get("emotion") or scene.get("emotional_beat") or "focused"),
                    visual_focus=str(scene.get("visual_focus") or "clear cinematic character action"),
                    description=str(scene.get("description") or scene.get("summary") or "A clear cinematic story beat."),
                    transition=str(scene.get("next_scene_transition") or "Cut to the next scene."),
                )
            )
        return scenes

    def _build_prompt_package(
        self,
        task: ProductionTask,
        context: AgentExecutionContext,
        episode_plan: dict[str, Any],
        episode_script: str,
        scenes: list[PromptScene],
        plan_path: Path,
        script_path: Path,
    ) -> dict[str, Any]:
        language = str(episode_plan.get("language") or task.language)
        platform = str(episode_plan.get("target_platform") or episode_plan.get("platform") or task.platform)
        project_id = str(episode_plan.get("project_id") or task.metadata.get("project_id") or task.project)
        episode_id = str(episode_plan.get("episode_id") or task.episode)
        global_style = self._global_style(episode_plan)
        prompts = [self._build_scene_prompt(scene, global_style) for scene in scenes]

        return {
            "schema_version": "1.0",
            "pipeline_version": str(episode_plan.get("pipeline_version") or task.metadata.get("pipeline_version") or "1.0"),
            "project_id": project_id,
            "project": str(episode_plan.get("project") or task.project),
            "episode_id": episode_id,
            "episode": task.episode,
            "source_script_id": episode_id,
            "language": language,
            "target_platform": platform,
            "platform": platform,
            "prompt_style_version": "immortalstudio_prompt_v1",
            "source_episode_plan": plan_path.as_posix(),
            "source_episode_script": script_path.as_posix(),
            "global_style": global_style,
            "prompts": prompts,
            "scenes": prompts,
            "validation_notes": [
                "Generated locally without external AI providers.",
                "Every prompt object maps to one episode plan scene.",
                "Prompts are provider-independent and deterministic.",
                "Episode script was loaded as required input.",
            ],
            "metadata": {
                "script_character_count": len(episode_script),
                "memory_summary": context.metadata.get("memory_summary", {}),
                "scene_count": len(prompts),
            },
            "validation_status": "draft",
        }

    @staticmethod
    def _global_style(episode_plan: dict[str, Any]) -> str:
        tone = episode_plan.get("tone") or "cinematic, mysterious, character-driven"
        return (
            "semi-realistic anime style, consistent character design, cinematic composition, "
            f"high quality lighting, readable action, tone: {tone}"
        )

    def _build_scene_prompt(self, scene: PromptScene, global_style: str) -> dict[str, Any]:
        characters = ", ".join(scene.characters)
        image_prompt = (
            f"{global_style}. Scene purpose: {scene.purpose}. Location: {scene.location}. "
            f"Characters: {characters}. Emotion: {scene.emotion}. Visual focus: {scene.visual_focus}. "
            f"Description: {scene.description}. Use cinematic composition, consistent character design, "
            "semi-realistic anime style, high quality lighting."
        )

        return {
            "scene_id": scene.scene_id,
            "order": scene.order,
            "scene_title": scene.title,
            "image_prompt": image_prompt,
            "negative_prompt": (
                "low quality, distorted face, inconsistent character, bad anatomy, unreadable text, "
                "watermark, extra limbs, blurry image"
            ),
            "animation_prompt": (
                f"Use a slow stable camera move focused on {scene.visual_focus}. "
                f"Character movement should express {scene.emotion}. Add subtle environmental motion. "
                f"Use energy effects only if they support the scene purpose: {scene.purpose}. "
                f"Transition direction: {scene.transition}"
            ),
            "voice_prompt": (
                f"Narration tone should be clear, cinematic, and paced for {scene.emotion}. "
                "Character tone should match the scene emotion without overacting. Keep pacing readable."
            ),
            "music_prompt": (
                f"Mood: {scene.emotion}. Tempo: medium-slow. Genre: cinematic fantasy underscore. "
                "Intensity: restrained, rising only near the end of the scene."
            ),
            "sound_effects_prompt": (
                f"Use subtle sound effects for the location '{scene.location}' and emphasize transitions without overpowering dialogue."
            ),
            "subtitle_prompt": "Create concise subtitles that preserve narration and dialogue timing.",
            "visual_continuity_notes": [
                "Maintain semi-realistic anime style.",
                "Keep lighting and camera language consistent across scenes.",
                "Avoid redesigning recurring visual elements.",
            ],
            "character_continuity_notes": [
                f"Keep character identities consistent for: {characters}.",
                "Do not change faces, silhouettes, clothing identity, or voice assumptions without approval.",
            ],
            "character_references": [
                {
                    "character_id": character,
                    "required_traits": ["consistent design", "clear silhouette", f"emotion: {scene.emotion}"],
                }
                for character in scene.characters
            ],
            "world_references": [
                {
                    "location_id": scene.location,
                    "required_traits": ["consistent location identity", "cinematic readability"],
                }
            ],
            "output_targets": {
                "image": f"images/{scene.scene_id}.png",
                "animation": f"animation/{scene.scene_id}.mp4",
                "voice": f"voice/{scene.scene_id}.wav",
                "music": f"music/{scene.scene_id}.wav",
                "subtitles": f"subtitles/{scene.scene_id}.srt",
            },
            "aspect_ratio": "9:16",
            "mood": scene.emotion,
        }

    @staticmethod
    def _save_json(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")


def create_agent() -> PromptEngineerAgent:
    """Factory used by FileSystemAgentRegistry."""

    return PromptEngineerAgent()
