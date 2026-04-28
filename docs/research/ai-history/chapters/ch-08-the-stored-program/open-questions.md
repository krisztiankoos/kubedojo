# Open Questions: Chapter 8 — The Stored Program

## Q1. Was the public-domain disclosure of the *First Draft* deliberate or accidental?

**Status: Yellow (interpretation-dependent; one party's reading)**

Eckert in OH 13 (1977, pp.46-47) is unambiguous: von Neumann arranged the distribution to put the engineers' work into the public domain so he could continue to consult freely for IBM (OH 13 p.37). Goldstine in *The Computer from Pascal to von Neumann* (1972) gives a different account that emphasizes the wartime declassification calendar and the openness norms of academic mathematics.

What would resolve this:
- Direct page anchors from Goldstine 1972 (physical book; archive-blocked).
- Stern 1981 *From ENIAC to UNIVAC* page anchors for Stern's own analysis (physical book).
- Penn archives: Pender's letters to Eckert and Mauchly during the 1945-1946 patent-assignment dispute. The University of Pennsylvania Archives and Records Center holds the ENIAC Patent Trial Collection (UPD 8.10).
- Library of Congress records: any contemporary documentation of the *First Draft*'s deposit and the technical-report-bar mechanism.

What the chapter must do until this is resolved: present Eckert's reading as Eckert's, alongside the documented fact of distribution, without converting interpretation into established cause-and-effect.

## Q2. Who actually authored which ideas in the *First Draft*?

**Status: Yellow (likely permanently un-decidable in detail)**

Haigh 2014 p.5 ("at least some of the ideas") and Eckert OH 13 pp.46-47 (Eckert's stronger claim that all the engineering ideas pre-dated von Neumann) define the bracket of plausible answers. Per Haigh-Priestley-Rope 2014 p.4, the question may be malformed — what later writers compress into a single "stored-program concept" is actually three distinct ideas, each with a different origin story:

- The **modern code paradigm** (writable executable instructions in main memory) has roots in the Eckert/Mauchly EDVAC discussions, which pre-date von Neumann's involvement.
- The **von Neumann architecture paradigm** (CA/CC/M/I/O organ subdivision) is most cleanly stated in von Neumann's own typescript and may genuinely be his synthesis-and-formalism.
- The **EDVAC hardware paradigm** (mercury delay lines, serial bit-stream layout) is Eckert's invention, used as a constraint that shaped the *First Draft*'s discussion of word lengths.

What would help:
- The 30 September 1945 Eckert/Mauchly progress report on the EDVAC ("Automatic High Speed Computing"), Plaintiff Exhibit 3540 in Honeywell-Sperry. Penn archives.
- Mauchly's August 1942 memorandum, "The Use of High Speed Vacuum Tube Devices for Calculating." Penn archives.
- The 1944-1945 EDVAC team meeting minutes — particularly the "Minutes of EDVAC meetings" series at the Moore School.

The chapter must avoid both "von Neumann sole-authored the ideas" (the popular but false view) and "Eckert and Mauchly sole-authored the ideas, von Neumann was just the rapporteur" (Eckert's 1977 view).

## Q3. Was the original *First Draft* typescript exactly 101 pages?

**Status: Yellow (widely repeated but not directly anchored)**

Wikipedia and many secondary sources report 101 pages. The Godfrey 1992 TeX reset (the version Claude has direct access to) is 49 pages of typeset content. The original typescripts at the APS Library and the Moore School Library — per Godfrey's introduction (verified by Claude on 2026-04-28 in the IA mirror) — differ from each other in pagination and layout, and the APS copy contains additional sections (§§13.6-13.7 and a final-table description of three planned EDVAC models) not in the Moore School copy.

What would resolve this:
- Direct fetch of the IEEE Annals of the History of Computing Vol. 15, No. 4 (1993) reprint, which gives the document with original-typescript page numbers preserved. IEEE Xplore institutional access.
- Mai Sugimoto, "On the original copies of 'First Draft of a Report on the EDVAC' by John von Neumann," PHS Studies No.6, Feb 2012, pp.83-89. Cited at hdl.handle.net (per Godfrey's update note); not directly fetched by Claude.

The chapter must say "≈100-page typescript" rather than asserting the 101-page count as Green.

## Q4. What was the actual June 1945 distribution list for the *First Draft*?

**Status: Yellow**

Wikipedia mentions an early run of 24 copies on June 25 plus the formal June 30 release. The full recipient list — who got copies in the first wave — is not Green-anchored. Standard candidates include Alan Turing (who cited the document in his Pilot ACE proposal within months), the British team at NPL, and various U.S. academic and military computing groups.

What would resolve this:
- Goldstine's correspondence files at the Smithsonian Institution Archives.
- The IAS archives.
- Penn archives.

The chapter handles this by saying "Goldstine mailed copies to scientists in the U.S. and the U.K." without asserting a specific count or full list.

## Q5. Is the four-grounds enumeration in *Honeywell v. Sperry Rand* (1973) verbatim from Judge Larson's ruling?

**Status: Yellow on the verbatim wording; Green on the headline that the *First Draft* counted**

Multiple secondary sources list four grounds for invalidation, including (1) public use before the critical date, (2) commercial sale before the critical date, (3) enabling disclosure via the *First Draft* and Eckert/Mauchly's September 1945 progress report, (4) derivation from Atanasoff. The 248-page ruling text (*Findings of Fact, Conclusions of Law, and Order for Judgment*, October 19, 1973) is in the CBI archive (Sperry Rand Corporation, Univac Division. Honeywell vs. Sperry litigation records, `archives.lib.umn.edu/repositories/3/resources/66`); Claude could not fetch the full text from a public PDF on 2026-04-28.

What would resolve this:
- Direct request to CBI for the ruling text or for an authoritative secondary quotation.
- Stern 1981 (physical book) — Stern was reportedly motivated in part by what she saw as the ruling's underestimation of Mauchly, so her treatment of the ruling is likely detailed.

The chapter must say "one of the cited grounds was that the *First Draft* (June 30, 1945) constituted enabling disclosure prior to the patent application" — Green at that level — and not assert the verbatim wording of the four-grounds enumeration.

## Q6. Does Bartik's "ENIAC was really the first stored program computer" claim hold up under the three-paradigm test?

**Status: Yellow (the claim is real; its calibration depends on which paradigm one cares about)**

Bartik says it directly (CHM oral history p.32, anchored Green). Haigh 2014 p.4 also says ENIAC's 1948 modification "ran a complex program written in the new style, including conditional branches, data reads from calculated addresses, and a subroutine called from more than one point in the code" — i.e., a complete demonstration of the modern code paradigm. But the Manchester Baby of June 21, 1948 was a purpose-built stored-program machine; ENIAC was a retrofit. Priority depends on:

- **Modern code paradigm execution priority**: ENIAC may well be first, depending on which 1948 month the retrofit ran its first program (not Green-anchored to a specific date in Bartik CHM).
- **Purpose-built stored-program machine priority**: Manchester Baby (June 21, 1948, Green-anchored via Haigh 2014).
- **Stored-program machine in production use**: EDSAC (May 6, 1949) is generally considered the first.

What would resolve this:
- Bartik CHM p.32 already gives Bartik's claim verbatim; what's missing is a specific date for the first 1948 ENIAC stored-program run.
- Haigh-Priestley-Rope's other articles (notably "Engineering 'The Miracle of the ENIAC': Implementing the Modern Code Paradigm," IEEE Annals 36(2), 2014) likely give a specific date. Claude has not fetched that article on 2026-04-28.

The chapter must record Bartik's claim verbatim and immediately situate it within the three-paradigm decomposition. Do not assert ENIAC priority unqualified.

## Q7. What did the Moore School Lectures (summer 1946) actually transmit?

**Status: Yellow (chapter context, not load-bearing)**

The Moore School Lectures were a summer school held at Penn from approximately July 8 to August 31, 1946. Haigh 2014 p.5 says historians have credited the event "as a crucial vector for the spread of the stored-program concept." Eckert lectured; Maurice Wilkes attended and went home to build EDSAC; the lectures' proceedings were published by MIT Press in 1985 (Campbell-Kelly and Williams, eds.).

This question is a context question, not a load-bearing one for Ch8's argument — but the chapter could be richer if a single specific Wilkes-at-Moore-School quotation could be anchored. The Campbell-Kelly/Williams volume is a physical book; not directly anchored by Claude on 2026-04-28.

## Q8. Cross-chapter handoff: what should Ch9 (the memory miracle) inherit from this chapter?

**Status: Open for Ch9 author**

The chapter ends on the observation that the *First Draft*'s architecture worked only because — and only because — Williams tubes, mercury delay lines, and ferrite cores eventually gave it the silent, reliable, large-enough storage it needed. Ch9 inherits:

- The architectural specification (CA/CC/M/I/O) as a *requirement*: Ch9 has to deliver M.
- The unsolved memory problem at the end of 1945: ENIAC's 200 decimal digits of writable electronic memory were not nearly enough; mercury delay lines were Eckert's then-recent invention but not yet mass-produced.
- The cross-cutting tension: the architecture is right, the hardware is wrong, and the chapter's reader knows it and wants Ch9 to fix it.

Ch8 should NOT anticipate Ch9's specific resolutions (Williams tubes, mercury delay lines, ferrite cores); Ch8's last paragraph should *name the gap* and point forward.
