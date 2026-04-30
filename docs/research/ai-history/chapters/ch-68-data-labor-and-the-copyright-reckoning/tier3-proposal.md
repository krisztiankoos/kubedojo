# Chapter 68 — Tier 3 reader-aid proposal

Author: Claude (claude-opus-4-7), 2026-04-30
Reviewer (cross-family): Codex (gpt-5.5)
Spec: `docs/research/ai-history/READER_AIDS.md` Tier 3 (elements 8, 9, 10).

## Element 8 — Inline parenthetical definition

**SKIPPED.** Per the spec, every chapter skips this element until a non-destructive Astro `<Tooltip>` component lands. The Tier 1 *Plain-words glossary* (RLHF, Common Crawl, The Pile/Books3, LAION-5B, fair use, motion to dismiss, robots.txt/GPTBot) covers the same job non-destructively.

## Element 9 — Pull-quote (`:::note[]` callout)

**PROPOSED-BY-CONCEPT.** The chapter's strongest legal anchor is the June 23, 2025 Bartz v. Anthropic fair-use order (Alsup, J., N.D. Cal.), which the prose treats as the load-bearing court record. The order itself is the chapter's source of the "split" between training use, purchased print-to-digital scanning, and pirated central-library copies. The chapter paraphrases this split (lines beginning "In that order, training copies were treated as fair use…") but does *not* block-quote any operative sentence from the order.

**Candidate insertion anchor:** immediately *after* the chapter paragraph beginning "In June 2025, the Bartz v. Anthropic order drew distinctions that should shape how the whole chapter is read…" — i.e., the paragraph that paraphrases the split.

**Source target (Codex must fetch + confirm verbatim):** *Bartz et al. v. Anthropic PBC*, Order on Fair Use, N.D. Cal., June 23, 2025. Anchors per `sources.md`: lines 42-51 (issue framing), lines 1800-1844 (the operative split), lines 1860-1865 (summary-judgment grants/denials). CourtListener PDF: https://storage.courtlistener.com/recap/gov.uscourts.cand.434709/gov.uscourts.cand.434709.231.0_4.pdf

**Why this element:**
- It is the chapter's single most narrowly cited legal anchor and the only one that gives the whole chapter its anti-slogan ethic ("not 'training is legal,' not 'training is illegal'").
- The chapter paraphrases but does not block-quote, so adjacent-repetition risk is low.
- A direct sentence from Alsup's order would put the reader inside the actual judicial language, not the chapter's narrative voice.

**Proposed annotation (≤1 sentence, doing new work):** Note Alsup's order is *one* district-court ruling on a narrow procedural posture and a split fact pattern — the chapter's wider claim that "data became infrastructure someone could block, price, license, or sue over" rests on that narrowness, not on a sweeping merits answer.

**Word budget:** verbatim-dependent. Aim for ≤40 words quoted + ~25 words annotation ≤ 60-word cap. Codex should REVISE or trim if the chosen verbatim sentence runs longer.

**Codex verification request:** Please fetch the order PDF and:
1. Either confirm a verbatim sentence on the training-vs-piracy split that fits the ≤60-word combined cap, **or**
2. REVIVE with a different verbatim from a different primary source — the strongest alternatives are:
   - **OpenAI, "OpenAI and journalism" (Jan. 8, 2024)** — a verbatim sentence on training as fair use or on the regurgitation framing. The chapter paraphrases OpenAI's four-point position; a primary-source sentence would balance the Bartz/court voice with the OpenAI/company voice. URL: https://openai.com/index/openai-and-journalism/ (sources.md anchors lines 43-47, 50-61, 64-75).
   - **Getty Images statement (Jan. 17, 2023)** — a verbatim sentence stating Getty licenses content for AI training. URL: https://newsroom.gettyimages.com/en/getty-images/getty-images-statement (sources.md anchors lines 13-17).
   - **NYT v. OpenAI motion-to-dismiss opinion (Stein, J., Apr. 4, 2025)** — a verbatim sentence on the assumed-true posture or on which DMCA claims survived/were dismissed. URL: https://cdn.openai.com/pdf/gov.uscourts.nysd.612697.514.0_1.pdf (sources.md anchors lines 101-129, 131-133, 1548-1554).
3. Or REJECT entirely if no candidate sentence is genuinely quote-worthy without paraphrase-of-paraphrase risk.

## Element 10 — Plain-reading aside

**SKIPPED.** Ch68 is narrative/historical: labor reporting, dataset chronology, complaint allegations, court orders, and licensing announcements. There are no symbolically dense paragraphs (no formulas, no derivations, no stacked abstract definitions). The closest candidate — the Bartz split paragraph — is *legally* dense but not symbolically dense; the spec reserves Plain-reading asides for symbolic density (formulas, derivations, definitions stacked), not narrative or legal density. The Tier 1 glossary already explains "fair use" and "motion to dismiss" in plain words.

## Summary

| Element | Author proposal | Rationale |
|---|---|---|
| 8 | SKIP | Bit-identity rule (every chapter, until Astro `<Tooltip>` lands) |
| 9 | PROPOSE-BY-CONCEPT | Bartz/Anthropic split language is the chapter's load-bearing legal anchor and is paraphrased, not quoted; Codex to fetch + confirm verbatim or REVIVE from OpenAI / Getty / NYT-opinion |
| 10 | SKIP | No symbolic density; chapter is narrative/historical/legal, not formula-driven |

**Awaiting Codex adversarial review.** Be willing to REJECT (if no verbatim sentence in the Bartz order both fits the cap and does work the prose has not done), REVISE (annotation length), or REVIVE (a different verbatim sentence from OpenAI's "OpenAI and journalism" post, Getty's January 2023 statement, or the NYT/OpenAI motion-to-dismiss opinion). For Element 9 you MUST fetch the cited primary source(s) and either confirm verbatim or supply a verified replacement.
