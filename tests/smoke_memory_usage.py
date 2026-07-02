"""Smoke check for practical world and character memory usage."""

from __future__ import annotations

import json
import logging
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core import ProductionRequest, create_default_director  # noqa: E402


WORLD_MEMORY = ROOT / "projects" / "ImmortalAcademy" / "world" / "world.md"
CHARACTER_MEMORY = ROOT / "projects" / "ImmortalAcademy" / "characters" / "protagonist.md"


def main() -> None:
    """Run the local pipeline with temporary memory content and clean artifacts."""

    original_world = WORLD_MEMORY.read_text(encoding="utf-8")
    original_character = CHARACTER_MEMORY.read_text(encoding="utf-8")
    task_output_directory: Path | None = None

    try:
        WORLD_MEMORY.write_text(
            "Immortal Academy is a floating mountain school where ancient swords react to spiritual discipline.",
            encoding="utf-8",
        )
        CHARACTER_MEMORY.write_text(
            "The protagonist is a cautious new disciple with a calm voice and a hidden talent for sword resonance.",
            encoding="utf-8",
        )

        director = create_default_director(ROOT)
        task = director.start_production(
            ProductionRequest(
                project="ImmortalAcademy",
                episode="episode_memory_smoke",
                idea="A new disciple awakens an ancient sword.",
                language="English",
                platform="YouTube Shorts",
                episode_goal="Verify practical world and character memory usage.",
                duration_seconds=60,
            )
        )
        task_output_directory = task.output_directory

        task_path = task.output_directory / "production_task.json"
        plan_path = task.output_directory / "episode_plan.json"
        prompts_path = task.output_directory / "scene_prompts.json"

        production_task = json.loads(task_path.read_text(encoding="utf-8"))
        episode_plan = json.loads(plan_path.read_text(encoding="utf-8"))
        scene_prompts = json.loads(prompts_path.read_text(encoding="utf-8"))

        memory_context = production_task["metadata"]["memory_context"]
        assert memory_context["summary"]["world_non_empty_files"] >= 1
        assert memory_context["summary"]["character_non_empty_files"] >= 1
        assert memory_context["world"][0]["path"] == "world.md"
        assert memory_context["characters"][0]["path"] == "protagonist.md"

        memory_references = episode_plan["memory_references"]
        assert memory_references["world"][0]["path"] == "world.md"
        assert memory_references["characters"][0]["path"] == "protagonist.md"
        assert any("world.md" in note for note in episode_plan["continuity_notes"])
        assert any("protagonist.md" in note for note in episode_plan["continuity_notes"])

        first_prompt = scene_prompts["prompts"][0]
        assert scene_prompts["memory_references"]["world"][0]["path"] == "world.md"
        assert "Memory context:" in first_prompt["image_prompt"]
        assert any("world.md" in note for note in first_prompt["visual_continuity_notes"])
        assert any("protagonist.md" in note for note in first_prompt["character_continuity_notes"])
        assert production_task["status"] == "completed"
        assert not list(ROOT.rglob("__pycache__")), "__pycache__ directories must not remain."
    finally:
        logging.shutdown()
        WORLD_MEMORY.write_text(original_world, encoding="utf-8")
        CHARACTER_MEMORY.write_text(original_character, encoding="utf-8")
        if task_output_directory is not None:
            _cleanup_task_directory(task_output_directory)


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
    print("smoke_memory_usage_ok")
