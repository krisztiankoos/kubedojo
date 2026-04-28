# People: Chapter 35 — Indexing the Mind

Verified protagonist bios. Bios are kept short — material that does not directly bear on the 1996-2003 Stanford-to-Google window stays out. Verification colors track how confident the chapter can be in load-bearing biographical claims when drafting.

## The Algorithm Authors

### Lawrence ("Larry") Page (b. 1973)
- **Position 1996-1998:** PhD candidate, Stanford CS Department; previously BSE in Computer Engineering, University of Michigan Ann Arbor (1995).
- **Role in the chapter:** First author of *The PageRank Citation Ranking* (1999) and second author (after Brin) of *The Anatomy of a Large-Scale Hypertextual Web Search Engine* (1998). Also acknowledged as a hardware-architecture contributor in Barroso 2003 — a useful chapter-internal beat that cuts against the algorithm-vs-infrastructure split the founder myth tends to draw.
- **Why he matters here:** Chapter co-protagonist for the algorithm and infrastructure crystallization. Later corporate biography (Google CEO, Alphabet) is out of scope.
- **Verification:** **Green** for educational background and Stanford CS PhD candidacy at the time of the Anatomy paper — Anatomy 1998 PDF p18 (author bio), verified Claude `pdftotext` 2026-04-28. **Green** for hardware-architecture acknowledgment — Barroso 2003 PDF p7. Yellow for biographical detail beyond the papers (birth year, family background, undergraduate experience): widely repeated in secondaries but no primary anchor in this set.

### Sergey Brin (b. 1973)
- **Position 1996-1998:** PhD candidate, Stanford CS Department; previously BS in mathematics and computer science, University of Maryland College Park (1993); MS Stanford (1995). NSF Graduate Fellow.
- **Role in the chapter:** Co-author with Page on both load-bearing primary papers; first author of the Anatomy paper. Brought a data-mining and large-scale-text-collection research background to the project.
- **Why he matters here:** Chapter co-protagonist. Later corporate role (Google President, Alphabet) is out of scope.
- **Verification:** **Green** for educational background and NSF Graduate Fellowship — Anatomy 1998 PDF p18 (author bio), verified Claude `pdftotext` 2026-04-28. The bio explicitly names "search engines, information extraction from unstructured sources, and data mining of large text collections and scientific data" as Brin's research interests at the time. Yellow for biographical detail beyond the papers.

## The Infrastructure Authors

### Urs Hölzle
- **Position 2003:** Google Fellow; previously vice president of engineering responsible for managing development and operation of the Google search engine "during its first two years."
- **Role in the chapter:** Third author of Barroso-Dean-Hölzle 2003. The chapter's primary infrastructure-architect figure. The "first two years" attribution in his Barroso-2003 bio (which dates to ~1999-2001) places him at Google as the search engine matured into the production cluster the 2003 paper documents.
- **Why he matters here:** Co-author of the primary commodity-cluster anchor; the engineering voice in the algorithm-to-infrastructure transition. Educational credentials (diploma, ETH Zürich; PhD, Stanford CS) are anchored in his Barroso 2003 bio.
- **Verification:** **Green** for Google role and educational background — Barroso 2003 PDF p7 (author bio), verified Claude `pdftotext` 2026-04-28.

### Luiz André Barroso
- **Position 2003:** Member of the Systems Lab at Google, focused on Google's web-search efficiency and hardware architecture.
- **Role in the chapter:** First author of Barroso-Dean-Hölzle 2003. Later co-author (with Hölzle) of *The Datacenter as a Computer* (2009/2013) — the codification of warehouse-scale computing as an academic discipline.
- **Why he matters here:** Brought a computer-architecture research perspective (BS/MS Pontifícia Universidade Católica, Brazil; PhD computer engineering, USC) to the cluster-architecture documentation. The 2003 paper's voice is largely his.
- **Verification:** **Green** for Google role and educational background — Barroso 2003 PDF p7 (author bio), verified Claude `pdftotext` 2026-04-28.

### Jeffrey Dean
- **Position 2003:** Distinguished engineer in the Systems Lab at Google, working on crawling, indexing, and query-serving systems with a focus on scalability and improving relevance.
- **Role in the chapter:** Second author of Barroso-Dean-Hölzle 2003. Later first author of MapReduce (2004), Bigtable (2006), and many subsequent foundational Google systems papers — but those postdate the chapter's primary-anchor set and are referenced only as forward-pointers.
- **Why he matters here:** Co-author of the primary commodity-cluster anchor. Educational credentials (BS UMinnesota; PhD CS UWashington) are anchored in his Barroso 2003 bio.
- **Verification:** **Green** for Google role and educational background — Barroso 2003 PDF p7 (author bio), verified Claude `pdftotext` 2026-04-28. NB the chapter must not over-attribute the entire software-fault-tolerance stack to Dean alone; the 2003 paper is silent on individual contributions. Phrase as "engineers including Dean, Ghemawat, Hölzle, and others."

