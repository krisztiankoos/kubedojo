# Infrastructure Log: Chapter 9 — The Memory Miracle

Technical and institutional metrics relevant to the chapter's "memory crisis solved by a switch in physical substrate" thesis. Each row is what made each scene operationally possible (or what its operational limits were). Verification colors are tracked because infrastructure claims that look like throwaway facts are often the ones secondary sources copy from each other without primary evidence.

## Williams-Tube Electrostatic CRT Memory (1947-1953)

| Item | Value | Verification |
|---|---|---|
| Storage substrate | Charge pattern on the inner phosphor screen of a commercial cathode-ray tube. | **Green** — Kilburn 1947 internal report (Manchester transcription), Summary section. |
| Short-term retention (passive, no refresh) | Approximately 0.2 seconds, "provided by the insulating properties of the screen material." | **Green** — Kilburn 1947 report, Summary section verbatim. |
| Long-term retention (with refresh) | Indefinite, provided the charge pattern is regenerated at a frequency greater than 5 cycles per second. | **Green** — Kilburn 1947 report, Summary section verbatim. |
| Hypothetical-machine instruction time (series mode) | 600 microseconds per instruction set up and obeyed. | **Green** — Kilburn 1947 report, Summary section verbatim. |
| Storage encoding | Five candidate dot/dash systems: (1) dot-dash display, (2) dash-dot display, (3) defocus-focus display, (4) focus-defocus display, (5) anticipation. | **Green** — Kilburn 1947 report, Section 3 Contents listing. |
| Reliability characterization (Forrester recollection) | "Expensive and short-lived and not very reliable." | **Green** as a verbatim Forrester recollection (Concord 1994 oral history); Yellow as a broader industry claim (single-source). |
| Failure modes | Erased by static discharge, environmental electromagnetic interference (the "passing streetcar" anecdote is widely repeated tertiary; primary anchor pending), or by the act of reading itself if not refreshed. | Yellow — the dramatic anecdotes are widely cited but lack a single primary anchor. The Kilburn 1947 report makes the same point structurally (refresh required >5 Hz) without the dramatic framing. |
| Capacity per tube | Modest — early commercial CRTs supported on the order of 1,024 to 2,048 bits per tube depending on dot spacing. | Yellow — secondary sources widely cite this range; Kilburn 1947 report Section 5.2 ("Storage capacity of a single C.R.T.") would anchor specific numbers but the body text was not extracted in this anchor pass. |

## Mercury Acoustic Delay Lines (1948-1953, contemporary alternative)

| Item | Value | Verification |
|---|---|---|
| Storage substrate | Shock-wave propagation through a column of mercury, with piezoelectric crystals at each end for transduction. | **Green** — Forrester Concord 1994 oral history verbatim description. |
| Tube length | Approximately one meter. | **Green** — Forrester Concord 1994 oral history. |
| Transit time | Approximately one millisecond. | **Green** — Forrester Concord 1994 oral history. |
| Storage capacity per line | "Maybe something like a thousand of these shocks that were either present or absent in the tube traveling down the tube." | **Green** as a Forrester recollection. |
| Access time | Worst case ~1 millisecond — must wait for the bit to come out the far end. | **Green** as a Forrester recollection of the operational constraint. |
| Reliability | "It worked. But it was slow." | **Green** as Forrester recollection. |

## Magnetic Core Memory (1949-1956+)

