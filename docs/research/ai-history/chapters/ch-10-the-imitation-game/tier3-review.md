# Tier 3 adversarial review — Codex (gpt-5.5)

Direct `codex exec` dispatch (bypassing the `ab ask-codex` wrapper, which silently dropped the prompt). Task `394-ch10-tier3-codex-review-v3`. Reviewer: Codex / gpt-5.5 with `model_reasoning_effort=high`. Response captured at `/tmp/ch10-tier3-codex-out.txt`.

---

## Codex's verdicts (verbatim)

> **Element 8 — Inline Tooltip: APPROVE-SKIP.** Correct. `READER_AIDS.md` makes this universally skipped until a non-destructive Astro tooltip exists. No issue.
>
> **Element 9 — Pull-Quote: REJECT-SKIP.** The author is right that all 7 surveyed candidates are already quoted in-prose and should not be duplicated. But the survey misses one quote-worthy sentence that is not already quoted verbatim and does deserve typographic weight:
>
> Insertion anchor: immediately after the paragraph beginning `This leads to Section 7, "Learning Machines,"...`
>
> ```markdown
> :::note
> > "Instead of trying to produce a programme to simulate the adult mind, why not rather try to produce one which simulates the child's?"
>
> This is the pivot from performance test to training programme: Turing turns intelligence into a staged engineering problem, with education doing work hand-coded instruction cannot.
> :::
> ```
>
> Reason: the chapter paraphrases this move, but does not quote it. It is a genuine hinge sentence in *Mind* §7, and the annotation adds stakes rather than paraphrasing.
>
> **Element 10A — 10⁹ / 70% / Five-Minute Prediction: APPROVE-SKIP.** Correct skip. The next paragraph already performs the plain-reading work almost exactly: frequency claim, average interrogators, five-minute bound, storage estimate, and warning against over-reading the byte conversion.
>
> **Element 10B — Universality Argument: APPROVE-SKIP.** Correct skip. This is abstract, but the following paragraph already translates the point into the hardware bridge: not reproducing a nervous system physically, but generating test-relevant behaviour given storage, speed, and programming.
>
> **Element 10C — Supercritical Mind / Atomic-Pile Analogy: APPROVE-SKIP.** Correct skip. This is metaphorical density, not symbolic density. The chapter already unpacks subcritical vs. supercritical and ties it back to Lovelace.
>
> **Missed Plain-Reading Asides: APPROVE NO ADDITION.** No missed paragraph clears both tests: symbolic density and non-duplicative explanation. The other number-heavy paragraphs are already explained in surrounding prose, and the child-machine decomposition is clarified before and after the quoted three-part list.
>
> **Final Verdict.** Reject the all-SKIP proposal only for Element 9. Land one pull-quote. Keep Element 8 skipped and land zero Element 10 plain-reading asides.

---

## Decisions and rationale

| # | Element | Codex verdict | Action taken | Why |
|---|---|---|---|---|
| 8 | Inline tooltip | APPROVE-SKIP | **SKIP** | Universal skip until a non-destructive tooltip component lands. |
| 9 | Pull-quote | REJECT-SKIP — propose Mind §7 child-mind sentence | **APPLY** (verbatim with light annotation tweak) | Codex correctly identified that the prose paraphrases the child-mind hinge sentence without quoting it. The proposed annotation does new work — names the move ("hinge of the paper"; "from a hand-coded artefact into a staged engineering problem"). The chapter prose retains its existing paraphrase one paragraph earlier and unpacks the move in subsequent paragraphs (Helen Keller, the evolutionary analogy, the chess-vs-sense-organs split); the pull-quote complements rather than duplicates. |
| 10A | Plain-reading: 10⁹ / 70% / 5-min prediction | APPROVE-SKIP | **SKIP** | Both reviewers agree the next paragraph already does the plain-reading work. |
| 10B | Plain-reading: universality argument | APPROVE-SKIP | **SKIP** | Both reviewers agree. |
| 10C | Plain-reading: supercritical mind | APPROVE-SKIP | **SKIP** | Both reviewers agree the analogy is metaphorical, not symbolic. |
| — | Missed asides | APPROVE NO ADDITION | **None added** | Codex confirmed no symbolically-dense paragraph in Ch10 was overlooked. |

---

## Final landed elements

1. `:::note` pull-quote callout immediately after the "This leads to Section 7" paragraph, quoting Turing's *Mind* §7 child-mind sentence verbatim with a 1-sentence annotation that frames the move as "the hinge of the *Mind* paper."

**Tally: 1 of 5 candidates landed (1 pull-quote, 0 plain-reading asides, 0 tooltip).** Calibration is consistent with Part 1 (Ch01 2/5, Ch03 1/3, Ch04–Ch09 0/3 each).

This is exactly the workflow the Tier 3 protocol is designed to produce: the author drafted an honest all-SKIP refusal; the cross-family adversary identified one element the author had not surveyed; the disagreement was resolved on its merits and one element earned its interruption.

## Notes on dispatch

The `scripts/ab ask-codex` wrapper silently dropped two consecutive dispatches (zero-byte output, exit 0, no error). Direct `codex exec -m gpt-5.5 -c model_reasoning_effort=high` worked on the first try. Probable wrapper bug — flag for `feedback_codex_dispatch_sequential.md` consideration: the failure mode here was not concurrency (only one dispatch was in flight at a time) but the `ab ask-codex` heredoc/stdin pipeline itself.
