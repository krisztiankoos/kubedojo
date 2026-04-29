# Tier 3 adversarial review — Codex (gpt-5.5)

Bridge message: claude → codex, task `394-ch01-tier3-codex-review`, response received 2026-04-29T06:05:34Z.

---

## Codex's verdicts (verbatim)

> **2 Pull-quote: REVISE.** The sentence is already quoted verbatim in the existing paragraph at line 99, so placing the pull-quote immediately after creates adjacent repetition. If you still want the typographic event, make the note's commentary do new work and keep it short, or move it before the paragraph as a preview. Do not claim the prose only paraphrases it.
>
> **3a Plain reading after `$x^2 = x`: APPROVE,** with a light trim. This is the strongest aid: it clarifies the inference direction rather than just defining terms. Keep the "ordinary arithmetic → only 0 and 1 → logical boundary classes" sequence.
>
> **3b Plain reading after `$x + y(1 - x)`: REVISE.** The existing paragraph already says almost exactly this: modern inclusive-OR, read it slowly, all of `x` plus the part of `y` not already in `x`, no double-counting. To earn the interruption, make the aside more visual and less duplicative, e.g. "In a Venn diagram, shade all of `x`; then shade only the unshaded part of `y`." Otherwise reject as filler.
>
> **Skipped tooltip and Jevons aside: agree with skip.**

---

## Decisions and rationale

| # | Element | Codex verdict | Action taken | Why |
|---|---|---|---|---|
| 1 | Inline tooltip | AGREE with skip | **SKIP** | Starlight has no tooltip component; HTML `<abbr>` violates bit-identity. Both reviewers agree. |
| 2 | Pull-quote | REVISE | **SKIP after attempting revise** | The contract template requires the callout *after* the paragraph the quote comes from, but the prose already quotes the full sentence verbatim ("It is a consequence of the fact that the fundamental equation of thought is of the second degree…"). Any insertion immediately after creates adjacent repetition. Moving before would break the template. New commentary cannot avoid the duplication of the quote itself. The honest call is to skip — the chapter prose already gives the sentence its typographic weight via direct quotation. |
| 3a | Plain reading after $x^2 = x$ | APPROVE with light trim | **APPLY (lightly trimmed)** | Codex's "strongest aid" verdict. Tightened by removing one filler sentence; kept the inference-direction sequence. |
| 3b | Plain reading after $x + y(1 - x)$ | REVISE → Venn-diagram framing | **APPLY (revised)** | Replaced the prose-paraphrase framing with the Venn-shading instruction Codex suggested. The aside now does work the surrounding prose does not. |
| 3c | Plain reading after Jevons paragraph | AGREE with skip | **SKIP** | Both reviewers agree the paragraph is narratively dense, not symbolically dense. |

---

## Final landed elements

1. `:::tip[Plain reading]` after the Chapter III $x^2 = x$ derivation paragraph (line 95 in the pre-Tier-3 file).
2. `:::tip[Plain reading]` after the Chapter IV $x + y(1 - x)$ workaround paragraph (line 105 in the pre-Tier-3 file), with Venn-shading framing.

Two of five proposed elements landed. Three were skipped on principle (tooltip infrastructure absent, pull-quote duplicative, Jevons paragraph narratively but not symbolically dense). The Codex review actively pruned one element (pull-quote) and substantially improved another (3b).

This is the workflow the prototype is supposed to demonstrate: Tier 3 is *selective* — its components apply only when they earn their interruption. Forced Tier 3 elements produce filler, and the adversarial review caught and rejected exactly one such case.
