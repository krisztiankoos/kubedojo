# Tier 3 Proposal: Chapter 38 — The Human API

Author: Claude (claude-sonnet-4-6)
Date: 2026-04-30

---

## Element 8 — Inline parenthetical definition (Starlight tooltip)

**Disposition: SKIPPED (globally)**

Per READER_AIDS.md, this element is skipped on every chapter until a non-destructive
tooltip component lands. Collapsible glossary (Tier 1, item 4) covers the same job.

---

## Element 9 — Pull-quote

**Disposition: SKIPPED**

**Rationale:** The chapter is narrative-historical throughout. Three sentences are
candidates for load-bearing weight:

1. "AWS described MTurk as reversing the normal request flow: a computer program could
   ask a human to perform a task and return results." — This is already paraphrased
   verbatim from the AWS announcement (G8) and the surrounding paragraph restates it.
   Duplicating it as a callout would create adjacent repetition, which is the spec's
   explicit refusal criterion (b).

2. "The intelligence in 'Artificial Artificial Intelligence' was never artificial all
   the way down." — The most rhetorically forceful sentence in the chapter, but it is
   also the chapter's own closing sentence. Extracting it into an immediately preceding
   callout would duplicate it within two lines of its prose context.

3. "That was the deeper significance of placing MTurk beside the other early AWS
   services." — Analytical synthesis, not a quotable claim; no primary source behind it.

No candidate sentence is simultaneously quote-worthy, non-verbatim in its immediate
context, and backed by a Green primary citation in sources.md. SKIPPED on all three
counts.

---

## Element 10 — Plain-reading asides (dense-paragraph asides)

**Disposition: SKIPPED**

**Rationale:** Ch38 is a narrative-historical chapter about a marketplace, a patent,
a product launch, and two empirical studies. There are no symbolically dense paragraphs
(no mathematical formulas, derivations, or abstract definitions stacked). The densest
passages are the patent-parameter paragraph (paragraph 4: "Those parameters are what
made the design more than a queue of odd jobs…") and the Snow et al. cost paragraph
("The economic results of this approach were striking…"), but both are dense with
historical detail and institutional mechanics — narrative density, not symbolic density.
Per READER_AIDS.md item 10: "Use only on paragraphs that are symbolically dense
(mathematical formulas, derivations, abstract definitions stacked) — not narratively
dense (history, biography, who-said-what)." Neither candidate qualifies.

SKIPPED: no paragraph in Ch38 is symbolically dense.

---

## Summary

| Element | Disposition | Reason |
|---|---|---|
| 8 (tooltip) | SKIPPED | Global skip per spec |
| 9 (pull-quote) | SKIPPED | All candidates fail criterion (b): verbatim or immediate adjacent repetition |
| 10 (plain-reading aside) | SKIPPED | No symbolically dense paragraphs; chapter is narrative-historical throughout |

No Tier 3 elements proposed for adversarial review. This is consistent with the
Part 5 guidance: "For Ch38 (Mechanical Turk), expect narrative-historical content
with light statistics. Default to SKIP unless surprising symbolic density appears."
