"""Parser and validator for the structured Codex report block."""

from __future__ import annotations

import re
from ast import literal_eval
from dataclasses import dataclass

_REPORT_BEGIN = "=== CODEX REPORT BEGIN ==="
_REPORT_END = "=== CODEX REPORT END ==="
_FIELD_RE = re.compile(r"^([A-Z][A-Z0-9_]*):(?:\s*(.*))?$")
_VALID_STATUSES = {"success", "partial", "failed"}


@dataclass
class CodexReport:
    task_id: str
    status: str
    commit_sha: str | None
    files_touched: list[str]
    notes: list[str]
    extra: dict[str, str]


def _extract_report_block(text: str) -> str | None:
    """Return the report body between the begin/end markers."""
    start = text.find(_REPORT_BEGIN)
    if start == -1:
        return None
    start += len(_REPORT_BEGIN)
    end = text.find(_REPORT_END, start)
    if end == -1:
        return None
    return text[start:end].strip("\n")


def _parse_fields(block: str) -> dict[str, str]:
    """Parse KEY: value fields from the report body."""
    fields: dict[str, list[str]] = {}
    current_key: str | None = None

    for line in block.splitlines():
        if not line.strip():
            if current_key is not None:
                fields[current_key].append("")
            continue

        match = _FIELD_RE.match(line)
        if match:
            current_key = match.group(1)
            initial_value = match.group(2) or ""
            fields[current_key] = [initial_value]
            continue

        if current_key is None:
            continue

        fields[current_key].append(line.strip())

    return {
        key: "\n".join(value_lines).strip()
        for key, value_lines in fields.items()
    }


def _parse_list_value(raw: str) -> list[str]:
    """Parse a list field from inline or multi-line report syntax."""
    if not raw:
        return []

    if raw.startswith("[") and raw.endswith("]"):
        try:
            parsed = literal_eval(raw)
        except (SyntaxError, ValueError):
            parsed = None
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]

    items: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            stripped = stripped[2:].strip()
        items.append(stripped)
    return items


def _optional_scalar(raw: str | None) -> str | None:
    """Normalize optional scalar fields."""
    if raw is None:
        return None
    value = raw.strip()
    if not value or value.lower() in {"none", "null", "n/a"}:
        return None
    return value


def parse_codex_report(text: str) -> CodexReport | None:
    """Parse the ``=== CODEX REPORT BEGIN ===`` block from Codex output."""
    block = _extract_report_block(text)
    if block is None:
        return None

    fields = _parse_fields(block)
    known_keys = {"TASK_ID", "STATUS", "COMMIT_SHA", "FILES_TOUCHED", "NOTES"}
    extra = {
        key: value
        for key, value in fields.items()
        if key not in known_keys and value
    }

    return CodexReport(
        task_id=fields.get("TASK_ID", "").strip(),
        status=fields.get("STATUS", "").strip(),
        commit_sha=_optional_scalar(fields.get("COMMIT_SHA")),
        files_touched=_parse_list_value(fields.get("FILES_TOUCHED", "")),
        notes=_parse_list_value(fields.get("NOTES", "")),
        extra=extra,
    )


def validate_codex_report(report: CodexReport) -> list[str]:
    """Return validation errors for a parsed report."""
    errors: list[str] = []

    if not report.task_id.strip():
        errors.append("TASK_ID is required")
    if not report.status.strip():
        errors.append("STATUS is required")
    elif report.status not in _VALID_STATUSES:
        errors.append(
            f"STATUS must be one of: {', '.join(sorted(_VALID_STATUSES))}"
        )

    return errors
