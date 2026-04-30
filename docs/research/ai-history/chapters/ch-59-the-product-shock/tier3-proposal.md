# Chapter 59 — Tier 3 reader-aid proposal

Author: Claude (claude-opus-4-7), 2026-04-30
Reviewer (cross-family): Codex (gpt-5.5)
Spec: `docs/research/ai-history/READER_AIDS.md` Tier 3 (elements 8, 9, 10).

## Element 8 — Inline parenthetical definition

**SKIPPED.** Per the spec, every chapter skips this element until a non-destructive Astro `<Tooltip>` component lands. The Tier 1 *Plain-words glossary* covers research preview, RLHF, MAU, ChatGPT Plus, Bing/Bard, jailbreak/adversarial prompting, and hallucination.

## Element 9 — Pull-quote (`:::note[]` callout)

**PROPOSED-by-concept (Codex, please fetch and verify the verbatim wording).** Candidate primary source: OpenAI, "Introducing ChatGPT," November 30, 2022 (https://openai.com/index/chatgpt/).

The chapter's load-bearing thesis is that the conversational *interface* — not new science — is what shocked the world. The OpenAI launch page says, in its introductory paragraph, that ChatGPT can answer follow-up questions, admit mistakes, challenge incorrect premises, and reject inappropriate requests. The chapter's prose paraphrases this list at line 18 ("ChatGPT could answer follow-up questions, admit mistakes, challenge incorrect premises, and reject inappropriate requests") — adjacency-repetition risk is HIGH if I block-quote that exact sentence again.

A safer candidate is the page's *framing* sentence describing the dialogue interface. Per `sources.md`, the OpenAI ChatGPT page opens with language to the effect of: *"The dialogue format makes it possible for ChatGPT to answer follow-up questions, admit its mistakes, challenge incorrect premises, and reject inappropriate requests."* The chapter prose paraphrases the second half of this sentence but not the first half (the *dialogue-format-makes-it-possible* framing). Block-quoting the full sentence would install OpenAI's own causal claim — that the *format* unlocks the behaviours — at the moment the chapter is making the same argument from the outside.

**Insertion anchor:** immediately after the chapter paragraph beginning "OpenAI's launch page described exactly that surface…" (the paragraph that paraphrases the four behaviours but not the dialogue-format causal claim).

**Tentative annotation (1 sentence, doing new work):** OpenAI's own framing puts the work on the *format* rather than the model — a subtle but load-bearing claim, since it is what lets the chapter argue the shock was packaging, not new science.

**What Codex should do:**
1. Fetch https://openai.com/index/chatgpt/ and locate the verbatim opening sentence about the dialogue format.
2. If the verbatim sentence exists and is ≤30 words, APPROVE with the exact wording captured.
3. If the wording differs from my reconstruction, REVISE with the actual sentence.
4. If the page no longer carries this sentence (post-launch edits), REVIVE with a different verbatim candidate from one of the primary sources in `sources.md` — Microsoft Bing post, Google Bard post, Stack Overflow ban policy post, or Chalkbeat. Each of those carries one or two genuinely quote-worthy sentences.
5. If no candidate clears adjacency-repetition AND verbatim-fidelity bars, REJECT.

**Word budget:** sentence ~25 words + annotation ~30 words ≈ 55 words. Under the ≤60 cap.

## Element 10 — Plain-reading aside

**SKIPPED.** Ch59 is narrative/historical: launch chronology, adoption-metric anchoring, institutional reaction, product-race timeline. No paragraph is *symbolically* dense (no formulas, derivations, or stacked abstract definitions). Plain-reading asides apply only to symbolic density per the spec.

## Summary

| Element | Author proposal | Rationale |
|---|---|---|
| 8 | SKIP | Bit-identity rule (no Tooltip component yet) |
| 9 | PROPOSE-by-concept | OpenAI ChatGPT page dialogue-format opening sentence — chapter paraphrases the four behaviours but not the causal-frame; needs Codex verbatim verification |
| 10 | SKIP | No symbolic density — narrative/historical chapter |

**Awaiting Codex adversarial review.** Be willing to REJECT (if you judge the chapter's "OpenAI's launch page described exactly that surface…" paragraph paraphrases the same content too closely), REVISE (with the exact verbatim wording from the page), or REVIVE (a different verbatim sentence — e.g., from the Stack Overflow ban policy post about "low average correctness" plus "plausible-looking" or from the Microsoft Bing reinventing-search post).
