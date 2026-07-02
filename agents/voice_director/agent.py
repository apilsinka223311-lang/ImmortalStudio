"""Deterministic local Voice Director agent."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.models.production import ProductionTask
from core.pipeline.agents import AgentExecutionContext, AgentResult


@dataclass(frozen=True)
class VoicePlan:
    """Planned voice artifact for one scene."""

    scene_id: str
    scene_title: str
    source_voice_prompt: str
    planned_output_file: str
    plan_path: Path


class VoiceDirectorAgent:
    """Creates deterministic voice planning artifacts without generating audio."""

    agent_id = "voice_director"
    version = "voice_director_v1"

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, task: ProductionTask, context: AgentExecutionContext) -> AgentResult:
        """Create voice plan JSON files from script, prompts and image manifest."""

        script_path = context.output_directory / "episode_script.md"
        prompts_path = context.output_directory / "scene_prompts.json"
        image_manifest_path = context.output_directory / "images" / "image_manifest.json"
        voice_directory = context.output_directory / "voice"

        missing_result = self._missing_input_result(script_path, prompts_path, image_manifest_path)
        if missing_result is not None:
            return missing_result

        episode_script = script_path.read_text(encoding="utf-8")
        prompt_package = self._load_json(prompts_path)
        image_manifest = self._load_json(image_manifest_path)
        voice_plans = self._build_voice_plans(prompt_package, voice_directory)

        voice_directory.mkdir(parents=True, exist_ok=True)
        for plan in voice_plans:
            self._save_json(
                plan.plan_path,
                self._voice_plan_payload(plan, prompt_package, episode_script),
            )

        manifest_path = voice_directory / "voice_manifest.json"
        manifest = self._manifest_payload(
            task=task,
            prompt_package=prompt_package,
            image_manifest=image_manifest,
            script_path=script_path,
            prompts_path=prompts_path,
            image_manifest_path=image_manifest_path,
            voice_plans=voice_plans,
        )
        self._save_json(manifest_path, manifest)

        self.logger.info("Voice Director created voice manifest: %s", manifest_path)
        return AgentResult(
            success=True,
            status="voice_plans_created",
            message="Voice Director created deterministic voice planning artifacts.",
            output_path=manifest_path,
            metadata={
                "source_episode_script": script_path.as_posix(),
                "source_scene_prompts": prompts_path.as_posix(),
                "source_image_manifest": image_manifest_path.as_posix(),
                "voice_manifest": manifest_path.as_posix(),
                "scene_count": len(voice_plans),
                "audio_status": "planned_not_generated",
            },
        )

    def _missing_input_result(
        self,
        script_path: Path,
        prompts_path: Path,
        image_manifest_path: Path,
    ) -> AgentResult | None:
        required_paths = (script_path, prompts_path, image_manifest_path)
        for path in required_paths:
            if not path.is_file():
                message = f"Required Voice Director input is missing: {path}"
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

    def _build_voice_plans(
        self,
        prompt_package: dict[str, Any],
        voice_directory: Path,
    ) -> list[VoicePlan]:
        prompts = prompt_package.get("prompts") or prompt_package.get("scenes") or []
        plans: list[VoicePlan] = []

        for index, scene_prompt in enumerate(prompts, start=1):
            scene_id = str(scene_prompt.get("scene_id") or f"scene_{index:03d}")
            scene_title = str(scene_prompt.get("scene_title") or f"Scene {index}")
            planned_output_file = str(
                scene_prompt.get("output_targets", {}).get("voice") or f"voice/{scene_id}.wav"
            )
            plans.append(
                VoicePlan(
                    scene_id=scene_id,
                    scene_title=scene_title,
                    source_voice_prompt=str(scene_prompt.get("voice_prompt") or ""),
                    planned_output_file=planned_output_file,
                    plan_path=voice_directory / f"{scene_id}.json",
                )
            )
        return plans

    def _voice_plan_payload(
        self,
        plan: VoicePlan,
        prompt_package: dict[str, Any],
        episode_script: str,
    ) -> dict[str, Any]:
        scene_prompt = self._find_scene_prompt(prompt_package, plan.scene_id)
        emotion = str(scene_prompt.get("mood") or "focused")
        script_context = self._script_context(episode_script, plan.scene_id)

        return {
            "scene_id": plan.scene_id,
            "scene_title": plan.scene_title,
            "source_voice_prompt": plan.source_voice_prompt,
            "narration_plan": {
                "narrator_tone": "clear cinematic narrator",
                "pacing": self._pacing_for_emotion(emotion),
                "emotion": emotion,
                "line_purpose": "Support the scene story beat without adding new plot facts.",
                "scene_context": script_context,
            },
            "dialogue_plan": self._dialogue_plan(scene_prompt, emotion),
            "voice_style": {
                "narrator": "consistent, warm, cinematic, readable for short-form video",
                "characters": "distinct but restrained voices based on scene emotion",
            },
            "pacing": self._pacing_for_emotion(emotion),
            "emotion": emotion,
            "planned_output_file": plan.planned_output_file,
            "audio_status": "planned_not_generated",
            "continuity_notes": [
                "Keep narrator voice consistent across all scenes.",
                "Keep recurring character voices consistent across the episode.",
                "Avoid sudden accent, age, pitch, or tone changes unless the script explicitly requires them.",
            ],
            "generation_notes": [
                "No audio was generated by this deterministic Voice Director.",
                "This file is a future voice generation plan.",
                "Do not treat planned_output_file as an existing audio asset.",
            ],
            "metadata": {
                "source_scene_id": plan.scene_id,
                "source_prompt_style_version": prompt_package.get("prompt_style_version"),
                "subtitle_prompt": scene_prompt.get("subtitle_prompt"),
                "sound_effects_prompt": scene_prompt.get("sound_effects_prompt"),
            },
        }

    @staticmethod
    def _dialogue_plan(scene_prompt: dict[str, Any], emotion: str) -> list[dict[str, str]]:
        character_references = scene_prompt.get("character_references") or []
        if not character_references:
            return [
                {
                    "character_name": "narrator",
                    "intended_emotion": emotion,
                    "delivery_style": "measured and cinematic",
                    "placeholder_line": "Continue the scene beat with clear narration.",
                }
            ]

        dialogue: list[dict[str, str]] = []
        for character in character_references:
            character_id = str(character.get("character_id") or "character")
            dialogue.append(
                {
                    "character_name": character_id,
                    "intended_emotion": emotion,
                    "delivery_style": "natural, concise, and consistent with established character identity",
                    "placeholder_line": f"{character_id} reacts to the scene with {emotion} energy.",
                }
            )
        return dialogue

    @staticmethod
    def _pacing_for_emotion(emotion: str) -> str:
        lowered = emotion.lower()
        if any(word in lowered for word in ("awe", "mystery", "uncertainty", "nervous")):
            return "slow, spacious, and suspenseful"
        if any(word in lowered for word in ("action", "fear", "urgent", "danger")):
            return "fast but clearly articulated"
        return "medium pace with clear pauses"

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

    def _manifest_payload(
        self,
        task: ProductionTask,
        prompt_package: dict[str, Any],
        image_manifest: dict[str, Any],
        script_path: Path,
        prompts_path: Path,
        image_manifest_path: Path,
        voice_plans: list[VoicePlan],
    ) -> dict[str, Any]:
        return {
            "project": prompt_package.get("project") or task.project,
            "episode": prompt_package.get("episode") or task.episode,
            "task_id": task.task_id,
            "voice_director_version": self.version,
            "source_episode_script": script_path.as_posix(),
            "source_scene_prompts": prompts_path.as_posix(),
            "source_image_manifest": image_manifest_path.as_posix(),
            "total_scenes": len(voice_plans),
            "audio_status": "planned_not_generated",
            "scenes": [
                {
                    "scene_id": plan.scene_id,
                    "scene_title": plan.scene_title,
                    "plan_file": plan.plan_path.relative_to(script_path.parent).as_posix(),
                    "planned_output_file": plan.planned_output_file,
                    "audio_status": "planned_not_generated",
                }
                for plan in voice_plans
            ],
            "validation_notes": [
                "Voice Director produced JSON planning artifacts only.",
                "No real audio was generated.",
                "No placeholder WAV or MP3 files were created.",
                "Each scene prompt has a corresponding voice plan JSON file.",
            ],
            "metadata": {
                "prompt_style_version": prompt_package.get("prompt_style_version"),
                "source_scene_count": len(prompt_package.get("prompts") or prompt_package.get("scenes") or []),
                "source_image_status": image_manifest.get("image_status"),
            },
        }

    @staticmethod
    def _save_json(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")


def create_agent() -> VoiceDirectorAgent:
    """Factory used by FileSystemAgentRegistry."""

    return VoiceDirectorAgent()
