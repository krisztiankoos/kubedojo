# Open Questions: Chapter 35 — Indexing the Mind

Surfaced from `brief.md` *Conflict Notes* and the Yellow/Red entries in `sources.md`. Each question identifies the specific evidence needed to resolve it. Drafting cannot rely on any open-question item until its evidence is in hand.

## Lower-Priority Questions (Do Not Block Drafting)

The chapter's three load-bearing claim layers (algorithm framing, eigenvector / random-surfer, commodity cluster) are all anchored to primary papers at contract time. The questions below are mostly *narrative-color* gaps that affect Scene 1 (Stanford folklore) and Scene 5 (the inheritance argument) — the chapter's two smallest scenes by design.

### Q1. The Stanford founding chronology — primary anchors

- **Question:** What primary anchors exist for the Brin-Page Stanford-1995 meeting, the 1996 BackRub project start, the September 1997 google.com domain registration, the August/September 1998 Bechtolsheim $100,000 check, and the September 4, 1998 incorporation date?
- **Why it matters:** Scene 1's narrative color (the Stanford-folklore framing) currently rests entirely on three secondary narratives (Levy 2011, Battelle 2005, Vise & Malseed 2005). All three converge on the same chronology, but they may also be copying each other. A single primary anchor (canceled check, incorporation filing, WHOIS history) would lift the load-bearing folklore beat from Yellow to Green.
- **Evidence needed:**
  - California Secretary of State business search for Google Inc., Sept 1998 — primary
  - WHOIS history snapshots (DomainTools, archive.org WHOIS) for `google.com` registration date — primary
  - Stanford OTL filings around the PageRank patent — primary, would corroborate Stanford-1996-onward affiliation
  - Bechtolsheim's own CHM oral history — primary, corroborates the $100,000 check folklore
- **Status:** Yellow. Tractable without physical archive trips. Worth attempting before drafting begins.

### Q2. Levy 2011 / Battelle 2005 page anchors for Scene 1 narrative color

- **Question:** What specific pages in Levy 2011 *In the Plex* and Battelle 2005 *The Search* anchor (a) the PageRank-as-academic-citation framing; (b) the BackRub-name origin; (c) the dorm-room infrastructure folklore; (d) the Bechtolsheim check folklore?
- **Why it matters:** The chapter's secondary narrative attribution is currently "Levy 2011 generally" and "Battelle 2005 generally" — too vague for production prose. Page-level anchors are needed before Scene 1 can be drafted at the planned 500-700-word range.
- **Evidence needed:** Physical or e-book copies of both books with page-level extraction.
- **Status:** Yellow. Requires book access. If unavailable, Scene 1 caps below 500 words on primary anchors only.

### Q3. The PageRank patent (US 6,285,999)

- **Question:** Does the PageRank patent provide useful primary-document anchors for the algorithm's institutional history? Filed January 1998, granted September 4, 2001. Larry Page assignor; Stanford University assignee.
- **Why it matters:** The patent would provide an additional primary anchor for the algorithm's January 1998 timestamp (which currently rests on the PageRank PDF cover date). It would also document the Stanford OTL ownership structure that shaped the early-Google business arrangement.
- **Evidence needed:** USPTO PAIR or Google Patents retrieval; full patent text.
- **Status:** Yellow. Tractable. Useful for Scene 2 and Scene 5 but not load-bearing.

### Q4. Hennessy-Patterson 5e Chapter 6 page anchors for Scene 5

- **Question:** What does Hennessy-Patterson 5e (2011) Chapter 6 say specifically about Google as the originating warehouse-scale-computing prototype? Does it cite Barroso 2003 directly, and what claims does it draw from that paper?
- **Why it matters:** Scene 5's "the pattern became canonical" beat needs a textbook anchor. The bibliographic fact of the chapter's existence is Yellow; specific page-level claims would be Green.
- **Evidence needed:** Physical or e-book copy of Hennessy-Patterson 5e, Chapter 6.
- **Status:** Yellow. Library access. If unavailable, Scene 5 caps at the planned 400-600-word range without further expansion.

### Q5. Barroso-Hölzle 2009 *Datacenter as a Computer* PDF retrieval

- **Question:** Can the open-access Synthesis Lecture PDF be retrieved from Morgan & Claypool, ACM Digital Library, or any institutional mirror? The 2026-04-28 fetch attempts failed.
- **Why it matters:** The 2009 monograph is the same authors' generalization of their own 2003 paper — a high-value secondary that, if retrieved, would give Scene 5 a primary-author anchor.
- **Evidence needed:** Direct PDF retrieval; Stanford or Berkeley institutional library access; or CHM digital collection.
- **Status:** Yellow. Tractable but the standard public URLs failed once.

