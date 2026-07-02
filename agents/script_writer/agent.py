"""Deterministic local Script Writer agent."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.models.production import ProductionTask
from core.pipeline.agents import AgentExecutionContext, AgentResult


@dataclass(frozen=True)
class ScriptScene:
    """Normalized scene data used to render the Markdown screenplay."""

    scene_id: str
    order: int
    title: str
    duration_seconds: int
    location: str
    characters: list[str]
    visual_description: str
    narration: str
    dialogue: list[str]
    camera_direction: str
    sound_direction: str
    transition: str


class ScriptWriterAgent:
    """Converts `episode_plan.json` into a deterministic `episode_script.md`."""

    agent_id = "script_writer"

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, task: ProductionTask, context: AgentExecutionContext) -> AgentResult:
        """Create an episode script from the current production task."""

        plan_path = context.output_directory / "episode_plan.json"
        script_path = context.output_directory / "episode_script.md"

        if not plan_path.is_file():
            message = f"episode_plan.json is missing: {plan_path}"
            self.logger.error(message)
            return AgentResult(
                success=False,
                status="missing_input",
                message=message,
                metadata={"missing_file": plan_path.as_posix()},
            )

        episode_plan = self._load_episode_plan(plan_path)
        scenes = self._build_scenes(episode_plan)
        script = self._render_script(task, episode_plan, scenes)
        script_path.write_text(script, encoding="utf-8")

        self.logger.info("Script Writer created episode script: %s", script_path)
        return AgentResult(
            success=True,
            status="episode_script_created",
            message="Script Writer created episode_script.md.",
            output_path=script_path,
            metadata={
                "source_plan": plan_path.as_posix(),
                "scene_count": len(scenes),
                "schema_version": "1.0",
            },
        )

    @staticmethod
    def _load_episode_plan(plan_path: Path) -> dict[str, Any]:
        with plan_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _build_scenes(self, episode_plan: dict[str, Any]) -> list[ScriptScene]:
        scenes: list[ScriptScene] = []
        for index, scene in enumerate(episode_plan.get("scenes", []), start=1):
            scene_id = str(scene.get("scene_id") or f"scene_{index:03d}")
            title = str(scene.get("title") or scene.get("heading") or f"Scene {index}")
            location = str(scene.get("location") or scene.get("location_id") or "unspecified_location")
            characters = self._normalize_characters(scene)
            description = str(
                scene.get("description")
                or scene.get("summary")
                or "The scene advances the episode plan with a clear visual beat."
            )
            emotion = str(scene.get("emotion") or scene.get("emotional_beat") or "focused")

            scenes.append(
                ScriptScene(
                    scene_id=scene_id,
                    order=int(scene.get("order") or index),
                    title=title,
                    duration_seconds=int(scene.get("estimated_duration_seconds") or 10),
                    location=location,
                    characters=characters,
                    visual_description=description,
                    narration=self._build_narration(scene, episode_plan),
                    dialogue=self._build_dialogue(scene, characters, emotion),
                    camera_direction=self._build_camera_direction(scene),
                    sound_direction=self._build_sound_direction(scene, emotion),
                    transition=str(scene.get("next_scene_transition") or "Cut to the next scene."),
                )
            )
        return scenes

    @staticmethod
    def _normalize_characters(scene: dict[str, Any]) -> list[str]:
        raw_characters = scene.get("characters") or scene.get("character_ids") or ["protagonist"]
        return [str(character) for character in raw_characters]

    @staticmethod
    def _build_narration(scene: dict[str, Any], episode_plan: dict[str, Any]) -> str:
        summary = str(scene.get("summary") or scene.get("description") or "")
        if summary:
            return summary
        return str(episode_plan.get("logline") or "The story continues through a clear cinematic beat.")

    @staticmethod
    def _build_dialogue(scene: dict[str, Any], characters: list[str], emotion: str) -> list[str]:
        speaker = characters[0] if characters else "protagonist"
        purpose = str(scene.get("purpose") or "move the story forward")
        return [
            f"{speaker}: \"I can feel this moment changing everything.\"",
            f"{speaker}: \"I have to {purpose.lower()}.\"",
            f"Direction: Deliver these lines with {emotion}."
        ]

    @staticmethod
    def _build_camera_direction(scene: dict[str, Any]) -> str:
        visual_focus = str(scene.get("visual_focus") or "the main character and the core action")
        return f"Use a stable cinematic shot focused on {visual_focus}."

    @staticmethod
    def _build_sound_direction(scene: dict[str, Any], emotion: str) -> str:
        return (
            f"Use restrained sound design that supports {emotion}. "
            "Keep narration and dialogue clear."
        )

    def _render_script(
        self,
        task: ProductionTask,
        episode_plan: dict[str, Any],
        scenes: list[ScriptScene],
    ) -> str:
        title = str(episode_plan.get("title") or "Untitled Episode")
        language = str(episode_plan.get("language") or task.language)
        platform = str(episode_plan.get("target_platform") or episode_plan.get("platform") or task.platform)
        duration = int(episode_plan.get("target_duration_seconds") or task.metadata.get("duration_seconds") or 60)
        continuity_notes = episode_plan.get("continuity_notes") or []

        lines = [
            f"# {title}",
            "",
            "## Metadata",
            "",
            "- Schema Version: 1.0",
            f"- Pipeline Version: {episode_plan.get('pipeline_version', '1.0')}",
            f"- Project: {episode_plan.get('project', task.project)}",
            f"- Project ID: {episode_plan.get('project_id', task.metadata.get('project_id', 'unknown'))}",
            f"- Episode: {episode_plan.get('episode', task.episode)}",
            f"- Episode ID: {episode_plan.get('episode_id', task.episode)}",
            f"- Source Episode Plan ID: {episode_plan.get('episode_id', task.episode)}",
            f"- Language: {language}",
            f"- Platform: {platform}",
            f"- Target Duration Seconds: {duration}",
            f"- Validation Status: draft",
            "",
            "## Logline",
            "",
            str(episode_plan.get("logline") or episode_plan.get("summary") or "No logline provided."),
            "",
            "## Scene Breakdown",
            "",
        ]

        for scene in scenes:
            lines.extend(self._render_scene(scene))

        lines.extend(
            [
                "## Continuity Notes",
                "",
                *[f"- {note}" for note in continuity_notes],
                "",
                "## Script Writer Validation Notes",
                "",
                "- Generated locally without external AI providers.",
                "- Every script scene maps to one episode plan scene.",
                "- Markdown is structured for deterministic parsing by future tools.",
                "",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _render_scene(scene: ScriptScene) -> list[str]:
        dialogue_lines = [f"- {line}" for line in scene.dialogue]
        return [
            f"### Scene {scene.order}: {scene.title}",
            "",
            f"- Scene ID: {scene.scene_id}",
            f"- Estimated Duration Seconds: {scene.duration_seconds}",
            f"- Location: {scene.location}",
            f"- Characters: {', '.join(scene.characters)}",
            "",
            "#### Visual Description",
            "",
            scene.visual_description,
            "",
            "#### Narration",
            "",
            scene.narration,
            "",
            "#### Dialogue",
            "",
            *dialogue_lines,
            "",
            "#### Camera Direction",
            "",
            scene.camera_direction,
            "",
            "#### Sound Direction",
            "",
            scene.sound_direction,
            "",
            "#### Transition To Next Scene",
            "",
            scene.transition,
            "",
        ]


def create_agent() -> ScriptWriterAgent:
    """Factory used by FileSystemAgentRegistry."""

    return ScriptWriterAgent()
