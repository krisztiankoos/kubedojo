# Chapter 58 — Tier 3 reader-aid proposal

Author: Claude (claude-opus-4-7), 2026-04-30

## Element 8 — SKIPPED (Tooltip component not available)

## Element 9 — Pull-quote

**SKIPPED.** Considered candidates:

1. *Sohl-Dickstein et al. 2015 abstract* on "iterative forward diffusion process… learn a reverse diffusion process that restores structure" — chapter paragraphs around line 24 already paraphrase this with the same content density, and Ho et al. 2020's reformulation makes the 2015 wording less load-bearing for modern readers.
2. *Ho et al. 2020 abstract* on "high-quality image synthesis" — chapter already includes the sample-quality emphasis; would be ornamental.
3. *Dhariwal & Nichol 2021 title* "Diffusion Models Beat GANs on Image Synthesis" — chapter at line 36 already names this title verbatim, so a callout would create adjacent repetition.
4. *Stability AI 2022 release post* on consumer-GPU feasibility — chapter at the closing section already describes this.

The chapter's load-bearing claims are made cleanly in the chapter's authorial voice, paired with a heavy Tier 2 math sidebar that already carries the symbolic weight. A pull-quote would be ornamental rather than evidentiary. Per the Ch48 / Ch52 / Ch54 precedents (where the math sidebar or the chapter's systems framing carried the load), I author-skip Element 9. Codex should be willing to REVIVE if it locates a sentence I missed that does *new* work — particularly a primary-source admission of a limitation, a labour/data-provenance acknowledgement, or a concrete number (e.g., the 4,000-A100 detail) stated in the original release.

## Element 10 — SKIPPED

The chapter's Tier 2 math sidebar carries the symbolic load (matching the Ch44 Word2Vec precedent and the Ch24 / Ch25 / Ch27 / Ch29 sidebar precedents). The prose body explains diffusion *conceptually* in natural language; no formula/derivation paragraphs are stacked in the prose itself. Plain-reading asides on top would only paraphrase already-natural-language prose.

## Summary

| Element | Author proposal | Rationale |
|---|---|---|
| 8 | SKIP | Bit-identity rule |
| 9 | SKIP | Math sidebar + chapter authorial voice carry the load (Ch48/52/54 precedent) |
| 10 | SKIP | Math sidebar carries symbolic load (Ch44 precedent) |

**Awaiting Codex adversarial review.** The math sidebar is dense; please verify the formulas are correct (especially the closed-form forward $\bar{\alpha}_t$, the reverse-step formula, and the CFG mixing equation). If any formula is wrong, FLAG in a "## Math sidebar verification" section like the Ch55 review.
