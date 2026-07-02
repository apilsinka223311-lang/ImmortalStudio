"""Smoke check for the deterministic Image Director pipeline transition."""

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
    """Run the pipeline through Image Director and clean generated artifacts."""

    director = create_default_director(ROOT)
    task = director.start_production(
        ProductionRequest(
            project="ImmortalAcademy",
            episode="episode_image_smoke",
            idea="A new disciple awakens an ancient sword.",
            language="English",
            platform="YouTube Shorts",
            episode_goal="Verify the Image Director planning transition.",
            duration_seconds=60,
        )
    )

    try:
        task_path = task.output_directory / "production_task.json"
        prompts_path = task.output_directory / "scene_prompts.json"
        images_dir = task.output_directory / "images"
        manifest_path = images_dir / "image_manifest.json"

        assert task_path.is_file(), f"Missing production task: {task_path}"
        assert prompts_path.is_file(), f"Missing scene prompts: {prompts_path}"
        assert images_dir.is_dir(), f"Missing images directory: {images_dir}"
        assert manifest_path.is_file(), f"Missing image manifest: {manifest_path}"
        assert not list(images_dir.glob("*.png")), "Image Director must not create fake PNG files."

        production_task = json.loads(task_path.read_text(encoding="utf-8"))
        scene_prompts = json.loads(prompts_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        assert "story_architect" in production_task["completed_stages"]
        assert "script_writer" in production_task["completed_stages"]
        assert "prompt_engineer" in production_task["completed_stages"]
        assert "image_director" in production_task["completed_stages"]
        assert "image_director" not in production_task["pending_stages"]
        assert "voice_director" in production_task["completed_stages"]
        assert "video_editor" in production_task["completed_stages"]
        assert production_task["current_stage"] == "analytics"
        assert production_task["status"] == "Waiting for Analytics implementation."
        assert "image_director" in production_task["metadata"]["stage_results"]

        scene_count = len(scene_prompts["prompts"])
        assert manifest["image_status"] == "planned_not_generated"
        assert manifest["total_scenes"] == scene_count
        assert manifest["source_scene_prompts"].endswith("scene_prompts.json")

        plan_files = sorted(images_dir.glob("scene_*.json"))
        assert len(plan_files) == scene_count
        for plan_file in plan_files:
            plan = json.loads(plan_file.read_text(encoding="utf-8"))
            assert plan["image_status"] == "planned_not_generated"
            assert plan["planned_output_file"].endswith(".png")
            assert plan["source_prompt"]
            assert "metadata" in plan
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
    print("smoke_image_director_ok")
