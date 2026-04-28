# Infrastructure Log: Chapter 35 — Indexing the Mind

Technical and institutional metrics relevant to the chapter's infrastructure-history thesis. Each row is what made the algorithm and the cluster *operationally* possible (or what their operational limits were). Verification colors are tracked because infrastructure claims that look like throwaway facts are often the ones secondary sources copy from each other without primary evidence.

## The 1998 Architecture (Anatomy paper)

| Item | Value | Verification |
|---|---|---|
| Index size | 24 million pages fetched (76.5 million URLs seen, 1.6 million 404s) | **Green** — Anatomy 1998 PDF p14 Table 1, verified Claude `pdftotext` 2026-04-28. |
| Storage: raw repository | 147.8 GB total fetched pages | **Green** — Anatomy 1998 PDF p14 Table 1. |
| Storage: compressed repository | 53.5 GB | **Green** — Anatomy 1998 PDF p14 Table 1. |
| Storage: total infrastructure footprint (excluding repository) | 55.2 GB | **Green** — Anatomy 1998 PDF p14 Table 1. |
| Storage: total with repository | 108.7 GB | **Green** — Anatomy 1998 PDF p14 Table 1. |
| Crawler throughput (best sustained) | 11 million pages in 63 hours = ~48.5 pages/second | **Green** — Anatomy 1998 PDF p14 §5.2. |
| Total crawl duration | "roughly 9 days to download the 26 million pages (including errors)" | **Green** — Anatomy 1998 PDF p14 §5.2. |
| Indexer throughput | ~54 pages/second | **Green** — Anatomy 1998 PDF p14 §5.2. |
| Sorter machines | 4 (parallel sort took ~24 hours) | **Green** — Anatomy 1998 PDF p14 §5.2. |
| Search latency (current 1998) | "between 1 and 10 seconds" — dominated by NFS disk I/O | **Green** — Anatomy 1998 PDF p14 §5.3. |
| Architecture pipeline | URLserver → distributed crawlers → storeserver → indexer → sorter → searcher (web server) | **Green** — Anatomy 1998 PDF p7 §4.1. |
| Implementation language | C and C++ | **Green** — Anatomy 1998 PDF p7 §4.1. |
| Operating systems | Solaris and Linux | **Green** — Anatomy 1998 PDF p7 §4.1. |
| BigFiles abstraction | Virtual files spanning multiple file systems, addressable by 64-bit integers; handles file-descriptor allocation since OSes did not provide enough | **Green** — Anatomy 1998 PDF p8 §4.2.1. |
| Lexicon size (in-memory) | "fixed at 14 million words" base lexicon | **Green** — Anatomy 1998 PDF p11 §4.4. |
| Disk seek time assumption | ~10 ms per seek (drove design to minimize seeks) | **Green** — Anatomy 1998 PDF p7 §4.2. |
| Hosting | `google.stanford.edu` (Stanford CS Department) | **Green** — Anatomy 1998 PDF p1 (Abstract); PageRank 1999 PDF p15 reference [BP]. |
| Predecessor URL | `google.stanford.edu/~backrub/` (BackRub project) | **Green** — Anatomy 1998 PDF p17 References. |

## The 1998 Algorithm (PageRank paper)

