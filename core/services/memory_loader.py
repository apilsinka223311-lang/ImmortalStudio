"""Project memory loading services."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from core.services.project_loader import ProjectConfig


@dataclass(frozen=True)
class ProjectMemory:
    """Loaded memory required by the first production pipeline."""

    world: dict[str, str] = field(default_factory=dict)
    characters: dict[str, str] = field(default_factory=dict)
    prompts: dict[str, str] = field(default_factory=dict)
    previous_episodes: dict[str, str] = field(default_factory=dict)
    style_guide: str | None = None

    def summary(self) -> dict[str, int | bool]:
        """Return a compact summary suitable for task metadata."""

        return {
            "world_files": len(self.world),
            "character_files": len(self.characters),
            "prompt_files": len(self.prompts),
            "previous_episode_files": len(self.previous_episodes),
            "has_style_guide": self.style_guide is not None,
        }


class MemoryLoader:
    """Loads project-scoped world, character and production memory."""

    MEMORY_EXTENSIONS = {".md", ".txt", ".json"}

    def __init__(self, root_path: Path) -> None:
        self.root_path = root_path

    def load(self, project_config: ProjectConfig) -> ProjectMemory:
        """Load the minimum memory bundle required by Studio Director."""

        directories = project_config.project_directories
        return ProjectMemory(
            world=self._load_directory(directories["world"]),
            characters=self._load_directory(directories["characters"]),
            prompts=self._load_directory(directories["prompts"]),
            previous_episodes=self._load_directory(directories["episodes"]),
            style_guide=self._load_optional_file(self.root_path / "docs" / "STYLE_GUIDE.md"),
        )

    def _load_directory(self, directory: Path) -> dict[str, str]:
        memory: dict[str, str] = {}
        if not directory.exists():
            return memory

        for path in sorted(directory.rglob("*")):
            if path.is_file() and path.suffix.lower() in self.MEMORY_EXTENSIONS:
                memory[path.relative_to(directory).as_posix()] = self._read_text(path)
        return memory

    @staticmethod
    def _load_optional_file(path: Path) -> str | None:
        if not path.is_file():
            return None
        return MemoryLoader._read_text(path)

    @staticmethod
    def _read_text(path: Path) -> str:
        return path.read_text(encoding="utf-8")
