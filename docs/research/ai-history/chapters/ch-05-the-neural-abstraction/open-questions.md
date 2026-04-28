# Open Questions: Chapter 5 — The Neural Abstraction

The questions below are concrete (per the TEAM_WORKFLOW guidance: "Need Pearl 1986 page anchor for local propagation in singly connected networks" beats "need more sources"). Each names the specific anchor, why it would matter, and what archive would supply it.

## Q1. Did von Neumann's *First Draft of a Report on the EDVAC* (June 1945) actually cite only McCulloch & Pitts 1943? — **RESOLVED 2026-04-28**

- **Resolution.** Yes. Verified by Claude `curl` + `pdftotext -layout` on the Internet Archive scan (`https://archive.org/download/firstdraftofrepo00vonn/firstdraftofrepo00vonn.pdf`). The M-P 1943 citation appears at Section 4.2, p.12 verbatim: "Following W. Pitts and W. S. McCulloch ('A logical calculus of the ideas immanent in nervous activity', Bull. Math. Bio-physics, Vol. 5 (1943), pp 115-133) we ignore the more complicated aspects of neuron functioning…" A `grep -E "Vol\.|Bull\."` pass over the entire 7,825-line OCR returns exactly this one citation pair. Gefter's claim stands.
- **Sources.md / timeline.md / infrastructure-log.md updated** to reflect Green status.

## Q2. Does Smalheiser 2000 confirm or contradict the Lettvin-oral-history Pitts scenes (1935 library, 1938 Chicago run-away, the Russell letter)?

- **Why it matters.** Smalheiser's *Perspectives in Biology and Medicine* paper is the most careful published Pitts biography. The chapter currently labels the scenes as "Lettvin-oral-history reconstruction" and pulls them from Gefter 2015. Smalheiser may explicitly hedge them, partially confirm them, or document independent sources (e.g., letters from Pitts's mother or Detroit school records) that change the story. The Pitts-biography layer's word budget hangs on whether Smalheiser holds up the dramatic specifics.
- **What would resolve it.** Physical-journal access to *Perspectives in Biology and Medicine* vol. 43, pp. 217-226. JHU MUSE returns Imperva captcha; the paper is closed-access on Semantic Scholar. A library-system PDF or a scanned reprint would convert all Pitts-biography Yellow rows in `sources.md` to Green/Yellow with paragraph anchors.
- **Estimated effort.** Depends on library access; not tractable without an institutional or interlibrary-loan route.

## Q3. Where exactly does the Russell-Whitehead bibliographic citation live in *Principia Mathematica*'s second edition, and does the M-P 1943 paper's in-text "1927" vs literature-list "1925" indicate Volume 1 vs. Volumes 2-3?

- **Why it matters.** *Principia* second edition was published 1925-1927 (Vol. 1: 1925; Vols. 2-3: 1927). M-P 1943 p.118 says "Russell and Whitehead (1927)" in the body but "Russell, B. and A. N. Whitehead. 1925. Principa Mathematics" in the literature list (p.131). This is probably a clerical inconsistency, not a substantive one — but the chapter's bibliographic discipline benefits from saying so explicitly.
- **What would resolve it.** A short bibliographic note checked against any *Principia* second-edition spine date. Low-priority, but worth a sentence in the chapter's bibliography or footnote.
- **Estimated effort.** ~10 minutes.

## Q4. Are there McCulloch-Pitts contemporary letters that document the writing of the 1943 paper itself (not just Pitts's later 1943 MIT letter to McCulloch)?

- **Why it matters.** The chapter currently has no primary anchor on the 1942-1943 collaboration as it happened. Gefter 2015 paraphrases Lettvin's later oral history and the McCulloch household scenes. McCulloch Papers BM139 at the American Philosophical Society almost certainly contains some pre-publication correspondence (drafts, referee responses from Rashevsky as editor, internal back-and-forth between McCulloch and Pitts). One or two such letters at paragraph anchor would dramatically firm up Scenes 1 and 2.
- **What would resolve it.** A research request to the American Philosophical Society for a finding-aid scan of BM139, Series I (Correspondence), Folder "Pitts, Walter" — covering 1942-1943. APS handles such requests by email and often provides scans within a few weeks for non-restricted items.
- **Estimated effort.** Asynchronous (~weeks). Out of scope for this contract; flagged for the human editor to consider before prose drafting.

