"""Project memory loading services."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

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
            "world_non_empty_files": self._non_empty_count(self.world),
            "character_files": len(self.characters),
            "character_non_empty_files": self._non_empty_count(self.characters),
            "prompt_files": len(self.prompts),
            "prompt_non_empty_files": self._non_empty_count(self.prompts),
            "previous_episode_files": len(self.previous_episodes),
            "previous_episode_non_empty_files": self._non_empty_count(self.previous_episodes),
            "has_style_guide": self.style_guide is not None,
            "has_non_empty_style_guide": bool(self.style_guide and self.style_guide.strip()),
        }

    def context(self, max_files_per_section: int = 3, max_excerpt_chars: int = 320) -> dict[str, Any]:
        """Return a small deterministic memory context for pipeline agents."""

        return {
            "summary": self.summary(),
            "world": self._excerpt_section(self.world, max_files_per_section, max_excerpt_chars),
            "characters": self._excerpt_section(self.characters, max_files_per_section, max_excerpt_chars),
            "prompts": self._excerpt_section(self.prompts, max_files_per_section, max_excerpt_chars),
            "previous_episodes": self._excerpt_section(
                self.previous_episodes,
                max_files_per_section,
                max_excerpt_chars,
            ),
            "style_guide": self._excerpt_text(self.style_guide or "", max_excerpt_chars),
        }

    @staticmethod
    def _non_empty_count(files: dict[str, str]) -> int:
        return sum(1 for content in files.values() if content.strip())

    @classmethod
    def _excerpt_section(
        cls,
        files: dict[str, str],
        max_files: int,
        max_excerpt_chars: int,
    ) -> list[dict[str, str]]:
        entries: list[dict[str, str]] = []
        for relative_path, content in sorted(files.items()):
            excerpt = cls._excerpt_text(content, max_excerpt_chars)
            if excerpt:
                entries.append({"path": relative_path, "excerpt": excerpt})
            if len(entries) >= max_files:
                break
        return entries

    @staticmethod
    def _excerpt_text(text: str, max_chars: int) -> str:
        normalized = " ".join(text.split())
        if len(normalized) <= max_chars:
            return normalized
        return normalized[: max_chars - 3].rstrip() + "..."


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
