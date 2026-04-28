# Infrastructure Log: Chapter 8 — The Stored Program

What infrastructure each scene actually relied on, with the source anchor for each detail. Where a number is **Yellow**, it is widely repeated in secondary sources but not directly anchored to a primary source Claude verified on 2026-04-28.

## Scene 1: ENIAC's plug-and-switch programming model (1944-1947)

**The machine**

- **Vacuum tubes**: 17,468 (per BRL Report 971, 1955, cited via Haigh 2014 footnote 12). The number fluctuated over the machine's operating life as components were added and removed. *Status: Yellow (anchored only to a 1955 BRL report Claude has not directly fetched).*
- **Weight, footprint, power consumption**: ~30 tons, ~1,800 sq ft, hundreds of kilowatts. Standard secondary-source claims, widely repeated; Claude has not directly anchored these to a primary source on 2026-04-28. *Status: Yellow.*
- **Arithmetic speed**: ~5,000 additions per second. *Status: Yellow.*
- **Numeric word memory**: 200 decimal digits of writable electronic memory; an additional ~7,000 digits of program-and-data information held in cables, function tables (large banks of switches originally for table-lookup), and switches across the machine. *Source: Haigh 2014 p.5 (Green).*

**The programming model**

- **Program trays**: ENIAC was a parallel machine with multiple memory buses; instead of a program counter, programs were laid out on "program trays" plugged in and out to stimulate the next operation. *Source: Bartik CHM oral history p.22 (Green).*
- **Master Programmer unit**: a dedicated 10-electronic-stepper subsystem that held loop coordination logic; an additional special-purpose memory inaccessible to the rest of the machine. Conditional branches were accomplished with a complex technique using special adaptors to route numerical data into program control lines. *Source: Haigh 2014 p.10 / PDF p.7 (Green).*
- **Function tables**: Originally designed to return interpolated function values. Each function table was a bank of switches; setting up the table to hold a numerical function took manual labor. Later (1948) the function tables were repurposed to hold a stored-program order code. *Source: Haigh 2014 pp.7, 10 (Green).*
- **Programming labor**: Setting up a new problem on the ENIAC required studying the wiring diagrams, mapping logic onto the machine's specialized units, and physically connecting cables and setting switches across the panels. The six women programmers learned this from blueprints — McNulty: "Somebody gave us a whole stack of blueprints, and these were the wiring diagrams for all the panels, and they said 'Here, figure out how the machine works and then figure out how to program it.'" *Source: Light 1999 p.470 (Green).*

**Where it lived**

- ENIAC was built in the Moore School of Electrical Engineering at the University of Pennsylvania. After its February 1946 dedication and subsequent operational period at Penn, it was moved to the Aberdeen Proving Ground (Maryland) — where Bartik joined the team. *Source: Bartik CHM oral history pp.10-15, 31-32 (Green for her presence at both locations).*

## Scene 2: The First Draft as a 1945 typescript

**Physical form**

- A typescript on a typewriter that lacked Greek-letter keys (Greek and other special symbols were written in by hand or substituted with normal letters, e.g., `t` for `τ`). *Source: Godfrey introduction in edvac-IA.txt (Green).*
- Reproduction was by mimeograph for a small distribution of copies. The exact number of copies is not Green-anchored; Wikipedia cites 24 copies in an early June 25 distribution.
- Length: secondary sources widely report 101 pages for the original typescript; the modern Godfrey 1992 TeX reset is 49 pages of typeset content. *Status: Yellow for the 101-page count; Green for the existence of multiple typescript versions (Moore School and APS Library).*

**Where the original lived (and where copies live)**

- One original typescript was held at the University of Pennsylvania Moore School Library. Another, with additional sections (§§13.6-13.7 and a final-table description of three planned EDVAC models), was held at the American Philosophical Society Library, Philadelphia (per Mai Sugimoto's 2012 archival finding, cited in Godfrey's 2020 update note). *Source: Godfrey introduction (Green).*
- The 1993 reprint in *IEEE Annals of the History of Computing* 15(4) (pp.27-43, later editions pp.27-75) made the document broadly accessible. *Source: Haigh 2014 footnote 2 (Green).*

**Authorship presentation**

- The title page lists exactly one author: "John von Neumann." It also lists Contract W-670-ORD-4926 between the U.S. Army Ordnance Department and the University of Pennsylvania, the Moore School affiliation, and the date June 30, 1945. *Source: First Draft (Godfrey TeX reset) title page (Green).*
- Inside the body, "J. W. Mauchly" is mentioned exactly once (in connection with a multiplication encoding scheme, around §7.4 of the body, near the discussion of carry-save addition). "Eckert" does not appear at all. *Source: Claude direct grep of the FabLab and IA mirrors of the Godfrey TeX reset (Green).*

## Scene 3: The 1946 IAS Preliminary Discussion

**Physical and institutional form**

- The 1946 *Preliminary Discussion* was issued from the Institute for Advanced Study, Princeton, NJ, under Contract W-36-034-ORD-7481 between the Research and Development Service, Ordnance Department, U.S. Army, and the Institute for Advanced Study. *Source: Burks/Goldstine/von Neumann 1946 preface (Green).*
- The IAS-hosted PDF mirror (`https://www.ias.edu/sites/default/files/library/Prelim_Disc_Logical_Design.pdf`) is 58 pages, scanned by an HP Digital Sending Device. The document was originally typed and mimeographed for distribution. *Status: Green for the bare facts; Yellow for the original print run size.*

**Authorship presentation**

