# Codex routing tier smoke tests — bridge auth path

Confirms `gpt-5.4-mini` and `gpt-5.3-codex-spark` are operational on the bridge auth path (`codex exec`) before promoting `dispatch_smart.py --agent codex` task-class routing (PR #872) to the default for cheap codex work.

## Results — 2026-05-05 01:57 CEST

| Model | Wall | Tokens | Stdout |
|---|---|---|---|
| `gpt-5.4-mini` | 6.4s | 780 | `hi from mini` |
| `gpt-5.3-codex-spark` | 4.8s | 11,332 | `hi from spark` |

Both runs invoked sequentially (per `feedback_codex_dispatch_sequential.md` — concurrent codex dispatches silently die with empty stdout/stderr). Auth path: `codex exec -m <model> "<prompt>" --skip-git-repo-check --sandbox read-only`. No 403 / quota errors.

This unblocks the routing PR. The empirical task-class mapping (`feedback_codex_model_routing.md`) — `search`→mini, `edit`/`draft`→spark, `review`/`architect`→gpt-5.5 — is now safe to ship as the codex default.

## Carryover context

This smoke test was queued during the 2026-05-03 → 2026-05-04 codex-out window (Codex out of weekly quota) and unblocked when codex came back online ~22:50 local on 2026-05-04. Smoke tests were re-confirmed on 2026-05-05 at the start of the next session.
