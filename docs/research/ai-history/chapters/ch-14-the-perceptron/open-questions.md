# Open Questions: Chapter 14 - The Perceptron

## Priority Open Questions

### Operator Manual Extraction

- **Question:** Which direct pages in *Mark I Perceptron Operators' Manual (Project PARA)* verify the 400-photocell input array, motorized potentiometers, association units, response units, plugboard layout, and forced-correction controls?
- **Current status:** Manual identified through `MarkI-Manual60` metadata: Hay and Murray, 15 February 1960, Contract No. Nonr-2381(00), DTIC PDF URL. Direct text extraction failed from browser in this pass.
- **Drafting risk:** The hardware detail is essential to the chapter, but the exact 400-photocell/motor-potentiometer wording should remain Yellow until the operator manual is page-anchored.
- **Next action:** Use a PDF-capable browser or local extractor outside this restricted shell; record page numbers for component diagram and operator procedures.

### New York Times Attribution

- **Question:** Does the "walk, talk, see, write, reproduce itself..." sentence belong to the reporter's paraphrase, Navy expectation, or Rosenblatt's own quoted speech?
- **Current status:** `NYT58` title/date/archive URL verified, but original text was not extracted. Multiple secondary snippets quote the sentence.
- **Drafting risk:** Misattributing the quote would distort Rosenblatt's technical claims.
- **Next action:** Pull original article scan/text and record headline, page, byline, and exact quote attribution.

### Separability Sources Before Principles

- **Question:** How does "Two Theorems of Statistical Separability in the Perceptron" differ from the convergence-theorem presentation in *Principles of Neurodynamics*?
- **Current status:** `TwoTheorems59` bibliographic reference identified. No page extraction yet.
- **Drafting risk:** If the chapter relies only on `POND61`, it may flatten the theorem chronology.
- **Next action:** Extract pages 421-456 from *Mechanisation of Thought Processes* and compare terminology: statistical separability, convergence, elementary perceptrons, and conditions for solutions.

### First Full Report

- **Question:** What exactly is in the 1958 CAL report `VG1196G1`, and how much of it was adapted into `PsychRev58`?
- **Current status:** `PsychRev58` p. 386 says the article is adapted from the first full program report, but the report pages were not extracted.
- **Drafting risk:** The chapter may over-rely on the published Psychological Review article and the later 1961 report.
- **Next action:** Locate and extract `VG1196G1`.

### Mark I Public Demonstration Date

- **Question:** Should the chapter date the public demonstration to June 23, 1960, or the Navy photo release to June 24, 1960?
- **Current status:** `NavyPhoto60` release is June 24, 1960. Secondary snippets mention a June 23 demonstration.
- **Drafting risk:** A wrong exact date is unnecessary and avoidable.
- **Next action:** Use "June 1960 public release/demonstration context" until a primary demonstration notice is extracted.

## Drafting Warnings

- **No failure framing:** The perceptron worked for restricted pattern-recognition tasks and supported a serious mathematical program. Ch17 owns later limits and controversy.
- **No neural-net priority claim:** Rosenblatt did not invent neural networks. Cross-link Ch5 for McCulloch-Pitts and Hebb.
- **No digital-only framing:** IBM 704 simulations were important, but Mark I was electromechanical analog hardware.
- **No press-as-capability framing:** The NYT sentence is rhetoric/reception, not evidence that the machine could do those things.
- **No Dartmouth placement:** Rosenblatt was outside the Dartmouth naming event. Ch11 owns exact conference details.
- **No modern tutorial drift:** Use modern terms like "linear classifier" and "stochastic gradient descent" only as interpretive bridges, not as period language.
- **No Ch17 preemption:** Do not explain the 1969 critique except as a forward-link.

## Yellow-to-Green Upgrade Worklist

| Claim | Needed Source | Why It Matters |
|---|---|---|
| 400 photocells in a 20x20 sensory array | `MarkI-Manual60` direct page | Required hardware specificity. |
| Motorized potentiometers implemented adjustable weights | `MarkI-Manual60` direct page | Makes analog learning physically concrete. |
| Exact A/R unit counts for the Mark I configuration | `MarkI-Manual60` direct page | Avoids mixing versions of Mark I. |
| NYT "walk, talk..." wording and attribution | `NYT58` original scan/text | Prevents quote misattribution. |
| Statistical separability theorem chronology | `TwoTheorems59` pages | Strengthens mathematics scene. |
| IBM 704 simulation experiment details | `IRE60` full pages | Supports a richer simulation paragraph. |
| CAL first full report content | `VG1196G1` pages | Connects 1958 report to article and book. |
| Minsky "loyal opposition" context | Minsky 1961 IRE article | Lets the chapter foreshadow Ch17 without importing it. |

## Gap-Audit Worklist Scaffolding

### Must-Check Before Prose

- Verify every Green claim in `sources.md` against the listed primary page or institutional section.
- Promote or demote the 400-photocell and motor-potentiometer details after operator-manual extraction.
- Resolve NYT attribution or leave the quote explicitly Yellow.
- Confirm whether to use the 1961 CAL report pagination or the 1962 Spartan pagination in final citations.

### Should-Check Before Prose

- Pull Olazaran 1996 pages on the "official history" and controversy framing.
- Pull Anderson/Rosenfeld reprint notes for how later neural-network researchers canonized the 1958 paper.
- Pull Nilsson pages for mathematical exposition of perceptron convergence and linearly separable limits.
- Pull one source on Rochester's neural-simulation work if he remains in the people file.

### Nice-to-Have

- Cornell internal images or Research Trends pages for the local-publication scene.
- ONR contract documents beyond the contract number.
- Smithsonian object images with curator notes on restoration, storage, or component identification.

## Capacity Warning

This contract can support a 4,000-6,000 word chapter only if the prose leans into verified machinery and mathematics. Without the operator manual and full NYT scan, the safe upper range is closer to 4,500 words. Do not pad with invented public-demo drama, rivalry psychologizing, or retrospective AI-winter summary.
