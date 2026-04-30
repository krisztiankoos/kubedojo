# Tier 3 — orchestrator override on Element 9 (pull-quote)

Author response to Codex `tier3-review.md` REVIVE verdict on Element 9.

## Codex's verdict

Codex revived Element 9 with a proposed pull-quote: *"Amazon Mechanical Turk does this, providing a web services API for computers to integrate Artificial Artificial Intelligence directly into their processing."* — claimed Green anchor: AWS launch announcement, sources.md G9.

## Override: SKIP

Two grounds:

1. **Adjacent-repetition fails the reader-experience test.** Chapter prose, line 71, reads: *"Amazon framed this service as providing a web-services API for computers to integrate 'Artificial Artificial Intelligence' directly into their processing."* The Codex pull-quote candidate differs from this prose sentence only cosmetically (subject "Amazon Mechanical Turk does this" vs. paraphrased "Amazon framed this service"; un-hyphenated "web services" vs. "web-services"; unquoted vs. quoted "Artificial Artificial Intelligence"). The substance is identical. A pull-quote callout immediately after this prose paragraph would put the same sentence in front of the reader twice. The READER_AIDS.md spec criterion (b) — "the prose paragraph already quotes the sentence verbatim" — should be read as a *reader-experience* test, not a literal verbatim test. The Part 5 batch (2026-04-30 night-2) landed 0 of 8 pull-quotes precisely because the conservative reading of (b) protected against filler.

2. **Codex's claimed verbatim wording does not match sources.md G9.** The G9 row in `sources.md` records the AWS announcement claim as: *"AWS said MTurk provided a web-services API for computers to integrate 'Artificial Artificial Intelligence' into their processing."* — the chapter prose paraphrases this nearly word-for-word. Codex's pull-quote candidate is a different sentence opener ("Amazon Mechanical Turk does this, providing…"), which is not anchored at line-level in `sources.md` and may be a Codex paraphrase or hallucination of the AWS announcement body. Per the `feedback_gemini_hallucinates_anchors.md` precedent (which applies to any model, not just Gemini), unanchored wording should not promote Yellow → Green. Without an authoritative quotation of the AWS launch page body that exactly matches Codex's candidate sentence, the pull-quote anchor is too soft to justify the marginal adjacent-repetition risk.

## Disposition applied

- Element 8 (tooltip): CONFIRM SKIP — agree with both author and Codex.
- Element 9 (pull-quote): **SKIP — orchestrator overrides Codex REVIVE.** Reasoning above.
- Element 10 (plain-reading asides): CONFIRM SKIP — agree with both author and Codex.

**0 of 3 Tier 3 elements landed.** This is the same outcome as the author's original proposal, but documented with the Codex review chain intact.

## Process note

The Tier 3 workflow gives the cross-family reviewer authority to revive SKIPped candidates. Orchestrator-level overrides should remain rare. The bar applied here: Codex's revive (a) failed the reader-experience adjacent-repetition test, and (b) cited an anchor whose verbatim wording is not in `sources.md`. Either ground alone might not justify override; both together do.