| Item | Value | Verification |
|---|---|---|
| Storage substrate | Toroidal ferrite cores arranged in a rectangular matrix, with intersecting select wires (X, Y, sense, inhibit). | **Green** — Forrester 1951 *J. Appl. Phys.* abstract; US Patent 2,736,880 face-sheet/abstract. |
| Required magnetic property | Rectangular hysteresis loop. | **Green** — US Patent 2,736,880 abstract verbatim ("substantially rectangular hysteresis properties"). |
| Selection mechanism | Coincident-current: simultaneous half-currents on X and Y wires sum to exceed the core's switching threshold; either current alone does not. | **Green** — US Patent 2,736,880 claim language verbatim ("the simultaneous (i.e. coincidental) application of two or more such currents"). |
| Switching time, metallic magnetic materials | 20 to 10,000 microseconds (too slow). | **Green** — Forrester 1951 *J. Appl. Phys.* abstract verbatim. |
| Switching time, nonmetallic magnetic materials (ferrites) | Less than one microsecond. | **Green** — Forrester 1951 *J. Appl. Phys.* abstract verbatim. |
| Discrimination ratio | 2:1 between full select current and half-select current. | **Green** — Forrester 1951 *J. Appl. Phys.* abstract verbatim. |
| Bits per core | One. | **Green** — Forrester 1951 *J. Appl. Phys.* abstract verbatim ("Only one magnetic core per binary digit is required"). |
| Wire scaling for 3D arrays | "3 ∛number of cores" input leads (i.e., for an N-core array, only 3 × N^(1/3) leads). | **Green** — US Patent 2,736,880 claim language verbatim. |
| Required residual flux density (Wang patent specification) | "At least 0.4-0.5, preferably greater than 0.80" of saturation flux density. | **Green** — US Patent 2,708,722 abstract verbatim. |
| Retention | Non-volatile; magnetization persists indefinitely without power. | **Green** — implicit in the magnetic-substrate physics; explicit in Forrester's 1994 oral history characterization. |
| First Whirlwind installation array dimensions | 32 × 32 × 16 bits (16 stacked planes, 1,024 cores per plane). | Yellow — Wikipedia *Magnetic-core memory* and CHM "1953: Whirlwind computer debuts core memory" tertiary; primary anchor in Bashe 1986 or Redmond & Smith 1980 needed. |
| Whirlwind core access time vs Williams-tube access time | Approximately 9 μs core vs ~25 μs CRT. | Yellow — Wikipedia *Magnetic-core memory* tertiary cite of Bashe 1986. |
| Cost trajectory (per bit, system level) | Roughly $1.00/bit early (~1953); roughly $0.01/bit by late 1960s; ~$0.0003 per core by 1970 at IBM volumes. | Yellow — Wikipedia *Magnetic-core memory* tertiary cite of Bashe 1986. |
| Cost per unstrung core, 1953 | Approximately $0.33. | Yellow — Wikipedia *Magnetic-core memory* tertiary cite. |
| Manufacturing labor (1953-1956 era) | "Assembled under microscopes by workers with fine motor control" — Forrester's coincident-current required one wire at 45° that resisted machine threading. | Yellow with strong caveat — Wikipedia paraphrases Bashe 1986; primary anchor pending. **Do NOT import Apollo / Raytheon "Little Old Ladies" labor history into this scene** (Rosner et al. 2018 CHI is anchored to 1960s core *rope* memory, a different technology). |
| 1956 IBM wiring efficiency improvement | Reduced X/Y select-line threading time on a 128×128 array from approximately 25 hours to approximately 12 minutes. | Yellow — Wikipedia *Magnetic-core memory* tertiary cite of Bashe 1986. |

## Project Whirlwind (MIT Digital Computer Laboratory, 1944-1953)

| Item | Value | Verification |
|---|---|---|
| Original sponsor | US Navy Special Devices Center (Long Island) under Perry Crawford. | **Green** — Forrester Concord 1994 oral history verbatim. |
| Original purpose | Aircraft stability and control analyzer (analog computer, 1944-1945) → flight-simulator-class digital control (1946+). | **Green** — Forrester Concord 1994 oral history verbatim. |
| Pivot to combat information centers | 1948 (two memoranda by Forrester). | **Green** — Forrester Concord 1994 oral history verbatim. |
| Building | 211 Massachusetts Avenue, Cambridge MA, "the building opposite the Necco factory and the building where presently the Graphics Department of MIT is located." | **Green** — Forrester Concord 1994 oral history verbatim. |
| Operational | 1951. | **Green** — IEEE Computer Society Pioneers entry on Forrester. |
| Original memory | Williams-tube electrostatic CRT storage. | **Green** — multiple sources (Forrester Concord 1994 oral history; Wikipedia *Magnetic-core memory*). |
| Memory upgrade | Magnetic-core memory installed summer 1953, replacing the Williams-tube store. | Yellow — tertiary sources converge on August 1953; primary anchor pending. |

## Memory Test Computer (MIT, ~1953)

| Item | Value | Verification |
|---|---|---|
| Purpose | Validate the magnetic-core memory at full scale before transplant into Whirlwind. | **Green** — Forrester Concord 1994 oral history verbatim. |
| Builders | Norman Taylor (chief engineer) and Kenneth Olsen (research assistant). | **Green** — Forrester Concord 1994 oral history verbatim. |
| Construction approach | Built "out of test equipment" — using the team's library of pre-existing digital building blocks (flip-flop circuits, amplifiers, etc.). | **Green** — Forrester Concord 1994 oral history verbatim. |
| Construction time | "About nine months" — Forrester says he "doubted that they could do it" in that time. | **Green** — Forrester Concord 1994 oral history verbatim. |
| Outcome | Validated the core memory; "within a couple of months after that, we moved it into the Whirlwind computer to replace the electrostatic storage tubes." | **Green** — Forrester Concord 1994 oral history verbatim. |

## SAGE (Semi-Automatic Ground Environment) Air Defense (1956-early 1980s)

| Item | Value | Verification |
|---|---|---|
| Predecessor study | Project Charles (~1950-1951) — proposed digital-computer-based air defense in response to Soviet 1949 atomic-bomb test. | **Green** — Forrester Concord 1994 oral history verbatim. |
| Institutional vehicle | MIT Lincoln Laboratory Division 6 (Forrester Head; Everett Associate Head). | **Green** — Forrester Concord 1994 oral history verbatim. |
| Manufacturer selection | IBM, selected from ~15 surveyed companies. | **Green** as Forrester recollection. |
| Production computer | IBM AN/FSQ-7 (a heavily-modified production version of the Whirlwind/Memory Test Computer architecture). | Yellow — widely cited tertiary; Bashe 1986 page anchor pending. |
| Number of control centers | 30-some, across North America. | **Green** as Forrester recollection. |
| Vacuum tubes per center | 60,000-80,000. | **Green** as Forrester recollection. |
| Building footprint per center | 4 stories high, ~160 feet square. | **Green** as Forrester recollection. |
| Operational availability | "About 99.8% of the time." | **Green** as Forrester recollection; Yellow as historical fact (single-source). |
| Vacuum-tube life improvement | From ~500 hours to ~500,000 hours per tube — "something like a thousand fold increase … by finding out why they were failing and taking away the cause." | **Green** as Forrester recollection. |
| Operating period | Mid-late 1950s through early 1980s. | **Green** as Forrester recollection; Yellow as precise dates. |

