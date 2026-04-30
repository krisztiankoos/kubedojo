# Tier 3 Review — Chapter 55: The Scaling Laws

Reviewer: Codex (gpt-5.5)
Date: 2026-04-30
Reviewing: tier3-proposal.md by Claude (claude-opus-4-7)

## Element 8 — Inline parenthetical definition
Author verdict: SKIPPED — Tooltip component is not available; `<abbr>` would modify prose and violate bit-identity.
Reviewer verdict: APPROVE
I approve the skip. The spec makes Element 8 skipped on every chapter until a non-destructive tooltip component exists, and the Tier 1 glossary already defines cross-entropy loss, power law, N/D/C, compute-optimal training, sample efficiency, the Bitter Lesson, and the Kaplan-vs-Chinchilla allocation without touching verified prose.

## Element 9 — Pull-quote
Author verdict: PROPOSED — Sutton 2019 "Bitter Lesson" opening sentence after the paragraph introducing Sutton's philosophical setup.
Reviewer verdict: REVISE
The Sutton sentence should land, but with a shorter annotation. It is primary, quote-worthy, and not verbatim-repeated in the prose. The adjacent paragraph paraphrases Sutton's thesis, but the pull-quote still does new work by preserving the force of the sentence's closing phrase and marking the claim as philosophical backdrop rather than Kaplan-style measurement.

Use Sutton's complete opening sentence from this anchor. Compliant excerpt:

> The biggest lesson that can be read from 70 years of AI research is that general methods that leverage computation are ultimately the most effective...

New annotation: This provenance matters: Sutton's blog framed a research instinct, not a fitted law; Kaplan later supplied the measured loss curves.

Primary anchor: Sutton 2019, "The Bitter Lesson," opening paragraph.

Do not revive the Kaplan abstract alternative. It is primary and chapter-central, but the chapter already says Kaplan reported power-law relationships with model size, dataset size, and training compute and immediately notes the abstract's seven-orders-of-magnitude framing. A pull-quote there would mostly restate adjacent prose.

## Element 10 — Plain-reading aside
Author verdict: SKIPPED — Math sidebar carries the symbolic load; prose already explains the equations in natural language.
Reviewer verdict: APPROVE
I approve the skip. The chapter has a real math sidebar, but the prose body is explanatory rather than symbolically dense: the N/D/C bottleneck paragraphs, compute-optimal training paragraphs, and Chinchilla correction all unpack the ideas in plain language. A `:::tip[Plain reading]` aside would repeat rather than clarify.

## Summary
- Approved: Element 8 skip; Element 10 skip
- Rejected: None
- Revised: Element 9 pull-quote annotation
- Revived: None

## Math sidebar verification
The Kaplan values are mostly correct, but the compute exponent needs notation tightening. Kaplan §1.2 gives `alpha_N ~ 0.076`, `alpha_D ~ 0.095`, and `alpha_C^min ~ 0.050` for optimally allocated compute `C_min`; Appendix A/Table 5 also lists a separate naive/fixed-batch `alpha_C = 0.057`. The sidebar should therefore write the compute law as `L(C_min) \propto C_min^{-alpha_C^min}` with `alpha_C^min \approx 0.050`, or use `alpha_C \approx 0.057` if it means the naive fixed-batch compute trend.

The compute-optimal allocation exponents are correct: Kaplan §1.2 / Eq. 1.7 says `N_opt \propto C_min^0.73`, `B \propto C_min^0.24`, and `S \propto C_min^0.03`; the paper also gives `D_opt \propto C_min^0.27` for one epoch.
