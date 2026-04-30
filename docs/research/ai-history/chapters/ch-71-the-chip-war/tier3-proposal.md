# Chapter 71 — Tier 3 reader-aid proposal

Author: Claude (claude-opus-4-7), 2026-04-30
Reviewer (cross-family): Codex (gpt-5.5)
Spec: `docs/research/ai-history/READER_AIDS.md` Tier 3 (elements 8, 9, 10).

## Element 8 — Inline parenthetical definition

**SKIPPED.** Per the spec, every chapter skips this element until a non-destructive Astro `<Tooltip>` component lands. The Tier 1 *Plain-words glossary* covers export controls, FDP, SME, EUV/DUV, HBM, advanced packaging/CoWoS, and the Entity List.

## Element 9 — Pull-quote (`:::note[]` callout)

**PROPOSED-by-concept.** Codex must verify the verbatim sentence against the cited primary source or supply a verified replacement.

The chapter's load-bearing dispute is the policy/product co-evolution loop: a regulator names a threshold, a company designs a product to fit, the threshold moves, and the product becomes controlled. The chapter paraphrases NVIDIA's 10-Q disclosure at line 62 ("NVIDIA said it incurred a $4.5 billion charge and warned that if it could not offer a competitive approved product, it might be foreclosed from China's data-center compute market") but does not block-quote the SEC filing's own language. A pull-quote here installs the company-disclosure voice directly rather than as institutional summary.

### Candidate A (preferred, from NVIDIA Form 10-Q quarter ended Jul 27, 2025)

`sources.md` cites NVIDIA 10-Q web lines 1561–1571 (URL: https://www.sec.gov/Archives/edgar/data/1045810/000104581025000209/nvda-20250727.htm). The verbatim sentence the chapter paraphrases is near lines 1567–1569 — the "foreclosed from China's data-center compute market if no competitive approved product exists" framing.

I do not have the verbatim wording in the contract files. **Codex, please fetch the NVIDIA 10-Q (SEC URL above) and either supply a verbatim sentence ≤40 words capturing the H20-license / $4.5B / China-foreclosure stake, or REJECT if no single sentence carries that weight cleanly.** A good candidate would be a sentence that contains the load-bearing risk language ("foreclosed", "if we are unable to offer competitive products", or similar) — i.e., the part of the disclosure that is *not* paraphrased adjacently in the chapter prose.

**Insertion anchor (if approved):** immediately after the chapter paragraph beginning "NVIDIA's public filings made that loop concrete." (the paragraph ending "…it might be foreclosed from China's data-center compute market if no competitive approved product exists.").

**Annotation (1 sentence, doing new work):** This sentence is the moment a U.S. semiconductor leader translated an export-control threshold into SEC-disclosed market-foreclosure risk — the policy/product loop priced into shareholder language.

### Candidate B (alternative, from ASML 2024 Annual Report)

`sources.md` cites ASML annual local lines 806–820 (PDF: https://ourbrand.asml.com/m/1d935e9653a216d7/original/2024-Annual-Report-based-on-IFRS.pdf). The chapter at line 76 paraphrases the EUV-uniqueness claim ("ASML is the world's only manufacturer of EUV lithography systems") — this risks adjacent-repetition rejection if Codex finds the verbatim sentence is essentially the chapter's wording. The stronger candidate inside the same source range is the EUV-vs-DUV comparison sentence at lines 806–820 ("EUV uses 13.5 nm light, prints smallest/highest-density features, simplifies advanced manufacturing versus DUV multiple patterning") — but again the chapter paraphrases this almost verbatim.

A better Candidate B target inside ASML materials is the **December 2024 ASML press release** (https://www.asml.com/en/news/press-releases/2024/asml-expects-impact-of-updated-export-restrictions-to-fall-within-outlook-for-2025) at web lines 190–194, which contains the company's own outlook on DUV-immersion exposure if Dutch authorities make similar assessments. The chapter at line 88 paraphrases this but does not block-quote the company's own outlook language. **Codex, if A fails (NVIDIA 10-Q has no clean ≤40-word sentence), please fetch the ASML Dec 2024 press release and supply a verbatim outlook sentence.**

**Insertion anchor (if approved):** immediately after the chapter paragraph beginning "ASML's own December 2024 statement showed the business side."

**Annotation (1 sentence, doing new work):** This is the moment lithography's sole EUV vendor translated U.S. and allied export rules into next-year revenue guidance — the supply chain learning to forecast policy.

### Candidate C (safe fallback, from BIS Oct 2022 Federal Register, 87 FR 62186)

`sources.md` cites Federal Register lines 418–428 (URL: https://www.federalregister.gov/documents/2022/10/13/2022-21658/implementation-of-additional-export-controls-certain-advanced-computing-and-semiconductor) — the passage that explicitly links advanced computing ICs, supercomputers, AI, PRC military modernization, WMD design/testing, and surveillance. The chapter at line 16 paraphrases this list directly. **High adjacent-repetition risk** — the chapter's paraphrase is almost verbatim. Codex should REJECT C unless a different load-bearing sentence in the same Federal Register section can be quoted that the chapter does *not* already paraphrase.

### Yield decision rule

- If A verifies cleanly (≤40 words, ≤60 words combined with annotation): APPROVE A, REJECT B and C.
- If A is too long / not single-sentenced but B verifies: APPROVE B.
- If neither A nor B is verifiable: APPROVE C only if Codex finds a non-paraphrased BIS sentence; otherwise SKIP Element 9.

## Element 10 — Plain-reading aside

**SKIPPED.** Ch71's prose is narrative / regulatory / supply-chain history. The chapter contains technical vocabulary (FDP, EUV, DUV, HBM, CoWoS, 4nm/3nm/2nm, $4.5B, $52.7B, 100/24/3/140, 7nm/69%, 17M wafers, 13.5nm) but those numbers and acronyms sit inside ordinary explanatory prose. No paragraph stacks formulas, derivations, or abstract definitions. The Tier 1 glossary covers the acronym-density problem non-destructively.

## Summary

| Element | Author proposal | Rationale |
|---|---|---|
| 8 | SKIP | Bit-identity rule; Tier 1 glossary covers the same job |
| 9 | PROPOSE (A preferred, B alternative, C high-risk fallback) | Codex must fetch NVIDIA 10-Q / ASML press release / BIS FR and verify verbatim or supply replacement |
| 10 | SKIP | No symbolic density |

**Awaiting Codex adversarial review.** Be willing to REJECT (if every candidate is paraphrased adjacently in chapter prose), REVISE (different verbatim sentence from the same source), or REVIVE (different primary source — e.g., BIS Dec 2024 press release on HBM/SME/software-tools, NIST CHIPS fact sheet, TSMC 2024 annual report on Taiwan-vs-Arizona concentration, or CSET MOFCOM translation on materials counter-controls).
