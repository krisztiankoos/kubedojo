# Chapter 63 — Tier 3 reader-aid proposal

Author: Claude (claude-opus-4-7), 2026-04-30
Reviewer (cross-family): Codex (gpt-5.5)
Spec: `docs/research/ai-history/READER_AIDS.md` Tier 3 (elements 8, 9, 10).

## Element 8 — Inline parenthetical definition

**SKIPPED.** Per the spec, every chapter skips this element until a non-destructive Astro `<Tooltip>` component lands. The Tier 1 *Plain-words glossary* covers autoregressive generation, KV cache, iteration-level scheduling, PagedAttention, TTFT/TPOT, goodput, and speculative decoding/sampling.

## Element 9 — Pull-quote (`:::note[]` callout)

**PROPOSED-by-concept (Codex, please fetch and verify the verbatim wording).** The chapter has several plausible primary-source pull-quotes; my preferred candidate is the **DistServe (Zhong et al., OSDI 2024) goodput-framing sentence** because the chapter paraphrases the goodput argument heavily (lines 88, 90, "the system is paid, in effect, for timely work") but never block-quotes the paper's own definition.

### Candidate A (preferred): DistServe goodput definition

**Primary source:** Yinmin Zhong et al., "DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving," OSDI 2024. PDF: <https://www.usenix.org/system/files/osdi24-zhong-yinmin.pdf>.

**Conceptual content** (Codex must fetch and supply verbatim): the abstract / Section 1 sentence that establishes (a) prefill and decoding are colocated/batched in existing systems, (b) this causes interference and resource coupling, and (c) DistServe disaggregates the two phases for *goodput* under SLOs. The chapter's prose paraphrases all three clauses at line 86 ("Zhong and collaborators argued that colocating prefill and decoding on the same GPUs can create interference and resource coupling…") but never quotes the paper.

**Insertion anchor:** immediately after the chapter paragraph beginning "DistServe separated the phases onto different GPUs and optimized for goodput under service-level objectives…" (the paragraph that reports the 7.4x / 12.6x numbers but not the verbatim framing sentence).

**Tentative annotation (1 sentence, doing new work):** The paper's own framing makes "goodput" — not throughput — the load-bearing economic metric, which is why disaggregating prefill from decode counts as an architecture change rather than a tuning choice.

### Candidate B (fallback): FlashAttention IO-awareness sentence

**Primary source:** Tri Dao et al., "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness," arXiv:2205.14135. PDF: <https://arxiv.org/pdf/2205.14135>.

**Conceptual content** (Codex must fetch and supply verbatim): the abstract sentence (or the page 1/2 statement) asserting that Transformers are slow and memory-hungry on long sequences and that FlashAttention reduces reads/writes between HBM and SRAM to get wall-clock speedups *without approximating* attention.

**Insertion anchor:** immediately after the chapter paragraph beginning "FlashAttention showed why attention performance was not only about arithmetic…" (line 34) — the chapter paraphrases the IO-awareness claim but does not block-quote the paper.

**Tentative annotation:** Note that the speedup is on *exact* attention — the IO-aware redesign costs no approximation, which is why the result transferred to production serving rather than staying a research curiosity.

### Candidate C (alternative fallback): PagedAttention KV-cache framing

**Primary source:** Woosuk Kwon et al., "Efficient Memory Management for Large Language Model Serving with PagedAttention," SOSP 2023 / arXiv:2309.06180.

**Risk:** the chapter line 48 paraphrases the abstract closely ("Kwon and collaborators described KV cache memory as huge, dynamic, and prone to waste through fragmentation and duplication"). Adjacency-repetition risk is HIGH unless Codex finds a sentence on a *different* facet (e.g., the per-request KV cache "10x more expensive than a traditional keyword query" framing, but `sources.md` explicitly flags that as Yellow).

### What Codex should do

