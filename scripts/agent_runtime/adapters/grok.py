"""GrokAdapter — wraps ``hermes -z`` (xai-oauth provider) for the agent runtime.

Fourth production adapter. Brings grok-4 (and successors) online as a peer
to codex / claude / gemini for code review, deliberation, and fix lanes.

Key design points:

- **Transport:** ``hermes`` CLI in oneshot mode (``-z -`` reads prompt
  from stdin). Hermes proxies to xAI via the ``xai-oauth`` provider
  (loopback PKCE OAuth set up via ``hermes login``). No API key required.
- **Modes:** All three (read-only / workspace-write / danger) supported.
  Mode → hermes toolset mapping is conservative for read-only (no
  terminal/file tools), permissive for workspace-write and danger.
- **Project context:** hermes injects KubeDojo project state via its
  ``memory`` + ``skills`` toolsets unless suppressed. We keep this on for
  review/code work (gives grok situational awareness) but disable via
  ``--ignore-user-config --ignore-rules`` when the caller passes
  ``tool_config={"isolated": True}`` (used for benchmark / calibration).
- **No session resume.** ``resume_policy=never`` in the registry — hermes
  has session semantics but cross-worktree contamination would mirror the
  Codex footgun. Defensively ignored even if passed.
- **Liveness:** hermes streams output to stdout, so the runner's stdout
  watchdog handles liveness. ``liveness_signal_paths()`` returns ``()``.

Status flagged for the user:
- Grok writer DQ'd by the #388 deterministic verifier gate (see memory
  ``project_grok_writer_word_cap_2026-05-16.md``). This adapter does NOT
  unlock the writer lane — the verifier gate is the floor. It DOES unlock
  reviewer, fixer, ab-discuss, and one-shot research lanes.

Issue: #1184 (agent-runtime), #1235 (reviewer reassignment context).
"""
from __future__ import annotations

import os
import re
import shutil
from pathlib import Path
from typing import Any

from ..result import ParseResult
from .base import InvocationPlan

# Rate-limit patterns. xAI returns 429 like everyone else; hermes
# surfaces rate-limit errors in stderr / stdout depending on transport.
_RATE_LIMIT_PATTERNS = (
    r"rate limit",
    r"rate_limit",
    r"usage limit",
    r"quota exceeded",
    r"too many requests",
    r"\bHTTP 429\b",
    r"\bstatus 429\b",
    r"\b429\b",
    r"xai.*rate",
    r"x-ai.*rate",
)
_RATE_LIMIT_RE = re.compile("|".join(_RATE_LIMIT_PATTERNS), re.IGNORECASE)

# Hermes startup warnings we strip before declaring success.
_HERMES_BANNER_RE = re.compile(
    r"^(💡 Python project detected\..*|hermes -z:.*)$",
    re.MULTILINE,
)

# Toolsets per mode. Hermes built-in toolsets are documented under
# `hermes tools list`. We deliberately exclude memory / skills from
# read-only to keep calibration runs reproducible; they're great for
# real review/code work though.
_TOOLSETS_READ_ONLY = "web"
_TOOLSETS_WORKSPACE = "web,file,terminal,code_execution,todo"
_TOOLSETS_DANGER = "web,file,terminal,code_execution,todo,memory,skills"


