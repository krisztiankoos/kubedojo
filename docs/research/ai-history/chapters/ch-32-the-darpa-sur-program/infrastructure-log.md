# Infrastructure Log: Chapter 32 — The DARPA SUR Program

Technical and institutional metrics relevant to the chapter's infrastructure-history thesis. Each row is what made the SUR program *operationally* possible (or what its operational limits were). Verification colors are tracked because infrastructure claims that look like throwaway facts are often the ones secondary sources copy from each other without primary evidence.

## SUR Program Charter (1971)

| Item | Value | Verification |
|---|---|---|
| Funder | ARPA-IPTO (Advanced Research Projects Agency, Information Processing Techniques Office) | **Green** — Newell 1971 cover acknowledgment: "The research reported in here was sponsored and supported by the Information Processing Techniques Office of the Advanced Research Projects Agency of the Office of the Secretary of Defense" (PDF p.3). |
| Study group chaired by | Allen Newell | **Green** — Newell 1971 cover (PDF p.3). |
| Study group report date | May 1971 | **Green** — Newell 1971 cover (PDF p.3). |
| Republication | North-Holland/American Elsevier, 1973 | **Green** — Bahl/Jelinek/Mercer 1983 Reference [21]. |
| Program duration | Five years (1971-1976) | **Green** — Newell 1971 Section 1.1 Conclusion 2: "Five years provides a reasonable chance of success for the system with the final specifications" (PDF p.11). Confirmed by CMU 1977 report Section I "five-year research program" (PDF p.7). |
| Number of contractor sites | Multiple (CMU, BBN, SDC, SRI by most secondary accounts) — exact contract values not pulled from primary ARPA-IPTO records. | Yellow for the specific list; Green for the multi-contractor structure as such (Newell 1971 Section 1.1 Conclusion 5 explicitly calls for "widespread involvement by several technical communities", PDF p.11; CMU 1977 report describes the CMU-internal multi-system approach). |

## Newell 1971 Final Specifications

The 19-item Final Specifications table (Section 1.2, PDF p.12) is the load-bearing infrastructure-charter artifact for the chapter. The columns below reproduce the table in spirit; for prose, cite the table directly.

| Spec # | Final Specification (1976 target) | Verification |
|---|---|---|
| (1) | accept continuous speech | **Green** — Newell 1971 §1.2. |
| (2) | from many | **Green** — Newell 1971 §1.2. |
| (3) | cooperative speakers of the General American dialect | **Green** — Newell 1971 §1.2. |
| (4) | in a quiet room | **Green** — Newell 1971 §1.2. |
| (5) | over a good quality microphone | **Green** — Newell 1971 §1.2. (Initial spec had said "over a telephone"; downgraded to good-quality microphone in the Final spec.) |
| (6) | allowing slight tuning of the system per speaker | **Green** — Newell 1971 §1.2. |
| (7) | but requiring only natural adaptation by the user | **Green** — Newell 1971 §1.2. |
| (8) | permitting a slightly selected vocabulary of 1,000 words | **Green** — Newell 1971 §1.2. (Initial spec was 10,000 words.) |
| (9) | with a highly artificial syntax | **Green** — Newell 1971 §1.2. |
| (10) | and a task like the data management or computer status tasks (but not the computer consultant task) | **Green** — Newell 1971 §1.2. |
| (11) | with a simple psychological model of the user | **Green** — Newell 1971 §1.2. |
| (12) | providing graceful interaction | **Green** — Newell 1971 §1.2. |
| (13) | tolerating less than 10% semantic error | **Green** — Newell 1971 §1.2. |
| (14) | in a few times real time | **Green** — Newell 1971 §1.2. |
| (19) | demonstrable in 1976 with a moderate chance of success | **Green** — Newell 1971 §1.2. (Initial spec had said "demonstrable in 1973".) |

## Newell 1971 Methodological Proposal (Section 8.6)

| Item | Verification |
|---|---|
| "Public Data and Public Analysis" subsection title and body text in §8.6 | **Green** — Newell 1971 PDF p.50. Verified verbatim: "If the claims are not made against a background of publicly available high quality data of known structure, it will never be possible to understand the claims or their basis. The issue is not one primarily of assigning credit, but of making progress by understanding success and failure." |
| Three-direction extension of the methodology in §8.7 | **Green** — Newell 1971 PDF p.50-51. Three directions: "adequate task description"; "instrumenting the systems (both hardware and software) and taking appropriate measurements"; "operating total speech-understanding system" as a baseline-readiness criterion. |

## HARPY (CMU, 1976) — measured against the Final Specifications

