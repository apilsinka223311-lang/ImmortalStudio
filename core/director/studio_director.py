"""Studio Director orchestration service."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from core.models.production import ProductionRequest, ProductionTask, new_task_id
from core.pipeline.agents import AgentExecutionContext, AgentResult
from core.pipeline.manager import PipelineManager
from core.pipeline.registry import FileSystemAgentRegistry
from core.services.memory_loader import MemoryLoader, ProjectMemory
from core.services.project_loader import ProjectConfig, ProjectLoader
from core.storage.json_storage import JsonStorage
from core.utils.logging import add_file_handler, get_logger, setup_logging
from core.validation import DefaultArtifactValidator


class StudioDirector:
    """Coordinates production stages without generating creative content itself."""

    def __init__(
        self,
        root_path: Path,
        project_loader: ProjectLoader,
        memory_loader: MemoryLoader,
        pipeline_manager: PipelineManager,
        storage: JsonStorage,
        artifact_validator: DefaultArtifactValidator | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.root_path = root_path
        self.project_loader = project_loader
        self.memory_loader = memory_loader
        self.pipeline_manager = pipeline_manager
        self.storage = storage
        self.artifact_validator = artifact_validator or DefaultArtifactValidator()
        self.logger = logger or get_logger(__name__)

    def start_production(self, request: ProductionRequest) -> ProductionTask:
        """Create a production task and run available pipeline stages."""

        self.logger.info("Studio Director received production request for project '%s'.", request.project)
        project_config = self.project_loader.load(request.project)
        memory = self.memory_loader.load(project_config)

        first_stage = self.pipeline_manager.first_stage()
        task_id = new_task_id()
        output_directory = self._build_output_directory(project_config, request, task_id)
        add_file_handler(self.logger, output_directory / "studio_director.log")

        task = ProductionTask.create(
            request=request,
            output_directory=output_directory,
            pending_stages=self.pipeline_manager.pending_stage_ids(),
            current_stage=first_stage.stage_id,
            metadata=self._build_initial_metadata(request, project_config, memory),
            task_id=task_id,
        )
        task.status = "in_progress"
        task.mark_stage_completed("studio_director")

        self._save_task(task)
        self.logger.info("Created production task '%s'.", task.task_id)
        self.logger.info("Production task saved to %s.", self._task_path(task))

        self._run_pipeline_until_blocked(task, project_config, memory)
        self._save_task(task)
        return task

    def _run_pipeline_until_blocked(
        self,
        task: ProductionTask,
        project_config: ProjectConfig,
        memory: ProjectMemory,
    ) -> None:
        """Run stages until a stage is missing, fails or the pipeline completes."""

        while task.current_stage != "completed":
            stage = self.pipeline_manager.get_stage(task.current_stage)
            result = self._execute_current_stage(task, project_config, memory)
            if result.success:
                result = self._validate_stage_output(task, stage.stage_id, result)
            self._record_stage_result(task, stage.stage_id, result)

            if not result.success:
                self._handle_stage_failure(task, stage.stage_id, stage.agent_id, stage.name, result)
                self._save_task(task)
                return

            task.mark_stage_completed(stage.stage_id)
            self.logger.info("Stage '%s' completed successfully.", stage.stage_id)

            next_stage = self.pipeline_manager.next_stage_after(stage.stage_id)
            if next_stage is None:
                task.current_stage = "completed"
                task.status = "completed"
                self._save_task(task)
                return

            task.current_stage = next_stage.stage_id
            task.status = "in_progress"
            self._save_task(task)

    def _execute_current_stage(
        self,
        task: ProductionTask,
        project_config: ProjectConfig,
        memory: ProjectMemory,
    ) -> AgentResult:
        context = AgentExecutionContext(
            root_path=self.root_path,
            project_path=project_config.project_path,
            output_directory=task.output_directory,
            metadata={
                "project": project_config.project_id,
                "memory_summary": memory.summary(),
            },
        )
        return self.pipeline_manager.execute_current_stage(task, context)

    def _validate_stage_output(
        self,
        task: ProductionTask,
        stage_id: str,
        result: AgentResult,
    ) -> AgentResult:
        validation_result = self.artifact_validator.validate_stage(stage_id, task.output_directory)
        metadata = dict(result.metadata)
        metadata["validation"] = validation_result.to_dict()

        if validation_result.skipped:
            self.logger.info("No JSON Schema validation contract configured for stage '%s'.", stage_id)
            return AgentResult(
                success=result.success,
                status=result.status,
                message=result.message,
                output_path=result.output_path,
                metadata=metadata,
            )

        if validation_result.success:
            self.logger.info("Stage '%s' output validation passed: %s", stage_id, validation_result.schema_name)
            return AgentResult(
                success=result.success,
                status=result.status,
                message=result.message,
                output_path=result.output_path,
                metadata=metadata,
            )

        message = f"Stage '{stage_id}' output failed JSON Schema validation: {validation_result.summary()}"
        self.logger.error(message)
        return AgentResult(
            success=False,
            status="validation_failed",
            message=message,
            output_path=result.output_path,
            metadata=metadata,
        )

    def _record_stage_result(self, task: ProductionTask, stage_id: str, result: AgentResult) -> None:
        task.metadata.setdefault("stage_results", {})
        task.metadata["stage_results"][stage_id] = {
            "status": result.status,
            "message": result.message,
            "output_path": result.output_path.as_posix() if result.output_path else None,
            "metadata": result.metadata,
        }

    def _handle_stage_failure(
        self,
        task: ProductionTask,
        stage_id: str,
        agent_id: str,
        stage_name: str,
        result: AgentResult,
    ) -> None:
        if result.status == "missing_agent":
            message = f"Waiting for {stage_name} implementation."
            task.set_waiting_for_agent(stage_id=stage_id, agent_id=agent_id, message=message)
            self.logger.warning("%s", message)
            self.logger.warning("Reason: %s", result.message)
            return

        task.current_stage = stage_id
        task.status = f"failed_{stage_id}"
        task.metadata["failure"] = {
            "stage": stage_id,
            "agent": agent_id,
            "message": result.message,
        }
        self.logger.error("Stage '%s' failed: %s", stage_id, result.message)

    def _build_output_directory(
        self,
        project_config: ProjectConfig,
        request: ProductionRequest,
        task_id: str,
    ) -> Path:
        safe_episode = self._safe_identifier(request.episode)
        return project_config.project_path / "production" / "tasks" / safe_episode / task_id

    def _build_initial_metadata(
        self,
        request: ProductionRequest,
        project_config: ProjectConfig,
        memory: ProjectMemory,
    ) -> dict[str, Any]:
        metadata = dict(request.metadata)
        metadata.update(
            {
                "pipeline_version": "1.0",
                "episode_goal": request.episode_goal,
                "duration_seconds": request.duration_seconds,
                "world": request.world,
                "project_id": project_config.project_id,
                "project_path": project_config.project_path.as_posix(),
                "project_documents": sorted(project_config.project_documents.keys()),
                "loaded_memory": memory.summary(),
                "global_config_keys": sorted(project_config.global_config.keys()),
                "notes": [
                    "FIRST_PIPELINE.md is treated as documentation, not runtime configuration."
                ],
            }
        )
        return metadata

    def _save_task(self, task: ProductionTask) -> None:
        self.storage.save(self._task_path(task), task.to_dict())

    @staticmethod
    def _task_path(task: ProductionTask) -> Path:
        return task.output_directory / "production_task.json"

    @staticmethod
    def _safe_identifier(value: str) -> str:
        chars: list[str] = []
        for char in value:
            if char.isalnum():
                chars.append(char.lower())
            elif chars and chars[-1] != "_":
                chars.append("_")
        return "".join(chars).strip("_") or "episode"


def create_default_director(root_path: Path | None = None) -> StudioDirector:
    """Create Studio Director with default filesystem-based dependencies."""

    setup_logging()
    resolved_root = (root_path or Path.cwd()).resolve()
    logger = get_logger("immortalstudio.studio_director")
    agent_registry = FileSystemAgentRegistry(resolved_root / "agents", logger=logger)
    pipeline_manager = PipelineManager(agent_registry=agent_registry, logger=logger)

    return StudioDirector(
        root_path=resolved_root,
        project_loader=ProjectLoader(resolved_root),
        memory_loader=MemoryLoader(resolved_root),
        pipeline_manager=pipeline_manager,
        storage=JsonStorage(),
        artifact_validator=DefaultArtifactValidator(),
        logger=logger,
    )
