# DECISION RECORD — Gap-fill plan post-synthesis

**Date**: 2026-05-17
**Channel**: inline chat (user online), no `ab discuss` needed (asymmetric trust — deepseek baseline, grok DQ for curriculum)
**GH umbrella**: [#1299](https://github.com/kube-dojo/kube-dojo.github.io/issues/1299)
**Inputs**:
- `audit/gap-analysis-2026-05-17/grok-report.html` (down-weighted)
- `audit/gap-analysis-2026-05-17/deepseek-report.html` (trusted baseline)
- `docs/research/gap-plan-2026-05-17.html` (synthesis)

## Decisions locked

| # | Question | Decision | Rationale |
|---|---|---|---|
| D1 | GitHub Actions dedicated module (T2-12) | **Cut entirely** | Referenced in 10+ files. Risk of producing a "10 most common Actions" listicle is high. Event-driven CI mental model folds into Modern DevOps as cross-cut. Per `feedback_teaching_not_listicles`. |
| D2 | Dapr + Buildpacks (T2-20) — split or combined | **Keep combined** | One "application definition beyond Helm" module with both as worked examples. Pedagogically richer than two thin modules. 1 codex call. |
| D3 | Docker absolute-beginner arc | **Cut + audit cloud-native-101** | Cloud-native-101 has no critical-rubric modules (verified via `/api/quality/scores`). No rewrite needed; cut entirely from gap list. |
| D4 | Cost lens execution (T2-9) | **Checklist-only first** | Add cost-lens checklist to `scripts/prompts/module-writer.md`. Revisit framing module after 5 modules use it. Cheap, revertible. |
| D5 | Priority — GCP audit vs Streaming ops first | **GCP audit first (now complete)** | 12 GCP modules already exist (~860 lines avg) — at AWS parity. **Net-new GCP gap eliminated.** Streaming ops Tier 1 advances. |

## Bonus findings during decision execution

- **GCP net-new gap dropped**: 12 modules already shipped at full size (~10,268 total lines). Removed from gap inventory.
- **gRPC/Envoy downgraded T2 → T3**: deepseek's "over-scoped" verdict accepted; Istio + service-mesh tracks substantially cover.
- **Harness/Symphony removed from inventory**: shipped as PRs #1220 + #1221 (modules 2.1 + 2.2 in `ai/ai-native-work/`).
- **Quality-floor gate shifted**: Platform Disciplines 65→44, Platform Toolkits 52→35, CKS 29→11 — three previously rewrite-first tracks are now writeable.

## Outputs (in progress)

1. **Decision Card recorded** (this file).
2. **Tier 1 per-module GH sub-issues filed** under #1299 (5 issues: Cloud Custodian, Azure App Gateway, Azure App Service, Streaming ops × 2).
3. **Tier 2 + net-new tracking issue** filed with checklist (single issue listing 19 modules under deepseek-verified backlog).
4. **`scripts/prompts/module-writer.md`** updated with cost-lens checklist (per D4).
5. **`docs/research/content-gaps-2026-05.md` + `gap-triangulation-roadmap-2026-05.html`** updated to reflect decisions.
6. **Codex writer dispatches** beginning with Cloud Custodian (highest-signal T1, 0 corpus mentions).

## Reviewer cascade (unchanged)

- Primary: grok-4 (xai-oauth via hermes) — `KUBEDOJO_388_PRIMARY_REVIEWER=grok`
- Fallback: claude-sonnet-4-6 via `dispatch_smart.py review --agent claude`
- Workspace mode: codex danger, per-issue worktree via `agent_runtime.runner.invoke`

## Surface protocol

User online → decision recorded inline (this file) + GH umbrella comment. No ab discuss escalation needed (deepseek/grok asymmetry didn't produce material disagreement on locked items).
