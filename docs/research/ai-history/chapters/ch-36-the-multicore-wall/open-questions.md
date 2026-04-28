# Open Questions: Chapter 36 — The Multicore Wall

What is still Yellow or Red, and what archival access would help. Each entry names the specific gap, the specific source that would close it, and the chapter scenes affected.

## Q1 — What was Tejas actually targeted at? (4 GHz line target vs sample-level reality)

**Status:** the chapter's Conflict-Notes treats this as a separable two-fact claim (Pentium 4 line target = 4 GHz; cancelled-Tejas sample reality = 2.8 GHz at ~150 W). The legacy prose collapses these into "Intel cancelled its 4 GHz chip," which is real-but-imprecise.

**What would resolve it:** a primary Intel 2003–2004 Pentium 4 roadmap document showing Tejas's *target* clock at production. *AnandTech*'s leaked 2.8 GHz / 150 W figures are sample-level and probably not what Intel intended to ship.

**Where to look:** Intel investor-relations archive (Wayback CDX search on `intel.com/pressroom/archive/releases/2003*` and `2004*`); Intel Q1 2004 and Q2 2004 earnings call transcripts; Otellini IDF 2003/2004 keynote transcripts.

**Affects:** Scenes 1 and 2.

## Q2 — Was Intel's on-record framing in May 2004 honest, or was the thermal reason already understood internally?

**Status:** the chapter currently treats the on-record framing ("single core chips just don't do it for the company anymore," Vance 2004-05-07) and the engineering-history consensus framing (heat, leakage, power density) as two distinct claims, not collapsed.

**What would resolve it:** a primary Intel internal document, Otellini call transcript, or Barrett interview from spring/summer 2004 that names the thermal motive in Intel's own voice.

**Where to look:** the Intel Museum archive at the Robert Noyce Center; the Computer History Museum oral-history collection for Otellini, Barrett, and Justin Rattner (then Intel CTO).

**Affects:** Scene 2.

## Q3 — Exact ship dates for Pentium D and Athlon 64 X2

**Status:** Yellow. Year-level claim ("2005, mainstream x86 dual-core arrives") is Green; specific ship dates (Pentium D 2005-05-26, Athlon 64 X2 2005-05-31, often repeated in tertiary sources) are not anchored to primary press releases.

**What would resolve it:** the original Intel and AMD press releases. Wikipedia references suggest the URLs but Claude's Wayback queries returned no snapshots 2026-04-28.

**Where to look:** Wayback CDX search on `intel.com/pressroom/archive/releases/2005*` and `amd.com/us/press-releases/Pages/*2005*`; the Internet Archive's full Intel pressroom dump; ZDNet/CNET 2005 coverage archives.

**Affects:** Scene 4. The chapter is explicit that this is Yellow; not load-bearing.

## Q4 — Was Pollack's Rule formally documented in a 1999 keynote text, or only in Borkar's later citations?

**Status:** Yellow. The chapter does not currently load-bear on Pollack 1999; it cites Pollack's Rule via Borkar & Chien 2011 (which cites Pollack via Wikipedia, an unsatisfactory chain).

**What would resolve it:** the original MICRO-32 (1999) keynote slides or proceedings text by Fred Pollack.

**Where to look:** the IEEE/ACM MICRO conference archive; the Computer History Museum's Intel-architecture papers.

**Affects:** Scene 1 only if the chapter chooses to elevate Pollack's Rule to a load-bearing claim. Currently it does not.

## Q5 — A primary Borkar 1999 quotation

**Status:** the chapter cites the 1999 paper's existence, date, venue, author, and effect (it was real enough to be cited by Asanovic et al. as evidence of insider acknowledgement) as Green via the secondary-confirmation chain. It does not put a quotation from the 1999 paper in prose.

**What would resolve it:** the IEEE Micro 19(4) issue. The full text is paywalled; Unpaywall confirms `oa_status: closed`.

**Where to look:** institutional library access to IEEE Xplore; or a campus computing-architecture course with a posted reading-list mirror that Wayback has captured. Several university course pages were probed and dead-ended; a more thorough CDX search may surface a snapshot.

**Affects:** Scene 1 (early-warning argument) and Scene 5 (the "Borkar warned, Borkar wrote the retrospective" arc). The chapter's current treatment is honest about the absence of a primary Borkar 1999 quote; the gap analysis should decide whether Yellow-via-secondary-chain is sufficient or whether a verbatim quote is required.

