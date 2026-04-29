# Tier 3 Proposal: Chapter 31 — Reinforcement Learning Roots

Author: Claude (Sonnet 4.6)
Date: 2026-04-30
Status: PROPOSED — awaiting adversarial cross-family review (Codex)

---

## Element 1: Pull-quote

**Status: PROPOSED**

**Candidate sentence** (from "Delayed Rewards Become Q Values"):

> A machine faces a position. It cannot search forever. It estimates value. It acts. Later evidence changes the estimate.

**Insertion anchor:** After the paragraph ending "…it was a judgment revised through consequences." (end of the Samuel/checkers scene, before the `## The Pole-Balancing Critic` heading is NOT where this appears — the sentence is at the close of the "Bellman and Samuel Give the Shape" section, in the paragraph ending "…a judgment revised through consequences.")

Correct anchor paragraph ends: "Checkers therefore belongs in the reinforcement-learning ancestry even though it / was not yet modern reinforcement learning. A later RL textbook would use / different notation, but the practical outline was already visible. Search had to / stop before the end of the game. A value estimate had to stand in for the / future. The value estimate could be improved by play. The improvement was not a / label attached by a human teacher to every position; it was a judgment revised / through consequences." — then the five-sentence summary paragraph follows.

**Proposed callout:**

```
:::note
> A machine faces a position. It cannot search forever. It estimates value. It acts. Later evidence changes the estimate.

The five-sentence cadence captures what separates reinforcement learning from supervised learning at its root: no teacher labels the position — consequence does, and only afterward.
:::
```

**Rationale:** The five-sentence paragraph is structurally distinct and load-bearing — it distills the Samuel-to-RL bridge that the whole scene builds toward. It is not already quoted in surrounding prose (the prose leads *up to* it; the paragraph *is* the landing). The annotation does new work: it names why this sentence is historiographically significant, not merely what it says.

**Adversary check requested:** Is this pull-quote genuinely quote-worthy, or does the surrounding prose render the callout redundant? Is the annotation doing new work, or restating what the paragraph already implies?

---

## Element 2: Plain reading aside — TD learning paragraph

**Status: SKIPPED**

The temporal-difference section is conceptually dense but uses a weather-forecaster analogy that already unpacks the idea in accessible language. Adding a `:::tip[Plain reading]` aside would restate what the surrounding prose already makes clear. The chapter is narratively dense in places, but not *symbolically* dense (no stacked mathematical formulas or abstract definitions requiring a second pass). The glossary entry for "Temporal difference (TD) learning" covers the non-specialist doorway.

---

## Element 3: Plain reading aside — Q-value/convergence theorem paragraph

**Status: SKIPPED**

The convergence-conditions paragraph ("The theorem did not say Q-learning would solve every real environment…") is already structured as a deliberate series of bounded claims, each one a plain-language hedge. A `:::tip[Plain reading]` aside would only repeat the hedging the prose already performs. Not symbolically dense enough to qualify.

---

## Summary table

| Element | Type | Decision | Rationale |
|---|---|---|---|
| Five-sentence Samuel bridge | Pull-quote | PROPOSED | Structurally isolated, load-bearing, not already quoted; annotation does new work |
| TD weather-forecaster paragraph | Plain reading aside | SKIPPED | Analogy already unpacks gist; aside would repeat |
| Q-convergence bounds paragraph | Plain reading aside | SKIPPED | Prose already structured as deliberate hedges; not symbolically dense |