1. Fetch the DistServe PDF and locate the verbatim sentence(s) closest to the conceptual content above for **Candidate A**. If a single ≤30-word verbatim sentence captures the goodput-framing claim, APPROVE Candidate A with that wording.
2. If Candidate A's wording is too long or splits across sentences, REVISE with a tighter primary-source sentence (e.g., from Section 2 or the Introduction) that still does the framing work.
3. If Candidate A is fully covered in the chapter's surrounding prose (adjacency-repetition risk too high), REJECT Candidate A and substitute **Candidate B** (FlashAttention IO-awareness).
4. If both A and B fail adjacency-repetition or fidelity bars, try **Candidate C** with care to pick a *different* facet from what line 48 paraphrases.
5. If no candidate clears the bars, REJECT the element entirely. Per the Ch01 prototype calibration, refusing the pull-quote is a legitimate outcome.

**Word budget:** sentence ~25–30 words + annotation ~25–30 words ≈ ≤60 words.

## Element 10 — Plain-reading aside (`:::tip[Plain reading]`)

**PROPOSED.** Ch63 has one paragraph that is *symbolically* dense in the spec's sense — not formula-dense, but **stacked-abstract-definitions** dense, which the spec explicitly admits as a qualifying form.

**Target paragraph** (chapter, currently around line 16 of the original prose):

> That loop turns latency into a compound problem. There is time to first token, the delay before a user sees the answer begin. There is time per output token, the rhythm at which the answer continues. There is throughput, the number of requests or tokens a serving system can handle. There is utilization, the fraction of expensive accelerator capacity doing useful work. There is goodput, the useful work completed while meeting the service-level objective rather than merely producing tokens too late to matter.

**Why this qualifies as symbolically dense:** the paragraph stacks five distinct abstract performance definitions (TTFT, TPOT, throughput, utilization, goodput) in five consecutive sentences. The reader hits five novel terms in roughly fifty words; each term will recur load-bearingly later in the chapter (Orca scene, vLLM scene, DistServe scene). A first-time reader who does not internalise these now will lose the rest of the chapter. This is exactly the spec's "abstract definitions stacked" case.

**Insertion anchor:** immediately after that paragraph (before "These quantities pull against one another…").

**Proposed aside (3 sentences):**

```
:::tip[Plain reading]
Five definitions are stacked in one paragraph, and the rest of the chapter leans on all of them: TTFT (how long until the first word appears), TPOT (how fast subsequent words stream), throughput (tokens or requests per second across the system), utilization (fraction of GPU capacity actually doing work), and goodput (work that finishes within the user's SLO and therefore counts). Goodput is the load-bearing one — Orca, vLLM, and DistServe each restructure the serving stack to lift goodput rather than raw throughput. When the chapter later reports a paper's "Nx throughput improvement," read it as "Nx more *goodput*-shaped throughput in that paper's setup," not as a universal speedup.
:::
```

**Word count:** ~115 words across 3 sentences. The spec allows 1–3 sentences; this proposal sits at the upper edge. If Codex judges this verbose, REVISE to ~2 sentences focused on the goodput-vs-throughput distinction.

**Why this aside does new work:** the chapter paragraph defines each term but does *not* tell the reader (a) which one is load-bearing, (b) how to read later "Nx improvement" claims through the goodput lens, or (c) why the field eventually converged on goodput rather than throughput. The aside installs the meta-frame the rest of the chapter relies on.

**Codex check:** REJECT if you judge the surrounding prose already does this meta-framing work, or if the paragraph is narratively dense rather than symbolically dense (i.e., if reading it feels like history-of-people rather than abstract-vocabulary-loading). REVISE the wording or trim to 2 sentences if it is too verbose. APPROVE only if the aside genuinely loads the goodput frame the rest of the chapter assumes.

## Summary

| Element | Author proposal | Rationale |
|---|---|---|
| 8 | SKIP | Bit-identity rule (no Tooltip component yet) |
| 9 | PROPOSE-by-concept | DistServe goodput framing (preferred); FlashAttention IO-awareness (fallback); PagedAttention KV-cache (alt fallback) — Codex must verify verbatim |
| 10 | PROPOSE | Stacked-abstract-definitions paragraph (TTFT / TPOT / throughput / utilization / goodput); rest of chapter depends on these terms |

**Awaiting Codex adversarial review.** Be willing to REJECT either or both elements. The Ch01 prototype's calibration (2 of 5 candidates landing) is the explicit benchmark — Tier 3 is the place to refuse.
