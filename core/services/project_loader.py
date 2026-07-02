"""Project loading and validation services."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class ProjectValidationError(RuntimeError):
    """Raised when a project cannot be used by the production pipeline."""


@dataclass(frozen=True)
class ProjectConfig:
    """Loaded project configuration and required project paths."""

    project_id: str
    project_name: str
    project_path: Path
    root_path: Path
    global_config: dict[str, Any] = field(default_factory=dict)
    project_documents: dict[str, str] = field(default_factory=dict)
    project_files: dict[str, Path] = field(default_factory=dict)
    project_directories: dict[str, Path] = field(default_factory=dict)


class ProjectLoader:
    """Loads project structure and validates the minimum v1 requirements."""

    REQUIRED_FILES = ("PROJECT.md", "README.md")
    REQUIRED_DIRECTORIES = (
        "world",
        "characters",
        "episodes",
        "production",
        "assets",
        "prompts",
    )

    def __init__(self, root_path: Path) -> None:
        self.root_path = root_path
        self.projects_path = root_path / "projects"
        self.config_path = root_path / "config"

    def load(self, project_name: str) -> ProjectConfig:
        """Load and validate a project by name or identifier."""

        project_path = self._resolve_project_path(project_name)
        project_files = self._validate_files(project_path)
        project_directories = self._validate_directories(project_path)

        return ProjectConfig(
            project_id=self._project_id(project_path.name),
            project_name=project_path.name,
            project_path=project_path,
            root_path=self.root_path,
            global_config=self._load_global_config(),
            project_documents=self._load_project_documents(project_files),
            project_files=project_files,
            project_directories=project_directories,
        )

    def _resolve_project_path(self, project_name: str) -> Path:
        if not self.projects_path.exists():
            raise ProjectValidationError(f"Projects directory does not exist: {self.projects_path}")

        normalized_name = self._normalize(project_name)
        for candidate in self.projects_path.iterdir():
            if candidate.is_dir() and self._normalize(candidate.name) == normalized_name:
                return candidate

        available = ", ".join(sorted(path.name for path in self.projects_path.iterdir() if path.is_dir()))
        raise ProjectValidationError(
            f"Project '{project_name}' was not found. Available projects: {available or 'none'}"
        )

    def _validate_files(self, project_path: Path) -> dict[str, Path]:
        files: dict[str, Path] = {}
        missing: list[str] = []

        for file_name in self.REQUIRED_FILES:
            path = project_path / file_name
            if path.is_file():
                files[file_name] = path
            else:
                missing.append(file_name)

        if missing:
            raise ProjectValidationError(
                f"Project '{project_path.name}' is missing required files: {', '.join(missing)}"
            )
        return files

    def _validate_directories(self, project_path: Path) -> dict[str, Path]:
        directories: dict[str, Path] = {}
        missing: list[str] = []

        for directory_name in self.REQUIRED_DIRECTORIES:
            path = project_path / directory_name
            if path.is_dir():
                directories[directory_name] = path
            else:
                missing.append(directory_name)

        if missing:
            raise ProjectValidationError(
                f"Project '{project_path.name}' is missing required directories: {', '.join(missing)}"
            )
        return directories

    def _load_global_config(self) -> dict[str, Any]:
        config: dict[str, Any] = {}
        if not self.config_path.exists():
            return config

        for path in sorted(self.config_path.glob("*.json")):
            config[path.stem] = self._load_json_file(path)
        return config

    @staticmethod
    def _load_project_documents(project_files: dict[str, Path]) -> dict[str, str]:
        return {
            name: path.read_text(encoding="utf-8")
            for name, path in project_files.items()
        }

    @staticmethod
    def _load_json_file(path: Path) -> dict[str, Any]:
        if path.stat().st_size == 0:
            return {}
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    @staticmethod
    def _project_id(project_name: str) -> str:
        chars: list[str] = []
        for char in project_name:
            if char.isalnum():
                chars.append(char.lower())
            elif chars and chars[-1] != "_":
                chars.append("_")
        return "".join(chars).strip("_")

    @staticmethod
    def _normalize(value: str) -> str:
        return "".join(char.lower() for char in value if char.isalnum())