### Q6. The 2003-paper "first two years" Hölzle bio claim

- **Question:** Hölzle's Barroso 2003 author bio says he was responsible for "the development and operation of the Google search engine during its first two years." The chapter's reading of this is "approximately 1999-2001," but the exact dates of Hölzle's Google start are not anchored.
- **Why it matters:** Minor — affects Scene 5's framing of who built the 2003-era infrastructure.
- **Evidence needed:** Hölzle CV; Google's own corporate timeline; or his CHM oral history if one exists.
- **Status:** Yellow. Non-blocking.

### Q7. The "1,000 PCs" / "corkboard rack" folklore

- **Question:** Where does the specific image of "1,000 PCs in corkboard racks" originate? It's widely repeated in tech journalism but neither primary paper anchors it.
- **Why it matters:** The image is vivid and would make Scene 4 more textured, but it must not be load-bearing without an anchor. If a primary source (a Stanford photograph, Hölzle interview, contemporaneous news article) can be located, the image is usable; otherwise it stays out.
- **Evidence needed:** Stanford CS Department archives (photographs); Levy 2011 / Battelle 2005 specific page anchors.
- **Status:** Yellow. Non-blocking; the chapter can present the 2003 architecture without this specific image.

### Q8. Inktomi and Beowulf prior-art comparison

- **Question:** What were Inktomi's (1996, Berkeley) and Beowulf clusters' (1994, NASA) commodity-cluster architectures, and how did they compare to Google's 2003 architecture?
- **Why it matters:** Scene 4's boundary contract claims that Google did not invent the commodity cluster. Some specificity about *what* Google did differently (the combination of scale + software fault tolerance + parallelizable application) would tighten the claim.
- **Evidence needed:** Inktomi's contemporary papers (Eric Brewer's lab); Beowulf project documentation (NASA/CESDIS).
- **Status:** Yellow. Non-blocking. Scene 4 can phrase the boundary contract without specific prior-art comparison.

### Q9. The Page-Brin-Motwani-Winograd authorship of PageRank

- **Question:** Why does the PageRank paper have four authors (Page, Brin, Motwani, Winograd) while the Anatomy paper has two (Brin, Page)? What were Rajeev Motwani's and Terry Winograd's specific contributions?
- **Why it matters:** Minor — the PageRank paper's title page lists all four as authors, but secondary narratives (Levy 2011, Battelle 2005) typically credit only Page and Brin. Motwani was a Stanford theory-of-computing professor; Winograd was Page's PhD advisor. Acknowledging their contributions cuts against the founder-myth simplification.
- **Evidence needed:** PageRank paper acknowledgments section; secondary narrative attribution; Motwani's later papers; Winograd's published comments on PageRank.
- **Status:** Yellow. Non-blocking. Scene 2 should mention all four authors at least once.

## Notes on resolution sequence

The order of attempted resolution if the chapter is to push toward `4k-7k stretch`:

1. **Tractable, no archive trip:** Q3 (PageRank patent), Q1 partial (WHOIS, California SoS), Q5 (DCaaC PDF retry).
2. **Library access:** Q2 (Levy 2011 / Battelle 2005 page anchors), Q4 (Hennessy-Patterson 5e Chapter 6).
3. **Archive access:** Q1 (CHM oral histories, Stanford CS archives), Q7 (Stanford photograph archives).
4. **Lower-priority:** Q6, Q8, Q9 — all non-blocking.

## Notes on what *not* to research

The chapter is deliberately bounded. The following are **out of scope** and should not be researched for this contract:

- Google as a corporation, AdWords, the IPO — Ch35 does not cover post-1998 corporate history beyond the September 1998 incorporation as a Yellow background fact.
- The post-2003 Google software stack (MapReduce 2004, Bigtable 2006, Dremel 2010, etc.) — sparse forward-references only.
- Deep learning at Google or anywhere else — Ch36 onward.
- Anti-trust history, search-engine market dominance, modern Google product strategy.
- PageRank's specific role in modern Google ranking (long since superseded by RankBrain and successors).
- Sergey Brin's later research interests (Calico, Glass, etc.).
- Larry Page's later Alphabet leadership.

The chapter's contract has now reached `capacity_plan_anchored` status: every Prose Capacity Plan layer cites at least one verified page anchor in `sources.md`. Scene 1 and Scene 5 are honestly capped by available secondary anchors; Scenes 2, 3, 4 carry the chapter's load-bearing weight on three Green primary papers (PageRank 1999, Anatomy 1998, Barroso 2003) plus one Green corroborating primary (GFS 2003).
