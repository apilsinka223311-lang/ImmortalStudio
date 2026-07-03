"""Smoke check for The Origin System Episode 1 artifact contract."""

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


EPISODE_ID = "the_origin_system_episode_001_contract"
EPISODE_IDEA = (
    "The Origin System Episode 1: Lin Mo awakens during public humiliation in the Azure Sword Clan "
    "training courtyard. Lin Jian humiliates him as a cripple and disgrace. The Origin System initializes, "
    "detects artificially severed spiritual channels and a Foundation fragment, analyzes Lin Jian's weak point, "
    "and Lin Mo counters for the first time without becoming overpowered."
)

REQUIRED_MEMORY_REFERENCES = (
    "The Origin System",
    "Fallen Star Realm",
    "Lin Mo",
    "Lin Jian",
    "The Origin System has no shop",
)

REQUIRED_PLAN_BEATS = (
    "Lin Mo",
    "Lin Jian",
    "Azure Sword Clan",
    "public humiliation",
    "cripple",
    "disgrace",
    "artificially severed spiritual channels",
    "Foundation fragment",
    "weak point",
    "counters for the first time",
)

REQUIRED_PROMPT_CONTEXT = (
    "Lin Mo",
    "Lin Jian",
    "Azure Sword Clan",
    "training courtyard",
    "The Origin System",
    "public humiliation",
    "The Origin System has no shop",
)

FORBIDDEN_POSITIVE_CHANGES = (
    "system shop appears",
    "opens the system shop",
    "buys from the system shop",
    "purchases from the system shop",
    "Lin Mo becomes overpowered",
    "Lin Mo is instantly overpowered",
    "instant immortal lord",
)


def main() -> None:
    """Run the local pipeline and validate the first episode artifact contract."""

    director = create_default_director(ROOT)
    task = director.start_production(
        ProductionRequest(
            project="ImmortalAcademy",
            episode=EPISODE_ID,
            idea=EPISODE_IDEA,
            language="English",
            platform="YouTube Shorts",
            episode_goal="Validate the first canon episode artifact contract.",
            duration_seconds=60,
        )
    )

    try:
        task_path = task.output_directory / "production_task.json"
        plan_path = task.output_directory / "episode_plan.json"
        prompts_path = task.output_directory / "scene_prompts.json"
        final_metadata_path = task.output_directory / "final" / "metadata.json"

        assert task_path.is_file(), f"Missing production task: {task_path}"
        assert plan_path.is_file(), f"Missing episode plan: {plan_path}"
        assert prompts_path.is_file(), f"Missing scene prompts: {prompts_path}"
        assert final_metadata_path.is_file(), f"Missing final metadata: {final_metadata_path}"

        production_task = json.loads(task_path.read_text(encoding="utf-8"))
        episode_plan = json.loads(plan_path.read_text(encoding="utf-8"))
        scene_prompts = json.loads(prompts_path.read_text(encoding="utf-8"))
        final_metadata = json.loads(final_metadata_path.read_text(encoding="utf-8"))

        memory_text = _to_text(production_task["metadata"]["memory_context"])
        plan_text = _to_text(episode_plan)
        prompts_text = _to_text(scene_prompts)
        combined_text = "\n".join((memory_text, plan_text, prompts_text))

        _assert_contains_all(memory_text, REQUIRED_MEMORY_REFERENCES)
        _assert_contains_all(plan_text, REQUIRED_PLAN_BEATS)
        _assert_contains_any(plan_text.lower(), ("system initializes", "system awakening", "system activates"))
        _assert_contains_all(prompts_text, REQUIRED_PROMPT_CONTEXT)
        _assert_contains_any(prompts_text.lower(), ("system initializes", "system awakening", "system activates"))
        _assert_forbidden_phrases_absent(combined_text, FORBIDDEN_POSITIVE_CHANGES)

        assert production_task["status"] == "completed"
        assert production_task["current_stage"] == "completed"
        assert final_metadata["schema_version"] == "1.0"
        assert final_metadata["upload_status"] == "not_uploaded"
        assert not list(ROOT.rglob("__pycache__")), "__pycache__ directories must not remain."
    finally:
        logging.shutdown()
        _cleanup_task_directory(task.output_directory)


def _assert_contains_all(text: str, expected_values: tuple[str, ...]) -> None:
    for expected_value in expected_values:
        assert expected_value in text, f"Missing expected contract reference: {expected_value}"


def _assert_contains_any(text: str, expected_values: tuple[str, ...]) -> None:
    assert any(expected_value in text for expected_value in expected_values), (
        f"Expected one of {expected_values!r}."
    )


def _assert_forbidden_phrases_absent(text: str, forbidden_values: tuple[str, ...]) -> None:
    normalized_text = text.lower()
    for forbidden_value in forbidden_values:
        assert forbidden_value.lower() not in normalized_text, (
            f"Forbidden contract phrase found: {forbidden_value}"
        )


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
    print("smoke_first_episode_contract_ok")
