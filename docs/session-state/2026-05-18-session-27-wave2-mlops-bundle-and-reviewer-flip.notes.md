# Session 27 — late-arrival notes (post-handoff)

Sidecar to `2026-05-18-session-27-wave2-mlops-bundle-and-reviewer-flip.html`. Created after the main handoff committed; captures the T2-17 closure that landed minutes after the handoff was pushed.

## T2-17 closed in same session

The handoff documented T2-17 (module 5.10 production model-serving traffic patterns) as *in flight at handoff* — codex dispatch `bcu7x17za` was running when the user requested the session wrap. Codex completed ~minutes after the handoff commit; user opted to close it out in the same session rather than defer.

| | |
|---|---|
| PR | [#1328](https://github.com/kube-dojo/kube-dojo.github.io/pull/1328) |
| Merge commit | `106e5d28` |
| Module | `src/content/docs/platform/disciplines/data-ai/mlops/module-5.10-model-serving-traffic-patterns.md` |
| Lines | 2558 |
| Closes | #1304 Wave 2 T2-17 |

**Deepseek-v4-pro review path:**

- Round 1: 5/5 on 7 of 8 dimensions, one MUST-FIX — KServe install URL at line 1839 returned HTTP 404 (path `install/v0.17.0/kserve-knative-mode-full-install-with-manifests.sh` does not exist at the v0.17.0 tag). Deepseek verified two working alternatives and recommended the canonical `hack/setup/quick-install/` path.
- Inline fix: one-line URL swap to `hack/setup/quick-install/kserve-knative-mode-full-install-with-manifests.sh` (curl-verified HTTP 200). Committed as `79a7b6c9`. Inline (not dispatched) per `decision-card.md` "dead URLs → orchestrator fixes inline".
- Round 2: APPROVE high confidence in 60s.
- CI: 5/5 SUCCESS after `Incident dedup gate` cleared (took ~3 min after CodeQL).

**Nice-to-have deferred:** Line 2007 `SERVICE_HOSTNAME` extraction via `cut -d "/" -f 3` works for the common case; `jq`-based extraction would be more robust but doesn't block the lab.

## Updated session 27 totals

| | Pre-handoff | Including T2-17 |
|---|---|---|
| PRs merged | 4 | 5 |
| Net content lines | 6,136 | 8,694 |
| MLOps Discipline modules | 9 | 10 |
| Wave 2 #1304 progress | 3/9 | 4/9 |

## Wave 2 remaining (5 items)

| Item | Module | Path |
|---|---|---|
| T2-18 | Drift-triggered auto-retraining loop (5.11) | `platform/disciplines/data-ai/mlops/` |
| T2-19 | CML for ML CI (5.12) | `platform/disciplines/data-ai/mlops/` |
| T2-20 | Dapr + Buildpacks combined application-definition | `platform/toolkits/` |
| T2-23 | HCP Terraform workflow operations | `platform/toolkits/infrastructure-networking/iac-tools/` |
| T2-13 | Ansible operator arc (4-7 modules) | `platform/toolkits/infrastructure-networking/iac-tools/` |

Next session's first action: dispatch T2-18 drift retraining (continues the mlops sub-arc 5.7→5.8→5.9→5.10→5.11→5.12).
