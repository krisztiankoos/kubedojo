# Tier 3 adversarial review — Codex (gpt-5.5)

Direct `codex exec -m gpt-5.5 -c model_reasoning_effort=high` dispatch (bypassing the broken `ab ask-codex` wrapper). Task `394-ch11-tier3-codex-review`. Response captured at `/tmp/ch11-tier3-codex-out.txt`.

---

## Codex's verdicts (verbatim)

> **Element 8 — Tooltip: APPROVE-SKIP.** This matches `READER_AIDS.md`: Element 8 is universally skipped until a non-destructive tooltip component exists.
>
> **Element 9 — Pull-quote, Candidate A: REVISE.** The quoted sentence is verbatim correct:
>
> > "We propose that a 2 month, 10 man study of artificial intelligence be carried out during the summer of 1956 at Dartmouth College in Hanover, New Hampshire."
>
> Do not normalize `10 man` or add hyphens inside the quote. The proposed annotation is useful but exceeds the pull-quote cap and does too much exposition.
>
> Use this shorter callout instead:
>
> ```markdown
> :::note
> > "We propose that a 2 month, 10 man study of artificial intelligence be carried out during the summer of 1956 at Dartmouth College in Hanover, New Hampshire."
>
> The opening sentence frames AI as a fundable summer study; the attendance pattern shrank, but the title survived.
> :::
> ```
>
> **Element 10 — Candidate B, Seven Research Topics: APPROVE-SKIP.** This is a list of research areas, not symbolic density, and the paragraph immediately explains the terms in plain prose. A `Plain reading` aside would duplicate the surrounding text.
>
> **Element 10 — Candidate C, Alternative Names: APPROVE-SKIP.** This is disciplinary and political context, not symbolic density. The prose is narratively dense but already readable.
>
> **Element 10 — Candidate D, Institutional Condensation: APPROVE-SKIP.** The paragraph is metaphorical, not mathematically or definitionally dense, and the following paragraph explains the metaphor directly.
>
> **Missed Tier 3 Candidate.** One credible missed pull-quote alternative, not an additional element: the proposal's opening conjecture.
>
> > "The study is to proceed on the basis of the conjecture that every aspect of learning or any other feature of intelligence can in principle be so precisely described that a machine can be made to simulate it."
>
> This is load-bearing and paraphrased in the chapter, but because Element 9 allows at most one pull-quote, I would treat it as an alternative to Candidate A rather than a second insertion. For this chapter's naming/institutional thesis, Candidate A is the better fit after revision.
>
> **Final Verdict.** Element 8: APPROVE-SKIP. Element 9: REVISE with corrected shorter annotation above. Element 10: 0 PROPOSED. B/C/D skips: APPROVE-SKIP. Missed plain-reading aside: none. Missed alternate pull-quote: yes, opening conjecture, but do not add alongside Candidate A.

---

## Decisions and rationale

| # | Element | Codex verdict | Action taken | Why |
|---|---|---|---|---|
| 8 | Inline tooltip | APPROVE-SKIP | **SKIP** | Universal default. |
| 9 | Pull-quote, Candidate A (proposal opening) | REVISE — verbatim correct, annotation too long | **APPLY** with Codex's shorter annotation | The verbatim wording was confirmed correct (do not normalise `10 man`). My original annotation exceeded the ≤60-word pull-quote cap and over-explained the framing-vs-actuality gap that Scene 3–4 already covers. Codex's tighter framing — "frames AI as a fundable summer study; the attendance pattern shrank, but the title survived" — does the work in two clauses. |
| 10B | Plain-reading: seven research topics | APPROVE-SKIP | **SKIP** | Both reviewers agree the next paragraph already plain-reads each topic. |
| 10C | Plain-reading: alternative names | APPROVE-SKIP | **SKIP** | Narrative density, not symbolic. |
| 10D | Plain-reading: institutional condensation | APPROVE-SKIP | **SKIP** | Metaphor unpacked in the next paragraph. |
| — | Alternate pull-quote (proposal "conjecture" sentence) | "Yes, but as alternative not addition" | **DECLINED** | Codex itself recommended Candidate A is the better fit for this chapter's naming/institutional thesis. The conjecture sentence is a stronger candidate for a chapter focused on the methodological premise of AI; Ch11's thesis runs through institutional condensation, which Candidate A serves better. |

---

## Final landed elements

1. `:::note` pull-quote callout immediately after the four-organizers paragraph (line 62), with verbatim "2 month, 10 man study" wording (no normalisation) and Codex's shorter two-clause annotation.

**Tally: 1 of 5 candidates landed (1 pull-quote, 0 plain-reading asides, 0 tooltip).** Calibration consistent with Part 1 + Ch10.

The author's PROPOSED candidate cleared in modified form: verbatim verified by Codex against the Stanford-hosted PDF, annotation tightened to fit the pull-quote cap. Codex flagged but rejected adding a second pull-quote — the cap is one per chapter, and Codex agreed Candidate A was the better fit for Ch11's institutional thesis.
