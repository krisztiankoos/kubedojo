# Chapter 71 — Tier 3 reader-aid review (Codex)

Reviewer: gpt-5.5, 2026-04-30

## Element 8 — APPROVE SKIP

The spec requires skipping inline parenthetical definitions until a non-destructive tooltip component exists (`READER_AIDS.md` Tier 3, Element 8). Tier 1 *Plain-words glossary* covers the same job non-destructively.

## Element 9 — REVISE (verified replacement)

Candidate A (NVIDIA 10-Q "foreclosed from China's data-center compute market" framing) is verbatim-verifiable in the SEC filing, but **rejected as proposed** because the chapter paragraph at line 121 of the worktree prose already paraphrases the same beat ("might be foreclosed from China's data-center compute market if no competitive approved product exists"). A callout immediately after would create the adjacent-repetition failure the spec warns about.

**Verified replacement** (same source, different load-bearing sentence):

> Repeated changes in the export control rules are likely to impose compliance burdens on our business and our customers, negatively and materially impacting our business.

**Source anchor:** NVIDIA Form 10-Q, quarter ended July 27, 2025. Risk-factors section, https://www.sec.gov/Archives/edgar/data/1045810/000104581025000209/nvda-20250727.htm. Codex cited this as line 1551 in the SEC filing's source view.

**Annotation:** This turns moving export thresholds into SEC-disclosed operating risk, not just policy background — the moment a U.S. semiconductor leader priced rule volatility into shareholder language.

**Insertion anchor:** Immediately after the chapter paragraph beginning "NVIDIA's public filings made that loop concrete." in `src/content/docs/ai-history/ch-71-the-chip-war.md` — i.e., between the original H20-disclosure paragraph and the chapter's "That filing should not be turned into a NVIDIA monopoly chapter" follow-up.

**Word count:** 30 words quoted + ~28 words annotation ≈ 58 words. Within ≤60 cap.

**Reject B and C** as unnecessary: B (ASML) is also closely paraphrased in the chapter's ASML-press paragraph; C (BIS Federal Register list of military / WMD / surveillance) is paraphrased in the chapter's BIS-2022 paragraph.

## Element 10 — APPROVE SKIP

No paragraph is symbolically dense under the spec's definition. The chapter has acronym density (FDP, EUV, DUV, HBM, CoWoS, SME) and number density ($4.5B / $52.7B / 24 SME / 3 software / 140 Entity / 13.5 nm / 7nm 69% / 17M wafers), but those sit in narrative/regulatory explanation, not in stacked formulas, derivations, or abstract definitions.

## Author independent verification (2026-04-30)

I (Claude, the chapter aid author) independently verified Codex's verbatim sentence by fetching the SEC NVIDIA 10-Q (https://www.sec.gov/Archives/edgar/data/1045810/000104581025000209/nvda-20250727.htm), stripping HTML, and locating the string "Repeated changes in the export control rules are likely to impose compliance burdens on our business and our customers, negatively and materially impacting our business." at character offset 138,323 of the cleaned text — exactly as Codex supplied it. Per `feedback_citation_verify_or_remove.md` and `feedback_gemini_hallucinates_anchors.md`, the verification is recorded so the quote is not promoted on a reviewer's word alone.

## Final yield: 1 of 3 (E9 only)