### Sanjay Ghemawat (referenced, not author of Barroso 2003)
- **Position 2003:** Google engineer; first author of *The Google File System* (SOSP '03).
- **Role in the chapter:** Anchor figure for the GFS-as-corroboration claim (design-for-failure). Long-running collaborator with Dean.
- **Why he matters here:** GFS is the chapter's secondary primary anchor for the design-for-failure thesis. Ghemawat's name appears as first author on GFS; the chapter should phrase Dean and Ghemawat together where their joint work is referenced.
- **Verification:** **Green** for first authorship of GFS — GFS 2003 PDF p1, verified Claude `pdftotext` 2026-04-28. Yellow for biographical detail beyond the paper.

## Acknowledged Contributors (from Barroso 2003 acknowledgments)

### Gerald Aigner, Ross Biro, Bogdan Cocosel
- **Role in the chapter:** Named in Barroso 2003 acknowledgments as having "made contributions to Google's hardware architecture that are at least as significant as ours." The chapter does not need to develop these as protagonists, but acknowledging their existence is the honest move per the Citation Bar — the founder-myth tends to credit Page and Brin alone for everything Google built, which is wrong.
- **Verification:** **Green** for the acknowledgment — Barroso 2003 PDF p7 (Acknowledgments), verified Claude `pdftotext` 2026-04-28. Beyond the names, no primary biographical detail in this set.

## Cited Predecessor (Anchor for Chapter-Internal Echo)

### John McCarthy (1927-2011) — referenced, not author
- **Position 1998:** Professor emeritus, Stanford CS Department.
- **Role in the chapter:** McCarthy is *not* a protagonist of Ch35, but his home page is used as a personalization seed in the PageRank paper's experiments (PDF p11, p12). This creates a quiet chapter-internal echo: McCarthy named "Artificial Intelligence" at Dartmouth in 1956 (Ch11); his home page later anchors a personalization vector in the algorithm that built the foundational AI infrastructure (Ch35).
- **Why he matters here:** A one-sentence chapter-internal cross-reference; do not develop into a paragraph. The echo is the chapter's payoff for the careful naming work in Ch11.
- **Verification:** **Green** for the home-page-as-seed claim — PageRank 1999 PDF p11 ("the home page of a famous computer scientist, John McCarthy"), p12 (table comparing McCarthy's view to Netscape's view), verified Claude `pdftotext` 2026-04-28.

## Folklore Figures (Yellow — secondary anchoring only)

### Andy Bechtolsheim (b. 1955)
- **Role in folklore:** Wrote the legendary $100,000 check made out to "Google Inc." in August 1998, before the company was even formally incorporated, after a brief Stanford-driveway meeting with Page and Brin.
- **Verification:** Yellow — folklore widely repeated in Levy 2011 / Battelle 2005 / Vise & Malseed 2005; no primary anchor (canceled check or correspondence) in this set. Use only as Yellow narrative color attributed by author.

### David Cheriton, Ram Shriram, others (early angel investors)
- **Role in folklore:** Early angel investors who joined Bechtolsheim. Useful background for the founding-chronology beat in Scene 1.
- **Verification:** Yellow — same secondary-only basis. The chapter should not develop these into protagonists.

### Susan Wojcicki (b. 1968)
- **Role in folklore:** Owned the Menlo Park garage at 232 Santa Margarita Avenue that Brin and Page rented in September 1998 as Google's first office. Later joined Google and became CEO of YouTube.
- **Verification:** Yellow — folklore widely repeated; not load-bearing for Ch35's algorithmic or infrastructural arguments; can be one-sentence color in Scene 1 with secondary attribution.

## Notes on bios

- All bios are kept narrowly to the 1996-2003 Stanford-to-cluster window. Later corporate or research careers are deliberately out of scope.
- Bios are anchored to the primary papers' own author-bio sections wherever possible (Anatomy 1998 p18; Barroso 2003 p7; GFS 2003 p1). These are Green primary biographical anchors that do not require secondary corroboration.
- Folklore figures (Bechtolsheim, Wojcicki, Cheriton, etc.) stay out of load-bearing scenes and are used only as Yellow narrative color with explicit secondary attribution.
- No invented quotes. Where the chapter implies motive (e.g., "Brin and Page chose the academic citation framing because they were academics"), the implication must be either supported by the papers themselves (which do say "academic citation analysis" explicitly) or marked as conjecture.
