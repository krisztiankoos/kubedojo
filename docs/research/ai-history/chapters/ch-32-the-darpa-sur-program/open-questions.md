# Open Questions: Chapter 32 — The DARPA SUR Program

Surfaced from `brief.md` *Conflict Notes* and the Yellow/Red entries in `sources.md`. Each question identifies the specific evidence needed to resolve it. Drafting cannot rely on any open-question item until its evidence is in hand.

## Resolution Required Before Drafting

### Q1. Klatt 1977 page-level anchors for HWIM and SDC failure-to-meet-target numbers
- **Question:** What specific performance numbers did BBN HWIM and SDC achieve at the September 1976 demonstration, against which lines of the Newell 1971 Final Specifications?
- **Why it matters:** Scene 3 currently anchors HARPY (5% semantic error, 80× real-time) and HEARSAY-II (16%/26% semantic error, 2-20× slower than HARPY) at the page level via the CMU 1977 report and the Lowerre-Reddy 1979 chapter. The HWIM and SDC numbers are anchored only via Juang & Rabiner 2005's transmission of Klatt 1977. If Scene 3 wants to state specific HWIM or SDC numbers in prose, those numbers need direct primary anchoring.
- **Evidence needed:** Klatt 1977 *JASA* PDF (paywalled at AIP); ACM Digital Library mirror (`dl.acm.org/citation.cfm?id=108276`, requires institutional access); the BBN HWIM final report (likely BBN Technical Report or DTIC); the SDC SUR final report (likely SDC Technical Report or DTIC).
- **Status:** Yellow. Non-blocking for the chapter's thesis (which is methodological, not contractor-comparative). Drafting can proceed without the HWIM/SDC numbers if Scene 3 hedges with the framing "Of the four contractor systems, only HARPY met the Final Specifications" rather than stating specific HWIM/SDC numbers.

### Q2. Pierce 1969 verbatim text via the original JASA PDF
- **Question:** Are the verbatim Pierce quotes the chapter cites in Scene 1 (via Jelinek 2005 LREC slides and Church 2018 NLE) verifiable directly against the original *JASA* 46(4B):1049-1051 article?
- **Why it matters:** The chapter's Scene 1 currently treats Pierce 1969's verbatim text as Green-by-convergence (two independent secondary sources transmit identical wording). This is acceptable per the convergence rule used in Ch11 sources.md — but a direct PDF would Green-promote the quotes without convergence dependency.
- **Evidence needed:** The original Pierce 1969 *JASA* article PDF (paywalled at AIP at `https://pubs.aip.org/asa/jasa/article-abstract/46/4B/1049/746573`); a university library scan; or an archive.org scan if one exists.
- **Status:** Yellow. Non-blocking if the convergence-rule framing is accepted. Worth a fresh attempt before prose drafting unlocks.

### Q3. ARPA-IPTO contract values and recipients for SUR
- **Question:** Which contractor sites received ARPA-IPTO contracts under SUR, in what amounts, and on what schedule? The chapter currently lists CMU, BBN, SDC, SRI as contractor sites (per secondary sources) but does not anchor the contract values.
- **Why it matters:** Scene 2 (the Newell charter) and Scene 3 (the September 1976 demonstration) would benefit from knowing whether SUR's funding pattern matched what Newell 1971 §8.7 had recommended (a formal multi-contractor structure with cooperative-evaluation oversight). Without contract-level anchors, the institutional-history claim relies on Newell 1971's *recommendations* rather than ARPA's *implementation*.
- **Evidence needed:** ARPA-IPTO program records, NARA (National Archives and Records Administration); DTIC (Defense Technical Information Center) for SUR-era technical reports; Cornell or RAND Corporation archives for ARPA program-management documentation.
- **Status:** Red. Likely requires physical archive access or correspondence with archivists. Not load-bearing for the chapter's thesis.

