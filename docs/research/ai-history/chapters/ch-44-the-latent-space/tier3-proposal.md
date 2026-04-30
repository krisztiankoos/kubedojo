# Tier 3 Proposal — Chapter 44: The Latent Space

Per `docs/research/ai-history/READER_AIDS.md` Tier 3 workflow. Author: Claude. Reviewer: Codex (cross-family adversarial).

## Element 8 — Inline parenthetical definition (Starlight tooltip)

**SKIPPED** — universal default per READER_AIDS.md §Tier 3. The Plain-words glossary (Tier 1, item 4) covers all specialist terms non-destructively.

## Element 9 — Pull-quote (at most 1)

Survey of quote-worthy candidates from Green primary sources:

### Candidate A — Harris 1954: distributional definition

Source: S1, p. 146. "The distribution of an element will be understood as the sum of all its environments." This is the chapter's intellectual foundation sentence. **SKIPPED** — the chapter prose paraphrases this directly ("Harris argued that the distribution of a linguistic element should be understood simply as the sum of all its environments—the existing array of its co-occurrents") and the next sentence does the interpretive work. Elevating the verbatim to a callout adjacent to the prose paraphrase creates the repetition READER_AIDS.md §Tier 3, Element 9 explicitly flags as a refusal case.

### Candidate B — Bengio et al. 2003: curse-of-dimensionality illustration

Source: S3, p. 1137. The paper gives the 10^50 illustration. The chapter prose renders this in full narrative: "for a language model predicting sequences of ten consecutive words from a moderate vocabulary of 100,000 words, there are potentially ten to the fiftieth power possible combinations." Same adjacent-repetition problem.

### Candidate C — Mikolov et al. 2013 "Efficient Estimation," p. 1: atomic-index critique

Source: S4, p. 1. The paper states that "most of the current NLP systems and techniques treat words as atomic units — there is no notion of similarity between words." The chapter prose renders this: "the vast majority of systems still treated words as atomic vocabulary indices. In these discrete systems, there was no inherent notion of similarity between words; the discrete index for one concept possessed no geometric relationship to the discrete index for a closely related concept." The paraphrase is faithful and complete; no independent work left for a pull-quote callout.

### Candidate D — Mikolov, Yih, Zweig 2013 "Linguistic Regularities," p. 746: King-Man+Woman analogy

Source: S5, p. 746. This is the most famous sentence in the chapter's primary literature. The chapter prose quotes the result and its evaluation context directly: "The researchers reported that taking the continuous vector representation for the word 'King,' subtracting the vector for 'Man,' and adding the vector for 'Woman' resulted in a point in the high-dimensional space whose nearest neighboring word vector was 'Queen.'" The next two paragraphs do the interpretive work (what the arithmetic means, what "severity" the test carries). A pull-quote would sit adjacent to this already-quoted and interpreted passage.

**Status: SKIPPED.** All four surveyed candidates are either paraphrased-adjacent in the prose (Candidates A, B, C) or already quoted verbatim with full interpretive follow-on (Candidate D). No candidate satisfies the dual condition of being genuinely quote-worthy AND not already represented in the prose with adjacent framing.

## Element 10 — Plain-reading asides (0–3 per chapter)

READER_AIDS.md §Tier 3, Element 10 targets paragraphs that are *symbolically* dense — stacked mathematical formulas, derivations, or abstract definitions requiring multi-step parsing. The chapter is predominantly analytic narrative.

### Candidate E — Curse-of-dimensionality paragraph (Scene 2)

The paragraph beginning "The motivation for introducing learned distributed representations..." includes the $10^{50}$ calculation. However, the very same paragraph supplies its own plain reading: "there are potentially ten to the fiftieth power possible combinations. Because any practical training corpus contains only an infinitesimal fraction of these possible sequences, traditional discrete models fail to generalize..." A callout would restate what the prose already makes explicit.

**Status: SKIPPED.** The paragraph self-decodes its own symbolic moment.

### Candidate F — Vector-offset analogy paragraph (Scene 4)

The paragraph beginning "The arithmetic worked by turning relations into displacement..." unpacks the King-Man+Woman geometry. This paragraph is interpretive prose, not symbolically dense in the LaTeX-stacked sense. It uses no formulas; it is a plain reading of the preceding narrative scene. Adding a `:::tip[Plain reading]` on an already-plain-reading paragraph would be recursive and vacuous.

**Status: SKIPPED.** Paragraph is already a plain reading; not symbolically dense.

### Candidate G — Negative sampling paragraph (Scene 5)

The paragraph beginning "The change was not just an implementation trick..." explains the shift from full softmax to binary discrimination. The math sidebar (Tier 2) supplies the equation; this prose paragraph supplies the motivation without LaTeX. The two aid layers divide the work cleanly. No additional callout needed.

**Status: SKIPPED.** Tier 2 math sidebar handles the symbolic layer; prose paragraph handles the plain-language layer. A `:::tip[Plain reading]` would duplicate the prose paragraph itself.

## Summary verdict

- Element 8: SKIPPED (universal).
- Element 9: SKIPPED — all four surveyed candidates (A, B, C, D) are either paraphrased-adjacent or already quoted verbatim with interpretive follow-on in the prose.
- Element 10: SKIPPED — no paragraph is symbolically dense in the stacked-formula sense that READER_AIDS.md targets; all candidate paragraphs already contain their own plain-reading layer.

**Total: 0 PROPOSED, 3 SKIPPED.**
