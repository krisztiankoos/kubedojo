# Tier 3 review — Chapter 40

Reviewer: Codex (gpt-5.5, model_reasoning_effort=high), 2026-04-30, adversarial cross-family pass on PR for `claude/394-ch40-reader-aids`.

## Element 8 — Tooltip

Verdict: CONFIRM SKIP

One-line reason: The Tier 3 spec globally skips inline tooltips until a non-destructive Starlight tooltip component exists; adding an inline parenthetical or `<abbr>` would modify prose.

## Element 9 — Pull-quote

Verdict: REVIVE

One-line reason: The proposal correctly rejects chapter-prose self-quotation, but it misses a Green primary sentence from Deng et al. 2009 that is quote-worthy, not already in the prose, and useful as source provenance.

Full proposed insertion:

```markdown
:::note[Primary-source signal]
> "We hope that the scale, accuracy, diversity and hierarchical structure of ImageNet can offer unparalleled opportunities to researchers in the computer vision community and beyond."

Deng et al. made ImageNet's promise in opportunity-language before the later deep-learning story; this is ambition, not hindsight.
:::
```

Green primary anchor: Jia Deng, Wei Dong, Richard Socher, Li-Jia Li, Kai Li, and Li Fei-Fei, "ImageNet: A Large-Scale Hierarchical Image Database," CVPR 2009, p.248, abstract; covered by the Deng et al. 2009 Green primary-source entry in `sources.md`.

Insertion-anchor paragraph:

> The 2009 paper also had to make a methodological argument. ImageNet was large, but scale alone would not have made it useful. It was organized by a semantic hierarchy, populated with full-resolution images, and built through a repeatable collection-and-verification process. Those qualities made it different from a web crawl left in its raw form. They also made it different from a narrow benchmark whose categories had been selected mainly because they were convenient for a particular competition. The paper's underlying proposition was that a dataset could be both very large and carefully structured.

Adjacent-repetition test: The quoted sentence does not already appear in the chapter prose. The anchor paragraph summarizes the methodological features, but it does not reproduce the source's "unparalleled opportunities" claim or its "computer vision community and beyond" horizon. The callout would add primary-source provenance and period ambition rather than duplicating a nearby prose sentence.

## Element 10 — Plain-reading asides

Verdict: CONFIRM SKIP

One-line reason: The dense passages are procedural or narrative-dense, not symbolically dense; the chapter has no formulas, derivations, or stacked abstract definitions that require a Tier 3 plain-reading aside.

Symbolic-density check: The closest candidates are the 19-year labor calculation, WordNet synset/hypernym explanation, query-expansion pipeline, and redundancy/threshold quality-control discussion. Each is already unpacked in plain prose immediately after the mechanism appears. They contain numbers and terminology, but not mathematical notation, formal derivation, or abstract definition stacking under the Tier 3 standard.

## Summary

1 landed: Element 9 pull-quote should be revived with the Deng et al. 2009 p.248 abstract sentence above. 2 skipped: Element 8 remains globally skipped per the tooltip rule, and Element 10 remains skipped because Chapter 40 is not symbolically dense. This is not a blanket approval of Tier 3 aids; only the revived pull-quote clears the Green-source and adjacent-repetition gates.
