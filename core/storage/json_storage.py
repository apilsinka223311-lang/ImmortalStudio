"""JSON file storage helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonStorage:
    """Small JSON storage adapter with consistent formatting."""

    def save(self, path: Path, data: dict[str, Any]) -> None:
        """Save JSON data and create parent directories when needed."""

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.write("\n")

    def load(self, path: Path) -> dict[str, Any]:
        """Load JSON data from disk."""

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