| Item | Value | Verification |
|---|---|---|
| Experimental scale | "current repository of 24 million web pages" via Stanford WebBase | **Green** — PageRank 1999 PDF p6 §3. |
| Crawler indexing target | "process about 50 web pages per second" to index 24M in ~5 days | **Green** — PageRank 1999 PDF p6 §3. |
| Average outlinks per page | "about 11 links on" each page (line continued from p6) | **Green** — PageRank 1999 PDF p6 §3, verified 2026-04-28. |
| Total estimated web size (1998) | "over 150 million web pages with a doubling life of less than one year" | **Green** — PageRank 1999 PDF p2 §1 ("Introduction and Motivation"). |
| Crawlable web link estimate | "roughly 150 million nodes (pages) and 1.7 billion edges (links)" | **Green** — PageRank 1999 PDF p3 §2.2. |
| Personalization parameter | `\|E\|_1 = 0.15` (jump probability; "damping factor" = 0.85 is the complement) | **Green** — PageRank 1999 PDF p11. |
| Iterative computation | Fixed-point iteration `R_{i+1} ← AR_i + dE` until `\|R_{i+1} - R_i\|_1 < ε` | **Green** — PageRank 1999 PDF p6 §2.6. |
| Eigenvector formulation | `R'` is an eigenvector of `(A + E·1)` | **Green** — PageRank 1999 PDF p5 §2.4. |
| Personalization seeds tested | (a) uniform over all pages; (b) Netscape home page; (c) John McCarthy's home page | **Green** — PageRank 1999 PDF p11. |
| Ranks of "John McCarthy's Home Page" under McCarthy seed | 100% percentile | **Green** — PageRank 1999 PDF p12 (table). |

## The 2003 Architecture (Barroso paper)

| Item | Value | Verification |
|---|---|---|
| Cluster scale | More than 15,000 commodity-class PCs | **Green** — Barroso 2003 PDF p1. |
| Cluster topology | Geographically distributed clusters; each cluster ~"a few thousand machines"; DNS-based load balancing across clusters | **Green** — Barroso 2003 PDF p2. |
| Index replication | "dozens of copies of the Web across its clusters" | **Green** — Barroso 2003 PDF p3. |
| Per-cluster topology | Index servers + document servers + spell checker + ad server + Google Web Server, all behind a hardware-based per-cluster load balancer | **Green** — Barroso 2003 PDF p2 (Figure 1 + body); p3. |
| Sharding strategy | Index partitioned into "index shards" (random subset of documents); pool of machines per shard; intra-pool load balancer | **Green** — Barroso 2003 PDF p2-3. |
| CPU range | Single-processor 533 MHz Intel Celeron servers up through dual 1.4 GHz Intel Pentium III servers | **Green** — Barroso 2003 PDF p4. |
| Disk per server | One or more 80 GB IDE drives | **Green** — Barroso 2003 PDF p4. |
| Intra-rack network | 100 Mbps Ethernet | **Green** — Barroso 2003 PDF p4. |
| Inter-rack network | One or two gigabit uplinks per rack to a core gigabit switch | **Green** — Barroso 2003 PDF p4. |
| Servers per rack | 40 to 80 x86-based servers per rack ("each side of the rack contains twenty 20u or forty 1u servers") | **Green** — Barroso 2003 PDF p3. |
| Cost-comparison rack (late 2002) | 88 dual-CPU 2 GHz Xeon, 2 GB RAM, 80 GB disk per server — $278,000 from RackSaver.com | **Green** — Barroso 2003 PDF p4. |
| Cost-comparison alternative | 8-CPU 2 GHz Xeon server, 64 GB RAM, 8 TB disk — ~$758,000 | **Green** — Barroso 2003 PDF p4. |
| Server hardware lifecycle | "a server will not last beyond two or three years" before performance disparity makes load balancing infeasible | **Green** — Barroso 2003 PDF p4. |
| Power per server (dual 1.4 GHz P3) | ~90 W DC under load (~55 W CPUs + ~10 W disk + ~25 W RAM/motherboard) | **Green** — Barroso 2003 PDF p4. |
| Power per server (AC, including PSU efficiency ~75%) | ~120 W AC | **Green** — Barroso 2003 PDF p4. |
| Power per rack | ~10 kW | **Green** — Barroso 2003 PDF p4. |
| Rack footprint | ~25 ft² | **Green** — Barroso 2003 PDF p4. |
| Power density | ~400 W/ft² (dual P3); up to 700 W/ft² with higher-end CPUs | **Green** — Barroso 2003 PDF p4. |
| Commercial datacenter cooling capacity (typical) | 70 to "more than 700 W/ft²" range; Barroso 2003 explicitly notes Google was already pushing the upper bound | **Green** — Barroso 2003 PDF p4-5. |

