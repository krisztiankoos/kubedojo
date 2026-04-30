# Chapter 63 — Tier 3 reader-aid review (Codex)

Reviewer: gpt-5.5, 2026-04-30

## Element 8: APPROVE skip

The skip is correct. `docs/research/ai-history/READER_AIDS.md:43` says Element 8 is skipped for every chapter until a non-destructive tooltip component exists.

## Element 9: REVISE

Do not approve the concept-only wording as submitted. I fetched the DistServe PDF and the preferred claim is split across multiple sentences. Use this verified replacement from the DistServe abstract instead.

Primary source: Zhong et al., DistServe, OSDI 2024, USENIX PDF: https://www.usenix.org/system/files/osdi24-zhong-yinmin.pdf

```markdown
:::note
> As a result, DistServe significantly improves LLM serving performance in terms of the maximum rate that can be served within both TTFT and TPOT constraints on each GPU.

This quote forces the metric down to per-GPU SLO-compliant work: the economic unit is not raw token flow, but requests that land inside TTFT/TPOT limits.
:::
```

Suggested anchor: after the paragraph at `src/content/docs/ai-history/ch-63-inference-economics.md:88` (the "DistServe's goodput framing matters because throughput alone can be misleading…" paragraph), **not** after the "DistServe separated the phases…" paragraph at line 90. That avoids adjacent repetition with the existing "optimized for goodput under service-level objectives" sentence.

## Element 10: REVISE

The paragraph at `src/content/docs/ai-history/ch-63-inference-economics.md:16` genuinely qualifies as symbolically dense: it stacks TTFT, TPOT, throughput, utilization, and goodput as abstract definitions. But the proposed aside is too long and overstates Orca/vLLM as "goodput" systems.

Use a tighter version:

```markdown
:::tip[Plain reading]
Keep two axes separate: TTFT and TPOT describe what one user feels, while throughput and utilization describe how full the system is. Goodput is the bridge between them: work only counts economically when it finishes inside the product's latency promise, so later speedup numbers should be read as paper-specific capacity claims under stated latency constraints.
:::
```

## Summary

| Element | Codex verdict | Action |
|---|---|---|
| 8 | APPROVE skip | Skip — bit-identity rule |
| 9 | REVISE | Land Codex's verified DistServe abstract verbatim, anchored after the "DistServe's goodput framing matters…" paragraph |
| 10 | REVISE | Land Codex's tighter wording (2-axis frame; goodput as bridge) |

**Tier 3 yield: 2 of 3 candidates landing** (1 SKIP-by-spec + 2 REVISEs applied).
