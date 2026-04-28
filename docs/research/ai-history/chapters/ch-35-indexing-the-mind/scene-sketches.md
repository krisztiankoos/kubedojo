# Scene Sketches: Chapter 35 — Indexing the Mind

Citation-anchored scene beats. Each scene maps 1:1 to a layer in `brief.md` *Prose Capacity Plan*. Each beat must cite a specific source identifier; beats with no anchor are flagged Yellow or Red and stay out of prose until upgraded.

## Scene 1 — The Spam-Drowned Web (1994-1997)

Anchored layer: *500-700 words: The Spam-Drowned Web (Scene 1)* (brief.md Prose Capacity Plan).

| Beat | Anchor | Status |
|---|---|---|
| In 1994 the World Wide Web Worm (WWWW) had an index of 110,000 web pages and web-accessible documents — the contemporaneous baseline of search-engine scale. | Anatomy 1998 PDF p2 §1.1 (verified Claude `pdftotext` 2026-04-28). | **Green** |
| By November 1997 the top search engines claimed indices ranging from 2 million (WebCrawler) to 100 million web documents (per Search Engine Watch); query traffic had risen so dramatically that AltaVista was reporting "roughly 20 million queries per day." | Anatomy 1998 PDF p2 §1.1. | **Green** for the contemporaneous-claim framing. The chapter must phrase these as 1997-vintage industry claims that the Anatomy paper itself reports, not as the chapter's own measurements. |
| As of November 1997, "only one of the top four commercial search engines finds itself" when queried with its own name — the Anatomy paper's own diagnostic of how badly keyword-counting search had failed. | Anatomy 1998 PDF p2 §1.3.1. | **Green** |
| The "junk results" / "low-quality matches" framing is explicit in the Anatomy paper as the motivation for a new approach: "automated search engines that rely on keyword matching usually return too many low quality matches." | Anatomy 1998 PDF p1 §1 (Introduction). | **Green** |
| Brin and Page were Stanford CS PhD candidates working on a project they called BackRub. The Anatomy paper's references include the URL `google.stanford.edu/~backrub/pageranksub.ps`, anchoring the project's predecessor name in the published record. | Anatomy 1998 PDF p17 References. | **Green** for the URL existence; Yellow for the broader narrative that "the project was originally called BackRub" without a secondary anchor (Levy 2011 / Battelle 2005 widely confirm). |
| Larry Page and Sergey Brin met at Stanford during graduate-orientation week in 1995 and began collaborating on what became BackRub in 1996. | None primary. Levy 2011, Battelle 2005, Vise & Malseed 2005 widely confirm. | Yellow — folklore claim; phrase with secondary attribution; do not invent specific scenes from the meeting. |
| Brin and Page worked on borrowed equipment at Stanford including space in the Gates Computer Science Building. | None primary. Levy 2011 / Battelle 2005. | Yellow — phrase as Stanford-era working color, not as a load-bearing infrastructure beat. |

**Scene-level note:** The infrastructure beat to foreground is the *gap* between the web's exploding scale (110K pages 1994 → ≥150M pages estimated 1998) and the existing search engines' inability to keep up qualitatively, not just quantitatively. Don't draft folklore scenes from the BackRub era; the anchor weight is in the contemporaneous-industry-failure framing the Anatomy paper itself provides. Keep the chapter's voice analytical, not breathless about "two grad students who would change the world."

## Scene 2 — The Citation Insight (1996-1998)

Anchored layer: *700-900 words: The Citation Insight (Scene 2)* (brief.md Prose Capacity Plan).

