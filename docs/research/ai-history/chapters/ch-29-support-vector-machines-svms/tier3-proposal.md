# Tier 3 Proposal — Chapter 29: Support Vector Machines

Author: Claude (Sonnet 4.6)
Date: 2026-04-30
Status: PROPOSED — awaiting adversarial review by Codex

---

## Element 1 — Pull-quote (item 9)

**Candidate sentence** (from "What SVMs Changed"):

> "SVMs did not claim to contain human expertise. They did not claim to model
> the brain. They claimed to choose a disciplined boundary from data."

**Proposed insertion point:** Immediately after the paragraph ending "…They claimed to choose a disciplined boundary from data." in the "What SVMs Changed" section.

**Proposed render:**

```
:::note
> SVMs did not claim to contain human expertise. They did not claim to model
> the brain. They claimed to choose a disciplined boundary from data.

This three-part renunciation — no rules, no neuroscience, only geometry —
was the rhetorical and epistemic pivot that made SVMs credible after a decade
of AI promises that outran their operational proof.
:::
```

**Rationale:** The sentence trio is genuinely quote-worthy: it is the chapter's load-bearing historical claim stated in its most compressed form, and it names the intellectual pivot explicitly. The annotation does new work (labels the rhetorical strategy and connects it to the post-winter context) rather than paraphrasing. The sentence is not already quoted verbatim in prose — it appears as ordinary body text.

**Status: PROPOSED**

---

## Element 2 — Plain-reading aside: dual formulation paragraph (item 10)

**Target paragraph** (from "The Margin as a Contract"):

> "A reader did not have to begin with a full derivation of the dual problem or
> the Karush-Kuhn-Tucker conditions to grasp the historical point."

This paragraph is narrative, not symbolically dense — it explicitly tells the reader they do not need the math. A plain-reading aside would be redundant here.

**Status: SKIPPED** — paragraph is not symbolically dense; prose already performs the plain-reading job itself.

---

## Element 3 — Plain-reading aside: kernel-trick paragraph (item 10)

**Target paragraph** (from "The Kernel Move"):

> "One response is to transform the data into a richer feature space. In that
> space, a linear separator might become useful even if no simple separator
> worked in the original coordinates. The problem is that explicitly building a
> very high-dimensional feature space can be expensive or impossible to manage.
> The kernel move solves this in a beautifully machine-shaped way. Instead of
> constructing the high-dimensional vectors directly, the algorithm computes
> inner products through a kernel function."

**Proposed insertion point:** After this paragraph.

**Proposed render:**

```
:::tip[Plain reading]
The kernel trick lets the machine act as if it moved every training point into
a vast space of features — polynomial combinations, radial bumps, and so on —
without actually computing those high-dimensional coordinates. It only ever
computes one number: how similar two points are under the kernel. The
boundary it draws in the original space can be curved and complex; in the
implicit feature space it is still a flat, margin-maximising hyperplane.
:::
```

**Rationale:** The paragraph combines two ideas (feature-space transformation and inner-product substitution) that are abstractly stated and genuinely non-obvious to a reader without linear-algebra background. The aside does new work: it gives an intuitive picture (similarity score, curved boundary vs. flat hyperplane) that the prose does not supply. The aside is 3 sentences, within cap.

**Status: PROPOSED**

---

## Summary table

| Element | Type | Verdict |
|---|---|---|
| Pull-quote: "chose a disciplined boundary from data" | Pull-quote | PROPOSED |
| Plain-reading: dual-problem paragraph | Dense-paragraph aside | SKIPPED |
| Plain-reading: kernel-trick paragraph | Dense-paragraph aside | PROPOSED |
