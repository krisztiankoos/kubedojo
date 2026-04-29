# Tier 3 adversarial review - Codex (gpt-5.5)

Direct cross-family adversarial review of Claude's Tier 1 reader-aids and Tier 3 proposal for Chapter 17, "The Perceptron's Fall." Task `394-ch17-tier3-codex-review`. Codex verified Minsky and Papert's *Perceptrons* text by fetching the Green source-registry PDF at `https://papers.baulab.info/papers/Minsky-1969.pdf`, running `pdftotext`, and checking the Introduction pp.15-17 text around the prior-structure passage.

---

## Codex's verdicts (verbatim)

> **Element 8: APPROVE-SKIP.** Universal skip per `READER_AIDS.md`; no inline tooltip should land.
>
> **Candidate A - Minsky/Papert prior-structure pull-quote: REVISE.** The proposal's working quote is not verbatim in the Green PDF. The verified wording on Introduction p.16 is: "But we do believe that significant learning at a significant rate presupposes some significant prior structure." This is not quoted verbatim in the chapter prose, and it is the chapter's best Tier 3 pull-quote because it proves the critique was pro-learning but anti-unstructured-learning. Land the corrected sentence, not the proposal's hypothetical wording, and place it immediately after the paragraph ending "A big bag of possible features is not the same as the right representation."
>
> **Candidate B - Rosenblatt 1958 pull-quote: APPROVE-SKIP.** Rosenblatt's 1958 opening frame is Green and quotable, but the one-pull-quote cap should go to Minsky/Papert because the chapter's hinge is the move from theorem to prior-structure critique. The Rosenblatt program is already given sustained narrative weight in the prose.
>
> **Candidate C - Connectedness plain-reading aside: REJECT.** The candidate paragraph has technical terms, but it is not dense enough by the `READER_AIDS.md` symbolic-density threshold to justify a visible aside. More importantly, the paragraph already ends, "In plain terms, the local pieces did not scale into the global judgment," and the immediately following paragraph explains bounded local tests, broken bridges, growing retinas, and the need to smuggle global relations into partial predicates. The proposed aside would repeat adjacent prose.
>
> **Candidate D - Order/parity paragraph: APPROVE-SKIP.** Correct skip. The prose already plain-reads XOR as the small parity case and states that the historical issue is order growth as input grows.
>
> **Candidate E - Predicate/linear-combination paragraph: APPROVE-SKIP.** Correct skip. The paragraph defines predicate, partial predicate, weights, threshold, and geometric question in ordinary prose; a `Plain reading` callout would duplicate it.
>
> **Missed primary-source sentence: Yes, but not landing.** Minsky/Papert p.15 has another compact sentence worth noting: "The ease and uniformity of programming have been bought at a cost!" It matches the chapter's representation-as-cost thread, but it does not beat the p.16 prior-structure sentence under the one-pull-quote cap.
>
> **Final Tier 3 count:** 1 REVISED-TO-LAND, 4 SKIPPED, 1 REJECTED. No plain-reading aside should land.

---

## Decisions and rationale

| # | Element | Codex verdict | Action taken | Why |
|---|---|---|---|---|
| 8 | Inline tooltip | APPROVE-SKIP | **SKIP** | Universal default in `READER_AIDS.md`. |
| 9 / Cand A | Minsky/Papert prior-structure pull-quote | REVISE - corrected verbatim | **APPLY REVISED** | The proposed quote is not in the Green PDF. The verified p.16 sentence is strong, non-adjacent, and directly supports the chapter thesis. |
| 9 / Cand B | Rosenblatt 1958 pull-quote | APPROVE-SKIP | **SKIP** | Green source, but cap is one; Minsky/Papert better serves the theorem-to-winter hinge. |
| 10 / Cand C | Connectedness double-theorem aside | REJECT | **SKIP** | Technical vocabulary appears, but the paragraph and the next paragraph already plain-read the local/global intuition. |
| 10 / Cand D | Order/parity aside | APPROVE-SKIP | **SKIP** | Already written as a plain-reading bridge; not symbolically dense. |
| 10 / Cand E | Predicate/linear-combination aside | APPROVE-SKIP | **SKIP** | Definitions are unpacked in prose; an aside would duplicate. |
| - | Missed candidate | Not landed | **SKIP** | Minsky/Papert's p.15 cost sentence is quote-worthy but lower priority than the p.16 prior-structure sentence. |

---

## Final landed elements

1. `:::note[The 1969 hinge]` pull-quote callout immediately after the paragraph in "## The Mathematical Turn" ending:

   > A big bag of possible features is not the same as the right representation.

   Exact text to insert:

   ```markdown
   :::note[The 1969 hinge]
   > "But we do believe that significant learning at a significant rate presupposes some significant prior structure."

   The critique was not anti-learning; it shifted the burden from trainable weights to architecture and task-matched features.
   :::
   ```

No `:::tip[Plain reading]` asides should land.

**Tally: 1 APPROVED via revision, 4 SKIPPED, 1 REJECTED of 6 reviewed items including the newly flagged missed candidate. Of the 5 proposal candidates, 1 should land and 4 should skip/reject.**

