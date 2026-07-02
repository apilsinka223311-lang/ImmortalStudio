"""Deterministic local Story Architect agent."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.models.production import ProductionTask
from core.pipeline.agents import AgentExecutionContext, AgentResult


@dataclass(frozen=True)
class StorySeed:
    """Normalized inputs used to build a minimal episode plan."""

    project_id: str
    episode_id: str
    idea: str
    language: str
    platform: str
    duration_seconds: int
    episode_goal: str
    genre: str
    tone: str


class StoryArchitectAgent:
    """Creates a deterministic `episode_plan.json` for the first pipeline slice."""

    agent_id = "story_architect"

    def __init__(self, logger: logging.Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)

    def execute(self, task: ProductionTask, context: AgentExecutionContext) -> AgentResult:
        """Create an episode plan from the production task and context."""

        output_path = context.output_directory / "episode_plan.json"
        seed = self._build_seed(task)
        episode_plan = self._build_episode_plan(seed, task, context)
        self._save_json(output_path, episode_plan)

        self.logger.info("Story Architect created episode plan: %s", output_path)
        return AgentResult(
            success=True,
            status="episode_plan_created",
            message="Story Architect created episode_plan.json.",
            output_path=output_path,
            metadata={
                "schema_version": episode_plan["schema_version"],
                "scene_count": len(episode_plan["scenes"]),
            },
        )

    def _build_seed(self, task: ProductionTask) -> StorySeed:
        metadata = task.metadata
        duration = metadata.get("duration_seconds") or 60
        episode_goal = metadata.get("episode_goal") or "Create a clear short episode plan from the idea."

        return StorySeed(
            project_id=str(metadata.get("project_id") or self._safe_identifier(task.project)),
            episode_id=self._safe_identifier(task.episode),
            idea=task.idea.strip(),
            language=task.language,
            platform=task.platform,
            duration_seconds=int(duration),
            episode_goal=str(episode_goal),
            genre=str(metadata.get("genre") or "fantasy adventure"),
            tone=str(metadata.get("tone") or "cinematic, mysterious, character-driven"),
        )

    def _build_episode_plan(
        self,
        seed: StorySeed,
        task: ProductionTask,
        context: AgentExecutionContext,
    ) -> dict[str, Any]:
        title = self._build_title(seed.idea)
        scenes = self._build_scenes(seed)
        synopsis = self._build_synopsis(seed.idea)

        return {
            "schema_version": "1.0",
            "pipeline_version": str(task.metadata.get("pipeline_version") or "1.0"),
            "project_id": seed.project_id,
            "project": task.project,
            "episode_id": seed.episode_id,
            "episode": task.episode,
            "title": title,
            "summary": synopsis,
            "language": seed.language,
            "target_platform": seed.platform,
            "platform": seed.platform,
            "target_duration_seconds": seed.duration_seconds,
            "episode_goal": seed.episode_goal,
            "genre": seed.genre,
            "tone": seed.tone,
            "hook": self._build_hook(seed.idea),
            "logline": self._build_logline(seed.idea),
            "synopsis": synopsis,
            "story_structure": {
                "setup": scenes[0]["summary"],
                "conflict": scenes[1]["summary"],
                "turning_point": scenes[1]["description"],
                "resolution": scenes[2]["summary"],
            },
            "emotional_curve": ["curiosity", "tension", "wonder", "anticipation"],
            "scenes": scenes,
            "continuity_notes": self._build_continuity_notes(task, context),
            "required_assets": self._build_required_assets(scenes),
            "validation_notes": [
                "Generated locally without external AI providers.",
                "Scene ids are sequential.",
                "Scene durations sum to the target duration.",
                "No provider-specific prompt syntax is included.",
            ],
            "validation_status": "draft",
        }

    def _build_scenes(self, seed: StorySeed) -> list[dict[str, Any]]:
        durations = self._split_duration(seed.duration_seconds, 3)
        idea = seed.idea.rstrip(".")
        return [
            {
                "scene_id": "scene_001",
                "order": 1,
                "title": "Opening Image",
                "purpose": "Establish the situation and make the viewer understand the core idea quickly.",
                "summary": f"The episode opens with the central premise: {idea}.",
                "description": f"A clear opening scene introduces the world, the main situation, and the visual promise of: {idea}.",
                "location_id": "primary_location",
                "location": "Primary story location",
                "character_ids": ["protagonist"],
                "characters": ["protagonist"],
                "emotion": "curiosity",
                "emotional_beat": "curiosity",
                "visual_focus": "Readable character silhouette, strong environment framing, immediate story hook.",
                "estimated_duration_seconds": durations[0],
                "story_function": "setup",
                "next_scene_transition": "Cut from discovery into immediate complication.",
            },
            {
                "scene_id": "scene_002",
                "order": 2,
                "title": "Complication",
                "purpose": "Create pressure and reveal why the idea matters.",
                "summary": "The protagonist faces a sudden obstacle that forces action instead of observation.",
                "description": "The situation escalates, making the protagonist react under pressure while the core mystery becomes more visible.",
                "location_id": "primary_location",
                "location": "Primary story location",
                "character_ids": ["protagonist"],
                "characters": ["protagonist"],
                "emotion": "tension",
                "emotional_beat": "tension",
                "visual_focus": "Character reaction, visible stakes, focused cinematic composition.",
                "estimated_duration_seconds": durations[1],
                "story_function": "turning_point",
                "next_scene_transition": "Move from escalation into a short resolution with a future hook.",
            },
            {
                "scene_id": "scene_003",
                "order": 3,
                "title": "Aftermath Hook",
                "purpose": "Resolve the moment while creating momentum for the next episode.",
                "summary": "The immediate event resolves, but the final image suggests a larger story has just begun.",
                "description": "The protagonist understands that the event was not random, ending on a clean visual question for the audience.",
                "location_id": "primary_location",
                "location": "Primary story location",
                "character_ids": ["protagonist"],
                "characters": ["protagonist"],
                "emotion": "anticipation",
                "emotional_beat": "anticipation",
                "visual_focus": "Memorable final frame, clear emotional reaction, simple mystery beat.",
                "estimated_duration_seconds": durations[2],
                "story_function": "resolution",
                "next_scene_transition": "End episode.",
            },
        ]

    @staticmethod
    def _split_duration(total_duration: int, scene_count: int) -> list[int]:
        base = max(total_duration, scene_count) // scene_count
        durations = [base for _ in range(scene_count)]
        durations[-1] += max(total_duration, scene_count) - sum(durations)
        return durations

    @staticmethod
    def _build_title(idea: str) -> str:
        words = [word.strip(".,:;!?") for word in idea.split() if word.strip(".,:;!?")]
        if not words:
            return "Untitled Episode"
        return " ".join(words[:5]).title()

    @staticmethod
    def _build_hook(idea: str) -> str:
        return f"What changes when {idea.strip().rstrip('.')}?"

    @staticmethod
    def _build_logline(idea: str) -> str:
        return f"A short animated episode about {idea.strip().rstrip('.')}."

    @staticmethod
    def _build_synopsis(idea: str) -> str:
        return (
            f"The episode introduces the premise '{idea.strip().rstrip('.')}', "
            "then turns it into a simple three-scene arc with a clear setup, complication, and future hook."
        )

    @staticmethod
    def _build_continuity_notes(
        task: ProductionTask,
        context: AgentExecutionContext,
    ) -> list[str]:
        notes = [
            "Preserve project world rules and character memory loaded by Studio Director.",
            "Do not invent permanent lore facts without later memory updates.",
            "Keep the episode understandable as a short first-pipeline vertical slice.",
        ]
        memory_summary = context.metadata.get("memory_summary", {})
        notes.append(f"Loaded memory summary: {memory_summary}.")
        if task.metadata.get("world"):
            notes.append(f"Requested world context: {task.metadata['world']}.")
        return notes

    @staticmethod
    def _build_required_assets(scenes: list[dict[str, Any]]) -> list[dict[str, str]]:
        return [
            {
                "asset_id": f"{scene['scene_id']}_image",
                "type": "image",
                "description": f"Static illustration for {scene['title']}.",
            }
            for scene in scenes
        ]

    @staticmethod
    def _save_json(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")

    @staticmethod
    def _safe_identifier(value: str) -> str:
        chars: list[str] = []
        for char in value:
            if char.isalnum():
                chars.append(char.lower())
            elif chars and chars[-1] != "_":
                chars.append("_")
        return "".join(chars).strip("_") or "episode"


def create_agent() -> StoryArchitectAgent:
    """Factory used by FileSystemAgentRegistry."""

    return StoryArchitectAgent()
