"""Template adapter — reference implementation for new agents.

COPY THIS FILE when adding a new agent. Do NOT copy codex.py or any
production adapter — those have legacy quirks you don't want.

This template is NOT registered in registry.py (its ``cli_available``
flag is False) and is never loaded by the runner. It exists purely as
living documentation — the "add a new agent in 20 lines" reference
that the design doc and the agent-runtime-guide both point to.

---

HOW TO ADD A NEW AGENT (e.g., "grok"):

1. Copy this file to ``adapters/grok.py``.
2. Rename the class from ``TemplateAdapter`` to ``GrokAdapter``.
3. Fill in the class attributes at the top: ``name``, ``default_model``,
   ``supported_modes``.
4. Implement ``build_invocation`` — describe the CLI argv for each mode.
5. Implement ``parse_response`` — parse the CLI output into a ``ParseResult``.
6. Implement ``liveness_signal_paths`` — return files the runner can
   mtime-poll for stall detection. Return ``()`` if the CLI only writes
   to stdout (the runner's stdout streamer covers that case).
7. Update ``registry.AGENTS["grok"]`` with real values and set
   ``cli_available: True``.
8. Write unit tests for your adapter mirroring
   ``tests/test_agent_runtime.py`` shape.
9. Run ``.venv/bin/python -m pytest tests/test_agent_runtime.py``.
10. Profit.

COMMON MISTAKES to avoid:

- **Don't mutate os.environ.** Use ``InvocationPlan.env_overrides`` —
  the runner merges it onto ``os.environ`` fresh for each subprocess.
- **Don't call os.chdir().** Always pass ``cwd=`` to ``subprocess.Popen``.
  The runner does this for you — just include ``cwd`` correctly in your
  InvocationPlan if relevant.
- **Don't hardcode the binary path.** Use ``shutil.which("yourcli") or
  "yourcli"`` so the error on missing binary is clear.
- **Don't resume sessions in coding tasks.** If your agent supports
  session resume, set ``resume_policy="bridge_only"`` in the registry
  and defensively ignore ``session_id`` in write modes inside your
  ``build_invocation`` implementation.
- **Don't guess token counts.** If your CLI doesn't expose tokens,
  return ``tokens=None`` from ``parse_response`` — do NOT invent numbers.
- **Don't swallow parse errors.** On ambiguous output, return
  ``ParseResult(ok=False, ...)`` with a useful ``stderr_excerpt``
  rather than silently returning an empty success.

See ``docs/agent-runtime-guide.md`` for the full mental model.

Issue: #1184
"""
from __future__ import annotations

import shutil
from pathlib import Path

from ..result import ParseResult
from .base import InvocationPlan


class TemplateAdapter:
    """Reference adapter — copy for new agents. NOT a real adapter."""

    # ------------------------------------------------------------------
    # Class attributes — fill these in for each new agent
    # ------------------------------------------------------------------
    name: str = "template"
    default_model: str = "template-model-v1"
    supported_modes: frozenset[str] = frozenset({"read-only"})
    # Add "workspace-write" / "danger" to supported_modes if the CLI
    # has sandbox flags for writing. Most new CLIs start read-only only.

    # ------------------------------------------------------------------
    # Required methods
    # ------------------------------------------------------------------

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
        """Build the subprocess invocation for this agent.

        Template: replace with real CLI-specific logic.
        """
        # 1. Resolve binary. shutil.which handles PATH lookup.
        binary = shutil.which("template-cli") or "template-cli"

        # 2. Build the argv. Include the model, sandbox flags, and
        #    whatever else the CLI needs. Keep mode-specific logic in
        #    a helper method like _mode_flags() for readability.
        cmd: list[str] = [
            binary,
            "--model", model or self.default_model,
            # "-s", "read-only",  # example sandbox flag
            # "-o", str(some_output_file),  # example output file
        ]

        # 3. Decide whether the prompt goes via stdin or as a positional
        #    argument. Most CLIs accept stdin with a "-" marker.
        cmd.append("-")  # stdin marker

        # 4. Ignore session_id if resume isn't supported OR if this is a
        #    write-mode call (coherence footgun — see design doc § 6.3).
        # if mode in ("workspace-write", "danger"):
        #     session_id = None  # defensively drop

        # 5. Ignore tool_config keys you don't understand. Forward-compat.
        _ = tool_config  # template ignores entirely

        # 6. Return the InvocationPlan. cwd MUST be stamped — the runner
        #    uses it on Popen, and liveness_signal_paths(plan) can derive
        #    cwd-scoped state directories from it without reading the
        #    ambient process cwd.
        return InvocationPlan(
            cmd=cmd,
            cwd=cwd,
            stdin_payload=prompt,
            output_file=None,  # or Path("/tmp/template-output.txt")
            env_overrides={},  # or {"TEMPLATE_API_KEY": "..."} if needed
            liveness_paths=(),  # or (output_file,) if you use one
        )

    def parse_response(
        self,
        *,
        stdout: str,
        stderr: str,
        returncode: int,
        output_file: Path | None,
    ) -> ParseResult:
        """Parse CLI output into a ParseResult.

        Template: replace with real output parsing.
        """
        # 1. Detect rate-limiting. Use word-boundary patterns to avoid
        #    URL false positives (e.g. "\\b429\\b" not bare "429").
        rate_limited = any(
            pattern in (stderr or "").lower()
            for pattern in ("rate limit", "quota exceeded", "usage limit")
        )

        # 2. Classify success. Adjust the criteria to match your CLI.
        ok = returncode == 0 and not rate_limited

        # 3. Build the response. Read from output_file if you used one,
        #    otherwise use stdout.
        response = stdout.strip() if ok else ""

        # 4. Build the stderr excerpt on failure for debugging.
        stderr_excerpt: str | None = None
        if not ok and stderr.strip():
            stderr_excerpt = stderr.strip()[:500]

        # 5. Extract session ID if the CLI exposes one. Return None if not.
        session_id = None

        # 6. Tokens: return None if the CLI doesn't expose them.
        #    Do NOT invent numbers.
        tokens = None

        return ParseResult(
            ok=ok,
            response=response,
            stderr_excerpt=stderr_excerpt,
            rate_limited=rate_limited,
            session_id=session_id,
            tokens=tokens,
        )

    def liveness_signal_paths(
        self,
        plan: InvocationPlan,
    ) -> tuple[Path, ...]:
        """Return files the runner should mtime-poll for stall detection.

        Template: return () if this CLI only writes to stdout (the runner's
        stdout streamer handles liveness for that case). Otherwise return
        the output file + any session / log file the CLI updates
        continuously during execution.

        Cap your return at ~5 paths — the runner polls each one every 5s,
        and more than that becomes wasteful.
        """
        # Template: no fallback liveness signal, stdout streaming is enough.
        _ = plan
        return ()
