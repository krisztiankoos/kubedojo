# Module 2.5: SLIs, SLOs, and Error Budgets (Theory)

> **Complexity**: `[MEDIUM]` - Core SRE mental model
>
> **Time to Complete**: 20-30 minutes
>
> **Prerequisites**: Module 2.1 (What Is Reliability), Module 2.4 (Measuring and Improving Reliability)

---

## Outline
- Define SLIs and choose the right signals
- Set SLOs and compute error budgets
- Budget burn and alerting philosophy
- Design checklist for new services

---

## SLIs: Picking the Signal
- **Request-based**: success rate, latency percentiles (p50/p90/p99); best for user-facing APIs.
- **Event-based**: pipeline freshness, batch completion time; best for async jobs.
- **Coverage**: measure at the user boundary (ingress/load balancer) to capture full-path reliability, not just service internals.
- **Anti-patterns**: averages for latency, host-level metrics as proxies, or success counters without distinguishing error classes.

## SLOs and Error Budgets
- **SLO**: target over a window, e.g., `99.5% success over 28 days` or `p99 latency < 400ms`.
- **Error budget**: `1 - SLO`; for 99.5% over 28 days, budget = 0.5% of requests (~3h 22m of allowed error).
- **Window choice**: pair a long window (28–30d) for steadiness with shorter windows for responsiveness.

## Burn Rate and Alerting
- **Burn rate**: `(observed error rate) / (budget per unit time)`.
- **Multi-window alerts** (principle, tool-agnostic):
  - Fast burn (e.g., BR 14 over 1h) to catch acute failures.
  - Slow burn (e.g., BR 2 over 6h) to catch smoldering regressions.
- **Actionability**: page only when budget risk is real; route non-actionable detections to tickets/digests.

## Design Checklist
- Define the user journey and failure modes before picking metrics.
- Choose one primary SLI per journey; keep backup SLIs lean to avoid alert noise.
- Document assumptions: cache hit rates, dependency budgets, expected traffic shapes.
- Publish the SLO, budget, and burn thresholds alongside runbooks; review quarterly or when major changes ship.
