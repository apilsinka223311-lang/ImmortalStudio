"""Smoke check for loading approved creative memory canon at runtime."""

from __future__ import annotations

import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core import ProductionRequest, create_default_director  # noqa: E402


def main() -> None:
    """Run the local pipeline and verify approved canon reaches memory context."""

    director = create_default_director(ROOT)
    task = director.start_production(
        ProductionRequest(
            project="ImmortalAcademy",
            episode="episode_approved_memory_canon_smoke",
            idea="Lin Mo wakes during public humiliation and The Origin System activates.",
            language="English",
            platform="YouTube Shorts",
            episode_goal="Verify approved creative memory canon loading.",
            duration_seconds=60,
        )
    )

    try:
        task_path = task.output_directory / "production_task.json"
        plan_path = task.output_directory / "episode_plan.json"
        prompts_path = task.output_directory / "scene_prompts.json"

        production_task = json.loads(task_path.read_text(encoding="utf-8"))
        episode_plan = json.loads(plan_path.read_text(encoding="utf-8"))
        scene_prompts = json.loads(prompts_path.read_text(encoding="utf-8"))

        memory_context = production_task["metadata"]["memory_context"]
        world_text = _joined_excerpts(memory_context["world"])
        character_text = _joined_excerpts(memory_context["characters"])
        prompt_text = _joined_excerpts(memory_context["prompts"])

        assert "memory/world/world_overview.md" in _joined_paths(memory_context["world"])
        assert "memory/characters/lin_mo.md" in _joined_paths(memory_context["characters"])
        assert "memory/prompts/story_rules.md" in _joined_paths(memory_context["prompts"])
        assert "The Origin System" in world_text
        assert "Fallen Star Realm" in world_text
        assert "Lin Mo" in character_text
        assert "The Origin System has no shop" in prompt_text

        plan_references = episode_plan["memory_references"]
        plan_world_text = _joined_excerpts(plan_references["world"])
        plan_character_text = _joined_excerpts(plan_references["characters"])
        assert "The Origin System" in plan_world_text
        assert "Lin Mo" in plan_character_text
        assert any("memory/world/world_overview.md" in note for note in episode_plan["continuity_notes"])
        assert any("memory/characters/lin_mo.md" in note for note in episode_plan["continuity_notes"])

        prompt_references = scene_prompts["memory_references"]
        prompt_world_text = _joined_excerpts(prompt_references["world"])
        prompt_character_text = _joined_excerpts(prompt_references["characters"])
        prompt_rules_text = _joined_excerpts(prompt_references["prompts"])
        first_prompt = scene_prompts["prompts"][0]

        assert "Fallen Star Realm" in prompt_world_text
        assert "Lin Mo" in prompt_character_text
        assert "The Origin System has no shop" in prompt_rules_text
        assert "Memory context:" in first_prompt["image_prompt"]
        assert any("memory/world/world_overview.md" in note for note in first_prompt["visual_continuity_notes"])
        assert any("memory/characters/lin_mo.md" in note for note in first_prompt["character_continuity_notes"])
        assert production_task["status"] == "completed"
        assert not list(ROOT.rglob("__pycache__")), "__pycache__ directories must not remain."
    finally:
        logging.shutdown()
        _cleanup_task_directory(task.output_directory)


def _joined_excerpts(entries: list[dict[str, Any]]) -> str:
    return "\n".join(str(entry.get("excerpt", "")) for entry in entries)


def _joined_paths(entries: list[dict[str, Any]]) -> str:
    return "\n".join(str(entry.get("path", "")) for entry in entries)


def _cleanup_task_directory(output_directory: Path) -> None:
    tasks_root = ROOT / "projects" / "ImmortalAcademy" / "production" / "tasks"
    resolved_output = output_directory.resolve()
    resolved_tasks_root = tasks_root.resolve()

    if resolved_tasks_root not in resolved_output.parents:
        raise RuntimeError(f"Refusing to clean path outside tasks root: {resolved_output}")

    shutil.rmtree(resolved_output)

    episode_dir = resolved_output.parent
    if episode_dir.exists() and not any(episode_dir.iterdir()):
        episode_dir.rmdir()

    if tasks_root.exists() and not any(tasks_root.iterdir()):
        tasks_root.rmdir()


if __name__ == "__main__":
    main()
    print("smoke_approved_memory_canon_loading_ok")