class GrokAdapter:
    """Adapter for ``hermes -z`` with the xai-oauth provider."""

    name: str = "grok"
    # grok-4 is the canonical model identifier for hermes via xai-oauth.
    # User may override via env (e.g. when xAI ships grok-4.3 under a new
    # identifier or routes effort=xhigh via a separate slug).
    default_model: str = os.environ.get("AB_GROK_MODEL", "grok-4")
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
        """Build the hermes oneshot invocation.

        ``tool_config`` keys honored:
            - ``isolated: bool`` — if True, pass ``--ignore-user-config
              --ignore-rules`` to bypass hermes's project-context
              injection. Default False (project context is feature, not
              bug, for review/code work).
            - ``toolsets: str`` — comma-separated override for ``-t``.
              Wins over the mode-default mapping.
            - ``provider: str`` — override hermes provider. Default
              ``xai-oauth``. Useful for testing api-key transport once
              ``xai`` provider gets re-auth'd.
            - ``effort: str`` — reasoning effort label. Hermes does not
              expose this as a flag today; we forward it via prompt
              prefix when ``"xhigh"`` is requested. Tracking issue: see
              ``project_hermes_model_inventory.md``.
            - ``yolo: bool`` — pass ``--yolo`` (auto-accept tool calls).
              Default True for write modes, False for read-only.
            - ``accept_hooks: bool`` — pass ``--accept-hooks``. Default
              False; opt-in for callers that want project hooks to fire.
        """
        if mode not in self.supported_modes:
            raise ValueError(f"GrokAdapter: unsupported mode {mode!r}")

        tc: dict[str, Any] = tool_config or {}

        binary = shutil.which("hermes") or "hermes"
        cmd: list[str] = [binary]

        # Reasoning effort hint applied first so the final prompt string is
        # the argv positional we pass to -z.
        effort = tc.get("effort")
        final_prompt = prompt
        if effort and effort != "default":
            final_prompt = f"[Reasoning effort hint: {effort}]\n\n{prompt}"

        # Oneshot mode. Pass the prompt as argv positional, NOT stdin.
        # ``hermes -z -`` (stdin marker) is interpreted as "no prompt
        # provided, run in project-introspection mode" — the prompt
        # piped on stdin is ignored. ARG_MAX is ~1 MB on macOS so the
        # ~10 KB review prompts fit comfortably; if a caller needs to
        # pass a multi-megabyte prompt, write it to a temp file and use
        # a different transport (not the runtime's concern today).
        cmd.extend(["-z", final_prompt])

        # Model
        cmd.extend(["-m", model or self.default_model])

        # Provider — xai-oauth is the canonical KubeDojo path
        # (loopback PKCE; no API key required).
        provider = tc.get("provider", "xai-oauth")
        cmd.extend(["--provider", provider])

        # Toolset selection — caller override wins, else mode default.
        toolsets = tc.get("toolsets")
        if not toolsets:
            if mode == "read-only":
                toolsets = _TOOLSETS_READ_ONLY
            elif mode == "workspace-write":
                toolsets = _TOOLSETS_WORKSPACE
            else:  # danger
                toolsets = _TOOLSETS_DANGER
        cmd.extend(["-t", toolsets])

        # Auto-accept tool calls. Required for non-interactive runs that
        # do file edits or shell ops. Read-only stays prompt-only by
        # default so we don't accidentally grant network egress through
        # the web tool's confirm step.
        yolo_default = mode in ("workspace-write", "danger")
        if bool(tc.get("yolo", yolo_default)):
            cmd.append("--yolo")

        if bool(tc.get("accept_hooks", False)):
            cmd.append("--accept-hooks")

        # Isolation: bypass user config + project rules. Used for
        # calibration / benchmark runs where deterministic output is
        # more important than context awareness.
        if bool(tc.get("isolated", False)):
            cmd.extend(["--ignore-user-config", "--ignore-rules"])

        # Defensively drop session_id — resume_policy=never.
        _ = session_id
        _ = task_id

        return InvocationPlan(
            cmd=cmd,
            cwd=cwd,
            stdin_payload="",  # prompt is in argv; stdin must be empty
            output_file=None,
            env_overrides={},
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
        """Parse hermes -z output.

        Hermes prints the final assistant message to stdout. Diagnostic
        warnings ("💡 Python project detected.", argument errors) appear
        in stdout/stderr depending on how hermes was invoked.
        """
        _ = output_file
        _ = plan
        _ = call_start_time

        # Strip hermes banners that aren't part of the response.
        clean_stdout = _HERMES_BANNER_RE.sub("", stdout or "").strip()

        combined = f"{clean_stdout}\n{stderr or ''}"
        rate_limited = bool(_RATE_LIMIT_RE.search(combined))

        ok = returncode == 0 and bool(clean_stdout) and not rate_limited
        response = clean_stdout if ok else ""

        stderr_excerpt: str | None = None
        if not ok:
            excerpt_source = (stderr or "").strip() or (stdout or "").strip()
            stderr_excerpt = excerpt_source[:500] or None

        return ParseResult(
            ok=ok,
            response=response,
            stderr_excerpt=stderr_excerpt,
            rate_limited=rate_limited,
            session_id=None,
            tokens=None,
        )

    def liveness_signal_paths(self, plan: InvocationPlan) -> tuple[Path, ...]:
        """Hermes streams to stdout; the runner's stdout watchdog covers liveness."""
        _ = plan
        return ()