- Three named authors on the title page: Arthur W. Burks, Herman H. Goldstine, John von Neumann. Notable as a corrective to the *First Draft*'s sole-author title page. *Source: Burks/Goldstine/von Neumann 1946 title page (Green).*
- The preface explicitly thanks "Dr. John Tukey of Princeton University for many valuable discussions and suggestions" — a small but significant difference from the *First Draft*, which thanks no one. *Source: Burks/Goldstine/von Neumann 1946 preface (Green).*

**Architectural specification**

- The report explicitly states the unified-memory rule in §1.3 — much more cleanly than the *First Draft*'s tentative §2.5: "Conceptually we have discussed two different forms of memory: storage of numbers and storage of orders. If, however, the orders to the machine are reduced to a numerical code and if the machine can in some fashion distinguish a number from an order, the memory organ can be used to store both numbers and orders." *Source: Burks/Goldstine/von Neumann 1946 §1.3 (Green).*
- The report introduces the 32-bit-word IAS machine plan: a writable electronic memory of binary words, with one bit per word flagging whether the word held an instruction or data. A transfer to a data word fully overwrote it; a transfer to an instruction word overwrote only the address field. *Source: Haigh 2014 p.10 (Green) — Haigh's reading of the IAS report on word-tagging.*

## Scene 4: The credit dispute and the public-domain disclosure (1945-1946)

**Goldstine's distribution mechanism**

- Goldstine mimeographed copies of the *First Draft* and mailed them to scientists in the U.S. and the U.K. The exact distribution list is not Green-anchored; standard secondary references put the count at "tens" of recipients in the months after the document was issued. *Status: Yellow for distribution counts.*
- The mailing did not redact security-classified content because the project's classified status was being relaxed in mid-1945 in line with the war's end. *Status: Yellow — context, not load-bearing for any chapter claim.*

**The patent-bar mechanism (Eckert's reading, 1977)**

- Eckert's account in OH 13 (pp.46-47): von Neumann arranged for "all the reports of the engineers" to go to the Library of Congress, "which put a bar on any patents being obtained." Eckert presents this as deliberate on von Neumann's part — driven by his IBM consultancy interests (Eckert OH 13 p.37). *Status: Green for the existence of Eckert's claim; Yellow for whether the mechanism was deliberately engineered.*

**The 1973 legal aftermath**

- In *Honeywell, Inc. v. Sperry Rand Corp.*, 180 U.S.P.Q. 673 (D. Minn. 1973), Judge Earl R. Larson cited the *First Draft* (June 30, 1945) as one of four grounds for invalidating the ENIAC patent — the document's broad mid-1945 distribution constituted enabling disclosure prior to the ENIAC patent application's June 26, 1946 critical date. *Source: Wikipedia "Honeywell, Inc. v. Sperry Rand Corp." (verified 2026-04-28); CBI archival finding aid for the Sperry Rand-Honeywell litigation records (Green for the headline facts; Yellow for the four-grounds verbatim text).*

## Scene 5: The 1948 ENIAC retrofit and what came next

**The 1948 ENIAC stored-program conversion**

- Richard Clippinger (Ballistics Research Laboratory) contracted with the Moore School in 1948 to convert ENIAC to read instructions from its function tables. Bartik headed the four-programmer team; Adele Goldstine joined later. *Source: Bartik CHM oral history pp.31-32 (Green).*
- The "60 order code" was a single-address instruction set (von Neumann had argued Clippinger out of his original 3-address scheme during the Princeton consultations). Once installed, the order code "rendered the horrendous problem of programming the ENIAC gone" — programs ran by setting switches and function tables, not by re-cabling. *Source: Bartik CHM oral history p.32 (Green).*
- The 1948 modification let ENIAC run a Monte Carlo program with conditional branches, calculated-address data reads, and a subroutine called from more than one point in the code — a complete demonstration of the modern code paradigm. *Source: Haigh 2014 p.4 (Green).*

**The Manchester Baby and EDSAC**

- The Manchester "Baby" (Manchester Small-Scale Experimental Machine) ran its first stored program on 21 June 1948. It used a Williams tube (cathode-ray-tube electrostatic memory) for its main store. *Source: Haigh 2014 p.7 (Green).*
- Cambridge's EDSAC ran its first successful stored program on 6 May 1949. EDSAC used mercury delay lines for its main memory. EDSAC had ~3,000 vacuum tubes (cited via Williams 1985 p.118 — Yellow on the page anchor). *Source: Haigh 2014 p.7 and footnote 12 (Green for the dates and broad tube count).*
- The Manchester Mark 1 (a more elaborate Manchester machine, late 1949 onward) had ~1,300 vacuum tubes as of April 1949 (Williams 1985 p.118 — Yellow on page anchor). *Source: Haigh 2014 footnote 12 (Green at the cited level).*

**The IBM Test Assembly and the 1949 phrase**

- IBM's first electronic computer was the "Test Assembly," built by Nathaniel Rochester's team at Poughkeepsie around the firm's 604 Electronic Calculating Punch with a cathode-ray-tube memory and a magnetic drum. The 17 May 1949 internal report titled "A Calculator Using Electrostatic Storage and a Stored Program" is the earliest located use of the phrase "stored program" in a written document. *Source: Haigh 2014 p.5 and footnote 16 (Green for the historiographic finding).*
- The Test Assembly's design philosophy — that once "a certain level of complexity had been reached" the plug-board approach became impractical and the calculation program had to be loaded from cards into electronic storage — is what made "stored program" terminologically useful in IBM's vocabulary. *Source: Haigh 2014 p.5 (Green).*
