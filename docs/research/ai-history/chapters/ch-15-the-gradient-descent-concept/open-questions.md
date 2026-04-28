# Open Questions: Chapter 15 — The Gradient Descent Concept

The questions that remain Yellow or Red after this anchor pass, what archival access would help, and where the chapter's natural word-count cap sits.

## What's still Yellow

### Y1. Robbins-Monro 1951 Theorem 2 page anchor

- **What's needed**: a primary anchor for the convergence-in-probability theorem statement and the original step-size conditions on `c_n` (which the 1951 paper writes in a notation that later expositions reformulate as `Σ c_n = ∞`, `Σ c_n² < ∞`).
- **Why it matters**: lets the chapter cite the convergence theorem responsibly with page-level evidence rather than relying on the Project Euclid landing page abstract. Would unlock a 200–400 word expansion of Scene 2 toward the upper end of the 400–600 budget.
- **What to try**: (a) ResearchGate or arXiv historical mirror; (b) university library scan of *Annals of Mathematical Statistics* vol. 22; (c) Bottou-LeCun 2004 ("Large scale online learning," NIPS) as a *secondary* that quotes the theorem statement — would let the chapter cite responsibly without claiming a primary anchor.
- **Confidence the search would succeed**: medium. Many statistics-department library scans of the *Annals* exist outside the Project Euclid Imperva gate.

### Y2. Linnainmaa 1976 BIT paper page anchors

- **What's needed**: an English-language *primary* anchor for the reverse-mode AD machinery, via the 1976 *BIT Numerical Mathematics* 16(2) restatement (the 1970 thesis itself is in Finnish and not publicly hosted).
- **Why it matters**: would convert the entire Linnainmaa attribution from Yellow (single secondary chain through Schmidhuber 2015) to Green (primary). Would unlock a 200–300 word expansion of Scene 4 toward the upper end of the 500–700 budget.
- **What to try**: (a) the Springer / SpringerLink BIT archive (paywalled but library-accessible); (b) a citation chain through Griewank's 2012 "Who invented the reverse mode of differentiation?" Documenta Math. paper, which quotes the relevant Linnainmaa passages; (c) Helsinki University Library special-collections digital request for the 1970 thesis itself.
- **Confidence**: medium-high for (a) and (b), low for (c) due to language barrier.

### Y3. The "TR 1553-1" Stanford companion technical report

- **What's needed**: confirm whether a Stanford technical report numbered TR 1553-1 (or similar) exists as a companion to `WidrowHoff60`, and if so, what specific gradient/LMS detail it adds.
- **Why it matters**: the orchestrator's pre-staged note flagged this; the WESCON paper itself does not cite that number. If TR 1553-1 is real and findable, it might unlock additional analog-hardware infrastructure detail for Scene 3. If it is *not* real, this stays as a transparency note in `sources.md` (already done).
- **What to try**: Stanford Information Systems Laboratory (ISL) archive search; Stanford Digital Repository search for "Widrow technical report 1960"; a query to the ISL itself.
- **Confidence**: low. Without a hit on the WESCON reference list itself, this could be a citation that does not exist or that the orchestrator's pre-staged note received from a downstream secondary source that hallucinated it.

### Y4. The Adaline operator-experience anchor

- **What's needed**: any first-person account of operating the Adaline beyond what the 1960 WESCON paper documents (`WidrowHoff60` p. 96 Section C). Ideally a Hoff or Widrow oral history, or a contemporary photograph caption with operator description.
- **Why it matters**: would let Scene 3 reach the upper end of its 1,100–1,500 word budget without padding the misadjustment-formula bookkeeping.
- **What to try**: Stanford EE oral history archives; the Computer History Museum (CHM) Widrow interview if it exists; Fig. 2 (Adaline photograph) and Fig. 4 (classification experiment patterns) original captions in higher resolution.
- **Confidence**: medium. Stanford EE keeps oral histories of senior faculty; Widrow is still living.

## What's still Red (do not draft)

### R1. Hadamard 1908 as gradient-descent precursor

- Schmidhuber's parenthetical "(Hadamard, 1908)" at the head of Section 5.5 is the *only* anchor. The Hadamard paper is on equilibrium of clamped elastic plates and the connection to "minimization of errors through gradient descent" is at most metaphorical. **Do not draft a Hadamard scene.** Mention only as a parenthetical citation in Scene 4 if at all.

### R2. The "memistor" as Adaline storage

- The 1960 WESCON paper does *not* mention the memistor; the OCR text contains zero occurrences. The memistor is a *later* Widrow development. **Do not assert "memistor" in prose.** Use "MAD magnetic cores, with thin-film successors planned" — the language the WESCON paper actually uses.

### R3. Cauchy's note as a major paper for Cauchy

- Lemaréchal's framing is the opposite (`Lemarechal12` p. 251 parenthetical: "this reference takes a tiny place amongst his fundamental works on analysis, complex functions, mechanics, etc."). **Do not draft a "Cauchy's masterpiece" frame.** The note is the published-on-paper origin point of the gradient method but was not, for Cauchy, a major contribution.