### Q4. Was DARPA's post-1976 funding-cut decision tied to specific SUR outcomes, or part of a broader IPTO retrenchment?
- **Question:** Did DARPA cut speech-understanding funding because three of four contractor systems failed to meet the Final Specifications, or for broader institutional reasons (Mansfield Amendment effects, IPTO leadership changes, post-Vietnam DoD budget pressure)?
- **Why it matters:** The chapter's Scene 5 attributes the post-1976 funding winter to "DARPA did not extend SUR funding into a follow-on program" (Church 2018 framing). If the funding-cut was specifically tied to HWIM/SDC failure to meet targets, the chapter's narrative arc strengthens. If it was a broader institutional retrenchment, the connection to SUR's measurement methodology is more indirect.
- **Evidence needed:** ARPA-IPTO program-management memoranda from 1976-1978; Klatt 1977 §V "Discussion" or §VI "Conclusions" if those sections discuss DARPA's reception of the demonstrations; Reddy or Newell oral histories.
- **Status:** Yellow. Church 2018's "funding winter" framing is sufficient for the chapter's thesis. Deeper resolution would tighten Scene 5 but is not required.

### Q5. Did Charles Wayne explicitly cite Newell 1971 §8.6 when designing the mid-1980s common-task method?
- **Question:** Was Wayne's "common task method" a deliberate institutional return to Newell 1971's methodology, or an independent re-derivation?
- **Why it matters:** The chapter's central thesis claim — that SUR's most durable contribution was the measurement methodology that Newell named in 1971 and Wayne re-institutionalized — is structurally well-anchored at both endpoints. But the *causal* link between Newell 1971 §8.6 and Wayne's mid-1980s revival is currently inferential, not documentary. If Wayne explicitly cited Newell 1971 in his program designs, the link becomes direct.
- **Evidence needed:** Charles Wayne's program-management documents from DARPA (mid-1980s); any retrospective interviews with Wayne; the early NIST evaluation-program documentation for ATIS, Resource Management, etc.
- **Status:** Yellow. The chapter can make the structural-return claim without the explicit citation; prose should use careful framing ("Wayne's common-task method was structurally a return to Newell 1971 §8.6's proposal") rather than asserting deliberate inheritance.

## Lower-Priority Questions (Do Not Block Drafting)

### Q6. The exact 1971 ARPA contract award dates for SUR
- **Question:** When in 1971-1972 were the SUR contracts awarded to CMU, BBN, SDC, and SRI?
- **Why it matters:** Minor — the chapter does not depend on specific contract-award dates. The Newell 1971 study group report is dated May 1971; CMU 1977 frames the program institutionally as "In 1971, a group of scientists recommended the initiation of a five-year research program." Specific contract dates are background detail.
- **Evidence needed:** ARPA-IPTO program records; CMU institutional records.
- **Status:** Yellow. Non-blocking.

