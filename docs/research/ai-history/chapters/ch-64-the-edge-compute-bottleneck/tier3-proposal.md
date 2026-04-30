# Chapter 64 — Tier 3 reader-aid proposal

Author: Claude (claude-opus-4-7), 2026-04-30
Reviewer (cross-family): Codex (gpt-5.5)
Spec: `docs/research/ai-history/READER_AIDS.md` Tier 3 (elements 8, 9, 10).

## Element 8 — Inline parenthetical definition

**SKIPPED.** Per the spec, every chapter skips this element until a non-destructive Astro `<Tooltip>` component lands. The Tier 1 *Plain-words glossary* covers Neural Engine/NPU, depthwise separable convolution, GQA, quantization (bits-per-weight), KV cache, AICore, and Private Cloud Compute non-destructively.

## Element 9 — Pull-quote (`:::note[]` callout)

**PROPOSED.** Candidate sentence (Android Developers Blog, "Gemini Nano is now available on Android via experimental access," October 2024, lines 38–39 per `sources.md`):

> Gemini Nano is significantly smaller and less generalized than cloud equivalents.

(Phrasing per the chapter's paraphrase and contract anchor; contract notes the verbatim claim is "smaller and less generalized than cloud equivalents" with "significantly" optional. **Codex must fetch the Android blog and confirm the verbatim form** — if "significantly" is not present, drop it; if Google's wording differs, REVIVE with the verified verbatim.)

**Insertion anchor:** immediately after the chapter paragraph beginning "The Android developer blog made the trade-off more explicit." (the paragraph that paraphrases this exact claim — "Gemini Nano was described as smaller and less generalized than cloud equivalents" — without block-quoting Google's voice).

**Rationale:**
- The sentence is the load-bearing honest center of the entire chapter. The chapter's thesis — that on-device AI is *not* a smaller cloud, that the edge is a different machine with different physics — depends on this Google-authored admission. Promoting Google's own product blog statement to a callout converts the chapter's argument from "the author claims" to "the vendor itself acknowledges."
- The chapter paraphrases the sentence ("Gemini Nano was described as smaller and less generalized than cloud equivalents") rather than block-quoting it. Adjacent-repetition risk is low: the surrounding paragraph is summary commentary, not block-quote.
- The sentence comes from a first-party vendor blog, which is the most direct source available; an independent benchmark would actually be a *weaker* anchor for this kind of capacity claim, since the claim is product framing, not measurement.

**Annotation (1 sentence, doing new work):** This is a vendor-authored capacity caveat, not an external benchmark — the historical weight comes from Google itself naming the limit, which is what makes "edge AI as routing discipline" a vendor-acknowledged frame rather than an outside critique.

**Word budget:** 9 quoted words (or 10 with "significantly") + ~46 words annotation ≈ 55–56 words. Within the ≤60 cap. Codex should REVISE annotation length only if the verified verbatim from the blog runs longer.

## Element 10 — Plain-reading aside

**SKIPPED.** Ch64's prose is conceptual and narrative throughout. The chapter does discuss numerical specifications — ~3B parameters, GQA, 3.5 vs 3.7 bits per weight, KV cache, 10B-parameter Qualcomm claim, 20 tokens/sec for 7B Llama 2, "twice DRAM size with 4-5x CPU and 20-25x GPU speedups" — but these appear inside narrative sentences, not as formulas, derivations, or stacked abstract definitions. The two paragraphs closest to symbolic density are:

- The AFM-on-device paragraph ("AFM-on-device was about 3B parameters. It used grouped-query attention to reduce the KV-cache footprint…") — but this is a list of design choices in narrative form, not a derivation.
- The LLM-in-a-flash paragraph ("Alizadeh and collaborators described running language models that exceed available DRAM…") — but this is a result claim with one ratio, not a memory-hierarchy formula.

Neither paragraph is symbolically dense in the spec's sense. Element 10 applies only to formula/derivation/stacked-definition density. Codex may REVIVE if it judges either paragraph genuinely symbolic; otherwise SKIP.

## Summary

| Element | Author proposal | Rationale |
|---|---|---|
| 8 | SKIP | Bit-identity rule (spec-default skip) |
| 9 | PROPOSE | Android blog "smaller and less generalized than cloud equivalents" — vendor-authored capacity caveat at the chapter's thesis center; chapter paraphrases but does not block-quote |
| 10 | SKIP | No symbolic density — numerical specs appear in narrative form, not as formulas or derivations |

**Awaiting Codex adversarial review.** Specifically: (a) confirm the verbatim form of the Android blog sentence by fetching the URL listed in `sources.md` (https://android-developers.googleblog.com/2024/10/gemini-nano-experimental-access-available-on-android.html); (b) judge whether the chapter's paraphrase paragraph already stands too close to the verbatim form to warrant adjacent-repetition skip per Ch01 prototype precedent; (c) if rejecting, suggest a different verbatim sentence from the chapter's primary sources (e.g., MobileNets abstract on mobile/embedded design, Apple Newsroom "larger-than-pocket models" phrase, LLM-in-a-flash abstract on "models exceeding available DRAM").
