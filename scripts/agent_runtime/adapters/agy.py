"""AgyAdapter - wraps Antigravity CLI (``agy``) for the agent runtime.

Phase 1 of the Antigravity migration keeps this adapter alongside the
existing Gemini CLI adapter. ``agy`` model selection is controlled by the
interactive TUI and persists across ``agy -p`` invocations; there is no CLI
model flag today, so the runtime's model value is audit-only.

Known behavioral facts as of issue #1350:

- Headless prompt mode is ``agy -p "<prompt>"``. Stdin prompts are ignored.
- Resume/new conversation is ``--conversation=<uuid>``.
- Write-capable modes use ``--dangerously-skip-permissions``. In addition,
  ``dispatch_smart.py`` forces ``mode="danger"`` for ``--agent agy``
  unconditionally because read-only would otherwise hang on the CLI's
  interactive permission prompts (same protection as ``--agent codex``).
- No known on-disk session or liveness file exists, so stdout is canonical.

MCP / plugin configuration is a Phase-2 follow-up. ``agy plugin`` only
exposes ``import gemini|claude``, ``install <known-target>``, ``enable``,
and ``disable``. The CLI has no plugin-marketplace browse surface as of
1.0.0, and ``agy plugin import gemini`` is a no-op in a default install
because gemini-cli ships no extensions out of the box. The adapter
accepts ``tool_config["mcp_server_names"]`` for API parity with
``GeminiAdapter`` but does not act on it today — wire ``agy plugin
enable <name>`` here once we have concrete MCP servers to consume.
"""
from __future__ import annotations

import os
import re
import shutil
from pathlib import Path

from ..result import ParseResult
from .base import InvocationPlan


_MODEL_HINT_ENV = "KUBEDOJO_AGY_MODEL_HINT"

# Defensive defaults borrowed from Gemini CLI. Agy is new enough that these
# may need adjustment once we see real Antigravity rate-limit errors.
_RATE_LIMIT_PATTERNS = (
    r"RESOURCE_EXHAUSTED",
    r"usage limit reached",
    r"quota exceeded",
    r"daily.{0,10}limit.{0,10}exceeded",
)
_RATE_LIMIT_RE = re.compile("|".join(_RATE_LIMIT_PATTERNS), re.IGNORECASE)


class AgyAdapter:
    """Adapter for the ``agy`` Antigravity CLI."""

    name: str = "agy"
    default_model: str = os.environ.get("KUBEDOJO_AGY_MODEL", "gemini-3.5-flash-high")
    supported_modes: frozenset[str] = frozenset({"read-only", "workspace-write", "danger"})

    def build_invocation(
        self,
        *,
        prompt: str,
        mode: str,
        cwd: Path,
        model: str | None,
        task_id: str | None,
        session_id: str | None,
        tool_config: dict | None,
    ) -> InvocationPlan:
        """Build the ``agy`` print-mode invocation.

        ``model`` is intentionally not mapped to a CLI flag. The active model
        is whichever model the operator selected in the ``agy`` TUI panel.
        """
        if mode not in self.supported_modes:
            raise ValueError(f"AgyAdapter: unsupported mode {mode!r}")

        agy_bin = shutil.which("agy") or str(Path.home() / ".local/bin/agy")
        cmd: list[str] = [agy_bin, "-p", prompt]

        if session_id:
            cmd.append(f"--conversation={session_id}")

        if mode in ("workspace-write", "danger"):
            cmd.append("--dangerously-skip-permissions")

        # Phase 2 follow-up: agy uses `agy plugin` for MCP configuration,
        # not a per-invocation CLI flag like gemini-cli.
        _ = tool_config
        _ = task_id

        effective_model = model or self.default_model

        return InvocationPlan(
            cmd=cmd,
            cwd=cwd,
            stdin_payload="",
            output_file=None,
            env_overrides={_MODEL_HINT_ENV: effective_model},
            liveness_paths=(),
        )

    def parse_response(
        self,
        *,
        stdout: str,
        stderr: str,
        returncode: int,
        output_file: Path | None,
        plan: InvocationPlan | None = None,
        call_start_time: float | None = None,
    ) -> ParseResult:
        """Parse ``agy -p`` output.

        Stdout is the only known canonical response source. We deliberately do
        not attempt Gemini-style session-file recovery because no Antigravity
        on-disk session location is known yet.
        """
        _ = output_file
        _ = call_start_time

        stdout_response = (stdout or "").strip()
        stderr_text = (stderr or "").strip()
        combined = f"{stdout_response}\n{stderr_text}"
        hard_limit_hit = bool(_RATE_LIMIT_RE.search(combined))
        call_failed = returncode != 0 or not bool(stdout_response)
        rate_limited = hard_limit_hit and call_failed

        ok = returncode == 0 and bool(stdout_response) and not rate_limited
        response = stdout_response if ok else ""

        stderr_excerpt: str | None = None
        if not ok:
            excerpt_source = stderr_text or stdout_response
            stderr_excerpt = excerpt_source[:500] or None
        elif stderr_text:
            stderr_excerpt = stderr_text[:500]
        else:
            model_hint = self.default_model
            if plan is not None:
                hint = plan.env_overrides.get(_MODEL_HINT_ENV)
                if isinstance(hint, str) and hint:
                    model_hint = hint
            stderr_excerpt = (
                "agy active model: tracked in TUI panel; "
                f"--model arg '{model_hint}' is informational"
            )

        return ParseResult(
            ok=ok,
            response=response,
            stderr_excerpt=stderr_excerpt,
            rate_limited=rate_limited,
            session_id=None,
            tokens=None,
        )

    def liveness_signal_paths(self, plan: InvocationPlan) -> tuple[Path, ...]:
        """Agy has no known on-disk liveness signal; stdout is canonical."""
        _ = plan
        return ()
