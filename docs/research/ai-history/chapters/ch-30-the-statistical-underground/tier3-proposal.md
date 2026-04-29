# Tier 3 Proposal: Chapter 30 — The Statistical Underground

Author: Claude (Sonnet 4.6)
Date: 2026-04-30
Status: PROPOSED — awaiting cross-family adversarial review

---

## Element 1 — Pull-quote

**Verdict: PROPOSED**

**Candidate sentence** (from "The Noisy-Channel Contract" section, paragraph beginning "The price of that clarity"):

> "Speech recognition did not become easy. It became a place where probability could replace hand confidence with numeric uncertainty."

**Insertion anchor:** Immediately after the paragraph ending "…numeric uncertainty." (the closing paragraph of the "The Noisy-Channel Contract" section).

**Annotation (1 sentence):** This formulation — turning uncertainty into a measurable quantity rather than an obstacle — is the chapter's load-bearing intellectual move, and the sentence is not quoted elsewhere in the prose.

**Rationale for PROPOSED:** The sentence is genuinely quote-worthy: it names the cultural shift from symbolic hand-confidence to probabilistic engineering in the most compressed form the chapter achieves. It does not appear as a blockquote or set-off quotation in the surrounding prose, so there is no adjacent-repetition problem (the Ch01 refusal ground). The annotation adds provenance work (framing it as the chapter's thesis-sentence) rather than paraphrase.

---

## Element 2 — Dense-paragraph aside (Plain reading)

**Verdict: SKIPPED**

The chapter's "The Noisy-Channel Contract" section does contain the Bayes decomposition into language-model probability and acoustic-channel probability, and "Markov Models and Search" names Viterbi, dynamic programming, and stack search. However, neither section is *symbolically* dense in the Tier 3 sense: there are no inline mathematical formulas, derivations, or stacked abstract definitions. The prose explains each concept in plain language without using LaTeX or notation blocks. A `:::tip[Plain reading]` aside would merely paraphrase surrounding prose already written accessibly — exactly the refusal condition in READER_AIDS.md §Tier 3, item 10.

**Rationale for SKIPPED:** No paragraph in Ch30 crosses the symbolically-dense threshold that justifies a Plain-reading aside. The prose is narratively dense (history, measurements, model names) but not symbolically dense. Adding asides would produce filler.

---

## Element 3 — Inline parenthetical definitions (Starlight tooltip)

**Verdict: SKIPPED**

Per READER_AIDS.md §Tier 3, item 8: this element is SKIPPED on every chapter until a non-destructive tooltip component lands. The Plain-words glossary (Tier 1, item 4) covers the same job.

---

## Summary table

| Element | Decision | Reason |
|---|---|---|
| Pull-quote (noisy-channel thesis sentence) | PROPOSED | Genuinely quote-worthy; no adjacent repetition; annotation does new work |
| Dense-paragraph aside (Plain reading) | SKIPPED | No symbolically dense paragraphs; prose is already plain |
| Inline tooltip | SKIPPED | Universal skip per READER_AIDS.md until tooltip component exists |
