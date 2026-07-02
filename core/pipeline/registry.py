"""Agent discovery and registry implementations."""

from __future__ import annotations

import importlib.util
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from core.pipeline.agents import AgentExecutionContext, AgentExecutor, AgentResult
from core.models.production import ProductionTask


class AgentRegistry(Protocol):
    """Interface for resolving agent executors."""

    def get(self, agent_id: str) -> AgentExecutor:
        """Return an executor for an agent id."""


@dataclass(frozen=True)
class MissingAgentExecutor:
    """Graceful placeholder returned when an agent has no implementation yet."""

    agent_id: str
    reason: str = "agent_implementation_missing"

    def execute(self, task: ProductionTask, context: AgentExecutionContext) -> AgentResult:
        """Return a non-crashing result for missing agent implementations."""

        return AgentResult(
            success=False,
            status="missing_agent",
            message=f"Agent implementation is missing: {self.agent_id}",
            metadata={"agent_id": self.agent_id, "reason": self.reason},
        )


class FileSystemAgentRegistry:
    """Discovers agent implementations without coupling Studio Director to them."""

    IMPLEMENTATION_FILE = "agent.py"

    def __init__(self, agents_path: Path, logger: logging.Logger | None = None) -> None:
        self.agents_path = agents_path
        self.logger = logger or logging.getLogger(__name__)
        self._executors: dict[str, AgentExecutor] = {}

    def register(self, executor: AgentExecutor) -> None:
        """Register an in-process executor for tests or future plugins."""

        self._executors[executor.agent_id] = executor

    def get(self, agent_id: str) -> AgentExecutor:
        """Return an executor for an agent or a graceful missing executor."""

        if agent_id in self._executors:
            return self._executors[agent_id]

        agent_path = self.agents_path / agent_id
        if not agent_path.is_dir():
            self.logger.info("Agent directory is missing: %s", agent_path)
            return MissingAgentExecutor(agent_id)

        implementation_path = agent_path / self.IMPLEMENTATION_FILE
        if not implementation_path.is_file():
            self.logger.info("Agent has no executable implementation yet: %s", agent_path)
            return MissingAgentExecutor(agent_id)

        try:
            executor = self._load_executor(agent_id, implementation_path)
        except Exception as exc:
            self.logger.exception("Failed to load agent '%s' from %s.", agent_id, implementation_path)
            return MissingAgentExecutor(agent_id, reason=f"agent_load_failed: {exc}")
        self._executors[agent_id] = executor
        return executor

    def _load_executor(self, agent_id: str, implementation_path: Path) -> AgentExecutor:
        module_name = f"immortalstudio_agent_{agent_id}"
        spec = importlib.util.spec_from_file_location(module_name, implementation_path)
        if spec is None or spec.loader is None:
            self.logger.error("Cannot load agent module: %s", implementation_path)
            return MissingAgentExecutor(agent_id)

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        factory = getattr(module, "create_agent", None)
        if factory is None:
            self.logger.error("Agent module has no create_agent() factory: %s", implementation_path)
            return MissingAgentExecutor(agent_id)

        executor = factory()
        if getattr(executor, "agent_id", None) != agent_id:
            self.logger.error(
                "Agent '%s' returned incompatible executor id: %s",
                agent_id,
                getattr(executor, "agent_id", None),
            )
            return MissingAgentExecutor(agent_id)

        self.logger.info("Loaded agent '%s' from %s.", agent_id, implementation_path)
        return executor
