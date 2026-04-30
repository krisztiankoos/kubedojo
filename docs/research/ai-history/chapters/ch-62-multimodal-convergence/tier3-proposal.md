# Chapter 62 — Tier 3 reader-aid proposal

Author: Claude (claude-opus-4-7), 2026-04-30
Reviewer (cross-family): Codex (gpt-5.5)
Spec: `docs/research/ai-history/READER_AIDS.md` Tier 3 (elements 8, 9, 10).

## Element 8 — Inline parenthetical definition

**SKIPPED.** Per the spec, this element is skipped on every chapter until a non-destructive Astro `<Tooltip>` component lands. The Tier 1 *Plain-words glossary* covers the same job non-destructively for "multimodal model", "interleaved input", "native multimodality", "spacetime patches", "three-model voice pipeline", and "image-borne jailbreak".

## Element 9 — Pull-quote (`:::note[]` callout)

**PROPOSED.** Candidate sentence (OpenAI, "Video generation models as world simulators," February 15, 2024 — primary anchor in `sources.md`, lines 33–40 of the cited page):

> Sora is a text-conditional diffusion model … capable of generating videos and images spanning diverse durations, aspect ratios and resolutions, up to a full minute of high definition video.

**Insertion anchor:** immediately after the chapter paragraph beginning "Sora moved the public imagination there." (the paragraph that paraphrases this exact claim as "Sora was presented as capable of generating up to one minute of high-fidelity video" and "text-conditional diffusion model trained on videos and images, using spacetime patches of video and image latent codes").

**Rationale:**
- This sentence from the OpenAI world-simulators page is the precise scope statement that the chapter paraphrases. Block-quoting it installs the source's own framing — "diverse durations, aspect ratios and resolutions" plus "up to a full minute of high definition video" — without forcing the chapter to lean on those exact phrases in its prose.
- The annotation will do new work by naming what the quote *does not* say: it does not claim physical understanding, robust world modelling, or arbitrary length. The chapter's later paragraphs lean on Sora's own limitation list; this callout makes the specification half of the same page visible.
- Adjacent-repetition risk is moderate. The chapter says "up to one minute of high-fidelity video"; the source says "up to a full minute of high definition video". Codex should evaluate whether that is paraphrase-of-key-claim repetition (REJECT) or a justified verbatim anchor (APPROVE).
- **Verification status: PROPOSED-by-concept.** The candidate sentence above is reconstructed from the `sources.md` description of the page (Green-verified by Codex on 2026-04-28, lines 33–40). I have not re-fetched the page in this session. Codex must `curl -s https://openai.com/index/video-generation-models-as-world-simulators/` (or equivalent), confirm the verbatim wording, and either APPROVE the exact sentence or REVIVE with a confirmed alternative from the same page.

**Annotation (1 sentence, doing new work):** The claim names what Sora generates (variable-shape, up to a minute) but is silent on what it does not — physical correctness, object-state persistence, and causal continuity, all of which the same page lists later as explicit simulator limitations.

**Word budget:** ~30 words quoted + ~38 words annotation ≈ 68 words. Over the ≤60 cap. Codex should REVISE annotation length if landing.

## Element 10 — Plain-reading aside (`:::tip[Plain reading]`)

**SKIPPED.** Ch62 is narrative/historical: research lineage (CLIP → Flamingo), product launches (GPT-4V, Gemini, GPT-4o), and deployment-safety framing (Sora System Card). The most "technical" passages — spacetime patches, contrastive image-text training, end-to-end audio with 232 ms / 320 ms latency, three-model voice pipeline — are *narratively* dense, not *symbolically* dense. There are no formula derivations, no stacked abstract definitions, no proof steps. A plain-reading aside on top of these paragraphs would only paraphrase prose that is already written for non-specialists.

## Summary

| Element | Author proposal | Rationale |
|---|---|---|
| 8 | SKIP | Bit-identity rule; Tier 1 glossary covers the same job |
| 9 | PROPOSE (verification required) | Sora world-simulators scope sentence; chapter paraphrases close enough that Codex may justifiably REJECT or REVISE; verbatim wording must be confirmed from the source page |
| 10 | SKIP | No symbolically dense paragraphs — Ch62 is narrative/historical |

**Awaiting Codex adversarial review.** I deliberately surfaced the adjacent-repetition risk and the not-yet-re-verified verbatim wording. Codex should be willing to REJECT (paraphrase too close), REVISE annotation length, or REVIVE a different sentence from the same primary spine (e.g., the GPT-4o System Card "232 ms / 320 ms" latency sentence, the Gemini report's joint-training claim, or the GPT-4V System Card medical-limitation sentence).
