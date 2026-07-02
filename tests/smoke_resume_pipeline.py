"""Smoke check for resuming an existing production task."""

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
from core.pipeline.stages import FIRST_PIPELINE_STAGES  # noqa: E402


def main() -> None:
    """Create a partial saved task, resume it, verify completion, then clean artifacts."""

    director = create_default_director(ROOT)
    task = director.start_production(
        ProductionRequest(
            project="ImmortalAcademy",
            episode="episode_resume_smoke",
            idea="A new disciple awakens an ancient sword.",
            language="English",
            platform="YouTube Shorts",
            episode_goal="Verify resume from an existing production task.",
            duration_seconds=60,
        )
    )

    try:
        task_path = task.output_directory / "production_task.json"
        plan_path = task.output_directory / "episode_plan.json"
        script_path = task.output_directory / "episode_script.md"
        prompts_path = task.output_directory / "scene_prompts.json"
        final_metadata_path = task.output_directory / "final" / "metadata.json"

        assert task_path.is_file(), f"Missing production task: {task_path}"
        assert plan_path.is_file(), f"Missing episode plan: {plan_path}"

        _reset_task_to_script_writer(task_path)
        _remove_downstream_artifacts(task.output_directory)

        resumed_task = director.resume_production(task_path)
        production_task = json.loads(task_path.read_text(encoding="utf-8"))

        assert resumed_task.task_id == task.task_id
        assert plan_path.is_file(), "Resume must keep completed Story Architect output."
        assert script_path.is_file(), "Resume must recreate episode_script.md."
        assert prompts_path.is_file(), "Resume must recreate scene_prompts.json."
        assert final_metadata_path.is_file(), "Resume must complete the local pipeline package."
        assert production_task["current_stage"] == "completed"
        assert production_task["status"] == "completed"
        assert production_task["completed_stages"].count("story_architect") == 1
        assert production_task["completed_stages"].count("script_writer") == 1
        assert production_task["completed_stages"].count("publisher") == 1
        assert not production_task["pending_stages"]

        stage_results = production_task["metadata"]["stage_results"]
        assert "story_architect" in stage_results
        assert "script_writer" in stage_results
        assert "publisher" in stage_results
        assert stage_results["publisher"]["metadata"]["validation"]["success"] is True
        assert not list(ROOT.rglob("__pycache__")), "__pycache__ directories must not remain."
    finally:
        logging.shutdown()
        _cleanup_task_directory(task.output_directory)


def _reset_task_to_script_writer(task_path: Path) -> None:
    data = json.loads(task_path.read_text(encoding="utf-8"))
    stage_ids = [stage.stage_id for stage in FIRST_PIPELINE_STAGES]
    data["status"] = "Waiting for resume smoke test."
    data["current_stage"] = "script_writer"
    data["completed_stages"] = ["studio_director", "story_architect"]
    data["pending_stages"] = [stage_id for stage_id in stage_ids if stage_id != "story_architect"]

    stage_results = data.get("metadata", {}).get("stage_results", {})
    data["metadata"]["stage_results"] = {
        key: value
        for key, value in stage_results.items()
        if key == "story_architect"
    }

    task_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _remove_downstream_artifacts(output_directory: Path) -> None:
    for relative_path in (
        "episode_script.md",
        "scene_prompts.json",
        "episode_report.json",
    ):
        path = output_directory / relative_path
        if path.exists():
            path.unlink()

    for relative_path in ("images", "voice", "video", "final"):
        path = output_directory / relative_path
        if path.exists():
            shutil.rmtree(path)


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
    print("smoke_resume_pipeline_ok")
