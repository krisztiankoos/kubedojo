# Scene Sketches: Chapter 8 — The Stored Program

Five scenes mapped one-to-one to the Prose Capacity Plan layers in `brief.md`. Each scene lists the verified anchors that ground its content and the Green/Yellow status of each anchored element. Density is calibrated to Ch11 (the 2026-04-28 Claude template) and Ch24 (the canonical anchored-plan reference).

---

## Scene 1: The plug-and-switch machine (600-900 words; PCP layer 1)

**Setting.** Moore School of Electrical Engineering, University of Pennsylvania, late 1944 through 1946. The Aberdeen Proving Ground (Maryland) for the parallel human-computer pool that fed the Moore School project.

**Beats.**

1. **The human computers came first.** Roughly two hundred women, civilian and military, worked the BRL ballistics-table problem with mechanical desk calculators and the Bush differential analyzer. Light 1999 p.455: "Nearly two hundred young women, both civilian and military, worked on the project as human 'computers,' performing ballistics computations during the war." A trajectory took anywhere from twenty minutes to several days by hand. **Anchor**: Light 1999 p.455 (Green); Light 1999 p.470 (the trajectory time estimate at Light 1999 p.467, Yellow on the exact-page extraction).

2. **The six women selected.** When ENIAC was nearing operation in mid-1945, Goldstine selected six of the human computers to learn the machine itself. He "assigned six of the best computers to learn how to program the ENIAC and report to [John] Holberton." The six: Kathleen McNulty, Frances Bilas, Betty Jean Jennings (Bartik), Ruth Lichterman, Elizabeth Snyder (Holberton), Marlyn Wescoff. **Anchor**: Light 1999 p.469 (Green); Bartik CHM pp.21-22 (Green corroboration).

3. **The blueprints, not the machine.** McNulty's account: "Somebody gave us a whole stack of blueprints, and these were the wiring diagrams for all the panels, and they said 'Here, figure out how the machine works and then figure out how to program it.'" Their security clearances had not yet come through — they could not even see the ENIAC. **Anchor**: Light 1999 p.470 (Green for the McNulty quote); Bartik CHM pp.18-21 (Green for the security-clearance lag).

4. **What the programming actually was.** ENIAC was a parallel machine with multiple memory buses. Bartik: "instead of having a program counter... it had program trays which you plugged in and out of to stimulate the next operation. And then of course you had whatever the operation you were doing, instead of doing in software, you had to set the switches and round offs and all that kind of stuff." Conditional branching was accomplished with adaptors that routed numerical data into program control lines. The Master Programmer unit held loop coordination. **Anchor**: Bartik CHM p.22 (Green); Haigh 2014 p.10 (Green for the conditional-branch-via-adaptors mechanism).

5. **The role redefinition.** The original conception was that whoever had a problem to put on the ENIAC would program it themselves and the women would just plug up the machine. That broke down inside weeks: the wiring problem was so complex that the women became the actual programmers. Bartik: "our role switched so that we really were programmers." **Anchor**: Bartik CHM p.23 (Green).

**What this scene is NOT.** It is not a celebration scene; it is the chapter's *reason* scene. The point is to show that in 1944-1945 ENIAC's programming model was already at the edge of human tractability — and the people closest to it (Eckert, Mauchly, the six women) understood this before von Neumann arrived. The scene must NOT moralize about the historiographic erasure of the women programmers — Light 1999 already does that work; the chapter draws on Light's evidence but the chapter's argument is structural (about programming infrastructure), not corrective (about credit allocation in computing history).

---

## Scene 2: Von Neumann's draft (900-1,200 words; PCP layer 2)

**Setting.** Moore School, summer 1944 to June 1945. A fragmentary typescript on a typewriter without Greek letters; Greek symbols written in by hand.

**Beats.**