## Design Choices Made Explicit (Barroso 2003 §p3)

| Choice | Rejected alternative | Verification |
|---|---|---|
| Software-level reliability | Fault-tolerant hardware, redundant power supplies, RAID, high-quality components | **Green** — Barroso 2003 PDF p3. |
| Replication for throughput AND fault tolerance ("almost comes for free") | Separate hot-standby fault-tolerance hardware | **Green** — Barroso 2003 PDF p3. |
| Price/performance over peak performance | Top-bin CPUs, four-processor motherboards | **Green** — Barroso 2003 PDF p3. |
| Commodity x86 PCs | High-end SMP servers, mainframes, SCSI disks | **Green** — Barroso 2003 PDF p3-4. |
| IDE drives | SCSI disks ("two or three times as much as an equal-capacity IDE drive") | **Green** — Barroso 2003 PDF p4. |
| Throughput-oriented application design | Peak server response time | **Green** — Barroso 2003 PDF p2. |

## Adjacent Primary Source (GFS 2003)

| Item | Value | Verification |
|---|---|---|
| Design assumption | "component failures are the norm rather than the exception" | **Green** — GFS 2003 PDF p1 §1. |
| Hardware target | "hundreds or even thousands of storage machines built from inexpensive commodity parts" | **Green** — GFS 2003 PDF p1 §1. |
| File size assumption | "Multi-GB files are common" | **Green** — GFS 2003 PDF p1 §1. |
| Largest deployed cluster (at time of paper) | "hundreds of terabytes of storage across thousands of disks on over a thousand machines" | **Green** — GFS 2003 PDF p1 (Abstract). |

## Operational Limits Worth Naming in Prose

These are the infrastructure constraints the chapter should foreground when explaining why the commodity-cluster pattern was necessary, not just clever:

- **Disk seek dominated cost.** Anatomy 1998 PDF p7 §4.2 explicitly: "a disk seek still requires about 10 ms to complete." Every architectural decision that mattered (BigFiles, sharded inverted index, in-memory lexicon) was a workaround for the random-access penalty of spinning disks.
- **OS file-descriptor limits forced custom abstractions.** Anatomy 1998 PDF p8 §4.2.1: BigFiles existed *because* "operating systems do not provide enough" file descriptors for indexing operations of this scale. The infrastructure had to outgrow the OS, not just the disk.
- **Hardware failure was guaranteed at scale, not exceptional.** Barroso 2003 PDF p3 and GFS 2003 PDF p1 both treat this as the load-bearing design assumption. With 15,000+ commodity PCs, individual disk and motherboard failures happened daily; the only viable response was software-level routing around dead nodes.
- **Energy efficiency was a first-class design constraint by 2003, not an afterthought.** Barroso 2003 PDF p4 explicitly: power density of 400-700 W/ft² was already pushing the limits of commercial datacenter cooling capacity in 2003. Watts-per-query, not just CPU performance, was the optimization target.
- **The 1998 architecture and the 2003 architecture differ by orders of magnitude in scale.** The chapter must keep the timelines distinct: 24M pages in 1998 (Anatomy) vs. 15,000+ PCs across geographically distributed clusters in 2003 (Barroso). These are not the same system at different times of day; they are five years and one industry-defining transition apart.

## Notes

- Several "infrastructure facts" frequently repeated in tertiary sources (e.g., "1,000 PCs in a corkboard rack," "$1M IBM mainframe Google avoided") are *not* anchored in the primary papers and should not be treated as load-bearing claims. Those belong to the Yellow secondary-color category.
- The chapter's two key infrastructure-log scales — 1998 (Stanford prototype) and 2003 (production cluster) — should be separated visually in prose, not blurred. The cluster scale comes from Barroso 2003; the application scale (24M pages, 53.5GB compressed) comes from Anatomy 1998. Mixing them is the most common chapter-craft error.