| Spec | Newell 1971 target (Nov 1971) | HARPY achieved (Nov 1976) | Verification |
|---|---|---|---|
| Speakers | Many cooperative speakers | 5 (3 male, 2 female) | **Green** — CMU 1977 Figure 1 (PDF p.8); Lowerre & Reddy 1979 Figure 15-1. |
| Environment | Quiet room | Computer terminal room | **Green** — same anchors. |
| Microphone | Good-quality microphone | Close-talking microphone | **Green** — same anchors. |
| Per-speaker tuning | Slight | 20-30 sentences per talker (CMU 1977) / "substantial tuning (20-30 utterances/speaker)" (Lowerre & Reddy 1979) | **Green** — same anchors. The CMU 1977 wording is the more measured "20-30 sentences per talker"; prose should use that wording rather than the Lowerre-Reddy "substantial tuning" gloss. |
| Vocabulary | Slightly selected 1,000 words | 1,011 words, no post-selection (Lowerre & Reddy 1979) | **Green** — same anchors. |
| Syntax | Highly artificial | Combined syntactic and semantic constraints, average branching factor 33 (CMU 1977) / 10 (Lowerre & Reddy 1979) — discrepancy across the two CMU sources | **Green** for the average-branching-factor *concept*; **Yellow** for the specific number (10 vs. 33 across CMU primary sources). Use prose hedging: "an average branching factor reported between 10 and 33 across CMU's own retrospectives." |
| Task | Data management or computer status | Document retrieval | Yellow for whether "document retrieval" formally satisfies the Newell 1971 "data management" specification. The CMU sources treat this as in-scope; prose should not relitigate. |
| Semantic error | Less than 10% | 5% | **Green** — CMU 1977 Figure 1 (PDF p.8); Lowerre & Reddy 1979 Figure 15-1. |
| Real-time factor | A few times real time (taken to mean 200-500 MIPSS on a 100 MIPS machine, per Lowerre & Reddy 1979 footnote) | 28 MIPSS, equivalent to 80× real-time on a .35 MIPS PDP-KA10 | **Green** — Lowerre & Reddy 1979 Figure 15-1. |
| Demonstration deadline | 1976, moderate chance of success | Operational 13 August 1976 | **Green** — Lowerre & Reddy 1979 Figure 15-1. |
| Hardware | "Dedicated system with 10⁸ instructions per second" (Initial spec only — the Final spec dropped this constraint) | 256K of 36-bit words on a PDP-KA10 | **Green** — CMU 1977 Figure 1 (PDF p.8). |
| Cost per processed sentence | Not specified | About $5 per sentence (CMU 1977); reproduced in Lowerre & Reddy 1979. | **Green** — same anchors. |

## HEARSAY-II (CMU, 1976) — measured

| Spec | HEARSAY-II achieved (1977) | Verification |
|---|---|---|
| Vocabulary | 1,011 words (same task as HARPY) | **Green** — CMU 1977 PDF p.13. |
| Sentence error (AIX05 grammar) | About 16% | **Green** — CMU 1977 PDF p.13. (Note: this is sentence error, not semantic error; the report uses both metrics interchangeably in this section.) |
| Sentence error (AIX15 grammar — more complex syntax) | About 42% (semantic error 26%) | **Green** — CMU 1977 PDF p.13. |
| Speed | 2-20× slower than HARPY | **Green** — CMU 1977 PDF p.13. |
| Met Newell 1971 Final Specifications | No | **Green** by Juang & Rabiner 2005 PDF p.9 ("Neither Hearsay-II nor HWIM met the DARPA program's performance goal"). |

## BBN HWIM and SDC systems

| Item | Value | Verification |
|---|---|---|
| Met Newell 1971 Final Specifications | Neither HWIM nor SDC met the targets at the September 1976 demonstration | Yellow — anchored only via Klatt 1977 transmission through Juang & Rabiner 2005 PDF p.9. The Klatt 1977 PDF is paywalled at AIP. |
| HWIM design hallmark | Lexical decoding network with sophisticated phonological rules; lattice-based handling of segmentation ambiguity; word verification at the parametric level | **Green** for the design description — Juang & Rabiner 2005 PDF p.9-10. |
| SDC system design hallmark | Not characterized in available secondary sources beyond institutional listing | Red — would benefit from Klatt 1977 anchor for the SDC-specific architecture. |

## IBM Continuous Speech Recognition Group (1971+) — parallel infrastructure

