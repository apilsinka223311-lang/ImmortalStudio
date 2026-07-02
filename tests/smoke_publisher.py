"""Smoke check for the deterministic Publisher pipeline completion."""

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
    """Run the full deterministic pipeline through Publisher and clean artifacts."""

    director = create_default_director(ROOT)
    task = director.start_production(
        ProductionRequest(
            project="ImmortalAcademy",
            episode="episode_publisher_smoke",
            idea="A new disciple awakens an ancient sword.",
            language="English",
            platform="YouTube Shorts",
            episode_goal="Verify the Publisher local package transition.",
            duration_seconds=60,
        )
    )

    try:
        task_path = task.output_directory / "production_task.json"
        final_dir = task.output_directory / "final"
        metadata_path = final_dir / "metadata.json"
        package_manifest_path = final_dir / "package_manifest.json"

        assert task_path.is_file(), f"Missing production task: {task_path}"
        assert metadata_path.is_file(), f"Missing metadata: {metadata_path}"
        assert package_manifest_path.is_file(), f"Missing package manifest: {package_manifest_path}"
        assert (final_dir / "episode_plan.json").is_file()
        assert (final_dir / "episode_script.md").is_file()
        assert (final_dir / "scene_prompts.json").is_file()
        assert (final_dir / "episode_report.json").is_file()
        assert (final_dir / "images" / "image_manifest.json").is_file()
        assert (final_dir / "voice" / "voice_manifest.json").is_file()
        assert (final_dir / "video" / "video_manifest.json").is_file()
        assert not list(final_dir.rglob("*.mp4")), "Publisher must not create fake MP4 files."
        assert not list(final_dir.rglob("*.mov")), "Publisher must not create fake MOV files."

        production_task = json.loads(task_path.read_text(encoding="utf-8"))
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        package_manifest = json.loads(package_manifest_path.read_text(encoding="utf-8"))

        assert "publisher" in production_task["completed_stages"]
        assert "publisher" not in production_task["pending_stages"]
        assert production_task["current_stage"] == "completed"
        assert production_task["status"] == "completed"
        assert "publisher" in production_task["metadata"]["stage_results"]

        assert metadata["schema_version"] == "1.0"
        assert metadata["publisher_version"] == "publisher_v1"
        assert metadata["pipeline_status"] == "draft"
        assert metadata["upload_status"] == "not_uploaded"
        assert metadata["artifact_paths"]["video"] == "video/video_manifest.json"
        assert metadata["artifact_paths"]["script"] == "episode_script.md"
        assert metadata["artifact_paths"]["prompts"] == "scene_prompts.json"
        assert metadata["artifact_paths"]["report"] == "episode_report.json"
        assert metadata["archive_policy"]["preserve_planning_artifacts"] is True
        assert package_manifest["package_status"] == "local_package_created"
        assert "metadata.json" in package_manifest["files"]

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
    print("smoke_publisher_ok")
