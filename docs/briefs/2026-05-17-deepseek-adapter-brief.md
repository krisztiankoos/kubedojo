# DeepSeek V4 (Pro + Flash) — Production Adapter Brief

**Owner**: codex (gpt-5.5, danger mode)
**Worktree**: `.worktrees/deepseek-adapter`
**Branch**: `feat-deepseek-adapter`
**Precedent**: PR #1245 (`c490d19b feat(agents): integrate Grok-4 (xai-oauth via hermes) as full peer agent`)

## Why

Last session (PR #1285, session-21) added **DeepSeek V4 Pro + Flash** to the production roster via hermes (replacing dropped Mistral 3.5). Calibration showed Pro as **gold-tier reviewer** tied 5/5 with claude on content review; Flash is the cheap planner/architect lane. But **only the calibration ran** — the production-dispatch wiring never landed. The agent is not in `scripts/agent_runtime/registry.py`, not in `scripts/ai_agent_bridge/_channels_cli.py`, and cannot be dispatched via `agent_runtime.runner.invoke` or via channel-based `ab discuss` sessions today.

This brief closes that gap so DS is a first-class peer to codex / claude / gemini / grok.

## What changed

### 1) New file: `scripts/agent_runtime/adapters/deepseek.py`

Near-clone of `scripts/agent_runtime/adapters/grok.py`. Both adapters wrap `hermes -z`. Differences from Grok:

- **Provider**: `deepseek` (hermes API-key provider). DeepSeek API key is already in `~/.hermes/.env` (`hermes status` confirms: `DeepSeek ✓ sk-0…9d01`). Pass `--provider deepseek` instead of `--provider xai-oauth`.
- **Default model**: `deepseek-v4-pro`. Override via env `AB_DEEPSEEK_MODEL` (e.g. set to `deepseek-v4-flash` for the cheap lane).
- **Class name**: `DeepSeekAdapter`, `name = "deepseek"`.
- **Resume policy**: `never` (mirrors grok — hermes session semantics across worktrees are the same footgun).
- **Rate-limit patterns**: same regex set as grok (DeepSeek returns HTTP 429 like everyone; hermes surfaces it the same way).
- **Toolsets per mode**: identical to grok (`web` for read-only; `web,file,terminal,code_execution,todo` for workspace-write; same + `memory,skills` for danger).
- **Tool config keys honored**: same as grok — `isolated`, `toolsets`, `provider` (defaults to `deepseek`), `effort`, `yolo`, `accept_hooks`.

Keep the docstring contract identical to grok.py's (just swap "xai-oauth" → "deepseek", "grok-4" → "deepseek-v4-pro", drop the grok-writer-DQ note). Add a calibration footnote referencing `audit/2026-05-17-deepseek-mistral-calibration/REPORT.html`:

```
Calibration (2026-05-17): Pro tied 5/5 with claude on content review; gold-tier
reviewer. Hallucination rate 3/4 on code — caller should not promote a DS Pro
claim to Green without independent verification (curl+pdftotext+grep) for
factual claims (mirrors gemini hallucination policy per
[[feedback_gemini_hallucinates_anchors]]). Flash is 3× faster than Pro;
suited for plan / architect / UK translation lanes.
```

### 2) Update `scripts/agent_runtime/registry.py`

Add a fifth entry, ordered alphabetically before `gemini`:

```python
"deepseek": {
    "adapter": "scripts.agent_runtime.adapters.deepseek:DeepSeekAdapter",
    "default_model": os.environ.get("AB_DEEPSEEK_MODEL", "deepseek-v4-pro"),
    "cost_tier": "low",  # hermes-routed; cheaper than codex/claude/grok per-call
    "capabilities": frozenset({
        "code_review",
        "content_review",
        "adversarial_review",
        "research",
        "deliberation",
        "architecture",
    }),
    "cli_available": True,
    "resume_policy": "never",
},
```

Rationale for capabilities: Pro calibration showed 5/5 on review + content_review + research + architect + UK translation. Flash got 10/10 across all 10 roles in 11 minutes. So both share the cap set; the model-pick distinguishes (callers pass `model="deepseek-v4-flash"` for the cheap lane).

### 3) Update `scripts/ai_agent_bridge/_channels_cli.py`

Add `"deepseek"` to:
- `_DISCUSSION_CLARIFICATION_MODES` — value `"yolo"` (matches grok)
- `_DISCUSSION_RUNTIME_MODES` — value `"workspace-write"` (matches grok)

Extend `_agent_runtime_mode`:

```python
if agent_name == "deepseek":
    if sandbox_mode == "read-only":
        return "read-only"
    return "workspace-write"
```

Extend `_agent_tool_config` with the same sandbox-aware toolset / yolo gating that grok uses (the gemini-pro adversarial review on PR #1245 caught the hardcoded-write-tools bug — apply the same fix preventively to DS):

```python
if agent_name == "deepseek":
    if sandbox_mode == "read-only":
        ds_tc: dict[str, object] = {
            "toolsets": "web",
            "yolo": False,
        }
    else:
        ds_tc = {
            "toolsets": "web,file,terminal,code_execution,todo",
            "yolo": True,
        }
    return ds_tc
```

### 4) Tests

Mirror the grok test file layout if one exists (check `tests/test_agent_runtime_runner.py` and `tests/test_quality_dispatchers.py`). If grok-specific tests don't exist beyond `test_quality_dispatchers.py:33`'s negative-list, write a minimal `tests/test_deepseek_adapter.py`:

- `test_build_invocation_read_only` — verifies `-z prompt -m deepseek-v4-pro --provider deepseek -t web` (no `--yolo`).
- `test_build_invocation_workspace_write` — verifies `--yolo` present, toolset string is `web,file,terminal,code_execution,todo`.
- `test_build_invocation_danger` — verifies `memory,skills` are in the toolset.
- `test_model_override` — caller-passed `model="deepseek-v4-flash"` propagates to `-m`.
- `test_parse_response_strips_hermes_banner` — Python-project banner is stripped.
- `test_parse_response_detects_rate_limit` — `rate_limited=True` when stderr contains "rate limit".

Use the grok test as a template if it exists; otherwise write fresh.

### 5) Smoke verification (in your final commit message)

After landing the code, paste verbatim output of:

```bash
.venv/bin/python -c "
from scripts.agent_runtime.registry import AGENTS, available_agents
assert 'deepseek' in AGENTS, 'deepseek not registered'
assert AGENTS['deepseek']['cli_available']
print('registered:', sorted(available_agents()))
"

# Live smoke: must respond "PONG"
timeout 30 hermes -z 'Respond with exactly one word: PONG' -m deepseek-v4-pro --provider deepseek
timeout 30 hermes -z 'Respond with exactly one word: PONG' -m deepseek-v4-flash --provider deepseek
```

Both PONG responses MUST be in the PR body.

### 6) Changelog + memory note

- Add an entry to `changelog.md` (or wherever the existing grok integration entry lives — `git log -- changelog.md | grep -i grok` should find it).
- Do NOT update memory; orchestrator owns memory updates.

## Constraints

- **Single PR.** Title: `feat(agents): integrate DeepSeek V4 (Pro + Flash, hermes API-key) as full peer agent`. Base `main`. Closes nothing directly.
- **Mode**: danger (per `feedback_codex_danger_for_git_gh.md` — git push + gh pr create need danger).
- **Three-way agreement** (per `feedback_three_way_rule_agreement.md`): the adapter file + the registry entry + the channels-cli wiring + tests must all be in ONE commit. Don't split — if a future reader greps for "deepseek" in `scripts/`, all three sites must be in sync.
- **No memory writes** (orchestrator-only).
- **No `--no-verify`** on git commits.
- **Run the test suite** before pushing: `.venv/bin/pytest tests/test_agent_runtime_runner.py tests/test_quality_dispatchers.py tests/test_deepseek_adapter.py -q`. 0 failures required.
- **Push to remote and open the PR.** End your run by printing the PR URL.

## Out of scope

- Extending `dispatch_smart.py` SUPPORTED_AGENTS to include deepseek. Different change, separate PR.
- Updating ai-history dispatcher matrices.
- Writing the actual DS calibration audit committed to the repo (the audit dir is gitignored on disk).
- Mistral cleanup (already dropped this session).