| Beat | Anchor | Status |
|---|---|---|
| The PageRank paper opens by explicitly invoking academic citation analysis: "there is already a large literature on academic citation analysis" — and immediately distinguishes the web case (no quality control, no roughly-similar paper-as-unit assumption, links engineered to manipulate ranking). | PageRank 1999 PDF p1 §1.1; p2 §2.1. | **Green** |
| The contribution as the paper itself frames it: "It is obvious to try to apply standard citation analysis techniques to the web's hypertextual citation structure. One can simply think of every link as being like an academic citation." | PageRank 1999 PDF p2 §2.1. | **Green** |
| Simple backlink counting is insufficient: not all citations are equal; links from high-importance pages should weigh more than links from obscure pages. | PageRank 1999 PDF p2 §2.1 ("simple backlink counts have a number of problems on the web"). | **Green** |
| The Anatomy paper independently confirms that PageRank is "an approximation of citation importance on the web." | Anatomy 1998 PDF p4. | **Green** |
| The Brin-Page biographical context: both were Stanford CS PhD candidates at the time of publication. Brin (BS Maryland 1993, MS Stanford 1995, NSF Graduate Fellow) brought a data-mining and large-scale-text background; Page (BSE Michigan 1995) brought a link-structure / human-computer-interaction background. | Anatomy 1998 PDF p18 (author bios). | **Green** |
| The PageRank paper frames its goal as measuring objectively what is fundamentally subjective: "rating Web pages objectively and mechanically, effectively measuring the human interest and attention devoted to them." | PageRank 1999 PDF p1 (Abstract). | **Green** |
| The chapter must explicitly *not* claim PageRank invented citation analysis. The paper itself acknowledges Garfield 1995 and Goffman 1971 (citation-analysis prior literature) and Kleinberg's contemporaneous Hubs-and-Authorities work. | PageRank 1999 PDF p2 §2.1 (references [Gar95], [Gof71], [Kle98]). | **Green** for the prior-literature acknowledgment. |

**Scene-level note:** The chapter's "the algorithm is academic citation analysis applied to the web" claim is *the paper's own framing* — quote the paper, do not paraphrase as chapter-original insight. Avoid the breathless "they invented a way to measure semantic relevance" framing that secondary tech journalism likes; the paper's own framing is more modest and more accurate.

## Scene 3 — The Random Surfer and the Eigenvector (1998-1999)

Anchored layer: *800-1,000 words: The Random Surfer and the Eigenvector (Scene 3)* (brief.md Prose Capacity Plan).

| Beat | Anchor | Status |
|---|---|---|
| The PageRank definition is recursive: a page's rank depends on the ranks of pages linking to it. This requires a fixed-point computation. The paper gives an explicit iterative algorithm: `R_{i+1} ← AR_i + dE` repeated until `\|R_{i+1} - R_i\|_1 < ε`. | PageRank 1999 PDF p6 §2.6 ("Computing PageRank"). | **Green** |
| Mathematically: `R'` is an eigenvector of `(A + E·1)`, where A is the link-transition matrix and E is the personalization / random-jump source. | PageRank 1999 PDF p5 §2.4. | **Green** |
| The "Random Surfer Model" is the paper's own intuitive reading: PageRank equals the standing probability distribution of a random walk on the web's link graph, where the surfer "simply keeps clicking on successive links at random" but "if a real Web surfer ever gets into a small loop ... the surfer will jump to some other page." The E vector encodes the "got bored and jumped" probability. | PageRank 1999 PDF p5 §2.5. | **Green** — the "random surfer" name is the paper's own. |
| The convergence parameter used in experiments was `\|E\|_1 = 0.15` — i.e., the surfer "periodically gets bored" with 15% probability per step. The conventional "0.85 damping factor" is the complement (1 - 0.15). | PageRank 1999 PDF p11. | **Green** |
| The 1998 PageRank experiments ran on the Stanford WebBase crawl of "approximately 24 million web pages" — the same corpus the Anatomy paper independently anchors at p1 (Abstract) and p14 (Table 1). | PageRank 1999 PDF p6 §3; Anatomy 1998 PDF p1, p14 Table 1. | **Green** — two independent paper anchors for the same scale. |
| The web's link-graph scale at the time of the paper: "roughly 150 million nodes (pages) and 1.7 billion edges (links)" with "about 11 links on" each page. | PageRank 1999 PDF p3 §2.2; PageRank 1999 PDF p6 §3 (continuation). | **Green** |
| The "personalization" experiment used John McCarthy's home page as a seed E vector — yielding a personalized PageRank that put "John McCarthy's Home Page" at 100% percentile from McCarthy's view. The chapter-internal echo: McCarthy named "Artificial Intelligence" at Dartmouth in 1956 (Ch11); his home page anchors a personalization vector in the foundational web-search algorithm in 1998. | PageRank 1999 PDF p11 ("the home page of a famous computer scientist, John McCarthy"); p12 (table). | **Green** — useful chapter-craft beat for the cross-reference back to Ch11. |
| The chapter must explain the eigenvector / random-surfer equivalence at the level the paper itself does (intuitive, prose-level), not at a graduate-linear-algebra level. The chapter is history, not a tutorial. | n/a — chapter-craft note. | n/a |

