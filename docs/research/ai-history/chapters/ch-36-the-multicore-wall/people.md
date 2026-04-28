# People: Chapter 36 — The Multicore Wall

Actors with verified facts. Each person below is referenced in at least one Green claim in `sources.md`. The chapter must not invent dialogue or internal motives for any of them.

## Verified Protagonists

### Robert N. Dennard (IBM)

- **Role in chapter:** the absent founding figure. The 1974 IBM scaling recipe that bears his name is the framework whose breakdown the chapter narrates.
- **Verified claim:** "The basic recipe for technology scaling was laid down by Robert N. Dennard of IBM in the early 1970s and followed for the past three decades. The scaling recipe calls for reducing transistor dimensions by 30% every generation (two years) and keeping electric fields constant everywhere in the transistor to maintain reliability." (Borkar & Chien 2011 p.68)
- **Boundary:** Dennard does not appear as an in-scene character. The chapter cites his recipe as the regime that ended; do not narrate Dennard's reasoning or motivations.

### Shekhar Borkar (Intel Corporation)

- **Role in chapter:** the early Intel-internal warning voice. His July/August 1999 *IEEE Micro* paper "Design Challenges of Technology Scaling" is the on-record point at which a senior Intel engineer named the power-density wall five years before Intel acted on it. His May 2011 *CACM* article (with Andrew Chien) is the chapter's retrospective primary source.
- **Verified claims:**
  - The 1999 warning is cited by Asanovic et al. 2006 §4.1 ("even representatives from Intel ... warned that traditional approaches to maximizing performance through maximizing clock speed have been pushed to their limit [Borkar 1999]") and bibliographically confirmed in the Berkeley View references list.
  - The 2011 retrospective frames the post-2004 regime: "the frequency of operations will increase slowly, with energy the key limiter of performance, forcing designs to use large-scale parallelism, heterogeneous cores, and accelerators." (Borkar & Chien 2011 p.67)
  - Co-author with Andrew A. Chien (UC San Diego) of the 2011 retrospective.
- **Boundary:** Do not put quotations from the closed-access 1999 paper in prose without obtaining the full text. The 2011 paper is fully accessible and can be quoted at page level.

### Kunle Olukotun (Stanford)

- **Role in chapter:** the academic-architecture priority figure. The 1996 ASPLOS paper by Olukotun, Nayfeh, Hammond, Wilson, and Chang, "The Case for a Single-Chip Multiprocessor," is the on-record argument that the right architectural response to a fixed transistor budget is many smaller cores rather than one bigger one — eight years before Intel acted.
- **Verified claim:** the paper's existence (DOI `10.1145/237090.237140`) and title-level argument. The Berkeley group (Asanovic et al. 2006) positions itself in the Olukotun-Hydra lineage.
- **Boundary:** the full text is behind the ACM paywall; the chapter cites existence and title only, not internal claims.

### Patrick Gelsinger (Intel)

- **Role in chapter:** the second Intel-insider acknowledgement that frequency scaling was hitting its limit, alongside Borkar 1999. Gelsinger's 2001 ISSCC keynote "Microprocessors for the new millennium" is cited by Asanovic et al. 2006 §4.1 as part of the same evidence chain.
- **Verified claim:** the citation in Berkeley View 2006 references list (p.~46) confirms the 2001 ISSCC keynote and its use as evidence of the inflection.
- **Boundary:** Gelsinger is mentioned for completeness; not a load-bearing protagonist. The chapter should not reconstruct his keynote without verified primary text.

### Herb Sutter

- **Role in chapter:** the software-industry herald. His December 2004 / March 2005 *Dr. Dobb's Journal* article "The Free Lunch Is Over" is the canonical software-side account of the pivot. Sutter is a software architect (his self-introduction in the article: "prominent software architect"), Microsoft employee, and ISO C++ committee chair.
- **Verified claims (verbatim from Sutter 2005):**
  - The article's framing thesis: "Concurrency is the next major revolution in how we write software."
  - The historical inflection: "CPU performance growth as we have known it hit a wall two years ago. Most people have only recently started to notice."
  - The cause attribution: "It has become harder and harder to exploit higher clock speeds due to not just one but several physical issues, notably heat (too much of it and too hard to dissipate), power consumption (too high), and current leakage problems."
  - The future map: "Looking back, it's not much of a stretch to call 2004 the year of multicore."
  - The contemporaneous design judgment: "AMD's seems to have some initial performance design advantages, such as better integration of support functions on the same die, whereas Intel's initial entry basically just glues together two Xeons on a single die."