## IBM 704 (Commercial Successor, 1954-1960)

| Item | Value | Verification |
|---|---|---|
| Announced | 1954. | Yellow — Wikipedia *IBM 704* tertiary; Bashe 1986 page anchor pending. |
| First delivery | April 1955 (to Lawrence Livermore National Laboratory). | Yellow — same caveat. |
| Word size | 36 bits. | Yellow — Wikipedia *IBM 704*. |
| Standard core memory | 4,096 36-bit words (in the 737 Magnetic Core Storage Unit) — equivalent to 18,432 bytes. | Yellow — Wikipedia *IBM 704*. |
| Maximum core memory | 32,768 words. | Yellow — secondary widely cited. |
| Floating-point performance | Approximately 12,000 floating-point additions per second. | Yellow — Wikipedia *IBM 704*. |
| Weight | Approximately 19,500 pounds. | Yellow — Wikipedia *IBM 704*. |
| Production run | 123 units, 1955-1960. | Yellow — Wikipedia *IBM 704*. |
| Memory technology displaced | Williams-tube storage of the IBM 701 predecessor. | Yellow — Wikipedia *IBM 704* and *Magnetic-core memory*. |
| Indexing and floating-point hardware | First mass-produced computer to incorporate both as standard. | Yellow — secondary widely cited. |

## Patent Assignments

| Patent | Inventor | Filed | Issued | Assignee | Verification |
|---|---|---|---|---|---|
| US 2,708,722 "Pulse Transfer Controlling Device" | An Wang | 1949-10-21 | 1955-05-17 | Individual (later sold to IBM in 1956 for ~$500,000 — Yellow) | **Green** for face-sheet (Google Patents 2026-04-28). |
| US 2,736,880 "Multicoordinate Digital Information Storage Device" | Jay W. Forrester | 1951-05-11 | 1956-02-28 | Research Corporation (New York) | **Green** for face-sheet (Google Patents 2026-04-28). |
| (Specific Rajchman / RCA matrix-memory patent) | Jan A. Rajchman | (TBD) | (TBD) | Radio Corporation of America | Red — exact patent number not yet pinned among Rajchman's many core-memory patents. |

## Operational Limits Worth Naming in Prose

These are the infrastructure constraints the chapter should foreground when explaining why magnetic core was a project-saving switch:

- **Williams tubes lose their state in 0.2 seconds without active refresh.** This is the load-bearing operating limit of the Manchester-era stored-program substrate. The 1947 Kilburn report's Summary names it explicitly. Any program longer than the refresh interval is trusting the regeneration logic, not the storage substrate.
- **Mercury delay lines are reliable but serial.** Forrester's 1994 oral-history description gives the Boston-Buffalo television-link anecdote not as a joke but as a literal infrastructure proposal — that's how thin the alternatives looked in the late 1940s.
- **Real-time computing changes the tolerance.** A scientific batch computer can re-run a job tomorrow if the memory glitches; an air-defense control loop cannot. The Whirlwind project's pivot from flight-simulator to combat-information-center to SAGE air-defense made memory volatility a project-killing problem rather than an annoyance.
- **Magnetic core's 1-microsecond switching is not just a speed improvement; it changes what is computable.** Combined with non-volatility and sub-cubic-root wire scaling (3 × N^(1/3) for an N-core array), magnetic core moved memory from a per-bit hand-tuning problem to a fabrication-economics problem.
- **Industrial dominance came from MIT's institutional pipeline, not technical primacy alone.** The Memory Test Computer → Whirlwind core upgrade → SAGE → IBM 704 path was an MIT-Lincoln-Laboratory-to-IBM commercialization arc that Wang (Harvard) and Rajchman (RCA) didn't have. Patent licensing closed the loop financially in 1956.

## Notes

- Several "infrastructure facts" frequently repeated in tertiary sources (e.g., the dramatic "passing streetcar erased the memory" anecdote, the "core memory was woven by Asian textile workers" anecdote) belong either to scenes outside this chapter's window (Apollo-era core rope memory) or to dramatized retellings without primary anchors. The chapter must resist using these for color when more specific anchored claims (the 0.2-second retention figure; the 9-month Memory Test Computer build) carry the same narrative weight with verified evidence behind them.
- Infrastructure-log claims here stay narrowly *operational*: what was built, by whom, when, with what specifications, and what its limits were. Interpretive claims (why the technology mattered, what it enabled) live in `brief.md` (Boundary Contract) and `scene-sketches.md` (scene notes).