## Q5. What did Stephen Kleene's 1956 reading of M-P 1943 add or correct in the original calculus, and does Aizawa & Schlatter 2008 *Synthese* "Walter Pitts and 'A Logical Calculus'" treat the paper differently from Piccinini 2004?

- **Why it matters.** The chapter's honest close attributes "led to finite automata" to Piccinini 2004's abstract characterisation. Kleene's 1956 paper "Representation of Events in Nerve Nets and Finite Automata" (in the Shannon-McCarthy *Automata Studies* volume) is the actual document where the M-P-to-finite-automata move happens. If Kleene's reading is on hand, the honest close can replace a Piccinini-secondary paraphrase with a primary anchor. Aizawa-Schlatter 2008 may also clarify whether Piccinini's "first computational theory of mind and brain" claim is the consensus close-reading or a contested reading.
- **What would resolve it.** Fetch the Kleene 1956 paper (open-access in *Automata Studies* mirrors at Princeton or the Annals of Mathematics Studies series); fetch Aizawa-Schlatter 2008 metadata via Semantic Scholar and attempt an open-access route. If Piccinini's reading turns out to be contested, the chapter's honest close needs a hedging sentence.
- **Estimated effort.** ~1 hour of fetch + skim. Tractable but not done in this contract.

## Q6. Did the 1943 paper actually have any biological-neuroscience uptake in 1943-1949, or is the chapter's "biology absorbed it slowly" claim under-supported?

- **Why it matters.** The chapter claims that the 1943 paper's primary downstream reach was into computer science (Kleene, von Neumann), not biological neuroscience. Hebb 1949 p.xv treats M-P as part of a community whose work "has been obliged to simplify the psychological problem almost out of [recognition]" — which is suggestive of slow uptake but not definitive. McCorduck 1979 and Crevier 1993 likely contain detail; both are paywalled / physical-only.
- **What would resolve it.** Page anchors in McCorduck *Machines Who Think* (Ch.4 likely) on the M-P paper's reception in the late 1940s. Same physical-access problem as Q2; same library route.
- **Estimated effort.** Asynchronous, depends on library access.

## Q7. Was Pitts in fact only 18 (or 19) when he met McCulloch?

- **Why it matters.** Gefter 2015 paragraph 7 says "McCulloch, 42 years old when he met Pitts… Pitts, 18." If McCulloch was 42 and the meeting is in early 1942, McCulloch's birth year is c. 1900 (close to the standard 1898) and Pitts (b. 1923) would be 18 in early 1942 — consistent. But the brief.md and people.md hedge "18-19" because the exact meeting date is not anchored. Smalheiser 2000 likely fixes a precise date.
- **What would resolve it.** Same as Q2 (Smalheiser physical-journal access).
- **Estimated effort.** Same as Q2.

## Q8. Did McCulloch's pre-Pitts thinking about a Leibnizian / propositional-logic model of the brain leave a paper trail?

- **Why it matters.** Gefter 2015 paragraph 7 reports McCulloch as already pursuing "a Leibnizian logical calculus" before Pitts arrived. If McCulloch had unpublished notes, conference talks, or earlier papers from his Yale or Columbia years that prefigured the 1943 calculus, Scene 2 could promote its "McCulloch was looking for a logical foundation" claim from Yellow to Green via primary anchors. Probable archival home: McCulloch Papers BM139 or Yale's School of Medicine archives.
- **What would resolve it.** Same APS route as Q4, plus a secondary check on McCulloch's published bibliography in the 1930s for any propositional-logic precursor papers.
- **Estimated effort.** Asynchronous; out of scope for this contract.

## Priority Ladder

Q1 was resolved during this contract pass (2026-04-28). The remaining questions are ordered by tractability:

1. **Q5** (Kleene 1956 + Aizawa-Schlatter 2008) — tractable in ~1 hour of online fetch; would convert "led to finite automata" from Piccinini-secondary-paraphrase to a primary-paper anchor.
2. **Q3** (Russell-Whitehead 1925 vs 1927 dating clarification) — ~10 minutes; bibliographic discipline only.
3. **Q2 / Q7** (Smalheiser 2000 paragraph access) — needs library access, asynchronous; would resolve all Pitts-biography Yellow rows.
4. **Q4 / Q8** (McCulloch Papers BM139 at APS) — research request, weeks; would firm up Scenes 1 and 2.
5. **Q6** (McCorduck 1979 reception details) — library access; secondary-quality improvement.

The chapter can begin drafting at the lower end of the 3,600-5,100 word range without these. The upper end requires at least one of Q2 or Q4/Q8 to land.
