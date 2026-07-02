"""Production domain models for ImmortalStudio orchestration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    """Return the current UTC timestamp in ISO-8601 format."""

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_task_id() -> str:
    """Create a stable production task identifier."""

    return f"task_{uuid4().hex[:12]}"


@dataclass(frozen=True)
class ProductionRequest:
    """Input request received by Studio Director."""

    project: str
    idea: str
    episode: str = "episode_001"
    language: str = "English"
    platform: str = "YouTube Shorts"
    episode_goal: str | None = None
    duration_seconds: int | None = None
    world: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PipelineStage:
    """A single pipeline stage coordinated by Studio Director."""

    stage_id: str
    name: str
    agent_id: str
    expected_output: str | None = None


@dataclass
class ProductionTask:
    """Persistent task object saved as `production_task.json`."""

    task_id: str
    timestamp: str
    project: str
    episode: str
    idea: str
    language: str
    platform: str
    status: str
    current_stage: str
    completed_stages: list[str]
    pending_stages: list[str]
    output_directory: Path
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        request: ProductionRequest,
        output_directory: Path,
        pending_stages: list[str],
        current_stage: str,
        metadata: dict[str, Any] | None = None,
        task_id: str | None = None,
    ) -> "ProductionTask":
        """Build a new production task from a user request."""

        return cls(
            task_id=task_id or new_task_id(),
            timestamp=utc_now_iso(),
            project=request.project,
            episode=request.episode,
            idea=request.idea,
            language=request.language,
            platform=request.platform,
            status="created",
            current_stage=current_stage,
            completed_stages=[],
            pending_stages=pending_stages,
            output_directory=output_directory,
            metadata=metadata or {},
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the task into JSON-serializable data."""

        data = asdict(self)
        data["output_directory"] = self.output_directory.as_posix()
        return data

    def mark_stage_completed(self, stage_id: str) -> None:
        """Mark a stage as completed and remove it from pending work."""

        if stage_id not in self.completed_stages:
            self.completed_stages.append(stage_id)
        self.pending_stages = [
            pending_stage for pending_stage in self.pending_stages if pending_stage != stage_id
        ]

    def set_waiting_for_agent(self, stage_id: str, agent_id: str, message: str) -> None:
        """Store a graceful waiting status for a missing downstream agent."""

        self.current_stage = stage_id
        self.status = message
        self.metadata.setdefault("blocked_by", {})
        self.metadata["blocked_by"] = {
            "stage": stage_id,
            "agent": agent_id,
            "reason": "agent_implementation_missing",
        }
