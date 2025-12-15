# Module 4.3: Release Strategies (Theory)

> **Complexity**: `[QUICK]` - Patterns and trade-offs
>
> **Time to Complete**: 15-20 minutes
>
> **Prerequisites**: Module 4.1 (CI/CD), Module 4.2 (Application Packaging)

---

## Outline
- Core rollout patterns
- Signals for safe promotion/rollback
- Config and image versioning basics
- Mental model: traffic cop for releases—green light (roll), yellow (canary), red (rollback).
- Choose-your-pattern: match risk appetite and blast radius.

---

## Core Patterns
- **Rolling update**: Gradual replacement; default in Deployments. Good for most cases; watch readiness to avoid serving bad pods.
- **Blue/Green**: Run old (blue) and new (green) in parallel; switch traffic via Service/Ingress change. Fast rollback, higher resource cost.
- **Canary**: Send a small percent to the new version first (via labels/Service subsets/Ingress routes). Detect issues before full rollout.

## Promotion Signals
- **Readiness probes** gating Service Endpoints.
- **Metrics**: error rates, latency, saturation (CPU/memory), and user-facing checks.
- **Observability hooks**: logs/metrics/traces per version to spot regressions.

## Rollback Cues
- Rising 4xx/5xx, probe failures, increased latency, or saturation impacting SLOs.
- Keep previous version and config ready to restore; for Helm, `helm rollback <release> <rev>` (concept).

## Versioning Hygiene
- **Images**: Use immutable digests; avoid `latest`.
- **Config**: Separate config from images (ConfigMaps/Secrets) and version it. Coordinate config changes with rollouts to avoid mismatches.

> **Exam mindset**: Recognize patterns, when to use them, and what signals drive promotion or rollback. KCNA focuses on concepts, not full pipelines.

```
ASCII GUIDE
Traffic  --> [Service/Ingress]
             |-- Blue (v1) --|   # steady
             |-- Canary (v2) |   # small % first
             |-- Green (v2)  |   # full switch when ready
```

| Pattern | Use When | Risk Control |
|---------|----------|--------------|
| Rolling | Default change, low risk | Readiness probes + metrics |
| Blue/Green | Need instant rollback | Two stacks; flip traffic |
| Canary | Uncertain change | Start small; watch error/latency before 100% |

> **Reality check**: A canary without signals is just a smaller blast. Always pair the pattern with the metrics you’ll trust.
