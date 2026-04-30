# Chapter 64 — Tier 3 reader-aid review (Codex)

Reviewer: gpt-5.5, 2026-04-30
Spec: `docs/research/ai-history/READER_AIDS.md` Tier 3 (elements 8, 9, 10).

## Verdicts

**Element 8: APPROVE SKIP**

Correct. Tier 3 spec says inline parenthetical definitions are skipped on every chapter until a non-destructive tooltip component exists.

**Element 9: REVISE**

Do not approve the proposed wording as-is. It is not verbatim. The Android Developers Blog sentence is:

> Since on-device generative AI models run on devices with less computational power than cloud servers, they are significantly smaller and less generalized than their cloud-based equivalents.

Primary source: Android Developers Blog, "Gemini Nano is now available on Android via experimental access," October 1, 2024, lines 38-39: https://android-developers.googleblog.com/2024/10/gemini-nano-experimental-access-available-on-android.html

Use that full sentence, not "Gemini Nano is…". Keep the annotation shorter to stay under the 60-word cap:

> Google's caveat matters because it names edge AI as a capacity boundary from inside the vendor's own product framing.

Adjacent repetition: acceptable, but barely. The chapter paraphrases the same claim very closely, but it does not quote it verbatim, so this does not trigger the Ch01-style hard rejection. The callout earns its keep only if the annotation is provenance-focused, not another paraphrase.

**Element 10: APPROVE SKIP**

Correct. The candidate paragraphs are technical and numerically loaded, but not symbolically dense in the spec's sense. They contain no formulas, derivations, or stacked abstract definitions. The AFM and LLM-in-a-flash paragraphs are narratively dense explanations of constraints, so a `Plain reading` aside would mostly repeat the prose.

## Summary

| Element | Verdict |
|---|---|
| 8 | APPROVE SKIP |
| 9 | REVISE — use verified verbatim sentence + shorter provenance-focused annotation |
| 10 | APPROVE SKIP |

Tier 3 yield: **1 of 3** (E9 lands per Codex revision; E8 and E10 stay skipped).