## Q6 — What did Olukotun 1996 actually argue about thermal economics?

**Status:** Yellow. The chapter cites Olukotun et al. 1996 ASPLOS for the existence-and-thesis only. Olukotun's Stanford Hydra group continued working on CMP throughout the late 1990s (Hammond 2000 etc.), and the 1996 paper's specific power-density / die-area argument may already include a recognizable "this will be necessary because of thermal limits" claim that Borkar 1999 then independently restated. If so, the chapter could strengthen the priority story.

**What would resolve it:** the full text of Olukotun et al. 1996 (DOI `10.1145/237090.237140`). ACM open-access mirror returned access-gated HTML when probed.

**Where to look:** institutional library access to the ACM Digital Library; the Stanford Hydra project page (404 in 2026); Olukotun's own Stanford CSL page (also 404 for the canonical asplos96.pdf URL).

**Affects:** Scene 1. The chapter's current treatment is conservative.

## Q7 — Who was the unnamed Intel spokesman in Vance's May 7, 2004 article?

**Status:** Red. The on-record quote — "We are accelerating our dual-core schedule for 2005" — is verbatim per Vance, *The Register*, but the spokesman is not named. Standard Intel media-relations practice in 2004 would route a roadmap-cancellation comment through a senior communications official; a name would let the chapter cite the institutional voice with precision.

**What would resolve it:** a follow-up *Register*, *EE Times*, or *VARBusiness* piece that names Vance's source; or contemporaneous Intel media-relations records.

**Affects:** Scene 2. The chapter currently quotes the spokesman quote verbatim without naming.

## Q8 — Did Intel's 2004 dual-core schedule pull also accelerate the 65 nm Conroe / Core 2 Duo program, or was that a separate decision?

**Status:** Out of scope as currently framed. The chapter narrates the 90 nm Pentium D as the immediate replacement for the cancelled Tejas; the 65 nm Conroe / Core 2 Duo (mid-2006) is the chip that delivered the *thermal* recovery. Whether Conroe was already on the roadmap before May 2004 or accelerated as part of the same decision is a question the chapter does not currently need to answer.

**What would resolve it:** Intel 2003–2004 internal-roadmap documents.

**Affects:** Scene 4 only if the chapter chooses to extend its forward look to mid-2006.

## Q9 — What did the 2004 Intel earnings call attendees actually hear?

**Status:** Red. The Q1 2004 (April) and Q2 2004 (July) Intel earnings calls would include analyst questions about the cancelled Pentium 4 roadmap. Otellini, then COO, would likely have been the executive answering.

**What would resolve it:** SEC filings or Seeking Alpha / TheStreet earnings-call transcripts from April and July 2004.

**Affects:** Scenes 2 and 5. Would let the chapter quote Intel's own corporate voice on the cancellation, not just the May 7 spokesman.

## Q10 — Forward-link discipline

**Status:** the chapter currently restricts its forward references to one-line pointers (Part 7 GPU compute; Ch49 custom silicon). The boundary contract is intentionally tight.

**Open question for the gap-analysis pass:** is one forward-link pointer to Part 7 enough, or does the chapter close more cleanly with two? The current draft takes the conservative one-pointer approach; a reviewer may legitimately argue for a slightly broader forward look.

**Affects:** Scene 5 close.

## What the gap-analysis pass should check first

In rough priority order:

1. **Q5 (primary Borkar 1999 quote).** This is the single most-load-bearing closeable Yellow.
2. **Q1 (Tejas line target).** This affects the boundary contract and the legacy-prose-correction the chapter is making.
3. **Q3 (mainstream ship dates).** Would let Scene 4 expand confidently; not load-bearing but a clean win if available.
4. **Q9 (2004 earnings calls).** Would add an Intel-corporate-voice anchor to Scene 2; high upside if findable.
5. **Q6 (Olukotun 1996 internal arguments).** Would strengthen the priority arc in Scene 1.
6. **Q4, Q7, Q2, Q8, Q10** in roughly that priority.

If the gap-analysis pass cannot close any of Q1, Q5, Q9 to Green — i.e., if the chapter's load-bearing primary anchors remain the ones it has now — the chapter should still draft to its current 3,600–5,100 word estimate without padding, and the verdict should be `READY_TO_DRAFT_WITH_CAP` at 4k–5k rather than `NEEDS_ANCHORS`.
