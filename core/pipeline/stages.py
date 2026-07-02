"""Canonical first-pipeline stage definitions."""

from __future__ import annotations

from core.models.production import PipelineStage


FIRST_PIPELINE_STAGES: tuple[PipelineStage, ...] = (
    PipelineStage(
        stage_id="story_architect",
        name="Story Architect",
        agent_id="story_architect",
        expected_output="episode_plan.json",
    ),
    PipelineStage(
        stage_id="script_writer",
        name="Script Writer",
        agent_id="script_writer",
        expected_output="episode_script.md",
    ),
    PipelineStage(
        stage_id="prompt_engineer",
        name="Prompt Engineer",
        agent_id="prompt_engineer",
        expected_output="scene_prompts.json",
    ),
    PipelineStage(
        stage_id="image_director",
        name="Image Director",
        agent_id="image_director",
        expected_output="images/",
    ),
    PipelineStage(
        stage_id="voice_director",
        name="Voice Director",
        agent_id="voice_director",
        expected_output="voice/",
    ),
    PipelineStage(
        stage_id="video_editor",
        name="Video Editor",
        agent_id="video_editor",
        expected_output="episode.mp4",
    ),
    PipelineStage(
        stage_id="analytics",
        name="Analytics",
        agent_id="analytics",
        expected_output="episode_report.json",
    ),
    PipelineStage(
        stage_id="publisher",
        name="Publisher",
        agent_id="publisher",
        expected_output="metadata.json",
    ),
)