**Scene-level note:** The chapter's algorithmic centerpiece. Three independent paragraphs in the paper (random surfer §2.5; eigenvector §2.4; iterative algorithm §2.6) anchor distinct beats — use all three. The McCarthy personalization echo is a one-paragraph payoff, not a digression — frame it carefully as "the man who named AI in 1956 ends up as a personalization vector in 1998" without overclaiming significance.

## Scene 4 — The Commodity Cluster (1998-2003)

Anchored layer: *800-1,100 words: The Commodity Cluster (Scene 4)* (brief.md Prose Capacity Plan).

| Beat | Anchor | Status |
|---|---|---|
| The 1998 baseline architecture: a single distributed-crawler-plus-indexer pipeline (URLserver → crawlers → storeserver → indexer → sorter → searcher) implemented in C/C++ on Solaris and Linux machines, indexing 24M pages (147.8 GB raw, 53.5 GB compressed). | Anatomy 1998 PDF p7 §4.1; p14 Table 1. | **Green** |
| The 2003 production architecture: more than 15,000 commodity-class PCs across geographically distributed clusters, with DNS-based load balancing across clusters and per-cluster hardware load balancers. | Barroso 2003 PDF p1 (15,000 figure); p2 (DNS load balancing, multi-cluster topology). | **Green** |
| The three explicit design principles: software-level reliability instead of hardware fault tolerance; replication for throughput AND fault tolerance; price/performance over peak performance; commodity PCs over high-end servers. | Barroso 2003 PDF p3 (bulleted principles). | **Green** |
| What Google explicitly *eschewed*: redundant power supplies, RAID, high-quality components — and SCSI disks (in favor of IDE). | Barroso 2003 PDF p3 (RAID/redundant power); p4 (IDE vs SCSI: "two or three times as much as an equal-capacity IDE drive"). | **Green** |
| The price/performance case in concrete late-2002 dollars: a $278,000 RackSaver.com rack of 88 dual-CPU 2GHz Xeon servers (2GB RAM, 80GB disk each) versus a ~$758,000 single 8-CPU server with 64GB RAM and 8TB disk. ~3× cost for ~22× fewer CPUs. | Barroso 2003 PDF p4. | **Green** — the chapter's clearest single price/performance beat. |
| The hardware was heterogeneous and short-lived: CPU generations from single-processor 533MHz Intel Celeron through dual 1.4GHz Pentium III in active service simultaneously; servers replaced every 2-3 years because of performance-disparity load-balancing problems. | Barroso 2003 PDF p4. | **Green** |
| Energy was a first-class design constraint, not an afterthought: dual-1.4GHz P3 servers drew 90W under load (~120W AC after PSU losses); racks ran at ~10kW; power density was 400-700 W/ft², already pushing commercial datacenter cooling capacity in 2003. | Barroso 2003 PDF p4 ("The power problem"). | **Green** |
| The contemporaneous corroboration from GFS (SOSP 2003): file system designed for "hundreds or even thousands of storage machines built from inexpensive commodity parts" because "component failures are the norm rather than the exception." Largest cluster at the time: "hundreds of terabytes of storage across thousands of disks on over a thousand machines." | GFS 2003 PDF p1 §1; p1 (Abstract). | **Green** |
| The chapter must keep the 1998 and 2003 timelines distinct. The 1998 architecture was a Stanford prototype for academic research; the 2003 architecture was a production multi-datacenter service. The "1,000 PCs in a corkboard rack" folklore image is from the 1998-2000 era and is not anchored in the primary papers; phrase as Yellow secondary color (Levy 2011 / Battelle 2005). | n/a — chapter-craft note. | n/a |
| Folklore figures (Andy Bechtolsheim's $100,000 check; Susan Wojcicki's garage; the September 1998 incorporation date) belong to a one-paragraph founding-chronology beat with explicit secondary attribution. None is load-bearing for the infrastructure argument. | None primary. Levy 2011 / Battelle 2005 / Vise & Malseed 2005. | Yellow |

