"""Smoke check for the Prompt Engineer pipeline transition."""

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


def main() -> None:
    """Run a local pipeline smoke check and clean generated artifacts."""

    director = create_default_director(ROOT)
    task = director.start_production(
        ProductionRequest(
            project="ImmortalAcademy",
            episode="episode_prompt_smoke",
            idea="A new disciple awakens an ancient sword.",
            language="English",
            platform="YouTube Shorts",
            episode_goal="Verify the Prompt Engineer pipeline transition.",
            duration_seconds=60,
        )
    )

    try:
        task_path = task.output_directory / "production_task.json"
        plan_path = task.output_directory / "episode_plan.json"
        script_path = task.output_directory / "episode_script.md"
        prompts_path = task.output_directory / "scene_prompts.json"
        assert task_path.is_file(), f"Missing production task: {task_path}"
        assert plan_path.is_file(), f"Missing episode plan: {plan_path}"
        assert script_path.is_file(), f"Missing episode script: {script_path}"
        assert prompts_path.is_file(), f"Missing scene prompts: {prompts_path}"

        production_task = json.loads(task_path.read_text(encoding="utf-8"))
        scene_prompts = json.loads(prompts_path.read_text(encoding="utf-8"))

        assert "story_architect" in production_task["completed_stages"]
        assert "script_writer" in production_task["completed_stages"]
        assert "prompt_engineer" in production_task["completed_stages"]
        assert "prompt_engineer" not in production_task["pending_stages"]
        assert "voice_director" in production_task["completed_stages"]
        assert "video_editor" in production_task["completed_stages"]
        assert "analytics" in production_task["completed_stages"]
        assert "publisher" in production_task["completed_stages"]
        assert production_task["current_stage"] == "completed"
        assert production_task["status"] == "completed"
        assert "prompt_engineer" in production_task["metadata"]["stage_results"]
        assert scene_prompts["schema_version"] == "1.0"
        assert scene_prompts["project"] == "ImmortalAcademy"
        assert scene_prompts["episode"] == "episode_prompt_smoke"
        assert scene_prompts["source_episode_plan"].endswith("episode_plan.json")
        assert scene_prompts["source_episode_script"].endswith("episode_script.md")
        assert scene_prompts["prompts"]
        assert scene_prompts["scenes"] == scene_prompts["prompts"]

        first_prompt = scene_prompts["prompts"][0]
        required_fields = {
            "scene_id",
            "scene_title",
            "image_prompt",
            "negative_prompt",
            "animation_prompt",
            "voice_prompt",
            "music_prompt",
            "sound_effects_prompt",
            "subtitle_prompt",
            "visual_continuity_notes",
            "character_continuity_notes",
            "output_targets",
        }
        assert required_fields.issubset(first_prompt.keys())
    finally:
        logging.shutdown()
        _cleanup_task_directory(task.output_directory)


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
    print("smoke_prompt_engineer_ok")
