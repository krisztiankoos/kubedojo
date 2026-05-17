# dispatch_smart.py extension (gemini + deepseek) + tests/test_grok_adapter.py

**Owner**: codex (gpt-5.5, danger mode)
**Worktree**: `.worktrees/dispatch-smart-and-grok-tests`
**Branch**: `feat-dispatch-smart-gemini-deepseek-and-grok-tests`
**Precedent**: PR #1286 (DeepSeekAdapter just shipped — `tests/test_deepseek_adapter.py` is the test template).

## Why

Two carryovers from PR #1286 (DS adapter) and PR #1245 (Grok adapter):

1. **dispatch_smart.py SUPPORTED_AGENTS is incomplete.** Today it's `("claude", "codex", "grok")` (`scripts/dispatch_smart.py:75`). DeepSeek and Gemini are in `agent_runtime/registry.py` but cannot be invoked through the canonical CLI dispatch path. Callers wanting to dispatch DS-Pro for a review have to drop down to `hermes -z` or `agent_runtime.runner.invoke()` directly — both work but bypass the task-class abstraction (model selection, default mode, timeout, KUBEDOJO_DISPATCHED env injection).

2. **tests/test_grok_adapter.py never landed.** The PR #1245 (Grok integration) round-1 review flagged "missing unit tests, non-blocking." It's been a STATUS.md carryover since session 17 (2026-05-17 early). `tests/test_deepseek_adapter.py` (117 LOC) just shipped as the template — copy its shape for grok.

Bundled as ONE PR because both are sub-50-line surgical extensions of the same shipped subsystem.

## What changed

### 1) `scripts/dispatch_smart.py`

Extend `SUPPORTED_AGENTS`:

```python
SUPPORTED_AGENTS = ("claude", "codex", "deepseek", "gemini", "grok")
```

For each of the 5 `TASK_CLASSES` (`search`, `edit`, `draft`, `review`, `architect`), add `gemini` and `deepseek` keys to the `models=` dict. Recommended defaults (rationale in parens — keep these in the brief, do NOT add them as code comments):

| task_class | gemini | deepseek |
|---|---|---|
| `search` | `gemini-3.1-flash-lite-preview` (cheap scan) | `deepseek-v4-flash` (3× faster than Pro per calibration) |
| `edit` | `gemini-3.1-pro-preview` (writer-tier; matches GEMINI_WRITER_MODEL default) | `deepseek-v4-pro` (gold-tier per calibration) |
| `draft` | `gemini-3.1-pro-preview` | `deepseek-v4-pro` |
| `review` | `gemini-3.1-pro-preview` (NEVER flash for code/lab — `feedback_never_flash_for_code_review.md`) | `deepseek-v4-pro` (gold-tier reviewer; calibration tied 5/5 with claude) |
| `architect` | `gemini-3.1-pro-preview` | `deepseek-v4-pro` |

The argparse `--agent` `choices=SUPPORTED_AGENTS` line at `scripts/dispatch_smart.py:266` will pick up the new agents automatically once the tuple is extended. Verify with `python scripts/dispatch_smart.py --help` after edits — output should show all 5 agents.

**Test the new dispatch paths** in the same PR with two `--dry-run` smoke calls in the commit message body (NOT committed as test artifacts):

```bash
.venv/bin/python scripts/dispatch_smart.py review --agent deepseek --dry-run "test"
.venv/bin/python scripts/dispatch_smart.py search --agent gemini --dry-run "test"
```

Expected output: `model=deepseek-v4-pro` and `model=gemini-3.1-flash-lite-preview` respectively.

### 2) `tests/test_grok_adapter.py` (NEW)

Mirror `tests/test_deepseek_adapter.py` exactly — read it (`117 LOC`) and write the grok equivalent. Mappings to apply during the copy:

| In test_deepseek_adapter.py | In test_grok_adapter.py |
|---|---|
| `DeepSeekAdapter` | `GrokAdapter` |
| `from scripts.agent_runtime.adapters.deepseek import DeepSeekAdapter` | `from scripts.agent_runtime.adapters.grok import GrokAdapter` |
| `deepseek-v4-pro` default | `grok-4` default |
| `deepseek-v4-flash` override case | `grok-4-fast` (or skip the override test — use `AB_GROK_MODEL` env override path if test_deepseek's was env-based) |
| `--provider deepseek` | `--provider xai-oauth` |
| `provider="deepseek"` defaults | `provider="xai-oauth"` defaults |

Cover the same 6 tests:
1. `test_build_invocation_read_only` — `-z prompt -m grok-4 --provider xai-oauth -t web` (no `--yolo`).
2. `test_build_invocation_workspace_write` — `--yolo` present, toolset `web,file,terminal,code_execution,todo`.
3. `test_build_invocation_danger` — toolset includes `memory,skills`.
4. `test_model_override` — caller-passed `model="grok-4-fast"` propagates to `-m`.
5. `test_parse_response_strips_hermes_banner` — Python-project banner stripped.
6. `test_parse_response_detects_rate_limit` — `rate_limited=True` when stderr contains "rate limit".

Run the full test suite before pushing:

```bash
.venv/bin/pytest tests/test_grok_adapter.py tests/test_deepseek_adapter.py \
                 tests/test_agent_runtime_runner.py tests/test_quality_dispatchers.py -q
```

All tests must pass — 0 failures.

### 3) PR

- **Title**: `feat(dispatch): add deepseek + gemini to dispatch_smart + GrokAdapter unit tests`
- **Base**: `main`
- **Body**: list the two changes + dry-run smoke output + test count.
- **Single commit per concern, two commits total**:
  - `feat(dispatch_smart): add deepseek + gemini to SUPPORTED_AGENTS and task-class model maps`
  - `test(grok): add GrokAdapter unit tests mirroring DeepSeekAdapter shape`

## Constraints

- **Mode**: danger (need git push + gh pr create).
- **No memory writes** (orchestrator-only).
- **No `--no-verify`** on commits.
- **Three-way agreement** (`feedback_three_way_rule_agreement.md`): `SUPPORTED_AGENTS` + `TASK_CLASSES` + argparse choices must all agree on the agent name. The argparse `choices=SUPPORTED_AGENTS` pattern already enforces this — sanity-check that the help output shows all 5 after the edit.
- **Push and open PR.** End run with the PR URL.

## Out of scope

- Adding tests for `ClaudeAdapter` / `CodexAdapter` / `GeminiAdapter` (those have existing coverage via `tests/test_agent_runtime_runner.py` and `tests/test_quality_dispatchers.py`).
- Changing `agent_runtime/registry.py` (no schema change needed).
- Changing `ai_agent_bridge/_channels_cli.py` (the channel-discuss path is already wired for all 5; this PR is about the CLI dispatch path).
- Updating dispatch.py legacy commands (`ask-grok`, `ask-deepseek` — that's a separate gap).