1. **Von Neumann arrives in 1944.** As a consultant, not a permanent member of the team. The pre-existing Eckert/Mauchly EDVAC discussions — about a successor machine that would store programs in writable memory rather than in cables — were already underway. **Anchor**: Eckert OH 13 pp.46-47 (Green for Eckert's account that the ideas pre-dated von Neumann); Haigh 2014 p.5 ("the new breed of computers came from J. Presper Eckert and John Mauchly. As well as designing ENIAC, they had created at least some of the ideas included in the First Draft" — Green).

2. **The June 30, 1945 title page.** "First Draft of a Report on the EDVAC, by John von Neumann. Contract No. W-670-ORD-4926. Between the United States Army Ordnance Department and the University of Pennsylvania. Moore School of Electrical Engineering, University of Pennsylvania, June 30, 1945." Eckert's name does not appear. Mauchly's does not appear. **Anchor**: First Draft (Godfrey TeX reset) title page (Green).

3. **The five organs.** §2.2: a central arithmetical part, CA, "the first specific part." §2.3: a central control, CC, "the second specific part." §2.4-2.5: the memory M, "the third specific part of the device" — and crucially, "it is nevertheless tempting to treat the entire memory as one organ, and to have its parts even as interchangeable as possible." §2.7: input I, fourth. §2.8: output O, fifth. **Anchor**: First Draft §§2.2-2.8, all Green.

4. **The neuron analogy.** §2.6: "The three specific parts CA, CC (together C) and M correspond to the associative neurons in the human nervous system. It remains to discuss the equivalents of the sensory or afferent and the motor or efferent neurons." §4.2 cites "MacCulloch and Pitts ('A logical calculus of the ideas immanent in nervous activity')." This is the chapter's anchored bridge back to Ch5 (the neural abstraction): von Neumann himself drew the analogy, in 1945, in the document that would eventually be cited as the founding architecture of digital computing. **Anchor**: First Draft §§2.6, 4.2 (Green).

5. **What the document leaves unwritten.** The Godfrey 1992 introduction notes: "throughout the text von Neumann refers to subsequent Sections which apparently were never written. Most prominently, the Sections on programming and on the input/output system are missing." Forward-references in the typescript appear as `{}` empty braces. The document is a *first draft* in a literal sense — the design half is complete, the use half is sketched. **Anchor**: Godfrey 1992 introduction in edvac-IA.txt (Green).

6. **Mauchly mentioned once, Eckert never.** A direct grep of the Godfrey TeX reset shows "J. W. Mauchly" appears exactly once in the body, near §7.4, in a parenthetical attribution of a multiplication encoding scheme. "Eckert" does not appear. **Anchor**: Claude direct grep 2026-04-28 (Green).

7. **Goldstine mails it.** Distribution begins June 1945 (Wikipedia notes a smaller June 25 advance run of 24 copies and the formal June 30 distribution). The recipients are computer-science researchers in the U.S. and the U.K. — including Alan Turing, who within months cited the *First Draft* in his proposal for the Pilot ACE. **Anchor**: Wikipedia article (Yellow); Godfrey 1992 introduction footnote 1 ("Alan Turing cites it, in his Proposal for the Pilot ACE, as the definitive source for understanding the nature and design of a general-purpose digital computer" — Green).

**What this scene is NOT.** It is not a "von Neumann sees Turing's universal machine and instantly invents the modern computer" scene. It is a *what the document actually says, and what it leaves out* scene. Per Haigh 2014 p.5, von Neumann's language is "uncharacteristically tentative" — the unified-memory passage reads as a hesitation, not as a definitive design rule. The chapter's reader leaves Scene 2 understanding that the *First Draft* was a partial, fragmentary, single-author document — not the polished founding artifact later memory paints it as.

---

## Scene 3: The IAS re-formalization (600-900 words; PCP layer 3)

**Setting.** Institute for Advanced Study, Princeton, NJ. June 28, 1946 — almost exactly one year after the *First Draft*.

**Beats.**

1. **Three named authors.** Burks, Goldstine, von Neumann. Issued under Contract W-36-034-ORD-7481 between the Research and Development Service, Ordnance Department, U.S. Army, and the IAS. The preface thanks "Dr. John Tukey of Princeton University for many valuable discussions and suggestions" — small but significant, since the *First Draft* thanks no one. **Anchor**: Burks/Goldstine/von Neumann 1946 title page and preface (Green).

2. **The unified-memory rule, cleaned up.** §1.3 of the IAS report removes the *First Draft*'s tentativeness: "Conceptually we have discussed two different forms of memory: storage of numbers and storage of orders. If, however, the orders to the machine are reduced to a numerical code and if the machine can in some fashion distinguish a number from an order, the memory organ can be used to store both numbers and orders." This is the cleaner anchor for "the von Neumann architecture said memory should hold code and data" — not the *First Draft*'s hedged §2.5. **Anchor**: Burks/Goldstine/von Neumann 1946 §1.3 verbatim (Green).

3. **Word tagging.** The IAS design tags each 32-bit word with a flag bit indicating whether it is data or instruction. A transfer to a data word fully overwrites the word; a transfer to an instruction word overwrites only the address field. This makes possible the kind of self-modifying code that the *First Draft* had implicitly required for conditional branching, while preventing programs from accidentally clobbering their own opcodes. **Anchor**: Haigh 2014 p.10 / PDF p.7 (Green for Haigh's reading of the IAS report's word-tagging mechanism).

4. **What the IAS report represents in the chapter's argument.** The chapter's stance: the *First Draft* and the 1946 IAS *Preliminary Discussion* should be read together as a single architectural-design document staged in two acts. The *First Draft* gives the rough version; the IAS report cleans it up and adds the named co-authorship. Most of what later writers attribute to "the von Neumann architecture" is actually crisper in the 1946 IAS document than in the famous 1945 typescript. **Anchor**: This is a chapter-internal argument supported by direct comparison of First Draft §2.5 and IAS §1.3 (both Green).

**What this scene is NOT.** It is not the scene where "the credit dispute is resolved by Burks and Goldstine being added as authors" — Eckert and Mauchly are still not on this title page either. The 1946 report is the IAS's claim on the design, not the Moore School engineers' claim. The chapter notes that 1946 added two names but not the two whose absence was the original complaint.

---

## Scene 4: The credit dispute and the public-domain disclosure (600-900 words; PCP layer 4)

**Setting.** Moore School and IAS, 1945-1946; an Eckert oral-history interview at Sperry Univac in Blue Bell PA on October 28, 1977; the U.S. District Court for the District of Minnesota on October 19, 1973.

**Beats.**

1. **Goldstine's mailing as patent-bar.** By distributing the *First Draft* to scientists in the U.S. and the U.K. before any patents had been filed, Goldstine in effect placed the document's content in the public domain — patents on those ideas became prior-art-blocked. **Anchor**: Eckert OH 13 abstract (Green for the existence of the bar); Honeywell v. Sperry Rand 1973 (Green for the legal confirmation that the bar held).

2. **Eckert's 1977 reading: deliberate, IBM-driven.** Eckert: "Look, he sold all our ideas through the back door to IBM as a consultant for them" (OH 13 p.37). And the mechanism: "von Neumann went down and published all that stuff. All the reports of the engineers went to the Library of Congress which put a bar on any patents being obtained by any of his employees. And when they complained about it to him, he just said, 'Well, that's tough; that's the way I think; that stuff should be in the public domain.'" (OH 13 pp.46-47). The chapter must quote Eckert's words but frame them as Eckert's reading thirty-two years on, not as established fact. **Anchor**: Eckert OH 13 p.37, p.46-47 (Green for the existence of the claim; Yellow for the *deliberateness* attribution).

3. **The resignation.** March 1946: Eckert and Mauchly resign from the Moore School over the patent assignment dispute. They go on to found the Eckert-Mauchly Computer Corporation, which builds UNIVAC. **Anchor**: Eckert OH 13 (Green for the existence of the resignation; Yellow for the exact date). The chapter does not retell the EMCC business arc — that's Stern 1981's territory.

4. **The 1973 vindication-and-loss.** *Honeywell, Inc. v. Sperry Rand Corp.*, 180 U.S.P.Q. 673, U.S. District Court for the District of Minnesota, ruling October 19, 1973. Judge Earl R. Larson invalidates the ENIAC patent on four grounds, one of which is that the *First Draft* (June 30, 1945) constituted enabling disclosure prior to the patent application — exactly the public-domain mechanism Eckert had been worrying about for twenty-eight years. The legal vindication of Eckert's 1977 reading is also the legal cancellation of the ENIAC patent. **Anchor**: 180 U.S.P.Q. 673 (Green for headline facts; Yellow for the four-grounds verbatim text).

**What this scene is NOT.** It is not a vindication-of-Eckert scene; the scene's irony is that Eckert was right about the patent-bar mechanism but the legal recognition of that fact arrived, in 1973, as the cancellation of the patent he wanted. The scene also does not endorse or reject Eckert's "deliberately to support his IBM consulting" framing — it presents the framing as Eckert's, alongside Goldstine 1972's different account, and lets the reader weigh.

---

## Scene 5: The first machine actually to do it, and the honest close (800-1,100 words; PCP layer 5)

**Setting.** Moore School and Aberdeen Proving Ground, 1948; Princeton (consulting trips to von Neumann); Manchester and Cambridge, 1948-1949; IBM Poughkeepsie, 1949.

**Beats.**

1. **The 1948 ENIAC retrofit.** Richard Clippinger contracts with the Moore School to convert ENIAC's function tables into a stored-program memory holding a 60-instruction order code. He hires Bartik to head the four-programmer team. Bartik's account: Clippinger had wanted a 3-address instruction; "he talked to von Neumann, and von Neumann said no, to use a 1-address instruction." Consulting trips to Princeton; Adele Goldstine joins. The result: "the horrendous problem of programming the ENIAC was gone." **Anchor**: Bartik CHM pp.31-32 (Green).

2. **What ENIAC ran in the new mode.** Per Haigh 2014 p.4 — citing the ENIAC In Action research project's archival work — ENIAC under the 1948 modification ran "a complex program written in the new style, including conditional branches, data reads from calculated addresses, and a subroutine called from more than one point in the code." This is not a partial demonstration; this is the modern code paradigm running in production. **Anchor**: Haigh 2014 p.4 (Green).

3. **Manchester Baby and EDSAC.** The Manchester "Baby" (Manchester Small-Scale Experimental Machine, F.C. Williams and Tom Kilburn) ran its first stored program on June 21, 1948 — the first stored-program execution on a purpose-built stored-program machine, using a Williams-tube cathode-ray-tube electrostatic memory. Cambridge's EDSAC (Maurice Wilkes) ran its first successful stored program on May 6, 1949, using mercury delay lines. **Anchor**: Haigh 2014 p.7 (Green).

4. **The phrase "stored program" arrives, in 1949, at IBM.** Nathaniel Rochester's team at IBM Poughkeepsie writes a 17 May 1949 internal report titled "A Calculator Using Electrostatic Storage and a Stored Program" — the earliest located use of the phrase "stored program" in a written document. The phrase, ironically, names the concept four years after the *First Draft* described the mechanism without naming it, and in a document written by IBM (not by Eckert, not by Mauchly, not by von Neumann). **Anchor**: Haigh 2014 p.5 and footnote 16 (Green for the historiographic finding).

5. **The honest reframe.** The chapter closes on the three-paradigm decomposition from Haigh-Priestley-Rope 2014 p.4: what later writers call "the stored-program concept" is actually three things — the modern code paradigm (writable executable instructions in main memory), the von Neumann architecture paradigm (CA/CC/M/I/O organ subdivision), and the EDVAC hardware paradigm (mercury delay lines, serial bit-stream layout). The *First Draft* contained all three; not all three survived; the modern code paradigm is the one that became the modern computer. The chapter's last line points forward: the architecture worked because — and only because — Williams tubes, mercury delay lines, and ferrite cores eventually gave it the silent, reliable storage it needed. That story is Ch9. **Anchor**: Haigh 2014 p.4 (Green); pointer to Ch9 (chapter-internal).

**What this scene is NOT.** It is not the scene where "ENIAC was the first stored-program computer" gets celebrated unqualified. Bartik's claim ("the ENIAC was really the first stored program computer, actually") is recorded — verbatim, with Bartik's voice intact — and immediately situated against the three-paradigm decomposition. The chapter's last paragraph does not announce a winner of the priority dispute; it announces that the priority dispute was misframed because "stored program" is not a single thing.
