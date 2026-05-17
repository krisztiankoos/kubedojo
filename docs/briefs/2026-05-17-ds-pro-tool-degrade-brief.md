# DeepSeekAdapter — graceful tool-use degradation

**Owner**: codex (gpt-5.5, danger mode)
**Worktree**: `.worktrees/ds-pro-tool-degrade`
**Branch**: `fix-ds-pro-tool-use-degradation`
**Origin**: PR #1288 first-prod-use revealed DS Pro returns 217-char `I'll verify ... <bash>gh pr view 1288 ...</bash>` instead of an actual review when restricted to read-only mode's `web`-only toolset. Memorized in `feedback_ds_pro_review_needs_workspace_write.md` (this session).

## Why

DS V4 Pro is calibrated as gold-tier reviewer (session-21 brief: tied 5/5 with claude on content review). But in `read-only` mode the GrokAdapter pattern restricts the hermes toolset to `web` only — no `terminal`/`file`/`code_execution`. Grok-4 degrades gracefully (reviews the pasted diff). **DS Pro does not** — it emits a `<bash>` tool-use intent expecting execution, and the hermes layer returns the partial text response back to the caller. The orchestrator sees `ok=True` with a 217-char string that is not a review.

Two routes to fix:
- **Route A (parse-time guard)**: detect unfulfilled tool-use markup in `DeepSeekAdapter.parse_response`. Mark `ok=False`, write a useful `stderr_excerpt`, let the caller fall back to grok/claude.
- **Route B (auto-promote mode)**: in `dispatch_smart.py`, for `task_class="review"` + `--agent deepseek`, silently upgrade `read-only` → `workspace-write`. Grants tool authority.

**Go with Route A.** Reasons: (1) DS Pro hallucinated 3/4 on code in calibration — auto-granting terminal/file authority is the wrong direction; (2) explicit failure with a helpful message lets the caller make an informed choice (re-dispatch with `--mode workspace-write` if confident, or fall back). Route B is a future possibility but should be opt-in, not silent.

## What changed

### 1) `scripts/agent_runtime/adapters/deepseek.py`

In `parse_response`, after the existing `clean_stdout` extraction, before the `ok = ...` line, add a detection block:

```python
# Detect unfulfilled tool-use intent: DS Pro emits <bash>...</bash> or
# <tool_use>...</tool_use> blocks expecting execution. The hermes layer
# returns the text back unmodified when the tool isn't in the active
# toolset (e.g. read-only mode's `web` only). The "review" is then just
# the tool-call preamble — useless to the orchestrator.
_TOOL_USE_INTENT_RE = re.compile(
    r"<\s*(bash|tool_use|tool|terminal|shell)\b[^>]*>",
    re.IGNORECASE,
)

# ... inside parse_response, after computing clean_stdout:
tool_use_unfulfilled = bool(_TOOL_USE_INTENT_RE.search(clean_stdout))
if tool_use_unfulfilled and len(clean_stdout) < 1000:
    # Short response + tool-use intent = the model never produced real output.
    # Long responses with tool-use markup might be embedded code samples; leave those alone.
    ok = False
    response = ""
    stderr_excerpt = (
        "DS Pro returned tool-use intent without execution "
        f"({len(clean_stdout)} chars). The hermes toolset for this mode "
        "doesn't include the requested tool. For DS Pro reviews, re-dispatch "
        "with --mode workspace-write (grants terminal/file tools), or fall "
        "back to grok/claude. Raw stub: " + clean_stdout[:200]
    )
    return ParseResult(
        ok=False,
        response="",
        stderr_excerpt=stderr_excerpt,
        rate_limited=False,
        session_id=None,
        tokens=None,
    )
```

Put `_TOOL_USE_INTENT_RE` next to `_RATE_LIMIT_RE` at module scope.

**Threshold rationale**: 1000-char cap on the heuristic so a long, legitimate review that quotes `<bash>` in a code block doesn't false-trigger. The actual failure produces ≤300 chars in practice (217 observed).

### 2) Update DeepSeekAdapter docstring

Add a paragraph to the existing module-level docstring (near the calibration footnote) calling out the read-only/tool-use limitation. One short paragraph; reference `feedback_ds_pro_review_needs_workspace_write.md`.

### 3) Tests

Add to `tests/test_deepseek_adapter.py`:

```python
def test_parse_response_detects_unfulfilled_tool_use_intent():
    """DS Pro tool-use intent without execution → ok=False, helpful stderr."""
    adapter = DeepSeekAdapter()
    raw = (
        "I'll verify the PR commits first and then systematically review the diff.\n"
        "<bash>gh pr view 1288 --json commits</bash>"
    )
    result = adapter.parse_response(
        stdout=raw,
        stderr="",
        returncode=0,
        output_file=None,
    )
    assert result.ok is False
    assert result.response == ""
    assert "tool-use intent" in (result.stderr_excerpt or "")
    assert "workspace-write" in (result.stderr_excerpt or "")


def test_parse_response_long_response_with_bash_codeblock_still_passes():
    """A long real review that happens to quote <bash> in a code block must pass."""
    adapter = DeepSeekAdapter()
    # Padded to >1000 chars so the heuristic doesn't trigger.
    raw = (
        "VERDICT: APPROVE\n\n"
        + "SUMMARY: All criteria met. " * 30
        + "\n\nThe author also added the `<bash>` toolset gating which is correct."
    )
    result = adapter.parse_response(
        stdout=raw,
        stderr="",
        returncode=0,
        output_file=None,
    )
    assert result.ok is True
    assert result.response.startswith("VERDICT: APPROVE")
```

Run before push:

```bash
PYTHONPATH=/Users/krisztiankoos/projects/kubedojo/scripts \
  /Users/krisztiankoos/projects/kubedojo/.venv/bin/pytest \
  tests/test_deepseek_adapter.py -q
```

All tests (existing 6 + new 2 = 8 minimum) must pass.

### 4) PR

- **Title**: `fix(deepseek): detect unfulfilled tool-use intent in parse_response (PR #1288 first-prod finding)`
- **Base**: `main`
- **Body**: 1 paragraph summary + cite PR #1288 + `feedback_ds_pro_review_needs_workspace_write.md`.
- **Single commit**.

## Constraints

- **Mode**: danger.
- **No memory writes**.
- **No `--no-verify`**.
- **Push and open PR.** End with PR URL.

## Out of scope

- Route B (auto-mode-promotion in dispatch_smart). Separate PR if ever wanted; not in this one.
- Patching GrokAdapter or GeminiAdapter for similar tool-use detection. Grok degrades gracefully today; gemini hasn't shown the failure mode. Apply same heuristic only if those adapters break the same way in the future.
- Hermes-side fixes (not our code).
