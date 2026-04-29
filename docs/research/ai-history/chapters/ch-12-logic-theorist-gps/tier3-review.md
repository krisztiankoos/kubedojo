# Tier 3 adversarial review — Codex (gpt-5.5)

Direct `codex exec -m gpt-5.5 -c model_reasoning_effort=high` dispatch. Task `394-ch12-tier3-codex-review`. Codex verified P-1584 p. 1 against the bitsavers scan (https://bitsavers.trailing-edge.com/pdf/rand/ipl/P-1584_Report_On_A_General_Problem-Solving_Program_Feb59.pdf) before adjudicating.

---

## Codex's verdicts (verbatim)

> **Element 8 — Tooltip: APPROVE-SKIP.** `READER_AIDS.md` makes Element 8 universally skipped until a non-destructive tooltip component exists.
>
> **Element 9 — Pull-quote, Candidate A: REVISE.** The proposed wording is not verbatim P-1584 p. 1. It compresses two adjacent claims: GPS as a digital-computer program, and synthesis as the research method. The quote-worthy phrase is the synthesis sentence.
>
> Use this instead, immediately after the paragraph beginning "In the 1959 account...":
>
> ```markdown
> :::note[GPS as synthesis]
> > "Our principal means of investigation is synthesis: programming large digital computers to exhibit intelligent behavior..."
>
> The quote makes the methodological wager explicit: GPS was built as an instrument for studying problem solving, not just as a solver.
> :::
> ```
>
> **Element 9 — Candidate B: APPROVE-SKIP.** Candidate A, revised to the synthesis sentence, does stronger work for the chapter hinge. B is downstream and would spend the one-quote allowance on a claim the prose already handles.
>
> **Element 10 — Candidate C (means-ends recursion): APPROVE-SKIP.** The paragraph is already plain-reading prose. An aside would echo it.
>
> **Element 10 — Candidate D (three GPS goal types): REJECT.** The paragraph is symbolically dense, but the very next paragraph already unpacks the interaction among the three goal types: transform → reduce difference → apply operator → another transformation. The proposed aside repeats that surrounding prose almost sentence-for-sentence, so it fails the non-redundancy test.
>
> **Element 10 — Candidate E (IPL chronology): APPROVE-SKIP.** This is narrative-historical density, not symbolic density, and the paragraph already explains the chronology distinction.
>
> **Missed Tier 3 Candidates: None.** I considered the nearby objects/operators/differences and infrastructure-ceiling paragraphs, but they are already written as plain explanatory prose.

---

## Decisions and rationale

| # | Element | Codex verdict | Action taken | Why |
|---|---|---|---|---|
| 8 | Inline tooltip | APPROVE-SKIP | **SKIP** | Universal default. |
| 9 / Cand A | Pull-quote — GPS-I framing | REVISE — verbatim corrected to "synthesis" sentence | **APPLY** with Codex's revised verbatim and tighter annotation | My proposal compressed two adjacent P-1584 claims. Codex extracted the actual synthesis sentence from the bitsavers PDF and pointed out that the quote-worthy phrase is the methodological-wager sentence, not the program-description one. |
| 9 / Cand B | Pull-quote — 1961 simulation framing | APPROVE-SKIP | **SKIP** | Cap is 1; A serves the chapter hinge better. |
| 10 / Cand C | Plain-reading: means-ends recursion | APPROVE-SKIP | **SKIP** | Both reviewers agree the paragraph is already plain-reading. |
| 10 / Cand D | Plain-reading: three GPS goal types | **REJECT** | **SKIP after attempted PROPOSE** | The author hoped the goal-type recursion was symbolically-dense-with-non-redundant-clarification. Codex demonstrated the next paragraph already unpacks the interaction sentence-for-sentence. Honest call: SKIP. The aside would have been filler. |
| 10 / Cand E | Plain-reading: IPL chronology | APPROVE-SKIP | **SKIP** | Both reviewers agree: narrative density, not symbolic. |
| — | Missed Tier 3 candidates | None | — | Codex considered the objects/operators/differences and infrastructure-ceiling paragraphs and confirmed they are plain explanatory prose already. |

---

## Final landed elements

1. `:::note[GPS as synthesis]` pull-quote callout immediately after the "In the 1959 account…" paragraph (line 130 in the post-Tier-1 file), with verbatim P-1584 p. 1 wording (Codex-verified) and Codex's tighter annotation framing GPS as an instrument for studying problem solving.

**Tally: 1 of 5 candidates landed (1 pull-quote, 0 plain-reading asides, 0 tooltip).** Calibration consistent with Part 1 + Ch10 + Ch11.

The author's PROPOSED Candidate D (three goal types plain-reading aside) was actively rejected on non-redundancy grounds. Codex's revision of Candidate A — pulling the actual P-1584 synthesis sentence rather than my paraphrase — is exactly the kind of source-fidelity correction the cross-family review pattern is designed to catch.