- **Boundary:** the chapter should attribute design-judgment claims (especially the "Intel just glues together two Xeons" line) to Sutter and not present them as Intel's self-assessment.

### Ashlee Vance (then *The Register*)

- **Role in chapter:** the journalist who anchored the cancellation in real time. Her May 7, 2004 article "Intel says Adios to Tejas and Jayhawk chips" is the chapter's primary contemporaneous press source.
- **Verified claim:** her reporting of the Intel spokesman's verbatim statement: "We are accelerating our dual-core schedule for 2005."
- **Boundary:** Vance's article is cited as primary press, not as Intel corporate communication. The chapter should preserve that distinction.

### Anand Lal Shimpi (then *AnandTech*)

- **Role in chapter:** the trade journalist who anchored the pre-cancellation Tejas factual record. His January 9, 2004 article "Covert Ops in Taiwan — Intel Tejas & Socket 775 Unveiled" is the contemporaneous source for "Tejas samples ran at 2.8 GHz and ~150 W."
- **Boundary:** *AnandTech* operated under contemporary leak-driven reporting. Treat the figures as Green for "what one set of samples did" and Yellow for "what the production part would have been."

### Krste Asanović, David A. Patterson, and the Berkeley View 2006 group

- **Role in chapter:** the academic systematizers. The eleven co-authors of the December 2006 UC Berkeley technical report systematized the post-2004 regime as "Power Wall + Memory Wall + ILP Wall = Brick Wall" and reformulated computer-architecture conventional wisdom into 12 Old-CW / New-CW pairs.
- **Co-authors of record (verified from report cover, p.1):** Krste Asanović, Ras Bodik, Bryan Christopher Catanzaro, Joseph James Gebis, Parry Husbands, Kurt Keutzer, David A. Patterson, William Lester Plishker, John Shalf, Samuel Webb Williams, Katherine A. Yelick.
- **Verified claim:** the 12-pair Old-CW / New-CW table on pp.5–6 of the report; the explicit citations of Tejas + Borkar 1999 in §4.1 (p.~21).
- **Boundary:** the report is cited as a single corporate authorial voice ("the Berkeley View report" / "Asanovic et al. 2006") rather than attributing specific paragraphs to specific co-authors; the report does not internally do that itself.

### The unnamed Intel spokesman (May 7, 2004)

- **Role in chapter:** the institutional voice who delivered the cancellation. The on-record quote — "We are accelerating our dual-core schedule for 2005" — is verbatim per Vance, *The Register*, 2004-05-07.
- **Boundary:** unnamed in the source. Do not assign a name. The contemporaneous Intel CEO was Craig Barrett (CEO 1998–2005); Paul Otellini was COO and incoming CEO. The chapter must not assign the quote to either of them without primary verification.

## Boundary People (Mentioned but Not Drawn)

- **Andrew A. Chien** (UC San Diego) — co-author of Borkar & Chien 2011. Cited via the paper, not characterized.
- **Andrew Wolfe** (then *VARBusiness*) — wrote the May 17, 2004 follow-up "Intel Clears Up Post-Tejas Confusion" cited by Berkeley View 2006. Citation only; full article not retrieved.
- **W.A. Wulf and S.A. McKee** — coined the "memory wall" framing in 1995; cited in Berkeley View 2006 §2 CW pair #7. Background only, not a chapter scene.
- **Frederick Pollack** (Intel) — gave the MICRO-32 1999 keynote that became "Pollack's Rule." Borkar & Chien 2011 (pp.69, 72) reference Pollack's Rule throughout; the original keynote is not openly accessible. Cited at rule-level only.

## Excluded From Scope

- **Jensen Huang**, **Bill Dally**, **Geoffrey Hinton**, and other figures whose role belongs to Part 7 (GPU compute) or to the deep-learning chapters. The Multicore Wall is the *infrastructural backdrop* for those chapters, not the place to introduce them.
- **Craig Barrett** and **Paul Otellini** (Intel CEOs of the period). Cited only if a primary source surfaces them in connection with the Tejas cancellation; not currently anchored.
