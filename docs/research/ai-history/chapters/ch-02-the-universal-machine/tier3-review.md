# Tier 3 review — Chapter 2: The Universal Machine

Reviewer: Codex (cross-family adversarial)

## Element 1 — Pull-quote (`:::note`, ≤1 per chapter)

**Verdict: AGREE**

Agree with the skip. The chapter's strongest quotable sentences are already quoted in the prose, and READER_AIDS.md explicitly refuses pull-quotes when the source paragraph already quotes the sentence verbatim. A pull-quote here would create adjacent repetition rather than reader aid.

## Element 2 — Plain-reading aside after Gödel arithmetisation paragraph

**Verdict: REJECT**

The target paragraph is symbolically dense enough to qualify for consideration, but the proposed aside repeats work the prose already does. The prose already states the numbering move, the self-unprovability construction, both proof/negation branches, the consistency condition, and the conclusion that arithmetical truth outruns formal provability. The draft also exceeds the Tier 3 cap of 1-3 sentences.

There is a precision risk as well: the chapter has already noted Gödel's Theorem VI under omega-consistency, while the aside's "never contradicts itself" phrasing compresses that into plain consistency. Because the existing paragraph is already unusually clear, this is not worth landing as a revision.

## Element 3 — Plain-reading aside after §11 reduction paragraph

**Verdict: REJECT**

Reject. The proposed aside is a clean explanation of reduction, but it duplicates the chapter's own two-paragraph explanation almost line for line. The anchor paragraph already says Turing constructs `Un(M)`, that `Un(M)` is provable iff M prints 0, that §8 rules out a general print-0 decision procedure, and that Hilbert's decision procedure therefore cannot exist. The immediately following lemmas paragraph then restates the same conversion from print-symbol undecidability to provability undecidability.

Adding this aside would create three adjacent passes through the same reduction. It also exceeds the 1-3 sentence cap for plain-reading asides. If the author wants the word "translation" or "reduction" surfaced, that should be handled in the existing aid-free proposal notes or later PR summary, not by adding another visible callout.

## Element 4 — Inline parenthetical definition (Starlight tooltip)

**Verdict: AGREE**

Agree with the skip. READER_AIDS.md reserves inline parenthetical definitions for a future non-destructive tooltip component, and `<abbr title="...">` would alter prose lines. The Tier 1 glossary already carries the vocabulary burden for this chapter without violating the bit-identity rule.

## Summary table

| # | Element | Proposal Status | Review Verdict |
|---|---|---|---|
| 1 | Pull-quote | SKIPPED | AGREE |
| 2 | Plain-reading after Gödel arithmetisation | PROPOSED | REJECT |
| 3 | Plain-reading after §11 reduction | PROPOSED | REJECT |
| 4 | Inline parenthetical | SKIPPED | AGREE |
