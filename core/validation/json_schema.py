"""Small JSON Schema subset validator used by the deterministic pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValidationIssue:
    """One validation problem found in a JSON document."""

    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable representation."""

        return {"path": self.path, "message": self.message}


@dataclass(frozen=True)
class ValidationResult:
    """Result of validating one JSON artifact."""

    success: bool
    schema_name: str
    artifact_path: str
    issues: list[ValidationIssue] = field(default_factory=list)
    skipped: bool = False

    def summary(self) -> str:
        """Return a short human-readable result summary."""

        if self.skipped:
            return f"Validation skipped for {self.schema_name}."
        if self.success:
            return f"{self.schema_name} validation passed."
        return f"{self.schema_name} validation failed with {len(self.issues)} issue(s)."

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""

        return {
            "success": self.success,
            "schema_name": self.schema_name,
            "artifact_path": self.artifact_path,
            "skipped": self.skipped,
            "issues": [issue.to_dict() for issue in self.issues],
        }


class JsonSchemaValidator:
    """Validate JSON data against the subset of JSON Schema used in this project."""

    def validate(self, data: Any, schema: dict[str, Any], schema_name: str, artifact_path: str) -> ValidationResult:
        """Validate data and return all discovered issues."""

        issues: list[ValidationIssue] = []
        self._validate_value(data, schema, "$", issues)
        return ValidationResult(
            success=not issues,
            schema_name=schema_name,
            artifact_path=artifact_path,
            issues=issues,
        )

    def _validate_value(
        self,
        value: Any,
        schema: dict[str, Any],
        path: str,
        issues: list[ValidationIssue],
    ) -> None:
        expected_type = schema.get("type")
        if expected_type is not None and not self._matches_type(value, expected_type):
            issues.append(ValidationIssue(path, f"Expected type {expected_type}, got {type(value).__name__}."))
            return

        if "const" in schema and value != schema["const"]:
            issues.append(ValidationIssue(path, f"Expected constant value {schema['const']!r}."))

        if "enum" in schema and value not in schema["enum"]:
            issues.append(ValidationIssue(path, f"Expected one of {schema['enum']!r}."))

        if isinstance(value, dict):
            self._validate_object(value, schema, path, issues)
        elif isinstance(value, list):
            self._validate_array(value, schema, path, issues)

    def _validate_object(
        self,
        value: dict[str, Any],
        schema: dict[str, Any],
        path: str,
        issues: list[ValidationIssue],
    ) -> None:
        for field_name in schema.get("required", []):
            if field_name not in value:
                issues.append(ValidationIssue(f"{path}.{field_name}", "Missing required field."))

        properties = schema.get("properties", {})
        for field_name, field_schema in properties.items():
            if field_name in value:
                self._validate_value(value[field_name], field_schema, f"{path}.{field_name}", issues)

        if schema.get("additionalProperties") is False:
            allowed = set(properties)
            for field_name in value:
                if field_name not in allowed:
                    issues.append(ValidationIssue(f"{path}.{field_name}", "Unexpected additional field."))

    def _validate_array(
        self,
        value: list[Any],
        schema: dict[str, Any],
        path: str,
        issues: list[ValidationIssue],
    ) -> None:
        min_items = schema.get("minItems")
        if isinstance(min_items, int) and len(value) < min_items:
            issues.append(ValidationIssue(path, f"Expected at least {min_items} item(s)."))

        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(value):
                self._validate_value(item, item_schema, f"{path}[{index}]", issues)

    @staticmethod
    def _matches_type(value: Any, expected_type: str | list[str]) -> bool:
        if isinstance(expected_type, list):
            return any(JsonSchemaValidator._matches_type(value, item) for item in expected_type)

        if expected_type == "object":
            return isinstance(value, dict)
        if expected_type == "array":
            return isinstance(value, list)
        if expected_type == "string":
            return isinstance(value, str)
        if expected_type == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected_type == "number":
            return (isinstance(value, int) or isinstance(value, float)) and not isinstance(value, bool)
        if expected_type == "boolean":
            return isinstance(value, bool)
        if expected_type == "null":
            return value is None
        return True