| Item | Value | Verification |
|---|---|---|
| Institution | IBM Thomas J. Watson Research Center, Yorktown Heights NY | **Green** — Bahl/Jelinek/Mercer 1983 byline ("The authors are with the IBM T. J. Watson Research Center, Yorktown Heights, NY 10598"). |
| Group leader | Frederick Jelinek | **Green** — Juang & Rabiner 2005 PDF p.10 ("IBM's effort, led by Fred Jelinek"). |
| Acknowledged group members (1983) | J. K. Baker, J. M. Baker, R. Bakis, P. Cohen, A. Cole, R. Dixon, B. Lewis, E. Muckstein, H. Silverman | **Green** — Bahl/Jelinek/Mercer 1983 Acknowledgment section. NB: J. K. Baker is the same Jim Baker whose Dragon system was the within-SUR statistical exception at CMU; he subsequently moved to IBM. |
| Recognition framing | Maximum-likelihood decoding over a noisy communication channel | **Green** — Bahl/Jelinek/Mercer 1983 abstract (p.179) and §III. |
| Acoustic model | Markov sources (subsequently called HMMs) | **Green** — Bahl/Jelinek/Mercer 1983 §IV. |
| Parameter estimation | Forward-Backward Algorithm | **Green** — Bahl/Jelinek/Mercer 1983 §VII. |
| Task-difficulty metric | Perplexity (information-theoretic) | **Green** — Bahl/Jelinek/Mercer 1983 §IX. The 1983 paper is unambiguous: "vocabulary size … by itself is practically useless as a measure of difficulty. In this section we describe perplexity, a measure of difficulty based on well established information theoretic principles." |
| Tasks tested in 1983 paper | Raleigh Language; Laser Patent Text corpus; CMU-AIX05 (the same task CMU used for HARPY to meet the ARPA specifications) | **Green** — Bahl/Jelinek/Mercer 1983 §X p.189 explicitly notes the AIX05 task "is the task used by Carnegie-Mellon University in their Speech Understanding System to meet the ARPA specifications." |
| IBM acoustic-model accuracy comparison (Jelinek slide) | Phonetic baseforms / expert-estimated statistics: 35%; phonetic baseforms / automatically estimated: 75%; orthographic baseforms / automatically estimated: 43% | **Green** — Jelinek 2005 LREC slides PDF p.3-4 ("When Linguists Left the Group" slide). The exact dataset and year of the underlying experiment are not stated on the slide; cite carefully. |
| Methodological maxim | "There is no data like more data" — Mercer at Arden House, 1985 | **Green** — Jelinek 2005 LREC slides PDF p.5. |

## Hardware constraints worth foregrounding in prose

These are the infrastructure constraints the chapter should foreground when explaining why the 1971-1976 SUR program produced the systems it did and what made the IBM-statistical track plausible only later:

- **HARPY ran on a .35 MIPS PDP-10** at CMU. By Lowerre & Reddy 1979's own framing, the Newell 1971 "few times real time" target had been benchmarked against an assumed 100 MIPS dedicated machine (Initial spec) — meaning HARPY achieved the specification by being algorithmically efficient on much weaker hardware than the spec assumed (28 MIPSS at .35 MIPS = 80× real time). The HARPY achievement is therefore as much an algorithm-design result as a hardware-utilization result.
- **The IBM-statistical track was compute-bound until mid-1980s.** Bahl/Jelinek/Mercer 1983's acknowledgment that "recognition often requires many seconds of CPU time for each second of speech" (p.179) means the IBM Tangora demonstrations of the early 1980s were not "real-time" in the consumer sense. The statistical methods were data-bound and compute-bound; their later dominance was unlocked by Moore's-law compute and the Charles Wayne-era benchmark corpora, not by mid-1970s breakthroughs.
- **No shared evaluation server existed.** The "common task" methodology Newell 1971 §8.6 proposed required physical tape distribution and per-site evaluation through 1976. Charles Wayne's 1980s revival institutionalized NIST-evaluated benchmarks (Church 2018) — the missing piece Newell 1971 named but did not have the institutional plumbing to provide.

## Notes

- This chapter's infrastructure thesis is not "SUR had bad hardware and that's why HARPY was slow" — HARPY met its real-time target on weaker hardware than the spec assumed. The infrastructure thesis is that *the methodology was the infrastructure*: common tasks, instrumented systems, public data. That methodology is what propagated forward to the 1980s benchmark culture.
- Where this log lists numbers from CMU's own retrospectives (1977 report, 1979 chapter), prose should prefer the more measured of the two phrasings when both are anchored. CMU's 1977 report is consistently more cautious than Lowerre & Reddy 1979.
