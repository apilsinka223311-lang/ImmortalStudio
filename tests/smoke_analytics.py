"""Smoke check for the deterministic Analytics pipeline transition."""

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
    """Run the pipeline through Analytics and clean generated artifacts."""

    director = create_default_director(ROOT)
    task = director.start_production(
        ProductionRequest(
            project="ImmortalAcademy",
            episode="episode_analytics_smoke",
            idea="A new disciple awakens an ancient sword.",
            language="English",
            platform="YouTube Shorts",
            episode_goal="Verify the Analytics reporting transition.",
            duration_seconds=60,
        )
    )

    try:
        task_path = task.output_directory / "production_task.json"
        report_path = task.output_directory / "episode_report.json"
        prompts_path = task.output_directory / "scene_prompts.json"
        image_manifest_path = task.output_directory / "images" / "image_manifest.json"
        voice_manifest_path = task.output_directory / "voice" / "voice_manifest.json"
        video_manifest_path = task.output_directory / "video" / "video_manifest.json"

        assert task_path.is_file(), f"Missing production task: {task_path}"
        assert report_path.is_file(), f"Missing episode report: {report_path}"
        assert prompts_path.is_file(), f"Missing scene prompts: {prompts_path}"
        assert image_manifest_path.is_file(), f"Missing image manifest: {image_manifest_path}"
        assert voice_manifest_path.is_file(), f"Missing voice manifest: {voice_manifest_path}"
        assert video_manifest_path.is_file(), f"Missing video manifest: {video_manifest_path}"

        production_task = json.loads(task_path.read_text(encoding="utf-8"))
        scene_prompts = json.loads(prompts_path.read_text(encoding="utf-8"))
        report = json.loads(report_path.read_text(encoding="utf-8"))

        assert "story_architect" in production_task["completed_stages"]
        assert "script_writer" in production_task["completed_stages"]
        assert "prompt_engineer" in production_task["completed_stages"]
        assert "image_director" in production_task["completed_stages"]
        assert "voice_director" in production_task["completed_stages"]
        assert "video_editor" in production_task["completed_stages"]
        assert "analytics" in production_task["completed_stages"]
        assert "analytics" not in production_task["pending_stages"]
        assert "publisher" in production_task["completed_stages"]
        assert production_task["current_stage"] == "completed"
        assert production_task["status"] == "completed"
        assert "analytics" in production_task["metadata"]["stage_results"]

        scene_count = len(scene_prompts["prompts"])
        assert report["schema_version"] == "1.0"
        assert report["analytics_version"] == "analytics_v1"
        assert report["generation_summary"]["scene_count"] == scene_count
        assert report["generation_summary"]["real_images_generated"] == 0
        assert report["generation_summary"]["real_audio_files_generated"] == 0
        assert report["generation_summary"]["real_video_files_rendered"] == 0
        assert report["artifact_status"]["analytics"] == "report_created"
        assert report["validation_summary"]["scene_counts_match"] is True
        assert report["validation_summary"]["all_assets_are_planned_only"] is True
        assert report["cost_summary"]["external_api_cost"] == 0

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
    print("smoke_analytics_ok")
