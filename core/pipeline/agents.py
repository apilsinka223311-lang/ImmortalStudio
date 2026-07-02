"""Agent interfaces used by the pipeline manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from core.models.production import ProductionTask


@dataclass(frozen=True)
class AgentExecutionContext:
    """Runtime context passed to a pipeline agent."""

    root_path: Path
    project_path: Path
    output_directory: Path
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentResult:
    """Result returned by a pipeline agent execution attempt."""

    success: bool
    status: str
    message: str
    output_path: Path | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentExecutor(Protocol):
    """Interface implemented by future AI departments."""

    agent_id: str

    def execute(self, task: ProductionTask, context: AgentExecutionContext) -> AgentResult:
        """Execute one pipeline stage for a production task."""
