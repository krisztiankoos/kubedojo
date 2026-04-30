# Chapter 62 — Tier 3 reader-aid review (Codex)

Reviewer: gpt-5.5, 2026-04-30

## Verdicts

**Element 8: APPROVE skip.** The Tier 3 spec explicitly says inline parenthetical definitions are skipped until a non-destructive Tooltip component exists. Tier 1 glossary coverage is the right substitute.

**Element 9: REVIVE.** Codex fetched the OpenAI primary source ("Video generation models as world simulators", https://openai.com/index/video-generation-models-as-world-simulators/) and confirmed the proposed sentence was not verbatim — it blended/paraphrased source language. The submitted wording is rejected. Codex supplied a verified replacement from line 42 of the same primary source:

> Whereas LLMs have text tokens, Sora has visual patches.

Insertion anchor: after the paragraph beginning "The patch idea is important because video does not fit neatly into the same frame as text or a single image."

Primary source: OpenAI, "Video generation models as world simulators," February 15, 2024, line 42; limitation context at line 139.

Codex annotation suggestion (1 sentence, doing new work): "This is the source's tokenizer analogy; it frames patches as a representation choice, not proof of stable physics or causal continuity."

Word budget (Codex measured): ~28 words total, well under the ≤60 cap.

**Element 10: APPROVE skip.** Chapter 62 has technical explanation, but not symbolic density. The Sora patches, GPT-4o latency, and three-model voice pipeline passages are narratively/expositorily dense, not formulas, derivations, or stacked abstract definitions. A `Plain reading` aside would repeat prose already written for non-specialists.

## Tier 3 yield

| Element | Author | Reviewer | Landed |
|---|---|---|---|
| 8 | SKIP | APPROVE skip | no |
| 9 | PROPOSE (paraphrased candidate) | REVIVE (verified verbatim replacement) | yes |
| 10 | SKIP | APPROVE skip | no |

**1 of 3 lands** (E9 with the Codex-revived verbatim sentence).