### Q7. The IBM Tangora system's specific performance numbers in the early 1980s
- **Question:** What were the IBM Tangora system's specific performance benchmarks during the SUR-era and immediate post-SUR period?
- **Why it matters:** Scene 4 introduces the IBM-statistical track but does not (and should not, per the chapter's HMM-out-of-scope boundary) deeply benchmark Tangora. Specific Tangora numbers are useful only if they directly contrast with HARPY's 1976 demonstration; the chapter leans instead on the methodological framing in Bahl/Jelinek/Mercer 1983.
- **Evidence needed:** Bahl/Jelinek/Mercer 1983 §X experimental tables (already in hand at the page level — see `infrastructure-log.md`); IBM internal technical reports from 1979-1985; Juang & Rabiner 2005 expansion on Tangora.
- **Status:** Yellow. The 1983 paper's experimental tables are already in hand. Tangora-specific benchmarks would only be load-bearing if the chapter argued Tangora outperformed HARPY in the late 1970s — which the chapter does not.

### Q8. Whether HEARSAY-II's "blackboard architecture" was anticipated or independently arrived at
- **Question:** Was HEARSAY-II's parallel-asynchronous-blackboard knowledge-source architecture anticipated by anyone outside CMU, or was it CMU-internal?
- **Why it matters:** Background detail. Juang & Rabiner 2005 PDF p.9 calls HEARSAY-II's blackboard "a pioneering concept." The chapter does not explore this beyond a one-line mention.
- **Evidence needed:** Erman et al. 1980 *Computing Surveys* paper on the HEARSAY-II architecture; the Lesser et al. publications.
- **Status:** Yellow. Non-blocking.

### Q9. Pierce's pre-1969 statements on speech recognition
- **Question:** Did Pierce make critical statements about speech recognition before the 1969 *JASA* letter that the chapter should acknowledge?
- **Why it matters:** Background. The 1969 letter is widely treated as Pierce's definitive ASR critique. Earlier Pierce statements (e.g., in Bell Labs internal documents or 1960s talks) would deepen the funding-climate framing but are not load-bearing.
- **Evidence needed:** Bell Labs archives; Pierce's papers if archivally accessible.
- **Status:** Yellow. Non-blocking.

### Q10. The dissertation-summary vs. full-thesis discrepancy in Lowerre 1976
- **Question:** Why does the Stanford-hosted Lowerre 1976 PDF appear to be a "Thesis Summary" rather than the full dissertation, and where is the full dissertation accessible?
- **Why it matters:** The Stanford PDF documents only the smaller-vocabulary HARPY pilot tasks (37-word desk calculator); the headline 1,011-word task is anchored via the Lowerre & Reddy 1979 chapter and the CMU 1977 report instead. The chapter's anchors are sufficient; locating the full dissertation would only deepen Scene 3.
- **Evidence needed:** CMU library or proxy access to the full Lowerre 1976 dissertation.
- **Status:** Yellow. Non-blocking; current anchors are sufficient.

## Notes on resolution sequence

The order of attempted resolution:
1. ✅ **Done (Claude 2026-04-28):** Newell 1971 PDF (Sections 1.1, 1.2, 8.6 anchored), Bahl/Jelinek/Mercer 1983 PDF (abstract / Sections II/IV/VII/IX/X anchored), Jelinek 2005 LREC slides PDF (provenance of "fire a linguist" quote and verbatim Pierce transmission anchored), CMU 1977 SUR Summary Report PDF (HARPY-vs-target table and HEARSAY-II numbers anchored), Lowerre & Reddy 1979 chapter PDF (Section 15-2 + Figure 15-1 anchored), Juang & Rabiner 2005 PDF (SUR scope, IBM parallel track, late-1980s/1990s revival anchored), Church 2018 NLE tribute (Wayne, funding winter, Pierce verbatim anchored).
2. **Klatt 1977 JASA PDF** — would resolve Q1 (HWIM/SDC numbers) and partially Q4 (whether DARPA's funding cut was tied to specific SUR outcomes). Paywalled; tractable via institutional access.
3. **Pierce 1969 JASA PDF directly** — would resolve Q2 (verbatim convergence dependency). Paywalled; tractable via institutional access.
4. **ARPA-IPTO contract records** — would resolve Q3, Q4, Q6. Archive-blocked; requires NARA or DTIC access.
5. **Charles Wayne's mid-1980s DARPA program documents** — would resolve Q5 (Newell-1971-to-Wayne causal link). Archive-blocked or institutional-history archive access.

Rows 2-3 are tractable without physical archive trips. Rows 4-5 require either archive access or correspondence with archivists. The chapter has reached `capacity_plan_anchored` status: every Prose Capacity Plan layer cites at least one verified primary or transmitted-verbatim secondary anchor, and the Scene-Level Claim Table has 14 Green claims out of approximately 17 (the remaining 3 are Yellow with documented Klatt-1977-paywall or institutional-history dependencies).
