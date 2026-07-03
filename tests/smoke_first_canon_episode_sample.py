"""Smoke check for the first canon-driven episode production sample."""

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


EPISODE_ID = "the_origin_system_episode_001"
EPISODE_ID_SAFE = "the_origin_system_episode_001"
EPISODE_IDEA = (
    "The Origin System Episode 1: Lin Mo awakens during public humiliation in the Azure Sword Clan "
    "training courtyard. Lin Jian humiliates him as a cripple. The Origin System initializes, detects "
    "artificially severed spiritual channels and a Foundation fragment, analyzes Lin Jian's weak point, "
    "and Lin Mo counters for the first time."
)


def main() -> None:
    """Run the deterministic local pipeline for the first canon-driven sample."""

    director = create_default_director(ROOT)
    task = director.start_production(
        ProductionRequest(
            project="ImmortalAcademy",
            episode=EPISODE_ID,
            idea=EPISODE_IDEA,
            language="English",
            platform="YouTube Shorts",
            episode_goal="Create a canon-driven deterministic sample for The Origin System Episode 1.",
            duration_seconds=60,
        )
    )

    try:
        task_path = task.output_directory / "production_task.json"
        plan_path = task.output_directory / "episode_plan.json"
        prompts_path = task.output_directory / "scene_prompts.json"
        final_metadata_path = task.output_directory / "final" / "metadata.json"
        package_manifest_path = task.output_directory / "final" / "package_manifest.json"

        assert task_path.is_file(), f"Missing production task: {task_path}"
        assert plan_path.is_file(), f"Missing episode plan: {plan_path}"
        assert prompts_path.is_file(), f"Missing scene prompts: {prompts_path}"
        assert final_metadata_path.is_file(), f"Missing final metadata: {final_metadata_path}"
        assert package_manifest_path.is_file(), f"Missing package manifest: {package_manifest_path}"

        production_task = json.loads(task_path.read_text(encoding="utf-8"))
        episode_plan = json.loads(plan_path.read_text(encoding="utf-8"))
        scene_prompts = json.loads(prompts_path.read_text(encoding="utf-8"))
        final_metadata = json.loads(final_metadata_path.read_text(encoding="utf-8"))

        assert production_task["current_stage"] == "completed"
        assert production_task["status"] == "completed"
        assert "publisher" in production_task["completed_stages"]
        assert final_metadata["schema_version"] == "1.0"
        assert final_metadata["upload_status"] == "not_uploaded"
        assert production_task["episode"] == EPISODE_ID
        assert episode_plan["episode_id"] == EPISODE_ID_SAFE

        memory_context = production_task["metadata"]["memory_context"]
        _assert_contains_all(
            _to_text(memory_context),
            (
                "The Origin System",
                "Fallen Star Realm",
                "Lin Mo",
                "Lin Jian",
                "The Origin System has no shop",
            ),
        )

        plan_text = _to_text(episode_plan)
        _assert_contains_all(
            plan_text,
            (
                "Lin Mo",
                "Lin Jian",
                "Azure Sword Clan",
                "public humiliation",
                "weak point",
            ),
        )
        assert "system" in plan_text.lower()
        assert "awak" in plan_text.lower()

        prompts_text = _to_text(scene_prompts)
        _assert_contains_all(
            prompts_text,
            (
                "Lin Mo",
                "Lin Jian",
                "Azure Sword Clan",
                "training courtyard",
                "The Origin System has no shop",
            ),
        )
        assert "semi-realistic anime" in prompts_text
        assert "dark xianxia" in prompts_text or "Visual Style" in prompts_text
        assert not list(ROOT.rglob("__pycache__")), "__pycache__ directories must not remain."
    finally:
        logging.shutdown()
        _cleanup_task_directory(task.output_directory)


def _assert_contains_all(text: str, expected_values: tuple[str, ...]) -> None:
    for expected_value in expected_values:
        assert expected_value in text, f"Missing expected canon reference: {expected_value}"


def _to_text(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True)


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
    print("smoke_first_canon_episode_sample_ok")