### R4. The Stanford TR 1553-1 reference

- Until and unless an independent Stanford archive hit confirms it, **do not include a TR 1553-1 citation in the chapter**. See Y3 above.

## Archival access that would help

In rough order of expected value-per-effort:

1. **Library scan of *Annals of Mathematical Statistics* vol. 22** to anchor `RobbinsMonro51` Theorem 2 at the page level (Y1).
2. **Springer / SpringerLink BIT archive access** for Linnainmaa 1976 (Y2).
3. **Bottou-LeCun 2004 NIPS paper** as a secondary that quotes the Robbins-Monro theorem responsibly without a primary anchor (Y1 fallback).
4. **Stanford EE oral history archive** for any Widrow or Hoff first-person account of Adaline operation (Y4).
5. **Stanford ISL archive search** for any TR 1553-1 hit (Y3, low-priority).

Items 1–3 unlock concrete expansion of the Prose Capacity Plan. Item 4 unlocks density without expansion. Item 5 either confirms or buries an open question.

## Word-count cap honesty

- **Currently supported by anchored evidence**: 3,400–4,900 words (`3k-5k likely` per Word Count Discipline labels). This is the chapter's natural range with the four primary sources extracted in this pass.
- **What would lift it to 4,000–7,000 supported**: the conjunction of Y1 (Robbins-Monro Theorem 2 anchor) and Y2 (Linnainmaa 1976 BIT primary anchor). With both, Scene 2 grows to 700–900 words and Scene 4 grows to 800–1,000 words, pushing the total to 4,400–6,300 words. Either alone is not enough.
- **What would *not* responsibly lift it**: padding the Widrow-Hoff misadjustment-formula bookkeeping into a numerical-analysis tutorial; inventing institutional or biographical color around the Cauchy / Linnainmaa scenes; adopting Schmidhuber's contested priority claims (e.g., Ivakhnenko Section 5.3) to add scenes.
- **Recommended cap if Y1 and Y2 stay open**: **4,900 words.** Do not pad.

## Cross-family review focus areas

When this contract is sent to Codex (anchor verification) and Gemini (gap analysis):

- **For Codex**: verify that every Green claim in `sources.md` is reproducible via the same `pdftotext` / OCR commands used here. Verify that the page markers I used in `widrow-hoff-1960.txt` (96 at line 84, 97 at line 164, 98 at line 261, 100 at line 457, 102 at line 606, 103 at line 664, 104 at line 757) match the OCR output Codex gets when running `ocrmypdf --skip-text` on `widrow-hoff-1960.pdf`. Verify that the Schmidhuber 2015 page-90 and page-91 anchors are exact. Verify that the Lemaréchal 2012 page anchors (251, 252, 253, 254) match — this PDF is text-extractable, not OCR'd, so it should be deterministic.
- **For Gemini**: stress-test the boundary contract. Is the Cauchy → Widrow-Hoff → Linnainmaa → modern-reinterpretation arc tight enough? Are there scenes that should *not* be in this chapter at all (e.g., should the optimal-control precursor cluster of Scene 4 be cut entirely and absorbed into Ch24)? Is the 3,400–4,900 word range honest, or is the chapter under-promising on what the four anchored sources can support? Does the Robbins-Monro layer's compactness (400–600 words) read as honest restraint or as a structural weakness? Per the dual-review-required gate, both reviewers must be Green before this contract reaches `accepted`.
- **Special caution per `feedback_gemini_hallucinates_anchors.md`**: if Gemini suggests an additional source or page anchor, do not promote it to Green without independent verification (curl + pdftotext + grep). The 2026-04-27 cleanup commit `03640e20` and Issue #421 are still recent.

## Items the orchestrator's pre-staged note flagged that turned out NOT to need work

- **Schmidhuber's Linnainmaa attribution chain** — already extracted directly via `pdftotext` of `schmidhuber-2015.pdf` Section 5.5 page 91. No additional Schmidhuber work needed in this pass.
- **Lemaréchal's Cauchy reproduction** — already extracted directly via `pdftotext` of `lemarechal-cauchy.pdf` pp. 251–254. All seven Cauchy Green claims anchored.
- **Widrow-Hoff OCR** — succeeded with `ocrmypdf --skip-text` followed by `pdftotext -layout`. Eight new Green claims promoted vs. the bibliographic-only Green Ch14 had.

## Items the orchestrator's pre-staged note flagged for which the search was unsuccessful in this pass

- **Stanford TR 1553-1** — not located. See R4 / Y3 above.
- **Hadjisavvas 1986** historical note on Cauchy — not searched in this pass; Lemaréchal 2012 is the cleaner anchor and was sufficient.
- **Pierre-Louis Lions** as a Cauchy historiographic source — not used; Lemaréchal 2012 was sufficient.
- **Bottou & LeCun 2004 NIPS** "Large scale online learning" — not pulled in this pass; flagged as Y1 fallback.
