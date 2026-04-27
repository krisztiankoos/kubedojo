# Open Questions: Chapter 14 - The Perceptron

## Priority Open Questions

### Operator Manual Extraction

- **Question:** Which direct pages in *Mark I Perceptron Operators' Manual (Project PARA)* verify the 400-photocell input array, motorized potentiometers, association units, response units, plugboard layout, and forced-correction controls?
- **Current status:** Manual identified through `MarkI-Manual60` metadata: Hay and Murray, 15 February 1960, Contract No. Nonr-2381(00), DTIC PDF URL. Direct text extraction failed from browser in this pass.
- **Drafting risk:** The hardware detail is essential to the chapter, but the exact 400-photocell/motor-potentiometer wording should remain Yellow until the operator manual is page-anchored.
- **Next action:** Use a PDF-capable browser or local extractor outside this restricted shell; record page numbers for component diagram and operator procedures.

### New York Times Attribution

- **Question:** Does the "walk, talk, see, write, reproduce itself..." sentence belong to the reporter's paraphrase, Navy expectation, or Rosenblatt's own quoted speech?
- **Current status:** `NYT58` title/date/archive URL verified, but original text was not extracted. Multiple secondary snippets quote the sentence. The Scene-Level Claim Table now Red-flags any direct attribution of the precise wording to Rosenblatt's technical voice until the original scan is in hand.
- **Drafting risk:** Misattributing the quote would distort Rosenblatt's technical claims and violate the chapter's "serious scientist" thesis.
- **Next action:** Pull original article scan/text and record headline, page, byline, and exact quote attribution. Until then, prose must use "press rhetoric" framing, never "Rosenblatt said."

### Mark I Hardware Counts (Red on precise figures)

- **Question:** What are the exact Mark I component counts (photocells, A-units, R-units, potentiometers) under the Project PARA configuration?
- **Current status:** Yellow on the general 400-photocell / 20x20 retina / motorized potentiometer claim; Red on writing precise figures into prose without `MarkI-Manual60` page anchors. Secondary sources vary on Mark I hardware counts and using one without the primary engineering manual risks factual drift.
- **Drafting risk:** Stating "exactly 400 photocells" or "exactly N association units" without the operator manual would make the chapter vulnerable to a later correction by someone with the manual.
- **Next action:** Extract `MarkI-Manual60` from DTIC or Wayback and record verbatim hardware counts with page anchors. Until then, prose must use "approximately 400 photocells" or "a roughly 20x20 sensory array."

### NPL 1958 Symposium Detail

- **Question:** What were the session order, discussion record, and any documented direct interaction between Rosenblatt, Selfridge, and McCarthy at the November 1958 NPL symposium?
- **Current status:** `MTP59-NPL` proceedings table of contents confirms paper-list co-presence (Green); session-order, discussant remarks, and any chair commentary remain a worklist item (Yellow).
- **Drafting risk:** Asserting that "Rosenblatt and McCarthy debated face to face" or that "Selfridge supported Pandemonium against the perceptron" without proceedings-page evidence would over-dramatize the 1958 collision.
- **Next action:** Pull `MTP59-NPL` table of contents and (where available) discussion sections; record any documented cross-paper exchanges.

### Block 1962 / Novikoff 1962 Page Extraction

- **Question:** What does H. D. Block's 1962 *Reviews of Modern Physics* exposition specifically argue, and how does Novikoff's 1962 tightened convergence proof relate structurally to Rosenblatt's `POND61` chapter 5 statement?
- **Current status:** Both papers have Green bibliographic existence; the substance of the arguments is Yellow until pages are extracted.
- **Drafting risk:** Citing Block as endorsing Rosenblatt's position without page anchors could overstate the endorsement; citing Novikoff's proof as "tighter" without page anchors could misrepresent the assumption set.
- **Next action:** Extract `Block62-RMP` and `Novikoff62` from APS and the Symposium on the Mathematical Theory of Automata proceedings respectively.

### Widrow-Hoff ADALINE Page Extraction

- **Question:** What is the exact relationship between ADALINE's least-mean-squares weight-adjustment procedure and the perceptron error-correction reinforcement procedure?
- **Current status:** `WidrowHoff60` bibliographic record is Green; the structural-comparison claim with Mark I's reinforcement procedure is Yellow until both papers are fully extracted.
- **Drafting risk:** Asserting structural equivalence or precedence between ADALINE and the perceptron without page anchors would falsify a contested precedence claim that later neural-network-history literature still debates.
- **Next action:** Extract `WidrowHoff60` from Stanford archives or IRE WESCON records.

### Tobermory Continuity Records

- **Question:** What are the specific Tobermory publications, dates, and authorship breakdown for the auditory-perceptron CAL successor?
- **Current status:** Project existence and Wightman's continuing role at CAL are well-attested in secondary sources and Cornell records; specific publications remain a worklist item.
- **Drafting risk:** Naming Tobermory as a continuity beat without primary publications would weaken the program-continuity claim.
- **Next action:** Locate `Tobermory62-65` primary publication(s) with Wightman as continuity author.

### Rosenblatt 1971 Death Record

- **Question:** What is the primary record (Cornell faculty record, contemporary press obituary, ONR record) for Rosenblatt's 11 July 1971 sailing accident?
- **Current status:** Widely cited in secondary literature (Cornell Chronicle 2019; Olazaran 1996; Anderson and Rosenfeld 1988); a primary obituary is the Yellow-to-Green upgrade.
- **Drafting risk:** Asserting precise birthday-coincidence or boat-type detail without a primary record would make a melodramatic close vulnerable to correction.
- **Next action:** Locate a primary obituary.

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
| 400 photocells in a 20x20 sensory array | `MarkI-Manual60` direct page | Required hardware specificity; precise count is currently Red until manual page anchor lifts it. |
| Motorized potentiometers implemented adjustable weights | `MarkI-Manual60` direct page | Makes analog learning physically concrete. |
| Exact A/R unit counts for the Mark I configuration | `MarkI-Manual60` direct page | Avoids mixing versions of Mark I. |
| NYT "walk, talk..." wording and attribution direction | `NYT58` original scan/text | Currently Red against direct attribution to Rosenblatt's technical voice; lifts to Yellow or Green only with original scan. |
| Statistical separability theorem chronology | `TwoTheorems59` pages | Strengthens mathematics scene. |
| IBM 704 simulation experiment details | `IRE60` full pages | Supports a richer simulation paragraph. |
| CAL first full report content | `VG1196G1` pages | Connects 1958 report to article and book. |
| Minsky "loyal opposition" context | Minsky 1961 IRE article | Lets the chapter foreshadow Ch17 without importing it. |
| NPL 1958 symposium session order and discussion | `MTP59-NPL` proceedings pages | Anchors the documented 1958 collision without overdramatizing direct interaction. |
| Block 1962 mathematical exposition structure | `Block62-RMP` pages | Anchors the independent-legitimacy beat in Scene 4. |
| Novikoff 1962 tightened convergence proof | `Novikoff62` pages | Pairs with Block as outside-Rosenblatt mathematical legitimacy. |
| Widrow-Hoff ADALINE structure | `WidrowHoff60` pages | Anchors the contemporary cybernetic-hardware parallel. |
| Hubel-Wiesel V1 receptive-field hierarchy | `HubelWiesel59-62` pages | Confirms the structural-resonance beat in Scene 2. |
| Tobermory continuity record | `Tobermory62-65` primary publications | Anchors the program-continuity beat in Scene 5. |
| Rosenblatt 1971 sailing-accident record | `Rosenblatt71` primary obituary | Anchors the historiographic-muting beat in Scene 5. |

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
