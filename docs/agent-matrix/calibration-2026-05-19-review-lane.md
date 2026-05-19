# Review-Lane Calibration — 2026-05-19

**Purpose**: Replace grok (DQ'd as reviewer per user 2026-05-19; see `feedback_grok_truncated_diff_context`, `feedback_grok_curriculum_gap_analysis_dq`) with a new model. Following the quality-ceiling-first protocol (`feedback_quality_ceiling_then_cost_walk_down`).

**Ground truth**: codex `gpt-5.5` NEEDS_CHANGES verdict on PR #1333 round-1 commit `6f541af2`, with three specific findings:
- **F1**: `.github/workflows/zizmor.yml` missing `--strict-collection` flag (silently passes on unparseable workflows)
- **F2**: zizmor scan command targets only `.github/workflows/` while trigger paths include `.github/actions/` (scope gap)
- **F3**: `.github/dependabot.yml` missing `cooldown` (zizmor `dependabot-cooldown` audit fires; mitigates tag-mutation attacks)

**Methodology**: each candidate dispatched via `hermes --provider openrouter -m <model> -z "<diff + neutral prompt>"`. Prompt explicitly framed as adversary security review; did NOT mention codex's findings to avoid bias. Each candidate scored on (a) verdict match, (b) per-finding catch, (c) novel valid findings, (d) hallucinations.

**Test input**: PR #1333 round-1 diff (3086 chars, 5 files), captured to `/tmp/calib-diff.patch`. Outputs persisted as `/tmp/calib-{round}-{n}-{slug}.txt`.

---

## Round 1 — Quality ceiling (5 candidates, 3 vendors)

| Model | Latency | $in/M | $out/M | Verdict | F1 | F2 | F3 | Novel valid | Halluc |
|---|---:|---:|---:|:-:|:-:|:-:|:-:|---|---|
| `qwen/qwen3.6-plus` | 32s | 0.33 | 1.95 | ✓ | ✗ | ✗ | ✗ | pip-pin | — |
| `qwen/qwen3.6-27b` | 128s | 0.32 | 3.20 | ✓ | ✗ | ✗ | ✗ | pip-pin, GH_TOKEN | **fake `actions/cache@v4`** |
| `moonshotai/kimi-k2.6` | 396s | 0.73 | 3.49 | ✓ | ✗ | **✓** | ✗ | pip-pin | — |
| `z-ai/glm-5.1` | 134s | 0.98 | 3.08 | ✓ | ✗ | ✗ | ✗ | pip-pin (best fix) | — |
| `qwen/qwen3-max` | 19s | 0.78 | 3.90 | ✓ | ✗ | **✓** | ✗ | — | — |

### Critical observations

1. **0/5 caught F1** — codex's `--strict-collection` finding requires deep zizmor knowledge (failure mode is "unparseable workflow exits 0"). No candidate surfaced it.
2. **0/5 caught F3** — this is a **methodology gap, not a model gap**. Codex caught F3 by *running* zizmor and observing the `dependabot-cooldown` audit fire. Candidates received the diff text only; no tool execution. Not a fair point against them. To close this gap, future calibration prompts should include "run zizmor on the diff" as an optional capability if the model supports tool-use.
3. **4/5 surfaced a real issue codex missed**: the unpinned `pip install zizmor` in `.github/workflows/zizmor.yml`. This is the *same supply-chain attack class* PR #1333 defends against. **Codex's APPROVE on round 2 of PR #1333 is therefore incomplete** — we should fix this in a follow-up PR. Tracked as task #11.
4. **One candidate hallucinated**: `qwen/qwen3.6-27b` fabricated a finding about a "pre-existing unpinned `actions/cache@v4`" in `uk-quality-checks.yml`. That action is not in the workflow. **False-positive confidence is disqualifying for a reviewer** — auto-merge would treat the fabrication as ground truth.

### Round 1 winner

`moonshotai/kimi-k2.6` — 2 valid findings (F2 + pip-pin), no hallucinations, only candidate to match both. Cost on this PR ≈ $0.03. Latency 396s is the slowest in the set — worth tracking.

---

## Round 2 — Cost walk-down within kimi family (4 variants)

Per protocol, with one round-1 full-match and cheaper variants existing, round 2 tests whether kimi-family cheaper variants preserve k2.6's quality.

| Model | Latency | $in/M | $out/M | F2 caught | pip-pin caught | Halluc | Match k2.6? |
|---|---:|---:|---:|:-:|:-:|---|:-:|
| **`moonshotai/kimi-k2.5`** | **205s** | **0.40** | **1.90** | **✓** | **✓** | — | **✅ FULL MATCH** |
| `moonshotai/kimi-k2-thinking` | 93s | 0.60 | 2.50 | ✗ | ✓ | — | ✗ |
| `moonshotai/kimi-k2-0905` | 43s | 0.60 | 2.50 | ✗ | ✓ | — | ✗ |
| `moonshotai/kimi-k2` | 37s | 0.57 | 2.30 | ✗ | ✗ | **fake "persist-credentials weakens security"** | ✗ DQ'd |

### Round 2 winner

**`moonshotai/kimi-k2.5`** at $0.40/$1.90 (262k ctx, 205s).

Versus round-1 winner k2.6:
- **Quality**: equal (same findings, no hallucinations)
- **Cost**: 46% cheaper on output ($1.90 vs $3.49)
- **Latency**: 48% faster (205s vs 396s) — bonus
- **Context**: same 262k

Cleanest possible round-2 outcome: a cheaper, faster variant matches the ceiling exactly.

---

## Recommendation

**Review-lane primary reviewer (replacing grok)**: `moonshotai/kimi-k2.5` via `hermes --provider openrouter -m moonshotai/kimi-k2.5`.

**Important scope caveat**: this calibration was on **a small security PR (3KB diff)**. Generalizing to large content-module reviews (>1k lines) is unwarranted without a separate calibration. The memory `feedback_deepseek_pro_for_module_reviews` claims qwen-3.6 is preferred for >1k bodies — that claim is **untested** by this round and should NOT be conflated with this result.

**Pending separate calibrations** (do not assume kimi-k2.5 wins everywhere):
- Content-module review lane (>1k lines, prose-heavy) — qwen vs kimi vs deepseek
- Edit / draft lane (code generation) — qwen3-coder vs others
- Search lane (cheap+fast) — kimi-k2.5 likely too expensive; qwen3.6-flash or deepseek-v4-flash candidates

## Costs incurred for this calibration

- Round 1: 5 dispatches × ~6k tokens output @ avg $3/M ≈ $0.10
- Round 2: 4 dispatches × ~5k tokens output @ avg $2.30/M ≈ $0.05
- **Total: ~$0.15 USD**

Negligible. Calibration discipline scales.

---

## Methodology issues flagged for next round

1. **No tool-use in candidates** — gave the candidates the diff text only. Codex caught F3 (cooldown) because it ran zizmor. Next round: if a candidate model supports tool-calling via hermes, include "you may run zizmor on the diff" as an optional step. Levels the field.
2. **Single-PR ground truth** — n=1 is signal, not proof. Quality-first decisions should ideally have 2-3 ground-truth PRs across different categories. We accept n=1 for the grok-removal urgency but flag the limitation.
3. **Ground truth itself was incomplete** — codex's APPROVE missed the pip-pin issue. Future calibrations should use a *constructed* ground truth (multi-model consensus on actual findings) rather than one reviewer's verdict.