**Scene-level note:** The chapter's largest scene. Nine distinct primary anchors in Barroso 2003 alone, plus four primary anchors in Anatomy 1998 for the contrast baseline. The infrastructure-honesty rule: do not retroject the 15,000-PC scale onto 1998, and do not back-attribute the simplicity of 1998 onto 2003. Vivid imagery (corkboard racks, pizza-box servers) is Yellow folklore color from secondaries; do not phrase it as primary infrastructure fact.

## Scene 5 — The Inheritance (2003-onward, sparse pointer)

Anchored layer: *400-600 words: The Inheritance (Scene 5)* (brief.md Prose Capacity Plan).

| Beat | Anchor | Status |
|---|---|---|
| Larry Page is acknowledged in Barroso 2003 as a contributor to Google's hardware architecture (alongside Aigner, Biro, Cocosel) — useful as the chapter's closing beat, cutting against the founder-myth split between Page-the-algorithm-author and a separate infrastructure team. | Barroso 2003 PDF p7 (Acknowledgments). | **Green** |
| The same Barroso-Hölzle authorial team generalized the 2003 paper into *The Datacenter as a Computer: An Introduction to the Design of Warehouse-Scale Machines* (Synthesis Lectures, 2009; 2nd ed. 2013). | Bibliographic fact (publication metadata). PDF retrieval failed 2026-04-28. | Yellow |
| Hennessy and Patterson, *Computer Architecture: A Quantitative Approach*, 5th ed. (2011), added Chapter 6 "Warehouse-Scale Computers" — the canonical academic-textbook codification of the pattern. | Bibliographic fact. | Yellow |
| The commodity-cluster pattern Google documented in 2003 became the substrate that, a decade later, deep-learning training infrastructure was built on (TPU pods, GPU clusters, etc.). This is a sparse forward-reference, not a chapter-internal argument. | Forward-reference to Part 6 / Part 8 chapters. | Yellow — phrase as one sentence at the close, no further development. |
| The chapter caps here. The deep-learning-substrate argument belongs to later chapters. | n/a — chapter-craft cap. | n/a |

**Scene-level note:** The chapter's smallest scene by design. The inheritance argument is honestly thin from an anchor standpoint at contract time — Hennessy-Patterson 5e and Barroso-Hölzle 2009 are bibliographic facts but not page-anchored, and the deep-learning-substrate forward-reference is Yellow. The Page-as-systems-thinker close anchored in Barroso 2003 acknowledgments is the scene's strongest single beat. Cap the chapter and forward-reference; do not over-develop.

## Cross-scene notes

- **No invented dialogue or scenes.** Every quoted sentence must come from a primary source. Folklore scenes from Levy 2011 / Battelle 2005 / Vise & Malseed 2005 may appear as Yellow narrative color with explicit secondary attribution; they may not appear as load-bearing scenes.
- **The 1998 / 2003 timeline split is sacred.** The chapter must not blur the Anatomy-paper-era architecture and the Barroso-paper-era architecture. Use the two papers' own timestamps as the chapter's structural spine.
- **Founder-myth resistance.** The chapter should foreground the team — including Aigner, Biro, Cocosel, Hölzle, Dean, Ghemawat — rather than Page-and-Brin alone. Barroso 2003 acknowledgments and the 2003 author lineup are the chapter's primary anchors for this honest-credit move.
- **The McCarthy echo is a payoff, not a digression.** One paragraph maximum. The chapter must not over-develop the chapter-internal cross-reference into a self-congratulatory book-craft moment.
- **The deep-learning-substrate inheritance is a one-sentence close, not a chapter argument.** Resist the temptation to anticipate Part 6 / Part 8.
- **Honest cap.** If Levy 2011 / Battelle 2005 page anchors do not land before drafting, Scene 1 stays compact; if Hennessy-Patterson 5e page anchors do not land, Scene 5 stays compact. The chapter's natural length is `3k-5k likely`, not forced to `4k-7k stretch`.
