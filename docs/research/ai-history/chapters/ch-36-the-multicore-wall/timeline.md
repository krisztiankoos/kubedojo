# Timeline: Chapter 36 — The Multicore Wall

Dated events anchored to verified primary sources. All entries reference at least one Green claim in `sources.md`.

## Pre-history (1971–1999)

- **1971** — Intel ships the 4004, "1 core, no cache, 23K transistors" (Borkar & Chien 2011 p.68 figure caption). The architectural baseline against which the rest of the chapter measures.
- **early 1970s** — Robert N. Dennard of IBM lays down the technology-scaling recipe: shrink transistor dimensions by 30% per generation, keep electric fields constant, double density every two years (Borkar & Chien 2011 p.68).
- **1996, October** — Olukotun, Nayfeh, Hammond, Wilson, and Chang present "The Case for a Single-Chip Multiprocessor" at ASPLOS-VII in Cambridge MA. The architectural argument that future transistor budgets should be spent on multiple smaller cores predates the multicore pivot by eight years.
- **1999, July/August** — Shekhar Borkar publishes "Design Challenges of Technology Scaling" in *IEEE Micro* 19(4):23–29. Subsequent retrospective accounts (Asanovic et al. 2006 §4.1) cite this paper as Intel's own internal warning that frequency scaling had been pushed to its limit.

## The GHz Religion (2000–2003)

- **2000** — Intel introduces the NetBurst architecture, designed around a deep pipeline so that operating frequency could keep climbing (Borkar & Chien 2011 p.68 figure annotation).
- **2001, August** — Intel chips reach 2 GHz (Sutter 2005 §"Obstacles, and Why You Don't Have 10GHz Today").
- **2001** — IBM ships the dual-core POWER4 server processor, the first commercial dual-core chip in mass production. The chapter cites this as part of the existing-server-multicore precedent (Asanovic et al. 2006 p.4).
- **early 2003** — The Intel CPU clock-speed trend visibly flattens; Sutter, writing in late 2004, would later mark this point as where "CPU performance growth as we have known it hit a wall." (Sutter 2005 §"Obstacles, and Why You Don't Have 10GHz Today")

## The Cancellation Year (2004)

- **2004, January 9** — *AnandTech* publishes leaked information that 10 Tejas engineering samples have been distributed; the samples are running at 2.8 GHz at approximately 150 W (Shimpi, *AnandTech*, 2004-01-09). This is the contemporaneous record of Tejas's actual thermal envelope four months before cancellation.
- **2004, mid-year** — Intel delays its planned introduction of a 4 GHz Pentium 4 line chip from late 2004 to 2005 (Sutter 2005 §"Obstacles, and Why You Don't Have 10GHz Today").
- **2004, May 7, 23:24 UTC** — Intel confirms to *The Register* and other outlets that Tejas (Pentium 4 successor) and Jayhawk (Xeon successor) are cancelled. Both were 90nm parts originally slated for Q2 2005. Intel's on-record framing: "We are accelerating our dual-core schedule for 2005." Dual-core desktop is pulled "12 to 18 months ahead of previous schedules" (Vance, *The Register*, 2004-05-07).
- **2004, May 17** — *VARBusiness* publishes Andrew Wolfe's follow-up coverage, "Intel Clears Up Post-Tejas Confusion" (Yellow secondary; cited by Asanovic et al. 2006).
- **2004, fall** — Intel formally abandons the 4 GHz Pentium 4 line target altogether (Sutter 2005 §"Obstacles, and Why You Don't Have 10GHz Today").
- **2004, December** — Herb Sutter posts the first version of "The Free Lunch Is Over" to gotw.ca; the same text would appear formally in *Dr. Dobb's Journal* 30(3) the following March (Sutter 2005 masthead note).

## The Pivot Lands (2005–2006)

- **2005, early** — Sutter notes that Intel is "planning to ramp up a little further to 3.73GHz in early 2005" — the highest mainstream clock-speed point reached before the multicore transition (Sutter 2005 §"Obstacles, and Why You Don't Have 10GHz Today").
- **2005, March** — Sutter's "The Free Lunch Is Over" is published in *Dr. Dobb's Journal* 30(3). The article is the canonical software-industry account of the pivot.
- **2005** — Intel ships the Pentium D and AMD ships the Athlon 64 X2; both are mainstream x86 dual-core desktop parts. Sutter's contemporaneous read: AMD's design is more architecturally integrated; "Intel's initial entry basically just glues together two Xeons on a single die" (Sutter 2005 §"TANSTAAFL"). *Specific ship-date claims (Pentium D 2005-05-26, Athlon 64 X2 2005-05-31) remain Yellow pending primary press-release verification — see open-questions.md Q3.*
- **2005** — Sun Microsystems releases the Niagara processor (UltraSPARC T1), an 8-core server chip; Berkeley View 2006 names it as one of the two server-multicore precedents Intel followed (Asanovic et al. 2006 p.4).
- **2006, December 18** — Asanovic et al. publish "The Landscape of Parallel Computing Research: A View from Berkeley" (UCB/EECS-2006-183). The report names the post-2004 regime as "Power Wall + Memory Wall + ILP Wall = Brick Wall" (Asanovic et al. 2006 pp.5–6), explicitly cites Tejas's cancellation and Borkar 1999 as evidence of an industry inflection (p.~21 §4.1), and reformulates the conventional wisdom of computer architecture in 12 Old-CW / New-CW pairs.

## Post-history (2007–2011)

- **2011, May** — Shekhar Borkar and Andrew A. Chien publish "The Future of Microprocessors" in *Communications of the ACM* 54(5):67–77. Borkar's own seven-years-on retrospective frames the post-2004 regime as the new normal: "the frequency of operations will increase slowly, with energy the key limiter of performance, forcing designs to use large-scale parallelism, heterogeneous cores, and accelerators" (Borkar & Chien 2011 p.67). The paper documents that "single-thread performance has already leveled off, with only modest increases expected in the coming decades" (p.72).

## Conflict Notes (timeline-specific)

- The **2003 vs 2004 framing**: Sutter writing in late 2004 places the inflection point in early 2003 ("CPU performance growth as we have known it hit a wall two years ago"). The May 2004 Intel cancellation is the *industrial-action* moment, not the *physics* moment. The chapter should distinguish the two.
- The **"4 GHz" target dates**: Intel delayed the 4 GHz Pentium 4 chip "until 2005" in mid-2004 and abandoned it entirely in fall 2004 (Sutter 2005). Tejas, the chip that would have crossed 4 GHz on the line, was cancelled May 7 2004 — so "Intel cancelled its 4 GHz chip" is a real-but-imprecise characterization.
