# Tier 3 adversarial review — Codex (gpt-5.5)

Direct `codex exec -m gpt-5.5 -c model_reasoning_effort=high` dispatch. Task `394-ch13-tier3-codex-review`. Codex verified verbatim wording against McCarthy's Stanford HTML reproduction (https://www-formal.stanford.edu/jmc/recursive/node1.html) and a PDF/LaTeX reproduction.

---

## Codex's verdicts (verbatim)

> **Element 8: APPROVE-SKIP.** Universal skip remains correct until a non-destructive tooltip component exists.
>
> **Element 9 — Pull-Quote.** Candidate A — Russell `eval` anecdote: APPROVE-SKIP. Correct to avoid promoting a Yellow retrospective anecdote into a visible pull-quote.
>
> Candidate B — 1960 CACM opening: REVISE. The proposed wording is verbatim-correct as proposed, including `LISt` capitalization and `M.I.T.` punctuation, verified against McCarthy's Stanford HTML and the PDF/LaTeX reproduction. But I would not use it as the pull-quote. It is canonical but mostly bibliographic.
>
> Use the stronger missed sentence from the same 1960 introduction instead:
>
> > "We believe this formalism has advantages both as a programming language and as a vehicle for developing a theory of computation."
>
> Reason: this directly anchors the chapter's Tool-vs-Theory thesis in McCarthy's own published framing, not in the chapter's retrospective interpretation. Insert after the opening paragraph of `## eval, Lambda, cond, and Recursion` or after "The most compact way to see LISP's theory side is to follow `eval`."
>
> Candidate C — AIM-001 design rationale: APPROVE-SKIP. Good source, but the cap is one and the 1960 sentence above better serves the chapter-level thesis.
>
> **Element 10 — Plain-Reading Asides.**
>
> Candidate D — S-expression as code/data: APPROVE-SKIP. Already plain-read in prose and reinforced by the next paragraphs.
> Candidate E — `eval` as bridge: APPROVE-SKIP. Already doing the intended aside work.
> Candidate F — mark-and-sweep: APPROVE-SKIP. The paragraph is already an algorithm walkthrough in plain language.
> Candidate G — IBM 704 `car`/`cdr`: APPROVE-SKIP. The prose already decodes the machine terms inline.
>
> **Missed Primary-Source Sentence.** YES: the 1960 CACM introduction explicitly frames LISP as both programming language and theory-of-computation vehicle. That is the pattern analogous to the Ch10 Turing catch. It is paraphrased throughout this chapter's "theory and tool" argument but not quoted.
>
> No additional plain-reading aside is needed. The chapter is technically dense, but not symbolically dense in the Tier 3 sense: it contains concepts, not stacked formulas or derivations requiring an external gloss.
>
> **Final Verdict.** Element 8: SKIP approved. Element 9: REVISE Candidate B to the stronger 1960 formalism/theory sentence. Element 10: all SKIPs approved. Total landing recommendation: 1 pull-quote, 0 plain-reading asides.

---

## Decisions and rationale

| # | Element | Codex verdict | Action taken | Why |
|---|---|---|---|---|
| 8 | Inline tooltip | APPROVE-SKIP | **SKIP** | Universal default. |
| 9 / Cand A | Russell anecdote | APPROVE-SKIP | **SKIP** | Source flagged Yellow in chapter's own prose; both reviewers agree. |
| 9 / Cand B | 1960 CACM opening — bibliographic version | REVISE — same paper, different sentence | **APPLY** with Codex's revised sentence | Codex confirmed my proposed verbatim was correct (`LISt` capitalisation, `M.I.T.` punctuation), but flagged that the *next* sentence in the same introduction does stronger thesis work: "We believe this formalism has advantages both as a programming language and as a vehicle for developing a theory of computation." That sentence directly states the chapter's Tool-vs-Theory thesis in McCarthy's own published voice — exactly the historiographic move the cross-family review pattern is designed to catch (cf. the Ch10 child-mind sentence). |
| 9 / Cand C | AIM-001 design rationale | APPROVE-SKIP | **SKIP** | Cap is 1; the 1960 sentence wins. |
| 10 / Cand D | Plain-reading: S-exp code/data | APPROVE-SKIP | **SKIP** | Both reviewers agree. |
| 10 / Cand E | Plain-reading: `eval` as bridge | APPROVE-SKIP | **SKIP** | Both reviewers agree. |
| 10 / Cand F | Plain-reading: mark-and-sweep | APPROVE-SKIP | **SKIP** | Both reviewers agree. |
| 10 / Cand G | Plain-reading: IBM 704 `car`/`cdr` | APPROVE-SKIP | **SKIP** | Both reviewers agree. |
| — | Missed Tier 3 candidate | YES — same 1960 CACM intro, formalism/theory sentence | **APPLIED via Cand B revision** | Same insertion location. |

---

## Final landed elements

1. `:::note[McCarthy on the 1960 formalism]` pull-quote callout immediately after the "The most compact way to see LISP's theory side is to follow `eval`." line, with verbatim CACM 3(4) intro wording (Codex-verified) and a one-sentence annotation that names the dual claim in McCarthy's own voice.

**Tally: 1 of 7 candidates landed (1 pull-quote, 0 plain-reading asides, 0 tooltip).** Calibration consistent with Ch10/Ch11/Ch12.

The author's PROPOSED Candidate B was revised — same source, better sentence. Codex's verbatim verification + sentence selection is exactly the source-fidelity contribution the cross-family review is designed to deliver.
