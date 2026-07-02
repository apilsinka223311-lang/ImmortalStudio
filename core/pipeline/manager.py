"""Pipeline orchestration primitives."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from core.models.production import PipelineStage, ProductionTask
from core.pipeline.agents import AgentExecutionContext, AgentResult
from core.pipeline.registry import AgentRegistry
from core.pipeline.stages import FIRST_PIPELINE_STAGES


class PipelineManager:
    """Coordinates stage selection and delegates execution to agent interfaces."""

    def __init__(
        self,
        agent_registry: AgentRegistry,
        stages: Sequence[PipelineStage] = FIRST_PIPELINE_STAGES,
        logger: logging.Logger | None = None,
    ) -> None:
        self.agent_registry = agent_registry
        self.stages = tuple(stages)
        self.logger = logger or logging.getLogger(__name__)

    def pending_stage_ids(self) -> list[str]:
        """Return all pending stage identifiers for a fresh production task."""

        return [stage.stage_id for stage in self.stages]

    def first_stage(self) -> PipelineStage:
        """Return the first executable stage after Studio Director."""

        if not self.stages:
            raise RuntimeError("Pipeline has no stages configured.")
        return self.stages[0]

    def get_stage(self, stage_id: str) -> PipelineStage:
        """Find a stage by identifier."""

        for stage in self.stages:
            if stage.stage_id == stage_id:
                return stage
        raise RuntimeError(f"Unknown pipeline stage: {stage_id}")

    def next_stage_after(self, stage_id: str) -> PipelineStage | None:
        """Return the next stage after a completed stage."""

        for index, stage in enumerate(self.stages):
            if stage.stage_id == stage_id:
                next_index = index + 1
                if next_index >= len(self.stages):
                    return None
                return self.stages[next_index]
        raise RuntimeError(f"Unknown pipeline stage: {stage_id}")

    def execute_current_stage(
        self,
        task: ProductionTask,
        context: AgentExecutionContext,
    ) -> AgentResult:
        """Execute the task's current stage through the configured agent registry."""

        stage = self.get_stage(task.current_stage)
        self.logger.info("Executing stage '%s' with agent '%s'.", stage.stage_id, stage.agent_id)
        executor = self.agent_registry.get(stage.agent_id)
        return executor.execute(task, context)
