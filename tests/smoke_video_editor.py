"""Smoke check for the deterministic Video Editor pipeline transition."""

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
    """Run the pipeline through Video Editor and clean generated artifacts."""

    director = create_default_director(ROOT)
    task = director.start_production(
        ProductionRequest(
            project="ImmortalAcademy",
            episode="episode_video_smoke",
            idea="A new disciple awakens an ancient sword.",
            language="English",
            platform="YouTube Shorts",
            episode_goal="Verify the Video Editor planning transition.",
            duration_seconds=60,
        )
    )

    try:
        task_path = task.output_directory / "production_task.json"
        script_path = task.output_directory / "episode_script.md"
        prompts_path = task.output_directory / "scene_prompts.json"
        image_manifest_path = task.output_directory / "images" / "image_manifest.json"
        voice_manifest_path = task.output_directory / "voice" / "voice_manifest.json"
        video_dir = task.output_directory / "video"
        video_manifest_path = video_dir / "video_manifest.json"

        assert task_path.is_file(), f"Missing production task: {task_path}"
        assert script_path.is_file(), f"Missing episode script: {script_path}"
        assert prompts_path.is_file(), f"Missing scene prompts: {prompts_path}"
        assert image_manifest_path.is_file(), f"Missing image manifest: {image_manifest_path}"
        assert voice_manifest_path.is_file(), f"Missing voice manifest: {voice_manifest_path}"
        assert video_dir.is_dir(), f"Missing video directory: {video_dir}"
        assert video_manifest_path.is_file(), f"Missing video manifest: {video_manifest_path}"
        assert not list(video_dir.glob("*.mp4")), "Video Editor must not create fake MP4 files."
        assert not list(video_dir.glob("*.mov")), "Video Editor must not create fake MOV files."

        production_task = json.loads(task_path.read_text(encoding="utf-8"))
        scene_prompts = json.loads(prompts_path.read_text(encoding="utf-8"))
        video_manifest = json.loads(video_manifest_path.read_text(encoding="utf-8"))

        assert "story_architect" in production_task["completed_stages"]
        assert "script_writer" in production_task["completed_stages"]
        assert "prompt_engineer" in production_task["completed_stages"]
        assert "image_director" in production_task["completed_stages"]
        assert "voice_director" in production_task["completed_stages"]
        assert "video_editor" in production_task["completed_stages"]
        assert "video_editor" not in production_task["pending_stages"]
        assert "analytics" in production_task["completed_stages"]
        assert "publisher" in production_task["completed_stages"]
        assert production_task["current_stage"] == "completed"
        assert production_task["status"] == "completed"
        assert "video_editor" in production_task["metadata"]["stage_results"]

        scene_count = len(scene_prompts["prompts"])
        assert video_manifest["render_status"] == "planned_not_rendered"
        assert video_manifest["total_scenes"] == scene_count
        assert video_manifest["total_estimated_duration_seconds"] == 60
        assert video_manifest["planned_final_output_file"].endswith("episode.mp4")
        assert video_manifest["source_episode_script"].endswith("episode_script.md")
        assert video_manifest["source_scene_prompts"].endswith("scene_prompts.json")
        assert video_manifest["source_image_manifest"].endswith("image_manifest.json")
        assert video_manifest["source_voice_manifest"].endswith("voice_manifest.json")

        plan_files = sorted(video_dir.glob("scene_*.json"))
        assert len(plan_files) == scene_count
        for plan_file in plan_files:
            plan = json.loads(plan_file.read_text(encoding="utf-8"))
            assert plan["render_status"] == "planned_not_rendered"
            assert plan["planned_output_file"].endswith(".mp4")
            assert "source_image_plan" in plan
            assert "source_voice_plan" in plan
            assert "source_script_context" in plan
            assert "visual_track" in plan
            assert "voice_track" in plan
            assert "subtitle_track" in plan
            assert "music_track" in plan
            assert "sfx_track" in plan
            assert "metadata" in plan

        assert not list(ROOT.rglob("__pycache__")), "__pycache__ directories must not remain."
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
    print("smoke_video_editor_ok")
