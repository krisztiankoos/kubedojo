# Tier 3 Proposal: Chapter 39 — The Vision Wall

Author: Claude (claude-sonnet-4-6)
Date: 2026-04-30
Status: awaiting adversarial review (ask-codex)

---

## Element 8 — Inline parenthetical definition (Starlight tooltip)

**Disposition: SKIPPED (globally)**

Per READER_AIDS.md §Tier 3 item 8: this element is SKIPPED on every chapter until a non-destructive Astro `<Tooltip>` component lands. The plain-words glossary (Tier 1, item 4) covers the same job.

---

## Element 9 — Pull-quote

**Disposition: SKIPPED**

**Rationale:**

Three candidate sentences were evaluated:

1. *"The benchmark was no longer a neutral window onto the visual world. It was a visual world with its own texture."* (paragraph on dataset signatures, ~halfway through the chapter)
   - Quote-worthy phrasing. However, the surrounding prose already builds to this conclusion across two adjacent paragraphs, and the sentence immediately following provides the explanation. Extracting it as a callout would create near-adjacent repetition with the prose that sets it up and the prose that completes the thought. Rejected on adjacent-repetition grounds.

2. *"The car number is useful because it refuses both comforting stories."* (paragraph on 53.4% vs 27.5% AP)
   - The prose paragraph already walks through both numbers and both comforting stories in the sentences that follow. The sentence functions as a topic sentence, not a standalone insight. Extracting it would duplicate the paragraph's opening without doing new work. Rejected.

3. *"Maintenance was the product."* — not present in Ch39 (that sentence belongs to Ch28). Confirmed absent from Ch39 prose.

No candidate sentence is genuinely quote-worthy without creating adjacent repetition. **SKIPPED.**

---

## Element 10 — Plain-reading asides (dense-paragraph asides)

**Disposition: SKIPPED**

**Rationale:**

Ch39 describes mathematical concepts (SIFT invariance, HOG gradient histograms, SVM margins, Average Precision) but does so in narrative prose rather than symbolic notation. The chapter contains no displayed mathematical formulas, no derivations, and no stacked abstract definitions. The closest candidate paragraphs are:

- The SIFT pipeline paragraph (keypoint extraction → nearest-neighbour matching → Hough-transform clustering → pose verification): this is algorithmically described in plain English with no symbolic density. The paragraph is procedural-narrative, not formula-dense.
- The AP numbers (53.4%, 27.5%): these are cited figures, not symbolic derivations. The prose explains them in the same paragraph.
- The "1 LabelMe car sample is worth 0.26 PASCAL car samples" finding: again a cited empirical number explained in prose context.

None of these paragraphs meet the threshold for a plain-reading aside: *symbolically dense (mathematical formulas, derivations, abstract definitions stacked)*. All are narrative-dense or procedurally-narrative. **SKIPPED.**

---

## Summary

| Element | Disposition | Reason |
|---|---|---|
| 8 — Tooltip | SKIPPED | Globally deferred per spec |
| 9 — Pull-quote | SKIPPED | No candidate avoids adjacent repetition |
| 10 — Plain-reading asides | SKIPPED | No symbolically dense paragraphs in prose |
