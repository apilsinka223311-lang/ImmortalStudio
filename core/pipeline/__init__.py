"""Pipeline abstractions and managers."""

from core.pipeline.agents import AgentExecutionContext, AgentExecutor, AgentResult
from core.pipeline.manager import PipelineManager
from core.pipeline.registry import AgentRegistry, FileSystemAgentRegistry

__all__ = [
    "AgentExecutionContext",
    "AgentExecutor",
    "AgentResult",
    "AgentRegistry",
    "FileSystemAgentRegistry",
    "PipelineManager",
]
