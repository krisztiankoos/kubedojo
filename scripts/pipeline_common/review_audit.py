from __future__ import annotations

import fcntl
import os
import re
from datetime import UTC, datetime
from pathlib import Path


def _atomic_write_text(path: Path, content: str) -> None:
    """Stage to a unique tempfile in the same dir, then os.replace — survives SIGKILL mid-write."""
    path.parent.mkdir(parents=True, exist_ok=True)
    unique = f".{os.getpid()}.{datetime.now(UTC).strftime('%H%M%S%f')}.tmp"
    tmp = path.with_suffix(path.suffix + unique)
    try:
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)
    except Exception:
        if tmp.exists():
            try:
                tmp.unlink()
            except OSError:
                pass
        raise


def _format_duration(seconds) -> str:
    if seconds is None:
        return "unknown"
    try:
        total = max(0.0, float(seconds))
    except (TypeError, ValueError):
        return str(seconds)
    if total >= 60:
        minutes = int(total // 60)
        remainder = int(round(total - minutes * 60))
        if remainder == 60:
            minutes, remainder = minutes + 1, 0
        return f"{minutes}m {remainder}s"
    if total >= 10:
        return f"{int(round(total))}s"
    if total >= 1:
        return f"{total:.1f}s"
    return f"{int(round(total * 1000))}ms"


_HEADER_FIELD_RE = re.compile(r"^\*\*(?P<key>[^*]+?)\*\*:\s*(?P<val>.*)$", re.MULTILINE)


def _parse_existing_header(existing: str) -> dict[str, str]:
    """Extract **Key**: Value pairs from an existing audit header (before the first '---')."""
    header = existing.split("\n---\n", 1)[0] if "\n---\n" in existing else existing
    return {m.group("key").strip(): m.group("val").strip() for m in _HEADER_FIELD_RE.finditer(header)}


def _render_audit_entry(event: str, timestamp: str, fields: dict) -> str:
    raw_checks = fields.get("checks")
    checks: list = raw_checks if isinstance(raw_checks, list) else []
    passed = [str(c.get("id", "?")) for c in checks if isinstance(c, dict) and c.get("passed")]
    failed = [str(c.get("id", "?")) for c in checks if isinstance(c, dict) and not c.get("passed")]
    lines = [
        f"## {timestamp} — `{event}` — `{fields.get('verdict', '')}`",
        "",
        f"**Reviewer**: {fields.get('reviewer', 'unknown')}",
        f"**Attempt**: {fields.get('attempt', '?')}",
        f"**Severity**: {fields.get('severity', 'unknown')}",
        f"**Duration**: {_format_duration(fields.get('duration'))}",
        (f"**Checks**: {len(passed)}/{len(checks)} passed"
         + (f" ({' '.join(passed)})" if passed else "")
         + (f" | **Failed**: {' '.join(failed)}" if failed else "")),
        f"**Job Id**: {fields['job_id']}",
        f"**Lease Id**: {fields['lease_id']}",
    ]
    failed_evidence = [
        f"- **{c.get('id', '?')}**: {str(c.get('evidence', '')).strip()}"
        for c in checks
        if isinstance(c, dict) and not c.get("passed") and str(c.get("evidence", "")).strip()
    ]
    if failed_evidence:
        lines.extend(["", "**Failed check evidence**:", *failed_evidence])
    feedback = str(fields.get("feedback", "")).strip()
    if feedback:
        quoted = [f"> {ln}" if ln else ">" for ln in (feedback.splitlines() or [feedback])]
        lines.extend(["", "**Feedback**:", *quoted])
    return "\n".join(lines)


def append_review_audit(module_path: Path, event: str, **fields) -> Path:
    """Prepend a v1-compatible audit entry; de-dupes on (job_id, lease_id) and preserves
    header metadata written by v1 so v1 and v2 can coexist without silent drift.
    """
    if "module_key" not in fields:
        raise ValueError("append_review_audit requires an explicit module_key")
    module_key = str(fields.pop("module_key")).removesuffix(".md")
    repo_root = next(
        (p for p in (module_path.parent, *module_path.parents) if (p / ".pipeline").exists()),
        Path.cwd(),
    )
    target = repo_root / ".pipeline" / "reviews" / f"{module_key.replace('/', '__')}.md"
    timestamp = fields.pop("timestamp", None)
    if not isinstance(timestamp, str):
        current = timestamp or datetime.now(UTC)
        if current.tzinfo is None:
            current = current.replace(tzinfo=UTC)
        timestamp = current.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target.with_suffix(".lock"), "w", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        try:
            existing = target.read_text(encoding="utf-8") if target.exists() else ""
            # De-dup by (job_id, lease_id) — same attempt must not write twice.
            job_id, lease_id = fields.get("job_id"), fields.get("lease_id")
            if job_id and lease_id and f"**Job Id**: {job_id}\n**Lease Id**: {lease_id}" in existing:
                return target
            body = re.split(r"\n---\n+", existing, maxsplit=1)[1].lstrip() if "\n---\n" in existing else ""
            entry = _render_audit_entry(event, timestamp, fields)
            try:
                display_path = str(module_path.resolve().relative_to(repo_root))
            except ValueError:
                display_path = str(module_path.resolve())
            prior_ts = re.findall(r"^## ([0-9TZ:\-]+) — ", existing, re.MULTILINE)
            all_ts = prior_ts + [timestamp]
            existing_header = _parse_existing_header(existing)
            # Preserve v1-written phase/reviewer/severity when present; fall back to v2's knowledge.
            phase = existing_header.get("Current phase", "pending")
            reviewer = existing_header.get("Current reviewer", str(fields.get("reviewer", "-")))
            severity = existing_header.get("Current severity", str(fields.get("severity", "-")))
            header = "\n".join([
                f"# Review Audit: {module_key}",
                "",
                f"**Path**: `{display_path}`",
                f"**First pass**: {min(all_ts)}",
                f"**Last pass**: {max(all_ts)}",
                f"**Total passes**: {len(prior_ts) + 1}",
                f"**Current phase**: {phase}",
                f"**Current reviewer**: {reviewer}",
                f"**Current severity**: {severity}",
            ])
            content = f"{header}\n\n---\n\n{entry}"
            if body.strip():
                content += f"\n\n---\n\n{body.strip()}"
            content += "\n"
            _atomic_write_text(target, content)
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)
    return target
