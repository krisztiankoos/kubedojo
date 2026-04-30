# Tier 3 review — Chapter 39

Reviewer: Codex (gpt-5.5, model_reasoning_effort=high), 2026-04-30, adversarial cross-family pass on PR for `claude/394-ch39-reader-aids`.

## Element 8 — Tooltip

Verdict: CONFIRM SKIP

One-line reason: The skip is mandatory under `READER_AIDS.md` because the tooltip component does not yet exist and inline `<abbr>` would modify verified prose.

## Element 9 — Pull-quote

Verdict: REVIVE

One-line reason: The proposal correctly rejects prose-derived pull-quotes, but it misses a Green primary-source sentence from Torralba and Efros that reinforces the chapter's balance: datasets were an achievement before they were a diagnostic problem.

Full proposed insertion:

```markdown
:::note[Pull-quote]
> "Datasets have also played the leading role in making object recognition research look less like a black art and more like an experimental science."

Torralba and Efros make the chapter's balance explicit: the same dataset infrastructure that disciplined the field also exposed its limits.
:::
```

Green primary anchor: Antonio Torralba and Alexei A. Efros, "Unbiased Look at Dataset Bias," CVPR 2011, p. 1522.

Insertion-anchor paragraph:

> That mix of scientific and administrative machinery is easy to miss when a benchmark is reduced to a leaderboard. Someone had to define the classes, collect images, specify annotation formats, preserve train and validation splits, keep the test labels back, run the evaluation server, publish deadlines, and make the workshop legible to the community. The official VOC2012 page listed Everingham together with Luc van Gool, Chris Williams, John Winn, and Andrew Zisserman as organizers, spread across Leeds, ETH Zurich, Edinburgh, Microsoft Research Cambridge, and Oxford. The retrospective later described VOC not only as a dataset, but as a public collection of images, annotations, evaluation code, an annual competition, and a workshop. The achievement was infrastructural as much as algorithmic: VOC made many different labs participate in the same experiment.

Adjacent-repetition test: The quoted sentence does not already appear in the prose. The nearby paragraph argues that VOC was infrastructure, but it does not use the source's "black art" / "experimental science" framing. The annotation adds provenance and stakes by showing that Torralba and Efros themselves credited dataset infrastructure immediately before diagnosing dataset bias, so the callout does not merely restate the paragraph.

## Element 10 — Plain-reading asides

Verdict: CONFIRM SKIP

One-line reason: The chapter is conceptually and narratively dense, but it has no symbolically dense paragraphs with formulas, derivations, or stacked abstract definitions that need a plain-reading aside.

## Summary

1 landed by review: Element 9 pull-quote, revived from a Green primary source rather than from chapter prose. 2 skipped: Element 8 remains globally unavailable, and Element 10 has no qualifying symbolic-density target. The proposal's overall restraint was right, but its pull-quote search was too narrow because it evaluated chapter prose instead of the primary-source sentence pool required by the gate.
